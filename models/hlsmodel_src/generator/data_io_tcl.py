from params import *

def gen_data_io_tcl(filename, source_name):
    with open(filename, "w") as f:
        f.write(f"""\
open_project build_param_loader
open_solution -flow_target vivado sol
add_files {source_name}
create_clock -period {synthesis_clock_period_ns}ns
set_part {part_name}
set_top param_loader

csynth_design
export_design -format ip_catalog -ipname param_loader

open_project build_grad_extractor
open_solution -flow_target vivado sol
add_files {source_name}
create_clock -period {synthesis_clock_period_ns}ns
set_part {part_name}
set_top grad_extractor

csynth_design
export_design -format ip_catalog -ipname grad_extractor
""")
