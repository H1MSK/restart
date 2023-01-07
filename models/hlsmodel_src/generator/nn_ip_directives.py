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
    if not os.path.exists('vitis_hls.log'):
        print("Systhesis once to get II information")
        ret = os.system(f"vitis_hls -l vitis_hls.log {ip_tcl_name}")
        assert(ret == 0)

    fw_ii, bw_ii = _extract_ii_from_log('vitis_hls.log')
    
    if fw_ii == -1 or bw_ii == -1:
        print("Failed extracting II information from log, try resynthesising...")
        ret = os.system(f"vitis_hls -l vitis_hls.log {ip_tcl_name}")
        assert(ret == 0)

    fw_ii, bw_ii = _extract_ii_from_log('vitis_hls.log')
    
    assert(fw_ii != -1 and bw_ii != -1)

    return [
        f"set_directive_pipeline -II {fw_ii} ef",
        f"set_directive_pipeline -II {fw_ii} ssf",
        f"set_directive_pipeline -II {fw_ii} scf1",
        f"set_directive_pipeline -II {fw_ii} scf2",
        f"set_directive_pipeline -II {fw_ii} saf",
        f"set_directive_pipeline -II {fw_ii} lfi",
        f"set_directive_pipeline -II {fw_ii} lfc",
        f"set_directive_pipeline -II {fw_ii} tf",

        f"set_directive_pipeline -II {bw_ii} eb",
        f"set_directive_pipeline -II {bw_ii} ssb",
        f"set_directive_pipeline -II {bw_ii} scb1",
        f"set_directive_pipeline -II {bw_ii} scb2",
        f"set_directive_pipeline -II {bw_ii} sab",
        f"set_directive_pipeline -II {bw_ii} lbwi",
        f"set_directive_pipeline -II {bw_ii} lbwo",
        f"set_directive_pipeline -II {bw_ii} lbw",
        f"set_directive_pipeline -II {bw_ii} lbi",
        f"set_directive_pipeline -II {bw_ii} lb",
        f"set_directive_pipeline -II {bw_ii} tb"
    ]

def gen_nn_ip_directives(filename, ip_tcl_name):
    directives = _gen_target_ii(ip_tcl_name)
    with open(filename, 'w') as f:
        f.writelines(x + '\n' for x in directives)