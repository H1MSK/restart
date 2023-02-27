from template_loader import load_template
from dag import net
import math
from params import batch_size

def gen_cache_debug_mux():
    with open("generated_cache_debug_mux.v", "w") as f:
        f.write(load_template("system", "cache_debug_mux.v").substitute(
            input_ports=",\n    ".join(f"input[{math.ceil(math.log2(c.count * batch_size))}:0] cnt_{c.name}" for c in net.all_caches()),
            out_width=f"{math.ceil(math.log2(max(c.count * batch_size for c in net.all_caches())))}",
            selects=";\n            ".join(f"'d{i}: cnt_o <= cnt_{c.name}" for i, c in enumerate(net.all_caches())),
            cache_cnt=len(list(net.all_caches()))
        ))