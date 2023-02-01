from .dag import DAG
from params import nn_structures
from .node import NodeType, Node, Param, Cache

net = DAG()

def build():
    net.build_from_structure(nn_structures)
