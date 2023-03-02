from .generic_tcl import gen_tcl_of_ip

def gen_cache_tools_tcl(filename, source_filename):
    with open(filename, "w") as f:
        f.write(
            "\n".join(
                gen_tcl_of_ip(source_filename, None, ip_name, ip_name)
                for ip_name in ["cache_writter", "cache_reader", "cache_monitor"]
            )
        )
