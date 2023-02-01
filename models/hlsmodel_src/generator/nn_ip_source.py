from enum import Enum
from typing import List
from params import *
import logging
from template_loader import load_template
from dag import net, NodeType

_logger = logging.getLogger("nn_ip_source")

fw_general_port_signature = []
bw_general_port_signature = []
param_port_signature = []
grad_port_signature = []
fw_cache_port_signature = []
bw_cache_port_signature = []

fw_general_hls_pragma = []
bw_general_hls_pragma = []
param_port_hls_pragma = []
grad_port_hls_pragma = []
fw_cache_port_hls_pragma = []
bw_cache_port_hls_pragma = []

def _gen_param_info():
    # Params = Static input + static output + generated params + generated cache

    # Forward has axis output out_y. The T_READY in the interface can be used to drive ap_continue
    # Backward doesn't have other output than fifo and bram, so it can use hs
    fw_general_hls_pragma.append("INTERFACE mode=ap_ctrl_chain port=return")
    bw_general_hls_pragma.append("INTERFACE mode=ap_ctrl_hs port=return")

    fw_general_hls_pragma.append("DATAFLOW")
    bw_general_hls_pragma.append("DATAFLOW")

    fw_general_port_signature.append(f"hls::stream<{element_name}, {nn_in_size}>& in_x")
    fw_general_hls_pragma.append(f"INTERFACE mode=axis port=in_x register_mode=reverse depth={nn_in_size}")

    fw_general_port_signature.append(f"hls::stream<{element_name}, {nn_out_size}>& out_y")
    fw_general_hls_pragma.append(f"INTERFACE mode=axis port=out_y register_mode=forward depth={nn_out_size}")

    fw_general_port_signature.append(f"bool cache_en")
    fw_general_hls_pragma.append(f"INTERFACE mode=ap_none port=cache_en")
    fw_general_hls_pragma.append(f"STABLE variable=cache_en")

    bw_general_port_signature.append(f"hls::stream<{element_name}, {nn_out_size}>& in_grad_y")
    bw_general_hls_pragma.append(f"INTERFACE mode=axis port=in_grad_y register_mode=reverse depth={nn_out_size}")

    for p in net.all_params():
        param_name = 'param' + p.name
        grad_name = 'grad' + p.name
        param_port_signature.append(f"cm_float {param_name}[{p.count}]")
        param_port_hls_pragma.append(f"INTERFACE mode=bram storage_type=rom_1p port={param_name} latency=1")
        grad_port_signature.append(f"cm_float {grad_name}[{p.count}]")
        grad_port_hls_pragma.append(f"INTERFACE mode=bram storage_type=ram_s2p port={grad_name} latency=1")

    for cache in net.all_caches():
        cache_element = cache.element_type
        size = cache.count
        fw_cache_port_signature.append(f"hls::stream<{cache_element}>& {cache.name}")
        fw_cache_port_hls_pragma.append(f"INTERFACE mode=ap_fifo port={cache.name} depth={size * batch_size}")
        bw_cache_port_signature.append(f"hls::stream<{cache_element}>& {cache.name}")
        bw_cache_port_hls_pragma.append(f"INTERFACE mode=ap_fifo port={cache.name} depth={size * batch_size}")

def _gen_fw_content():
    _logger.info("Generating forward content...")
    contents = []

    for n in net.nodes:

        # Add comment to indicate code for which node
        contents.append(f"// {repr(n)}")

        # Generate function name
        if n.type == NodeType.Fork:
            class_name = f"Fork{len(n.outputs)}<{n.first_input_size}>"
        elif n.type == NodeType.Cat:
            class_name = f"Cat{len(n.inputs)}<{', '.join(str(x.data_count) for x in n.inputs)}>"
        elif n.type == NodeType.Linear:
            class_name = f"{str(n.type).split('.')[1]}<{n.first_input_size}, {n.first_output_size}>"
        else:
            class_name = f"{str(n.type).split('.')[1]}<{n.first_input_size}>"
        function_name = f"{class_name}::forward"

        # Generate parameters
        parameters = []
        if n.param != None:
            parameters.append(f"param{n.param.name}")
        for ch in n.inputs:
            parameters.append(ch.name)
        for ch in n.outputs:
            parameters.append(ch.name)
        if n.need_generate_cache:
            parameters.append(n.cache.name)
            parameters.append("cache_en")

        # Add output stream on need
        for ch in n.outputs:
            if ch == net.output.inputs[0]:
                continue
            contents.append(f"hls::stream<{element_name}, {ch.data_count}> {ch.name};")
        
        # Add function call
        contents.append(function_name + '(')
        for x in parameters[:-1]:
            contents.append("    " + x + ",")
        contents.append("    " + parameters[-1] + ");")
        contents.append("")

    _logger.info("Done.")
    return "\n".join("    " + x for x in contents)

def _gen_fw_function():
    return load_template("nn_ip", "function.cpp").substitute(
        function_name='top_forward',
        param_signatures=', '.join(fw_general_port_signature + param_port_signature + fw_cache_port_signature),
        param_hls_pragmas='\n'.join('    #pragma HLS ' + p for p in (fw_general_hls_pragma + param_port_hls_pragma + fw_cache_port_hls_pragma)),
        content=_gen_fw_content()
    )

def _find_bw_passes():
    _logger.info("Marking trimmable backward pathes...")
    passed_nodes = set()
    start_nodes = set()
    g = net.bfs_nodes()
    cur = next(g)

    try:
        while True:
            if cur.param != None:
                _logger.debug(f"{repr(cur)} is start node.")
                start_nodes.add(cur)
                cur = g.send(False)
            else:
                _logger.debug(f"{repr(cur)} can be trimmed.")
                passed_nodes.add(cur)
                cur = g.send(True)
    except StopIteration:
        pass

    # passed_nodes.add(net.input)
    passed_nodes.add(net.output)

    return passed_nodes, start_nodes

def _gen_bw_content():
    _logger.info("Generating backward content...")
    contents: List[str] = []
    passed_nodes, start_nodes = _find_bw_passes()
    reversed_nodes = reversed(list(net.bfs_nodes()))
    _logger.debug(passed_nodes)
    for n in reversed_nodes:
        if n in passed_nodes:
            continue

        # Split cache if it has more than 1 consumers
        # Since one backward function call will only consume one group of cache,
        # the batch_size is not multiplied in cache.count
        if (cache := n.cache) != None and len(cache.consumers) > 1 and n == cache.consumers[-1]:
            contents.append(f"// {cache.name}")
            for k in range(len(cache.consumers)):
                contents.append(
                    f"hls::stream<{cache.element_type}, {cache.count}> {cache.name}_{k};"
                )
            contents.append(f"Fork{len(cache.consumers)}<{cache.count}>::forward(")
            contents.append(f"    {cache.name}, ")
            for x in range(len(cache.consumers)-1):
                contents.append(f"    {cache.name}_{x},")

            contents.append(f"    {cache.name}_{len(cache.consumers)-1});")
            contents.append("")

        # Add comment to indicate code for which node
        contents.append(f"// {repr(n)}")

        # Generate function name
        if n.type == NodeType.Fork:
            class_name = f"Fork{len(n.outputs)}<{n.first_input_size}>"
        elif n.type == NodeType.Cat:
            class_name = f"Cat{len(n.inputs)}<{', '.join(str(x.data_count) for x in n.inputs)}>"
        elif n.type == NodeType.Linear:
            class_name = f"{str(n.type).split('.')[1]}<{n.first_input_size}, {n.first_output_size}>"
        else:
            class_name = f"{str(n.type).split('.')[1]}<{n.first_input_size}>"
        function_name = f"{class_name}::backward{'_no' if n in start_nodes else ''}"

        # Generate parameters
        parameters = []
        if n.param != None:
            parameters.append(f"param{n.param.name}")
            parameters.append(f"grad{n.param.name}")
        if n.cache != None:
            parameters.append(n.cache.name if len(n.cache.consumers) == 1
                else n.cache.name + '_' + str(n.cache.consumers.index(n)))
        for ch in n.outputs:
            parameters.append(ch.back_name)
        if n not in start_nodes:
            for ch in n.inputs:
                parameters.append(ch.back_name)

        # Add output stream on need
        for ch in n.inputs:
            if ch == net.output.inputs[0]:
                continue
            contents.append(f"hls::stream<{element_name}, {ch.data_count}> {ch.back_name};")

        # Add function call
        contents.append(function_name + '(')
        for x in parameters[:-1]:
            contents.append("    " + x + ",")
        contents.append("    " + parameters[-1] + ");")
        contents.append("")

    _logger.info("Done.")
    return "\n".join("    " + x for x in contents)

def _gen_bw_function():
    return load_template("nn_ip", "function.cpp").substitute(
        function_name='top_backward',
        param_signatures=', '.join(bw_general_port_signature + param_port_signature + grad_port_signature + bw_cache_port_signature),
        param_hls_pragmas='\n'.join('    #pragma HLS ' + p for p in bw_general_hls_pragma + param_port_hls_pragma + grad_port_hls_pragma + bw_cache_port_hls_pragma),
        content=_gen_bw_content()
    )

def _gen_top_function():
    return load_template("nn_ip", "top.cpp").substitute(
        nn_in_size=nn_in_size,
        nn_out_size=nn_out_size,
        param_signatures = ', '.join(param_port_signature),
        grad_signatures=', '.join(grad_port_signature),
        param_hls_pragmas='\n'.join(f'    #pragma HLS INTERFACE mode=bram storage_type=rom_2p port=param{param.name} latency=1' for param in net.all_params()),
        grad_hls_pragmas='\n'.join('    #pragma HLS ' + p for p in grad_port_hls_pragma),
        cache_definitions='\n'.join(
            (f"    hls::stream<{cache.element_type}, {cache.count}> {cache.name};\n"
             f"    #pragma HLS BIND_STORAGE variable={cache.name} type=fifo")
            for cache in net.all_caches()
        ),
        forward_func='top_forward',
        backward_func='top_backward',
        params=',\n        '.join("param" + param.name for param in net.all_params()),
        grads=',\n        '.join("grad" + param.name for param in net.all_params()),
        caches=',\n        '.join(cache.name for cache in net.all_caches())
    )

def gen_nn_ip_source(filename):
    _gen_param_info()

    with open(filename, "w") as f:
        f.write(load_template("nn_ip", "source.cpp").substitute(
            fw_function = _gen_fw_function(),
            bw_function = _gen_bw_function(),
            top_function = _gen_top_function()
        ))
