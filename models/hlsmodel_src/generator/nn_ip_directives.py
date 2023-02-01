from enum import Enum
import os
from params import *
import re

def _gen_target_ii():
    fast_pipelines = [
        "forward/lfc_cal_i",
        "forward_nc/lfn_cal_i",
        "backward_output/lbo_cal_i",
        "backward_param_calc/lbw_i"
    ]
    slow_pipelines = [
        "forward/lfc_o",
        "forward_nc/lfn_o",
        "backward/lbo_o",
        "forward/ef",
        "backward/eb",
        "forward/tf",
        "backward/tb",
        "forward/c2f_1",
        "forward/c2f_2",
        "forward/c3f_1",
        "forward/c3f_2",
        "forward/c3f_3",
        "backward/c2b_1",
        "backward/c2b_2",
        "backward/c3b_1",
        "backward/c3b_2",
        "backward/c3b_3",
        "forward/f2f",
        "forward/f3f",
        "backward/f2b",
        "backward/f3b",
        "run/f2r",
    ]
    directives = [
        f'set_directive_pipeline -II 256 "{x}"' for x in slow_pipelines
    ] + [
        f'set_directive_pipeline -II 1 "{x}"' for x in fast_pipelines
    ]
    return directives

def gen_nn_ip_directives(fw_name, bw_name):
    # fw_ii, bw_ii = _find_target_ii(ip_tcl_name)
    directives = _gen_target_ii()
    with open(fw_name, 'w') as f:
        f.writelines(x + '\n' for x in directives)
    with open(bw_name, 'w') as f:
        f.writelines(x + '\n' for x in directives)
