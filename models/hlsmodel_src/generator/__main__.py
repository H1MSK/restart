import logging
from typing import Set, Tuple
from preprocess import extract_info_from_structure
from nn_ip_source import gen_nn_ip_source
from nn_ip_tcl import gen_nn_ip_tcl
from nn_ip_directives import gen_nn_ip_directives
from data_io_source import gen_data_io_source
from data_io_tcl import gen_data_io_tcl
from sys import argv

if __name__ == '__main__':
    print(f"argc={len(argv)}, argv={argv}")
    ip_src = argv[1]
    ip_tcl = argv[2]
    fw_directive = argv[3]
    bw_directive = argv[4]
    data_io_src = argv[5]
    data_io_tcl = argv[6]

    extract_info_from_structure()
    logging.info("Generating top functions...")
    gen_nn_ip_source(ip_src)
    logging.info("Generating top functions...")
    gen_nn_ip_directives(fw_directive, bw_directive)
    gen_nn_ip_tcl(ip_tcl, ip_src, [fw_directive, bw_directive], export_design=True)
    gen_data_io_source(data_io_src)
    gen_data_io_tcl(data_io_tcl, data_io_src)
