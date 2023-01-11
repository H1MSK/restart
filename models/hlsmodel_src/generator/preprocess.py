from typing import List, Optional
from params import *
from collections import namedtuple

ForkInfo = namedtuple('ForkInfo', ['fork_nodes'])
PathInfo = namedtuple('PathInfo', ['fork_start', 'kth'])
CacheInfo = namedtuple('CacheInfo', ['element_name', 'size'])

class Info:
    fork_info: List[Optional[ForkInfo]] = []

    path_info: List[Optional[PathInfo]] = []

    param_size = []
    node_in_size = []
    node_out_size = []
    cache_info: List[Optional[CacheInfo]] = []

def _gen_fork_info():

    fork_pos = []
    fork_count = []
    forkpath_pos: List[List[int]] = []
    current_path_info = [PathInfo(-1, 0)]
    for kth, info in enumerate(nn_structures):
        Info.fork_info.append(None)

        if info[0] == "Fork":
            fork_pos.append(kth)
            fork_count.append(0)
            forkpath_pos.append([kth])
            current_path_info.append(PathInfo(kth, 0))
        elif info[0] == "ForkAgain":
            fork_count[-1] += 1
            forkpath_pos[-1].append(kth)
            current_path_info[-1] = PathInfo(current_path_info[-1].fork_start, fork_count[-1])
        elif info[0] == "Cat":
            forkpath_pos[-1].append(kth)
            
            Info.fork_info[-1] = Info.fork_info[fork_pos[-1]] = ForkInfo(forkpath_pos[-1])
            
            fork_count.pop()
            fork_pos.pop()
            forkpath_pos.pop()
            current_path_info.pop()

        Info.path_info.append(None if info[0] == "Cat" else current_path_info[-1])

    assert(len(fork_pos) == 0)
    assert(len(fork_count) == 0)
    assert(len(forkpath_pos) == 0)

def _gen_param_size():

    param_size_mapper = {
        "Linear": lambda info: info[1] * info[2] + info[2]
    }
    def _cal_param_size(layer_info):
        try:
            return param_size_mapper[layer_info[0]](layer_info)
        except KeyError:
            return None
    Info.param_size = list(_cal_param_size(x) for x in nn_structures)

def _gen_node_size():
    node_size_mapper = {
        "Linear": (lambda info: info[1], lambda info: info[2]),
        "Tanh": (lambda info: info[1], lambda info: info[1]),
        "Exp": (lambda info: info[1], lambda info: info[1]),
        "Fork": (lambda info: info[1], lambda info: info[1]),
        "Cat": (lambda info: 0, lambda info: info[1]),
    }

    def _cal_node_size(info, ith_lambda):
        try:
            m = node_size_mapper[info[0]]
            return m[ith_lambda](info)
        except KeyError:
            return 0

    Info.node_in_size = list(_cal_node_size(info, 0) for info in nn_structures)
    Info.node_out_size = list(_cal_node_size(info, 1) for info in nn_structures)

def _gen_cache_info():

    param_size_mapper = {
        "Linear": lambda info: CacheInfo(element_name, info[1]),
        "Tanh": lambda info: CacheInfo(element_name, info[1]),
        "Exp": lambda info: CacheInfo(element_name, info[1]),
    }
    def _cal_param_size(kth, layer_info):
        try:
            return param_size_mapper[layer_info[0]](layer_info)
        except KeyError:
            return None
    Info.cache_info = list(_cal_param_size(k, x) for k, x in enumerate(nn_structures))

def extract_info_from_structure():
    _gen_fork_info()
    _gen_param_size()
    _gen_node_size()
    _gen_cache_info()
