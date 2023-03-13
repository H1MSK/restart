from collections import deque
from typing import Deque, List, Mapping, Set, Tuple, Iterable
import typing
from .dag import Dag, _logger
from .node import Node, NodeType, Channel
import onnx
import onnx.checker


def _get_node_attribute(attrs: Iterable[onnx.AttributeProto], name, item, default):
    for attr in attrs:
        if attr.name == name:
            return getattr(attr, item, default)
    return default


def _calculate_data_count(shape: onnx.TensorShapeProto) -> int:
    count = 1
    for x in shape.dim:
        if x.HasField('dim_param'):
            assert(x.dim_param == 'batch_size')
        else:
            assert(x.HasField('dim_value'))
            count *= x.dim_value
    return count


_dt_bw_lut = {
    onnx.TensorProto.FLOAT: 32,
}


def _bitwidth_from_data_type(t: int):
    return _dt_bw_lut[t]


class DagFromOnnx(Dag):
    def __init__(self) -> None:
        super().__init__()
        self.onnx_model = None

    def build_from_onnx(
            self,
            onnx_file: str,
            /,
            output_debug_pngs = False):
        _logger.info("Building dag from onnx...")
        self._load_model(onnx_file)
        self._build_skeleton_from_model()
        if output_debug_pngs:
            self.output_dag("generated.1.skeleton.dag.png")
        _logger.info("Trimming...")
        self._trim_dag()
        if output_debug_pngs:
            self.output_dag("generated.2.trimmed.dag.png")
        _logger.info("Binding params and caches...")
        self._bind_params()
        if output_debug_pngs:
            self.output_dag("generated.3.param.dag.png")
        self._bind_caches()
        if output_debug_pngs:
            self.output_dag("generated.4.param_and_cache.dag.png")
        _logger.info("Generating names for channels...")
        self._set_channel_names()
        if output_debug_pngs:
            self.output_dag("generated.5.channel_names.dag.png")
        self._generate_class_names()
        _logger.info("Build finished")

    def _load_model(self, onnx_file):
        model = onnx.load(onnx_file)
        onnx.checker.check_model(model, full_check=True)
        self.onnx_model = model

    def _build_skeleton_from_model(self):
        graph = self.onnx_model.graph

        # Generate all nodes(to self.nodes) and channel providers/consumers
        providers, consumers, channel_data_count, channel_data_bitwidth = self._generate_link_info(
            graph)

        assert(sorted(providers.keys()) == sorted(consumers.keys()))

        # Param infomation for detecting output size
        param_shapes: Mapping[str, Tuple[int]] = {}
        for p in graph.initializer:
            param_shapes[p.name] = p.dims

        # Connect skeleton, insert Fork node on need
        for name in providers.keys():
            provider, idx = providers[name]
            consumer = consumers[name]
            bitwidth = channel_data_bitwidth[name]
            count = channel_data_count[name]
            if len(consumer) > 1:
                fork_node = Node(NodeType.Fork)
                self.nodes.append(fork_node)
                assert(len(provider.outputs) == idx)
                Node.add_link(provider, fork_node,
                              bitwidth=bitwidth, count=count)
                for c in consumer:
                    Node.add_link(fork_node, c,
                                  bitwidth=bitwidth, count=count)
            else:
                Node.add_link(
                    provider, consumer[0], bitwidth=bitwidth, count=count)

    def _generate_link_info(self, graph: onnx.GraphProto):
        _propogate_queue: Deque[str] = deque()
        _propogated_channels: Set[str] = set()
        _node_output_channels: Mapping[Node, List[str]] = {}

        providers: Mapping[str, Tuple[Node, int]] = {}
        consumers: Mapping[str, List[Node]] = {}
        channel_data_count: Mapping[str, int] = {}
        channel_data_bitwidth: Mapping[str, int] = {}

        def add_propogate_start_point(name, count, bitwidth):
            if name not in _propogated_channels:
                channel_data_count.setdefault(name, count)
                channel_data_bitwidth.setdefault(name, bitwidth)
                _propogate_queue.append(name)
                _propogated_channels.add(name)
            else:
                assert(count == channel_data_count[name] and
                       bitwidth == channel_data_bitwidth[name])

        param_data_types: Mapping[str, Tuple[list]] = {
            x.name: x.data_type for x in graph.initializer}

        param_shapes: Mapping[str, Tuple[list]] = {
            x.name: tuple(x.dims) for x in graph.initializer}

        # input
        providers[graph.input[0].name] = (self.input, 0)
        _node_output_channels.setdefault(
            self.input, []).append(graph.input[0].name)
        # TODO: split a single input into multiple graph inputs
        assert(len(graph.input) == 1)
        channel_data_count[graph.input[0].name] = _calculate_data_count(
            graph.input[0].type.tensor_type.shape)
        channel_data_bitwidth[graph.input[0].name] = _bitwidth_from_data_type(
            graph.input[0].type.tensor_type.elem_type)
        _propogate_queue.append(graph.input[0].name)
        _propogated_channels.add(graph.input[0].name)

        # content
        for node_proto in graph.node:
            if node_proto.op_type == "Gemm":
                node_type = NodeType.Linear
                weight_name = node_proto.input[1]
                weight_shape = param_shapes[weight_name]
                if _get_node_attribute(node_proto.attribute, 'transB', 'i', 0) == 1:
                    weight_shape = weight_shape[::-1]
                input_count = weight_shape[0]
                input_bitwidth = _bitwidth_from_data_type(
                    param_data_types[weight_name])
                output_count = weight_shape[1]
                output_bitwidth = _bitwidth_from_data_type(
                    param_data_types[weight_name])
            elif node_proto.op_type == "Tanh":
                node_type = NodeType.Tanh
                input_count = -1
                input_bitwidth = -1
                output_count = -1
                output_bitwidth = -1
            elif node_proto.op_type == "Exp":
                node_type = NodeType.Exp
                input_count = -1
                input_bitwidth = -1
                output_count = -1
                output_bitwidth = -1
            n = Node(node_type)
            self.nodes.append(n)
            assert(len(node_proto.output) == 1)

            for i, output in enumerate(node_proto.output):
                providers[output] = (n, i)
                _node_output_channels.setdefault(n, []).append(output)
                if output_count != -1:
                    add_propogate_start_point(
                        output, output_count, output_bitwidth)

            input_name = node_proto.input[0]
            assert(input_name not in (x.name for x in graph.initializer))
            consumers.setdefault(input_name, []).append(n)
            if input_count != -1:
                add_propogate_start_point(
                    input_name, input_count, input_bitwidth)

        # Output
        if len(graph.output) > 1:
            concat_node = Node(NodeType.Cat)
            self.nodes.append(concat_node)
            all_count = 0
            all_bitwidth = -1
            for output in graph.output:
                consumers.setdefault(output.name, []).append(concat_node)
                count = _calculate_data_count(output.type.tensor_type.shape)
                bitwidth = _bitwidth_from_data_type(
                    output.type.tensor_type.elem_type)
                if all_bitwidth == -1:
                    all_bitwidth = bitwidth
                else:
                    assert(all_bitwidth == bitwidth)
                add_propogate_start_point(output.name, count, bitwidth)
                all_count += count
            assert("output_concat" not in providers.keys())
            assert("output_concat" not in consumers.keys())
            providers["output_concat"] = (concat_node, 0)
            _node_output_channels.setdefault(
                concat_node, []).append("output_concat")
            consumers["output_concat"] = [self.output, ]
            add_propogate_start_point("output_concat", all_count, all_bitwidth)
        else:
            consumers[graph.output[0].name] = [self.output, ]
            count = _calculate_data_count(
                graph.output[0].type.tensor_type.shape)
            bitwidth = _bitwidth_from_data_type(
                graph.output[0].type.tensor_type.elem_type)
            add_propogate_start_point(graph.output[0].name, count, bitwidth)

        # Data count and bitwidth
        while len(_propogate_queue) > 0:
            channel = _propogate_queue.popleft()
            for consumer in consumers[channel]:
                if consumer.type in (NodeType.Exp, NodeType.Tanh):
                    assert(len(_node_output_channels[consumer]) == 1)
                    name = _node_output_channels[consumer][0]
                    add_propogate_start_point(
                        name,
                        channel_data_count[channel],
                        channel_data_bitwidth[channel])
                # else:
                #     raise NotImplementedError

        # Completeness check
        all_channels = set(providers.keys())
        assert(all_channels == set(consumers.keys()) and
               all_channels == set(channel_data_count.keys()) and
               all_channels == set(channel_data_bitwidth.keys()))

        return providers, consumers, channel_data_count, channel_data_bitwidth
