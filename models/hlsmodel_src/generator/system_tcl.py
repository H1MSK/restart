from itertools import chain
import math
from preprocess import Info
from template_loader import load_template
from params import *

def _gen_memory_scripts():
    scripts=[]

    for g in filter(None, Info.param_name):
        template = load_template("system", "param_memory.tcl")
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
        template = load_template("system", "grad_memory.tcl")
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

def _gen_bram_rst_connections():
    grads = (
        f"connect_bd_net [get_bd_pins gpio_connection/grad_reset] [get_bd_pins mem_{n}/rsta]"
        for n in filter(None, Info.grad_name))
    params = (
        f"connect_bd_net [get_bd_pins gpio_connection/param_reset] [get_bd_pins mem_{n}/rsta]"
        for n in filter(None, Info.param_name)
    )
    return '\n'.join(
        chain(grads, params)
    )

def _gen_bram_mux_sel_connections():
    return '\n'.join(
        f"connect_bd_net [get_bd_pins gpio_connection/bram_sel] [get_bd_pins mux_{n}/sel]"
        for n in filter(None, chain(Info.param_name, Info.grad_name))
    )

def _gen_param_rsta_busy_out_scripts():
    return '\n'.join(
        f"connect_bd_net [get_bd_pins concat_param_reset/In{i}] [get_bd_pins mem_{name}/rsta_busy]"
        for i, name in enumerate(filter(None, Info.param_name))
    )

def _gen_grad_rsta_busy_out_scripts():
    return '\n'.join(
        f"connect_bd_net [get_bd_pins concat_grad_reset/In{i}] [get_bd_pins mem_{name}/rsta_busy]"
        for i, name in enumerate(filter(None, Info.grad_name))
    )

def _gen_cache_scripts():
    scripts=[]
    template = load_template("system", "cache.tcl")
    for n, i in zip(Info.cache_name, Info.cache_info):
        if n == None:
            continue
        scripts.append(template.substitute(
            cache_name=n,
            cache_size_upscale=str(2 ** math.ceil(math.log2(i.size * batch_size)))
        ))
    return '\n'.join(scripts)

def gen_system_tcl(filename):
    with open(filename, "w") as f:
        f.write(load_template("system.tcl").substitute(
            memory_scripts=_gen_memory_scripts(),
            bram_rst_connections=_gen_bram_rst_connections(),
            bram_mux_sel_connections=_gen_bram_mux_sel_connections(),
            param_count=len(list(filter(None, Info.param_name))),
            cache_scripts=_gen_cache_scripts(),
            param_rsta_busy_out_scripts=_gen_param_rsta_busy_out_scripts(),
            grad_rsta_busy_out_scripts=_gen_grad_rsta_busy_out_scripts(),
        ))
