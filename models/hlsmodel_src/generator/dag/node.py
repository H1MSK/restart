from enum import Enum
from typing import List, Optional, Tuple
from params import element_bitwidth, element_name


class NodeType(Enum):
    Linear = 0x01,
    Tanh = 0x02,
    Exp = 0x03,
    ReLU = 0x04,

    Fork = 0x80,
    Cat = 0x81
    Input = 0x82,
    Output = 0x83


class NodeCacheType(Enum):
    NoCache = 0x00,
    CacheInput = 0x01,
    CacheOutput = 0x02,
    CustomCache = 0x03


def get_cache_type(node_type: NodeType):
    if node_type in (NodeType.Linear, ):
        return NodeCacheType.CacheInput
    elif node_type in (NodeType.Tanh, NodeType.Exp, ):
        return NodeCacheType.CacheOutput
    elif node_type in (NodeType.ReLU, ):
        return NodeCacheType.CustomCache
    else:
        return NodeCacheType.NoCache


class Channel:
    def __init__(self, predecessor, successor, /, data_count: int, data_bitwidth: int) -> None:
        self.predecessor: Node = predecessor
        self.successor: Node = successor
        self.data_bitwidth: int = data_bitwidth
        self.data_count: int = data_count
        self.name = None

    @property
    def is_valid(self):
        return (isinstance(self.predecessor, Node) and
                isinstance(self.successor, Node) and
                isinstance(self.data_count, int) and self.data_count > 0)

    def set_name(self, name):
        self.name = name

    def set_back_name(self, back_name):
        self.back_name = back_name

class Cache:
    def __init__(self, /, count: int, bitwidth: int, element_type: str, name: str = None) -> None:
        self.name = name
        self.count: int = count
        self.bitwidth: int = bitwidth
        self.element_type: str = element_type
        self.consumers: List[Node] = []

    _cache_count = 0

    @staticmethod
    def from_node(node):
        Cache._cache_count += 1
        kth = Cache._cache_count
        cache_type = get_cache_type(node.type)
        cache_element_type = element_name

        assert (cache_type != NodeCacheType.NoCache)
        if cache_type == NodeCacheType.CacheInput:
            count = node.first_input_size
            bitwidth = element_bitwidth
        elif cache_type == NodeCacheType.CacheOutput:
            count = node.first_input_size
            bitwidth = element_bitwidth
        else:
            # Custom cache type
            if node.type == NodeType.ReLU:
                count = node.first_input_size
                bitwidth = 1
                cache_element_type = 'ap_uint<1>'
            raise NotImplementedError

        return Cache(count=count, bitwidth=bitwidth,
                     name=f"cache{kth}_{count}w{bitwidth}",
                     element_type=cache_element_type)


class Param:
    def __init__(self, /, count: int, name: str = None) -> None:
        self.name: str = name
        self.count: int = count
        # self.bitwidth: int = None
        # self.consumer: Node = None

    _param_count = 0

    @staticmethod
    def from_node(node):
        Param._param_count += 1
        kth = Param._param_count
        if node.type == NodeType.Linear:
            count = (node.first_input_size+1) * node.first_output_size
        else:
            raise NotImplementedError

        return Param(count=count,
                     name=f"{kth}L_{count}o{node.first_output_size}w{element_bitwidth}")


class Node:
    _node_count = 0
    def __init__(self, node_type: NodeType, /) -> None:

        self.type = node_type
        self.class_name: str = ""

        Node._node_count += 1
        self.kth = Node._node_count

        self.inputs: List[Channel] = []
        self.outputs: List[Channel] = []
        self.param: Param = None
        self.cache: Cache = None

    @staticmethod
    def add_link(pred, succ, /, bitwidth=element_bitwidth, count=None, channel: Optional[Channel] = None):
        if channel == None:
            assert (isinstance(count, int) and count > 0)
            channel = Channel(pred, succ,
                              data_bitwidth=bitwidth,
                              data_count=count)
        else:
            channel.predecessor = pred
            channel.successor = succ
            assert (channel.is_valid)
        pred.outputs.append(channel)
        succ.inputs.append(channel)

    @staticmethod
    def del_link(pred, succ):
        pos_pred = 0
        while pos_pred < len(pred.outputs) and pred.outputs[pos_pred].successor != succ:
            pos_pred += 1

        pos_succ = 0
        while pos_succ < len(succ.inputs) and succ.inputs[pos_succ].predecessor != pred:
            pos_succ += 1

        assert (pos_pred < len(pred.outputs) and pos_succ < len(succ.inputs))

        c1 = pred.outputs.pop(pos_pred)
        c2 = succ.inputs.pop(pos_succ)
        assert (c1 is c2)

        return c1

    @property
    def first_input_size(self):
        try:
            return self.inputs[0].data_count
        except IndexError:
            return -1

    @property
    def first_output_size(self):
        try:
            return self.outputs[0].data_count
        except IndexError:
            return -1

    @property
    def need_generate_cache(self):
        return self.cache != None and self.cache.consumers[0] == self

    @property
    def is_cache_transparent(self):
        return self.type == NodeType.Fork

    def bind_param(self, param: Param):
        self.param = param

    def bind_cache(self, cache: Cache):
        self.cache = cache
        cache.consumers.append(self)

    def __repr__(self):
        return f"{str(self.type).split('.')[1]}{self.kth}i{self.first_input_size}o{self.first_output_size}"
