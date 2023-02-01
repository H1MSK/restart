from itertools import chain
import math
from dag import net
from template_loader import load_template
from params import *

def _gen_memory_scripts():
    scripts=[]
    param_template = load_template("system", "param_memory.tcl")
    grad_template = load_template("system", "grad_memory.tcl")

    for param in net.all_params():
        param_name = "param" + param.name
        grad_name = "grad" + param.name
        scripts.append(
            param_template.substitute(
                mem_name=f"mem_{param_name}",
                mux_name=f"mux_{param_name}",
                porta=f"{param_name}_PORTA",
                portb=f"{param_name}_PORTB",
                instance="param_loader"
            )
        )
        scripts.append(
            grad_template.substitute(
                mem_name=f"mem_{grad_name}",
                mux_name=f"mux_{grad_name}",
                porta=f"{grad_name}_PORTA",
                portb=f"{grad_name}_PORTB",
                instance="grad_extractor"
            )
        )

    return "\n".join(scripts)

def _gen_bram_rst_connections():
    grads = (
        f"connect_bd_net [get_bd_pins gpio_connection/grad_reset] [get_bd_pins mem_grad{p.name}/rsta]"
        for p in net.all_params())
    params = (
        f"connect_bd_net [get_bd_pins gpio_connection/param_reset] [get_bd_pins mem_param{p.name}/rsta]"
        for p in net.all_params())
    return '\n'.join(
        chain(grads, params)
    )

def _gen_bram_mux_sel_connections():
    return '\n'.join(
        f"connect_bd_net [get_bd_pins gpio_connection/bram_sel] [get_bd_pins mux_param{p.name}/sel]\n"
        f"connect_bd_net [get_bd_pins gpio_connection/bram_sel] [get_bd_pins mux_grad{p.name}/sel]"
        for p in net.all_params())

def _gen_param_rsta_busy_out_scripts():
    return '\n'.join(
        f"connect_bd_net [get_bd_pins concat_param_reset/In{i}] [get_bd_pins mem_param{p.name}/rsta_busy]"
        for i, p in enumerate(net.all_params()))

def _gen_grad_rsta_busy_out_scripts():
    return '\n'.join(
        f"connect_bd_net [get_bd_pins concat_grad_reset/In{i}] [get_bd_pins mem_grad{p.name}/rsta_busy]"
        for i, p in enumerate(net.all_params()))

def _gen_cache_scripts():
    scripts=[]
    template = load_template("system", "cache.tcl")
    for cache in net.all_caches():
        scripts.append(template.substitute(
            cache_name=cache.name,
            cache_size=cache.count*batch_size,
            cache_addr_width=math.floor(math.log2(cache.count*batch_size - 1))+1
        ))
    return '\n'.join(scripts)

def gen_system_tcl(filename):
    with open(filename, "w") as f:
        f.write(load_template("system.tcl").substitute(
            memory_scripts=_gen_memory_scripts(),
            bram_rst_connections=_gen_bram_rst_connections(),
            bram_mux_sel_connections=_gen_bram_mux_sel_connections(),
            param_count=len(list(net.all_params())),
            cache_scripts=_gen_cache_scripts(),
            param_rsta_busy_out_scripts=_gen_param_rsta_busy_out_scripts(),
            grad_rsta_busy_out_scripts=_gen_grad_rsta_busy_out_scripts(),
        ))
