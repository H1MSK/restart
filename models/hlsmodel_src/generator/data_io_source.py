from typing import List, Tuple
from template_loader import load_template
from dag import net, Param
from params import element_name, nn_in_size, nn_out_size

def _gen_pl_content():
    contents = []

    contents.append("int x = 0;")
    contents.append("")

    for p in net.all_params():
        contents.append(f"for (int i = 0; i < {p.count}; ++i)")
        contents.append(f"    param{p.name}[i] = in[x++];")
        contents.append("")

    return "\n".join("    " + x for x in contents)

def _gen_ge_content():
    contents = []

    contents.append("int x = 0;")
    contents.append("")

    for p in net.all_params():
        contents.append(f"for (int i = 0; i < {p.count}; ++i)")
        contents.append(f"    out[x++] = grad{p.name}[i];")
        contents.append("")

    return "\n".join("    " + x for x in contents)

def gen_data_io_source(filename):
    template_strings = {
        "param_signatures": ", ".join(
            f"{element_name} param{p.name}[{p.count}]" for p in net.all_params()
        ),
        "grad_signatures": ", ".join(
            f"{element_name} grad{p.name}[{p.count}]" for p in net.all_params()
        ),

        "nn_in_size": nn_in_size,
        "nn_out_size": nn_out_size,
        "all_param_count": sum(p.count for p in net.all_params()),

        "param_ram1p_pragmas": "\n    ".join(
            f"#pragma HLS INTERFACE mode=bram storage_type=ram_1p port=param{p.name} latency=1"
            for p in net.all_params()
        ),
        "grad_ram1p_pragmas": "\n    ".join(
            f"#pragma HLS INTERFACE mode=bram storage_type=ram_1p port=grad{p.name} latency=1"
            for p in net.all_params()
        ),
        "param_loader_content": _gen_pl_content(),
        "grad_extractor_content": _gen_ge_content()
    }

    with open(filename, "w") as f:
        f.write(load_template('data_io_source.cpp').substitute(
            template_strings
        ))
