from typing import List, Tuple
from template_loader import load_template
from dag import net, Param
from params import element_name

def _gen_signatures_pragmas_and_content(net_params: List[Param], name_prefix: str, storage_type: str, content_template: str) -> Tuple[str, str, str]:
    signatures = ",\n        ".join(
        (f"{element_name} {name_prefix}{p.name}[{p.count}]") for p in net_params
    )

    pragmas = "\n".join(
        (f"#pragma HLS INTERFACE mode=bram storage_type={storage_type} port={name_prefix}{p.name} latency=1") for p in net_params
    )

    readers = "\n".join((
        "\n".join((
            f"    for (int i = 0; i < {p.count}; ++i) {{",
            ("        " + content_template).format(name_prefix + p.name),
            f"    }}",
            "")
        ) for p in net_params
    ))

    return signatures, pragmas, readers
    

def gen_data_io_source(filename):
    template = load_template('data_io_source.cpp')

    filtered_params = list(net.all_params())

    param_signatures, param_pragmas, param_readers = (
        _gen_signatures_pragmas_and_content(filtered_params, "param", "ram_1p", "{}[i] = in.read();"))

    grad_signatures, grad_pragmas, grad_writers = (
        _gen_signatures_pragmas_and_content(filtered_params, "grad", "rom_1p", "out << {}[i];"))
    
    with open(filename, "w") as f:
        f.write(template.substitute(
            param_signatures=param_signatures,
            param_pragmas=param_pragmas,
            param_readers=param_readers,
            grad_signatures=grad_signatures,
            grad_pragmas=grad_pragmas,
            grad_writers=grad_writers
        ))
