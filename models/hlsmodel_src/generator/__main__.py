import logging
import dag
from nn_ip_source import gen_nn_ip_source
from nn_ip_tcl import gen_nn_ip_tcl
from nn_ip_directives import gen_nn_ip_directives
from nn_ip_simulation_compile import gen_nn_ip_simulation_product
from data_io_source import gen_data_io_source
from data_io_tcl import gen_data_io_tcl
from system_tcl import gen_system_tcl
from params import *

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    ip_src = "generated.nn.cpp"
    ip_tcl = "generated.nn.tcl"
    fw_directive = "generated.fw_directives.tcl"
    bw_directive = "generated.bw_directives.tcl"
    data_io_src = "generated.data_io.cpp"
    data_io_tcl = "generated.data_io.tcl"
    system_tcl = "generated.system.tcl"
    pg_system_tcl = "generated.pg_system.tcl"
    ip_sim_src = "generated.nn.sim.cpp"
    ip_test_src = "generated.nn.test.cpp"
    post_system_sh = "generated.wait_and_export.sh"

    dag.build()

    dag.net.output_dag("generated.dag.png")
    with open("generated.cache_usage.txt", "w") as f:
        f.write(dag.net.report_cache_usage())
    with open("generated.param_usage.txt", "w") as f:
        f.write(dag.net.report_param_usage())

    struct_id = f"{nn_in_size}.{act_size}.{nn_hidden_size}.{1 if act_continuous else 0}"
    ip_sim_lib = f"generated.nn.sim.{struct_id}.so"

    gen_nn_ip_source(ip_src, ip_sim_src, ip_test_src)
    gen_nn_ip_directives(fw_directive, bw_directive)
    gen_nn_ip_tcl(ip_tcl, ip_src, [fw_directive, bw_directive], export_design=True)
    gen_data_io_source(data_io_src)
    gen_data_io_tcl(data_io_tcl, data_io_src)
    gen_nn_ip_simulation_product(ip_sim_lib, [ip_src, ip_sim_src, data_io_src])
    gen_system_tcl(system_tcl, pg_system_tcl, post_system_sh, struct_id)
