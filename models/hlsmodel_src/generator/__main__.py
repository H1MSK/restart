import logging
from typing import Set, Tuple
from preprocess import extract_info_from_structure
from nn_ip_source import gen_nn_ip_source
from nn_ip_tcl import gen_nn_ip_tcl
from nn_ip_directives import gen_nn_ip_directives
from sys import argv

if __name__ == '__main__':
    print(f"argc={len(argv)}, argv={argv}")
    ip_top = argv[1]
    ip_tcl = argv[2]
    ip_directive = argv[3]

    extract_info_from_structure()
    logging.info("Generating top functions...")
    gen_nn_ip_source(ip_top)
    logging.info("Generating top functions...")
    gen_nn_ip_tcl(ip_tcl, ip_top, None)
    gen_nn_ip_directives(ip_directive, ip_tcl)
    gen_nn_ip_tcl(ip_tcl, ip_top, ip_directive, export_design=True)
