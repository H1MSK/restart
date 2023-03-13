from collections import deque
from typing import Deque, Dict, List, Optional, Tuple
from .node import Cache, Channel, Node, NodeType, Param, NodeCacheType, get_cache_type
from params import nn_in_size
from .dag import Dag, _logger


class DagFromStructures(Dag):
    def __init__(self) -> None:
        super().__init__()
        self.structures = None
    def build_from_structure(
            self,
            nn_structures: Tuple[Tuple[str, int, Optional[int]]],
            /,
            output_debug_pngs=False):
        _logger.info("Building dag from defined structure...")
        self._build_skeleton_from_structures(nn_structures)
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

    def _build_skeleton_from_structures(self, nn_structures):

        input_stack: List[Node] = []
        predecessor = self.input
        fork_tails: List[List[Node]] = []
        output_sizes: Dict[Node, int] = {self.input: nn_in_size}

        plain_nets = {
            "Linear": NodeType.Linear,
            "Tanh": NodeType.Tanh,
            "Exp": NodeType.Exp,
            "ReLU": NodeType.ReLU
        }

        def _get_output_size(info, pred: Node):
            if info[0] == "Linear":
                return info[1]
            return output_sizes[pred]

        for info in nn_structures:
            if info[0] == "Fork":
                current = Node(NodeType.Fork)
                self.nodes.append(current)
                input_stack.append(current)
                Node.add_link(predecessor, current,
                              count=output_sizes[predecessor])
                fork_tails.append([])
                output_sizes[current] = output_sizes[predecessor]
                predecessor = current
            elif info[0] == "ForkAgain":
                fork_tails[-1].append(predecessor)
                predecessor = input_stack[-1]
            elif info[0] == "Cat":
                current = Node(NodeType.Cat)
                fork_tails[-1].append(predecessor)
                self.nodes.append(current)
                total_count = 0
                for tail in fork_tails[-1]:
                    this_count = output_sizes[tail]
                    total_count += this_count
                    Node.add_link(tail, current, count=this_count)
                fork_tails.pop()
                output_sizes[current] = total_count
                input_stack.pop()
                predecessor = current
            else:
                # Doesn't catch KeyError
                node_type = plain_nets[info[0]]
                current = Node(node_type)
                self.nodes.append(current)
                Node.add_link(predecessor, current,
                              count=output_sizes[predecessor])
                output_sizes[current] = _get_output_size(info, predecessor)
                predecessor = current

        Node.add_link(predecessor, self.output,
                      count=output_sizes[predecessor])
