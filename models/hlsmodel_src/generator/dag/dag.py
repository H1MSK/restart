from collections import deque
from typing import Deque, Dict, List, Optional, Tuple
from .node import Cache, Channel, Node, NodeType, Param, NodeCacheType, get_cache_type
from params import nn_in_size
import logging

_logger = logging.getLogger("Dag")

class Dag:
    def __init__(self) -> None:
        self.nodes: List[Node] = []
        self.input = Node(NodeType.Input)
        self.output = Node(NodeType.Output)

    def build_from_onnx(self, onnx_file, /, output_debug_pngs = False):
        raise NotImplementedError

    def build_from_structure(self, nn_structures, /, output_debug_pngs = False):
        raise NotImplementedError

    def _generate_class_names(self):
        for n in self.nodes:
            # Generate function name
            if n.type == NodeType.Fork:
                class_name = f"Fork{len(n.outputs)}<{n.first_input_size}>"
            elif n.type == NodeType.Cat:
                class_name = f"Cat{len(n.inputs)}<{', '.join(str(x.data_count) for x in n.inputs)}>"
            elif n.type == NodeType.Linear:
                class_name = f"{str(n.type).split('.')[1]}<{n.first_input_size}, {n.first_output_size}>"
            else:
                class_name = f"{str(n.type).split('.')[1]}<{n.first_input_size}>"
            n.class_name = f"{class_name}"

    def _trim_dag(self):
        removed_nodes: List[Node] = []
        for node in self.nodes:
            if node in removed_nodes:
                continue
            if node.type in (NodeType.Fork, NodeType.Cat):
                _logger.debug(f"Trying to merge {node} with others...")
                merge_root = node
                merge_size = 0
                scan_queue = deque((node, ))
                input_channels: List[Channel] = node.inputs.copy()
                output_channels: List[Channel] = []
                while len(scan_queue) > 0:
                    cur = scan_queue.popleft()
                    merge_size += 1
                    _logger.debug(f"Inspecting {node} with {len(node.inputs)} inputs and {len(node.outputs)} outputs...")
                    for x in cur.inputs:
                        if (last := x.predecessor).type != node.type:
                            _logger.debug(f"Node {last} is an input.")
                            input_channels.append(x)
                        elif last != merge_root and last not in removed_nodes:
                            _logger.debug(f"Node {node} is mergable.")
                            Node.del_link(x.predecessor, x.successor)
                            removed_nodes.append(last)
                            scan_queue.append(last)
                    for x in cur.outputs:
                        if (next := x.successor).type != node.type:
                            _logger.debug(f"Node {next} is an output.")
                            output_channels.append(x)
                        elif next != merge_root and next not in removed_nodes:
                            _logger.debug(f"Node {node} is mergable.")
                            Node.del_link(x.predecessor, x.successor)
                            removed_nodes.append(next)
                            scan_queue.append(next)
                if merge_size > 1:
                    for ch in input_channels:
                        if ch.successor != merge_root:
                            Node.del_link(ch.predecessor, ch.successor)
                            Node.add_link(ch.predecessor, merge_root, channel=ch)
                    for ch in output_channels:
                        if ch.predecessor != merge_root:
                            Node.del_link(ch.predecessor, ch.successor)
                            Node.add_link(merge_root, ch.successor, channel=ch)
                    _logger.info(f"Merged {merge_size} nodes into {merge_root}.")
                else:
                    _logger.debug("Not trimable.")
        for n in removed_nodes:
            assert(len(n.inputs) == 0 and len(n.outputs) == 0)
            self.nodes.remove(n)

    def _bind_params(self):
        for node in self.nodes:
            if node.type == NodeType.Linear:
                node.bind_param(param=Param.from_node(node))

    def all_nodes(self):
        yield self.input
        for n in self.nodes:
            yield n
        yield self.output

    def bfs_nodes(self):
        """Returns a generator to do BFS on dag

        send False to generator to stop bfs from current node

        Yields:
            Node: current node
        """        
        visit_count: Dict[Node, int] = {x: 0 for x in self.nodes}
        visit_count.setdefault(self.input, -1)
        visit_count.setdefault(self.output, 0)
        que: Deque[Node] = deque((self.input, ))
        while len(que) > 0:
            front = que.popleft()
            visit_count[front] += 1
            if visit_count[front] == len(front.inputs):
                ret = yield front
                if ret == None or ret:
                    for x in front.outputs:
                        que.append(x.successor)

    def all_params(self):
        for n in self.nodes:
            if n.param != None:
                yield n.param

    def all_caches(self):
        for n in self.nodes:
            if n.need_generate_cache:
                yield n.cache

    def _mark_cache_id(self):
        """Scan for cache reusability

        If successive nodes cache identical elements, their cache are reusable

        Returns:
            Dict[Node, int]: Nodes with same number can share one cache, except 0 for unreusable
        """
        reusable_cache_id = {x: 0 for x in self.nodes}
        reusable_count = 0
        visited_nodes = set()
        _logger.info("Exploring cache shareability...")
        for node in self.nodes:
            if node in visited_nodes:
                continue
            
            if (cache_type := get_cache_type(node.type)) == NodeCacheType.CustomCache:
                _logger.info(f"Cache for {repr(node)} is not shareable.")
                visited_nodes.add(node)
                reusable_count += 1
                reusable_cache_id[node] = reusable_count
            elif cache_type == NodeCacheType.CacheOutput or node.is_cache_transparent:
                mergable_nodes = [node, ]
                scan_queue = deque((node, ))
                while len(scan_queue) > 0:
                    cur = scan_queue.popleft()
                    visited_nodes.add(cur)
                    for ch in cur.outputs:
                        suc = ch.successor
                        if get_cache_type(suc.type) == NodeCacheType.CacheInput:
                            visited_nodes.add(suc)
                            mergable_nodes.append(suc)
                        elif suc.is_cache_transparent:
                            mergable_nodes.append(suc)
                            scan_queue.append(suc)
                reusable_count += 1
                kth = reusable_count
                share_count = 0
                for n in mergable_nodes:
                    if not n.is_cache_transparent:
                        reusable_cache_id[n] = kth
                        share_count += 1
                if share_count > 1:
                    _logger.info(f"Cache#{kth} is shared by {len(mergable_nodes)} nodes.")
                else:
                    _logger.info(f"Cache#{kth} is not shareable.")

            elif cache_type != NodeCacheType.NoCache:
                reusable_count += 1
                reusable_cache_id[node] = reusable_count

        return reusable_cache_id

    def _bind_caches(self):
        reusable_cache_id = self._mark_cache_id()
        reusable_caches: Dict[int, Cache] = {}
        for x in self.nodes:
            if (id := reusable_cache_id[x]) != 0:
                try:
                    x.bind_cache(reusable_caches[id])
                    continue
                except KeyError:
                    # TODO: Use additional information to check which node creates
                    #       the cache. In current implementaion, it's the node that
                    #       first occurs in self.nodes
                    cache = Cache.from_node(x)
                    x.bind_cache(cache)
                    reusable_caches[id] = cache

    def _set_channel_names(self):
        for n in self.all_nodes():
            if len(n.outputs) == 1:
                n.outputs[0].set_name(f"{repr(n)}_o")
                continue
            for k, ch in enumerate(n.outputs):
                ch.set_name(f"{repr(n)}_o{k}")
        for n in self.all_nodes():
            if len(n.inputs) == 1:
                n.inputs[0].set_back_name(f"{repr(n)}_ro")
                continue
            for k, ch in enumerate(n.inputs):
                ch.set_back_name(f"{repr(n)}_ro{k}")
        assert(len(self.input.outputs) == 1 and
               len(self.output.inputs) == 1)
        self.input.outputs[0].set_name("in_x")
        self.output.inputs[0].set_name("out_y")
        self.output.inputs[0].set_back_name("in_grad_y")

    def output_dag(self, filename):
        import pydot
        graph = pydot.Dot("DAG", graph_type="graph")
        node_name: Dict[Node, str] = {}
        for node in self.bfs_nodes():
            name = repr(node)
            if node.param != None:
                name += "\nparam" + node.param.name
            if node.cache != None:
                name += "\n" + node.cache.name
            node_name[node] = name
            graph.add_node(pydot.Node(name=name))
            for o in node.inputs:
                graph.add_edge(pydot.Edge(
                    node_name[o.predecessor],
                    node_name[o.successor],
                    label=f"{o.data_count}w{o.data_bitwidth}"))
        graph.write_png(filename)

    def report_cache_usage(self)->str:
        report = ""
        for n in self.nodes:
            if n.cache != None and n.cache.consumers[0] == n:
                report += (
                    f"{n.cache.name}:\n"
                    f"    count:{n.cache.count}\n"
                    f"    bitwidth:{n.cache.bitwidth}\n"
                    f"    type:{n.cache.element_type}\n"
                    f"    consumers:{n.cache.consumers}\n"
                    "\n")
        return report

    def report_param_usage(self)->str:
        report = ""
        for n in self.nodes:
            if n.param != None:
                report += (
                    f"param{n.param.name}:{n.param.count}\n"
                )
        return report
