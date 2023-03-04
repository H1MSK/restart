from .generic_source import get_source_template_map
from template_loader import load_template
from dag import net

def gen_cache_tools_source(cache_debugger_filename):
    with open(cache_debugger_filename, "w") as f:
        f.write(load_template("cache_tools_source.cpp").substitute(
            get_source_template_map(
            cache_writter_cases="\n    ".join(
                f"case {i+1}: {c.name} << val; break;" for i, c in enumerate(net.all_caches())
            ),
            cache_reader_cases="\n    ".join(
                f"case {i+1}: *val = {c.name}.read(); break;" for i, c in enumerate(net.all_caches())
            ),
            cache_monitor_inputs=", ".join(f"int {c.name}_in" for c in net.all_caches()),
            cache_monitor_outputs=", ".join(f"int *{c.name}_out" for c in net.all_caches()),
            cache_monitor_pragmas="\n    ".join((
                f"#pragma HLS INTERFACE mode=ap_none port={c.name}_in\n    "
                f"#pragma HLS INTERFACE mode=s_axilite port={c.name}_out"
                ) for c in net.all_caches()),
            cache_monitor_content="\n    ".join((
                    f"*{c.name}_out = {c.name}_in;"
                ) for c in net.all_caches()),
            cache_loader_content="\n    ".join((
                    f"for (int i = 0; i < {c.count}; ++i) {c.name} << src[x++];"
                ) for c in net.all_caches()
            ),
            cache_extractor_content="\n    ".join((
                    f"for (int i = 0; i < {c.count}; ++i) dst[x++] = {c.name}.read();"
                ) for c in net.all_caches()
            ),
        )))
