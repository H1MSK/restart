from typing import Optional
from generic_tcl import gen_tcl_of_ip

def gen_nn_ip_tcl(filename, ip_source_name, ip_directive, /):
    with open(filename, "w") as f:
        f.write(
            gen_tcl_of_ip(ip_source_name, ip_directive, "forward", "top_forward") +
            gen_tcl_of_ip(ip_source_name, ip_directive, "backward", "top_backward"))