from typing import Dict
import dag
from params import element_name, batch_size, nn_in_size, nn_out_size


generic_template = None

def _gen_generic_template():
    global generic_template
    generic_template = {
        "param_static_definitions": ";\n".join(
            f"static {element_name} param{p.name}[{p.count}]" for p in dag.all_params()
        ),
        "param_signatures": ", ".join(
            f"{element_name} param{p.name}[{p.count}]" for p in dag.all_params()
        ),
        "param_variables": ", ".join(f"param{p.name}" for p in dag.all_params()),

        "grad_static_definitions": ";\n".join(
            f"static {element_name} grad{p.name}[{p.count}]" for p in dag.all_params()
        ),
        "grad_signatures": ", ".join(
            f"{element_name} grad{p.name}[{p.count}]" for p in dag.all_params()
        ),
        "grad_variables": ", ".join(f"grad{p.name}" for p in dag.all_params()),

        "cache_static_definitions": ";\n".join(
            f"static hls::stream<{c.element_type}, {c.count * batch_size}> {c.name}" for c in dag.all_caches()
        ),
        "cache_signatures": ", ".join(
            f"hls::stream<{c.element_type}, {c.count * batch_size}>& {c.name}" for c in dag.all_caches()
        ),
        "cache_variables": ", ".join(
            c.name for c in dag.all_caches()
        ),

        "nn_in_size": nn_in_size,
        "nn_out_size": nn_out_size,
        "all_param_count": sum(p.count for p in dag.all_params()),
        
        "param_ram1p_pragmas": "\n    ".join(
            f"#pragma HLS INTERFACE mode=bram storage_type=ram_1p port=param{p.name} latency=1 depth={p.count}"
            for p in dag.all_params()
        ),
        "param_rom1p_pragmas": "\n    ".join(
            f"#pragma HLS INTERFACE mode=bram storage_type=rom_1p port=param{p.name} latency=1 depth={p.count}"
            for p in dag.all_params()
        ),
        "param_rom2p_pragmas": "\n    ".join(
            f"#pragma HLS INTERFACE mode=bram storage_type=rom_2p port=param{p.name} latency=1 depth={p.count}"
            for p in dag.all_params()
        ),
        "grad_ram1p_pragmas": "\n    ".join(
            f"#pragma HLS INTERFACE mode=bram storage_type=ram_1p port=grad{p.name} latency=1 depth={p.count}"
            for p in dag.all_params()
        ),
        "grad_rams2p_pragmas": "\n    ".join(
            f"#pragma HLS INTERFACE mode=bram storage_type=ram_s2p port=grad{p.name} latency=1 depth={p.count}"
            for p in dag.all_params()
        ),

        "cache_fifo_interface_pragmas": "\n    ".join(
            f"#pragma HLS INTERFACE mode=ap_fifo port={c.name} depth={c.count * batch_size}"
            for c in dag.all_caches()
        ),
        "cache_fifo_storage_pragmas": "\n    ".join(
            f"#pragma HLS BIND_STORAGE variable={c.name} type=fifo"
            for c in dag.all_caches()
        )
    }

def get_source_template_map(special_dict: Dict[str, str] = {}, /, **kwargs):
    if generic_template == None:
        _gen_generic_template()
    return {**generic_template, **special_dict, **kwargs}