from typing import List
import os
import logging

_logger = logging.getLogger("IpSimCompil")


def gen_nn_ip_simulation_product(output_name, include_files: List[str]):
    _logger.info("Starting compiling simulation file for ip...")
    ret = os.system(
        f"g++ -fPIC -shared -o {output_name} {' '.join(x for x in include_files)} "
        " -I hls_headers -Wall -Wextra -Wno-unknown-pragmas -Wno-unused-label")
    if ret == 0:
        _logger.info("Compile succeeded.")
    else:
        _logger.error("Error occurs in compilation.")
        exit(1)