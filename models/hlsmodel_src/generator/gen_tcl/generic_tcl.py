from typing import Iterable, Optional
from params import *

def gen_tcl_of_ip(source_filename, directive_filename, ip_name, top_name, /, customized_directives=""):
    source_directive_cmd = f'source {directive_filename}' if directive_filename != None else ""
    return f"""\
open_project build_{ip_name}
open_solution -flow_target vivado sol
add_files {source_filename}
create_clock -period {synthesis_clock_period_ns}ns
set_clock_uncertainty {synthesis_clock_uncertainty}
set_part {part_name}
set_top {top_name}
{source_directive_cmd}
{customized_directives}

csynth_design
export_design -format ip_catalog -ipname {ip_name}
"""
