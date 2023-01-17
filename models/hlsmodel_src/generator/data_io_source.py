from typing import List, Tuple
from preprocess import Info
import os
import string

def _gen_signatures_pragmas_and_content(filtered_list: List[Tuple[str, int]], storage_type: str, content_template: str) -> Tuple[str, str, str]:
    signatures = ",\n        ".join(
        (f"cm_float {n}[{s}]") for n, s in filtered_list
    )

    pragmas = "\n".join(
        (f"#pragma HLS INTERFACE mode=bram storage_type={storage_type} port={n} latency=1") for n, s in filtered_list
    )

    readers = "\n".join((
        "\n".join((
            f"    for (int i = 0; i < {s}; ++i) {{",
            ("        " + content_template).format(n),
            f"    }}",
            "")
        ) for n, s in filtered_list
    ))

    return signatures, pragmas, readers
    

def gen_data_io_source(filename):
    with open(os.path.join(
        os.path.dirname(__file__),
        "templates",
        "data_io_source_template.cpp"
    ), "r") as f:
        template = f.read()

    template = string.Template(template)

    filtered_params = list(filter(lambda x: isinstance(x[0], str), zip(Info.param_name, Info.param_size)))

    param_signatures, param_pragmas, param_readers = (
        _gen_signatures_pragmas_and_content(filtered_params, "ram_1p", "{}[i] = in.read();"))

    filtered_params = list(filter(lambda x: isinstance(x[0], str), zip(Info.grad_name, Info.param_size)))

    grad_signatures, grad_pragmas, grad_writers = (
        _gen_signatures_pragmas_and_content(filtered_params, "rom_1p", "out << {}[i];"))
    
    with open(filename, "w") as f:
        f.write(template.substitute(
            param_signatures=param_signatures,
            param_pragmas=param_pragmas,
            param_readers=param_readers,
            grad_signatures=grad_signatures,
            grad_pragmas=grad_pragmas,
            grad_writers=grad_writers
        ))
