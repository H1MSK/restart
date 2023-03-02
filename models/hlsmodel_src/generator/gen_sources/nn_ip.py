from typing import List
from .generic_source import get_source_template_map
from params import *
import logging
from template_loader import load_template
from dag import net, NodeType

_logger = logging.getLogger("IpSrcGen")

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


def gen_nn_ip_source(source, simulation, test):
    template_strings = get_source_template_map(
        zero_grads=";\n    ".join(
            f"memset(grad{p.name}, 0, sizeof(grad{p.name}))" for p in net.all_params()
        ),
        fw_content=_gen_fw_content(),
        bw_content=_gen_bw_content())

    with open(source, "w") as f:
        f.write(load_template("nn_ip_source.cpp").substitute(template_strings))

    with open(simulation, "w") as f:
        f.write(load_template("nn_ip_simulated.cpp").substitute(template_strings))

    with open(test, "w") as f:
        f.write(load_template("nn_ip_test.cpp").substitute(template_strings))
