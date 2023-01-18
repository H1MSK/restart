from itertools import chain
from preprocess import Info
from template_loader import load_template

def _gen_memory_scripts():
    template = load_template("system", "memory.tcl")
    scripts=[]

    for g in filter(None, Info.param_name):
        scripts.append(
            template.substitute(
                mem_name=f"mem_{g}",
                mux_name=f"mux_{g}",
                porta=f"{g}_PORTA",
                portb=f"{g}_PORTB",
                instance="param_loader"
            )
        )

    for g in filter(None, Info.grad_name):
        scripts.append(
            template.substitute(
                mem_name=f"mem_{g}",
                mux_name=f"mux_{g}",
                porta=f"{g}_PORTA",
                portb=f"{g}_PORTB",
                instance="grad_extractor"
            )
        )

    return "\n".join(scripts)

def _gen_grad_rst_connections():
    return '\n'.join(
        f"connect_bd_net [get_bd_pins gpio_out_0/Dout] [get_bd_pins mem_{n}/rsta]"
        for n in filter(None, Info.grad_name)
    )

def _gen_bram_mux_sel_connections():
    return '\n'.join(
        f"connect_bd_net [get_bd_pins gpio_out_1/Dout] [get_bd_pins mux_{n}/sel]"
        for n in filter(None, chain(Info.param_name, Info.grad_name))
    )

def _gen_grad_rst_busy_connections():
    return '\n'.join(
        f"connect_bd_net [get_bd_pins mem_grad_rst_busy_concat/In{i}] [get_bd_pins mem_{name}/rsta_busy]"
        for i, name in enumerate(filter(None, Info.grad_name))
    )

def gen_system_tcl(filename):
    template = load_template("system.tcl")
    with open(filename, "w") as f:
        f.write(load_template("system.tcl").substitute(
            memory_scripts=_gen_memory_scripts(),
            grad_rst_connections=_gen_grad_rst_connections(),
            bram_mux_sel_connections=_gen_bram_mux_sel_connections(),
            param_count=len(list(filter(None, Info.param_name))),
            grad_rst_busy_connections=_gen_grad_rst_busy_connections()
        ))
