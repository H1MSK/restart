from .generic_source import get_source_template_map
from template_loader import load_template
import dag

def _gen_pl_content():
    contents = []

    contents.append("int x = 0;")
    contents.append("")

    for p in dag.all_params():
        contents.append(f"for (int i = 0; i < {p.count}; ++i)")
        contents.append(f"    param{p.name}[i] = in[x++];")
        contents.append("")

    return "\n".join("    " + x for x in contents)

def _gen_ge_content():
    contents = []

    contents.append("int x = 0;")
    contents.append("")

    for p in dag.all_params():
        contents.append(f"for (int i = 0; i < {p.count}; ++i)")
        contents.append(f"    out[x++] = grad{p.name}[i];")
        contents.append("")

    return "\n".join("    " + x for x in contents)

def gen_data_io_source(filename):
    with open(filename, "w") as f:
        f.write(load_template('data_io_source.cpp').substitute(
            get_source_template_map(
                param_loader_content=_gen_pl_content(),
                grad_extractor_content=_gen_ge_content(),
                zero_grads="\n        ".join(
                    f"memset(grad{p.name}, 0, sizeof(cm_float) * {p.count});" for p in dag.all_params()
                )
            )
        ))
