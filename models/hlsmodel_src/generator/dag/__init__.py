from .dag import Dag
from .node import NodeType, Node, Param, Cache

_net: Dag = None
_all_params = []
_all_nodes = []
_all_caches = []
_bfs_nodes = []

def _prepare_iterables():
    global _all_params
    global _all_nodes
    global _all_caches
    global _bfs_nodes
    _all_params = list(_net.all_params())
    _all_nodes = list(_net.all_nodes())
    _all_caches = list(_net.all_caches())
    _bfs_nodes = list(_net.bfs_nodes())

def build_from_structures(output_debug_pngs=False):
    global _net
    from params import nn_structures
    from .dag_from_structures import DagFromStructures
    _net = DagFromStructures()
    _net.build_from_structure(nn_structures, output_debug_pngs=output_debug_pngs)
    _prepare_iterables()

def build_from_onnx_file(file, output_debug_pngs=False):
    global _net
    from .dag_from_onnx import DagFromOnnx
    _net = DagFromOnnx()
    _net.build_from_onnx(file, output_debug_pngs=output_debug_pngs)
    _prepare_iterables()

def all_params():
    return _all_params

# Include virtual input and output
def all_nodes():
    return _all_nodes

def nodes():
    return _net.nodes

def output_node():
    return _net.output

def bfs_nodes():
    return _net.bfs_nodes()

def all_caches():
    return _all_caches

def output_dag(filename):
    _net.output_dag(filename)

def report_cache_usage():
    return _net.report_cache_usage()

def report_param_usage():
    return _net.report_param_usage()
