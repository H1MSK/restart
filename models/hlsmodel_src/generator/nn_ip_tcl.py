from params import *

def gen_nn_ip_tcl(filename, ip_source_name):
    with open(filename, "w") as f:
        f.write(f"""\
open_project build

open_solution -flow_target vivado sol_forward
add_files -cflags {ip_source_name}
create_clock -period {clock_period}
set_part {part_name}
set_top forward

csynth_design
export_design -format ip_catalog -ipname forward


open_solution -flow_target vivado sol_backward
add_files -cflags {ip_source_name}
create_clock -period {clock_period}
set_part {part_name}
set_top backward

csynth_design
export_design -format ip_catalog -ipname backward

""")
