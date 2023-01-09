from enum import Enum
import os
from params import *
import re

def _extract_ii_from_log(log_file):
    class State(Enum):
        IDLE = 1
        FW = 2
        BW = 3
    fw_ii = -1
    bw_ii = -1
    state = State.IDLE
    pattern = re.compile(r"Final II = (\d+)")
    with open(log_file, "r") as f:
        for line in f:
            if state == State.IDLE:
                if line.find('sol_forward') != -1:
                    state = State.FW
            elif state == State.FW:
                items = pattern.findall(line)
                if len(items):
                    print(f"Updated fw: {items}")
                    fw_ii = max(fw_ii, int(items[0]))
                if line.find('sol_backward') != -1:
                    state = State.BW
            elif state == State.BW:
                items = pattern.findall(line)
                if len(items):
                    print(f"Updated bw: {items}")
                    bw_ii = max(bw_ii, int(items[0]))
    return fw_ii, bw_ii

def _gen_target_ii(ip_tcl_name):
    fw_ii = -1
    bw_ii = -1
    if os.path.exists('vitis_hls.log'):
        fw_ii, bw_ii = _extract_ii_from_log('vitis_hls.without_directives.log')
        if fw_ii != -1 and bw_ii != -1:
            return

    if os.path.exists('vitis_hls.without_directives.log'):
        fw_ii, bw_ii = _extract_ii_from_log('vitis_hls.without_directives.log')
        if fw_ii != -1 and bw_ii != -1:
            return

    print("Systhesis once to get II information")
    ret = os.system(f"vitis_hls -l vitis_hls.without_directives.log {ip_tcl_name}")
    assert(ret == 0)

    fw_ii, bw_ii = _extract_ii_from_log('vitis_hls.without_directives.log')
    
    if fw_ii == -1 or bw_ii == -1:
        print("Failed extracting II information from log.")
        exit(1)

    return [
        f'set_directive_pipeline -II {fw_ii} "forward/ef"',
        f'set_directive_pipeline -II {fw_ii} "forward/ssf"',
        f'set_directive_pipeline -II {fw_ii} "forward/scf1"',
        f'set_directive_pipeline -II {fw_ii} "forward/scf2"',
        f'set_directive_pipeline -II {fw_ii} "forward/saf"',
        f'set_directive_pipeline -II {fw_ii} "forward/lfi"',
        f'set_directive_pipeline -II {fw_ii} "forward/lfc"',
        f'set_directive_pipeline -II {fw_ii} "forward/tf"',

        f'set_directive_pipeline -II {bw_ii} "backward/eb"',
        f'set_directive_pipeline -II {bw_ii} "backward/ssb"',
        f'set_directive_pipeline -II {bw_ii} "backward/scb1"',
        f'set_directive_pipeline -II {bw_ii} "backward/scb2"',
        f'set_directive_pipeline -II {bw_ii} "backward/sab"',
        f'set_directive_pipeline -II {bw_ii} "backward/lbwi"',
        f'set_directive_pipeline -II {bw_ii} "backward/lbwo"',
        f'set_directive_pipeline -II {bw_ii} "backward/lbw"',
        f'set_directive_pipeline -II {bw_ii} "backward/lbi"',
        f'set_directive_pipeline -II {bw_ii} "backward/lb"',
        f'set_directive_pipeline -II {bw_ii} "backward/tb"'
    ]

def gen_nn_ip_directives(filename, ip_tcl_name):
    directives = _gen_target_ii(ip_tcl_name)
    with open(filename, 'w') as f:
        f.writelines(x + '\n' for x in directives)