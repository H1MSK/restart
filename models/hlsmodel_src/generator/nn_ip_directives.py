from enum import Enum
import os
from params import *
import re

def _gen_target_ii():
    fw_directives = [
        'set_directive_pipeline -II 256 "run/ss"',
        'set_directive_pipeline -II 256 "run/sc1"',
        'set_directive_pipeline -II 256 "run/sc2"',
        'set_directive_pipeline -II 256 "run/sa"',

        'set_directive_pipeline -II 1 "forward_core/lfc_cal_i"',
        'set_directive_pipeline -II 256 "forward_core/lfc_o"',
        'set_directive_pipeline -II 256 "forward/tf"',
        'set_directive_pipeline -II 256 "forward/ef"'
    ]
    bw_directives = [
        'set_directive_pipeline -II 256 "run/ss"',
        'set_directive_pipeline -II 256 "run/sc1"',
        'set_directive_pipeline -II 256 "run/sc2"',
        'set_directive_pipeline -II 256 "run/sa"',

        'set_directive_pipeline -II 256 "backward/eb"',
        'set_directive_pipeline -II 1 "backward_output/lbo_cal_i"',
        'set_directive_pipeline -II 256 "backward_output/lbo_o"',
        'set_directive_pipeline -II 1 "backward_param_calc/lbw_i"',
        'set_directive_pipeline -II 256 "backward/tb"'
    ]
    return fw_directives, bw_directives

def gen_nn_ip_directives(fw_name, bw_name):
    # fw_ii, bw_ii = _find_target_ii(ip_tcl_name)
    fw_directives, bw_directives = _gen_target_ii()
    with open(fw_name, 'w') as f:
        f.writelines(x + '\n' for x in fw_directives)
    with open(bw_name, 'w') as f:
        f.writelines(x + '\n' for x in bw_directives)
