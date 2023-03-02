from .generic_tcl import gen_tcl_of_ip

def gen_data_io_tcl(filename, source_name):
    with open(filename, "w") as f:
        f.write(
            gen_tcl_of_ip(source_name, None, "param_loader", "param_loader",
                          customized_directives="config_interface -m_axi_addr64=false") +
            gen_tcl_of_ip(source_name, None, "grad_extractor", "grad_extractor",
                          customized_directives="config_interface -m_axi_addr64=false"))
