import os
from params import *


class _IpTclTemplate:
    def __init__(self, /, ip_name: str, node_type: str, top_file_f: str, top_name_f: str, top_file_b: str, top_name_b: str) -> None:
        self.ip_name = ip_name
        self.node_type = node_type
        self.top_file_f = top_file_f
        self.top_name_f = top_name_f
        self.top_file_b = top_file_b
        self.top_name_b = top_name_b

    def gen(self, *params):
        ip_name_str = self.ip_name.format(*params)
        node_type_str = self.node_type.format(*params)
        return f"""\
        # {node_type_str} forward
        open_solution -flow_target vivado sol_{ip_name_str}_f
        add_files -cflags "-DNodeType={node_type_str}" {self.top_file_f.format(*params)}
        create_clock -period {clock_period}
        set_part {part_name}
        set_top {self.top_name_f.format(*params)}
        csynth_design
        export_design -format ip_catalog -ipname {ip_name_str}_f
        
        # {node_type_str} backward
        open_solution -flow_target vivado sol_{ip_name_str}_b
        add_files -cflags "-DNodeType={node_type_str}" {self.top_file_b.format(*params)}
        create_clock -period {clock_period}
        set_part {part_name}
        set_top {self.top_name_b.format(*params)}
        csynth_design
        export_design -format ip_catalog -ipname {ip_name_str}_b
        
        
        """


_templates = {
    "Linear": _IpTclTemplate(
        ip_name="linear{}_{}",
        node_type="Linear<{},{}>",
        top_name_f="top_forward_p",
        top_file_f="top_pg.cpp",
        top_name_b="top_backward_p",
        top_file_b="top_pg.cpp"),
    "Tanh": _IpTclTemplate(
        ip_name="tanh{}",
        node_type="Tanh<{}>",
        top_name_f="top_forward",
        top_file_f="top_g.cpp",
        top_name_b="top_backward",
        top_file_b="top_g.cpp"),
    "Exp": _IpTclTemplate(
        ip_name="exp{}",
        node_type="Exp<{}>",
        top_name_f="top_forward",
        top_file_f="top_g.cpp",
        top_name_b="top_backward",
        top_file_b="top_g.cpp"),
}


def gen_build_ip_tcl(filename):
    created_layers = {name: set() for name in _templates.keys()}
    with open(filename, "w") as f:
        f.write("""\
            open_project nn_ips
            
            """)
        for item in nn_structures:
            if item is str:
                layer_type = item
            else:
                layer_type = item[0]
            params = item[1:]
            if params not in created_layers[layer_type]:
                created_layers[layer_type].add(params)
                bulk = _templates[layer_type].gen(*params)
                f.write(bulk)