from typing import Iterable, Optional
from params import *

_gen_separately = True

def gen_nn_ip_tcl(filename, ip_source_name, directive_names: Optional[Iterable[str]] = None, /, export_design = False):
    fw_source_directive = f'source {directive_names[0]}' if directive_names != None else ""
    bw_source_directive = f'source {directive_names[1]}' if directive_names != None else ""
    with open(filename, "w") as f:
        if _gen_separately:
            f.write(f"""\
open_project build_forward
open_solution -flow_target vivado sol
add_files {ip_source_name}
create_clock -period {synthesis_clock_period_ns}ns
set_clock_uncertainty {synthesis_clock_uncertainty}
set_part {part_name}
set_top top_forward
{fw_source_directive}

csynth_design
{'export_design -format ip_catalog -ipname forward' if export_design else ''}

open_project build_backward
open_solution -flow_target vivado sol
add_files {ip_source_name}
create_clock -period {synthesis_clock_period_ns}ns
set_clock_uncertainty {synthesis_clock_uncertainty}
set_part {part_name}
set_top top_backward
{bw_source_directive}

csynth_design
{'export_design -format ip_catalog -ipname backward' if export_design else ''}
""")
        else:
            f.write(f"""\
open_project build_nn_ip
open_solution -flow_target vivado sol
add_files {ip_source_name}
create_clock -period {synthesis_clock_period_ns}ns
set_clock_uncertainty {synthesis_clock_uncertainty}
set_part {part_name}
set_top nn_ip
{fw_source_directive}
{bw_source_directive}

csynth_design
{'export_design -format ip_catalog -ipname nn_ip' if export_design else ''}
""")