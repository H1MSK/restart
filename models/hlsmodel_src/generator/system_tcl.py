import math
from dag import net
from template_loader import load_template
from params import *
import os, stat

def _gen_memory_scripts():
    scripts=[]
    memory_template = load_template("system", "memory.tcl")

    for param in net.all_params():
        scripts.append(
            memory_template.substitute(
                suffix=param.name,
                mem_depth=param.count,
                mem_bitwidth=element_bitwidth,
            )
        )

    return "\n".join(scripts)

def _gen_pg_memory_scripts():
    scripts=[]
    memory_template = load_template("pg_system", "memory.tcl")

    for param in net.all_params():
        scripts.append(
            memory_template.substitute(
                suffix=param.name,
                mem_depth=param.count,
                mem_bitwidth=element_bitwidth,
            )
        )

    return "\n".join(scripts)

def _gen_param_rst_connections():
    params = (
        f"connect_bd_net [get_bd_pins gpio_connection/param_reset] [get_bd_pins mux_param{p.name}/inj_rst]"
        for p in net.all_params())
    return '\n'.join(params)

def _gen_grad_rst_connections():
    grads = (
        f"connect_bd_net [get_bd_pins gpio_connection/grad_reset] [get_bd_pins mux_grad{p.name}/inj_rst]"
        for p in net.all_params())
    return '\n'.join(grads)

def _gen_grad_mux_sel_connections():
    return '\n'.join(
        f"connect_bd_net [get_bd_pins gpio_connection/bram_sel] [get_bd_pins mux_grad{p.name}/sel]"
        for p in net.all_params())

def _gen_param_mux_sel_connections():
    return '\n'.join(
        f"connect_bd_net [get_bd_pins gpio_connection/bram_sel] [get_bd_pins mux_param{p.name}/sel]"
        for p in net.all_params())

def _gen_param_rstb_busy_out_scripts():
    return '\n'.join(
        f"connect_bd_net [get_bd_pins concat_param_reset/In{i}] [get_bd_pins mem_param{p.name}/rstb_busy]"
        for i, p in enumerate(net.all_params()))

def _gen_grad_rstb_busy_out_scripts():
    return '\n'.join(
        f"connect_bd_net [get_bd_pins concat_grad_reset/In{i}] [get_bd_pins mem_grad{p.name}/rstb_busy]"
        for i, p in enumerate(net.all_params()))

def _gen_cache_scripts():
    scripts=[]
    template = load_template("system", "cache.tcl")
    for cache in net.all_caches():
        scripts.append(template.substitute(
            cache_name=cache.name,
            cache_size=cache.count*batch_size,
            cache_addr_width=math.ceil(math.log2(cache.count*batch_size)),
            use_cache_debug_bridge=use_cache_debug_bridge,
            cache_on_bridge_module=cache_on_bridge_module,
            cache_off_bridge_module=cache_off_bridge_module
        ))
    return '\n'.join(scripts)

def gen_system_tcl(filename, pg_filename, post_filename, struct_id):
    mapping = {
        "param_rst_connections": _gen_param_rst_connections(),
        "grad_rst_connections": _gen_grad_rst_connections(),
        "param_mux_sel_connections": _gen_param_mux_sel_connections(),
        "grad_mux_sel_connections": _gen_grad_mux_sel_connections(),
        "param_count": len(list(net.all_params())),
        "cache_scripts": _gen_cache_scripts(),
        "param_rstb_busy_out_scripts": _gen_param_rstb_busy_out_scripts(),
        "grad_rstb_busy_out_scripts": _gen_grad_rstb_busy_out_scripts(),
        "system_clk_mhz": implement_clock_period_MHz
    }
    with open(filename, "w") as f:
        f.write(load_template("system.tcl").substitute(
            mapping,
            memory_scripts=_gen_memory_scripts(),
            use_cache_debug_bridge=use_cache_debug_bridge,
            cache_on_bridge_module=cache_on_bridge_module,
            cache_off_bridge_module=cache_off_bridge_module
        ))
    with open(pg_filename, "w") as f:
        f.write(load_template("pg_system.tcl").substitute(
            mapping,
            memory_scripts=_gen_pg_memory_scripts()
        ))

    with open(post_filename, "w") as f:
        f.write(load_template("system", "wait_and_export.sh").substitute(
            struct_id=struct_id
        ))

    os.chmod(post_filename, stat.S_IRWXU | stat.S_IRWXG | stat.S_IXOTH)
