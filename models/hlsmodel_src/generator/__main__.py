from typing import Set, Tuple
from preprocess import extract_info_from_structure
from nn_ip_source import gen_nn_ip_source
from nn_ip_tcl import gen_nn_ip_tcl
from sys import argv

if __name__ == '__main__':
    extract_info_from_structure()
    gen_nn_ip_source(argv[1])
    gen_nn_ip_tcl(argv[2], argv[1])
