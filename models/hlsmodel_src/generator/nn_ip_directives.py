from enum import Enum
import os
from params import *
import re

def _gen_target_ii(ip_tcl_name):
    return [
        'set_directive_pipeline -II 256 "run/ss"',
        'set_directive_pipeline -II 256 "run/sc1"',
        'set_directive_pipeline -II 256 "run/sc2"',
        'set_directive_pipeline -II 256 "run/sa"',

        'set_directive_pipeline -II 1 "forward_core/lfc_cal_i"',
        'set_directive_pipeline -II 256 "forward_core/lfc_o"',
        'set_directive_pipeline -II 256 "forward/tf"',
        'set_directive_pipeline -II 256 "forward/ef"',

        'set_directive_pipeline -II 256 "backward/eb"',
        'set_directive_pipeline -II 1 "backward_output/lbo_cal_i"',
        'set_directive_pipeline -II 256 "backward_output/lbo_o"',
        'set_directive_pipeline -II 256 "backward_param_calc/lbw_i"',
        'set_directive_pipeline -II 256 "backward/tb"'
    ]

def gen_nn_ip_directives(filename, ip_tcl_name):
    directives = _gen_target_ii(ip_tcl_name)
    with open(filename, 'w') as f:
        f.writelines(x + '\n' for x in directives)