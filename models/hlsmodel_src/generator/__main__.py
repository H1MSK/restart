import logging
import dag

from gen_sources.nn_ip import gen_nn_ip_source
from gen_tcl.nn_ip import gen_nn_ip_tcl
from gen_tcl.nn_ip_directives import gen_nn_ip_directives
from nn_ip_simulation_compile import gen_nn_ip_simulation_product

from gen_sources.data_io import gen_data_io_source
from gen_tcl.data_io import gen_data_io_tcl

from gen_sources.cache_tools import gen_cache_tools_source
from gen_tcl.cache_tools import gen_cache_tools_tcl

from system_tcl import gen_system_tcl
from params import *

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    struct_id = f"{nn_in_size}.{act_size}.{nn_hidden_size}.{1 if act_continuous else 0}"

    ip_src = "generated.nn.cpp"
    ip_sim_src = "generated.nn.sim.cpp"
    ip_test_src = "generated.nn.test.cpp"
    ip_tcl = "generated.nn.tcl"
    ip_directive = "generated.directives.tcl"
    
    data_io_src = "generated.data_io.cpp"
    data_io_tcl = "generated.data_io.tcl"

    cache_debugger_src = "generated.cache_tools.cpp"
    cache_debugger_tcl = "generated.cache_tools.tcl"

    ip_sim_lib = f"generated.nn.sim.{struct_id}.so"
    
    system_tcl = "generated.system.tcl"
    pg_system_tcl = "generated.pg_system.tcl"
    
    post_system_sh = "generated.wait_and_export.sh"

    dag.build()

    dag.net.output_dag("generated.dag.png")
    with open("generated.cache_usage.txt", "w") as f:
        f.write(dag.net.report_cache_usage())
    with open("generated.param_usage.txt", "w") as f:
        f.write(dag.net.report_param_usage())

    gen_nn_ip_source(ip_src, ip_sim_src, ip_test_src)
    gen_nn_ip_directives(ip_directive)
    gen_nn_ip_tcl(ip_tcl, ip_src, ip_directive)

    gen_data_io_source(data_io_src)
    gen_data_io_tcl(data_io_tcl, data_io_src)

    gen_cache_tools_source(cache_debugger_src)
    gen_cache_tools_tcl(cache_debugger_tcl, cache_debugger_src)

    gen_nn_ip_simulation_product(ip_sim_lib, [ip_src, ip_sim_src, data_io_src])

    gen_system_tcl(system_tcl, pg_system_tcl, post_system_sh, struct_id)
