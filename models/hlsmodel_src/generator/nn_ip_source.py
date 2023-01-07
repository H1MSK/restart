from enum import Enum
from typing import List
from params import *
import inspect
from preprocess import Info, CacheInfo

class NodeIO:
    def __init__(self, fw_istream_name, fw_ostream_name, bw_istream_name, bw_ostream_name) -> None:
        self.fi = fw_istream_name
        self.fo = fw_ostream_name
        self.bi = bw_istream_name
        self.bo = bw_ostream_name

node_io: List[NodeIO] = []
param_suffix: List[str] = []
cache_name: List[str] = []

fw_param_signature = []
bw_param_signature = []
fw_param_hls_pragmas = []
bw_param_hls_pragmas = []

def _gen_param_name_suffix():
    global param_suffix

    param_suffix_mapper = {
        "Linear": lambda kth, info: f"{kth}_{Info.param_size[kth]}o{info[2]}"
    }
    def _cal_param_suffix(kth, layer_info):
        try:
            return param_suffix_mapper[layer_info[0]](kth, layer_info)
        except KeyError:
            return None
    param_suffix = list(_cal_param_suffix(k, x) for k, x in enumerate(nn_structures))

def _gen_cache_name():
    global cache_name

    cache_name = [None if info is None else f"cache{k}_{info.size}" for k, info in enumerate(Info.cache_info)]

def _gen_fw_stream_names():
    global node_io

    current_input_name = "in_x"

    forkpath_names: List[List[str]] = []

    for kth, info in enumerate(nn_structures):
        if info[0] == "Fork":
            node_io[kth].fi = current_input_name
            node_io[kth].fo = tuple(f"fork{kth}_f{i}" for i in range(len(Info.fork_info[kth].fork_nodes) - 1)) # ignore ForkEnd
            current_input_name = node_io[kth].fo[0]
            forkpath_names.append([])
        elif info[0] == "ForkAgain":
            # No need to generate node
            node_io[kth] = None
            forkpath_names[-1].append(current_input_name)
            current_input_name = node_io[Info.path_info[kth].fork_start].fo[Info.path_info[kth].kth]
        elif info[0] == "ForkEnd":
            forkpath_names[-1].append(current_input_name)
            node_io[kth].fi = forkpath_names[-1]
            forkpath_names.pop()
            out_name = f"forkend{kth}_fo"
            node_io[kth].fo = out_name
            current_input_name = out_name
        else:
            node_io[kth].fi = current_input_name
            out_name = f"{info[0].lower()}{kth}_fo"
            node_io[kth].fo = out_name
            current_input_name = out_name

def _gen_bw_stream_names():
    global node_io

    current_input_name = "in_grad_y"
    forkpath_names: List[List[str]] = []

    for kth, info in enumerate(reversed(nn_structures)):
        kth = len(nn_structures) - 1 - kth
        if info[0] == "ForkEnd":
            node_io[kth].bi = current_input_name
            node_io[kth].bo = tuple(f"fork{kth}_b{i}" for i in range(len(Info.fork_info[kth].fork_nodes) - 1))
            current_input_name = node_io[kth].bo[0]
            forkpath_names.append([])
        elif info[0] == "ForkAgain":
            # No need to generate node
            node_io[kth] = None
            forkend_pos = Info.fork_info[Info.path_info[kth].fork_start].fork_nodes[-1]
            forkpath_names[-1].append(current_input_name)
            current_input_name = node_io[forkend_pos].fo[Info.path_info[kth].kth]
        elif info[0] == "Fork":
            node_io[kth].bi = forkpath_names[-1]
            forkpath_names.pop()
            out_name = f"forkend{kth}_bo"
            node_io[kth].bo = out_name
            current_input_name = out_name
        else:
            node_io[kth].bi = current_input_name
            out_name = f"{info[0].lower()}{kth}_bo"
            node_io[kth].bo = out_name
            current_input_name = out_name

def _gen_stream_names():
    global node_io
    node_io = [NodeIO("", "", "", "") for info in nn_structures]
    _gen_fw_stream_names()
    _gen_bw_stream_names()

def _gen_param_info():
    # Params = Static input + static output + generated params + generated cache
    global fw_param_signature

    fw_param_hls_pragmas.append("INTERFACE mode=ap_ctrl_chain port=return")
    bw_param_hls_pragmas.append("INTERFACE mode=ap_ctrl_chain port=return")

    fw_param_hls_pragmas.append("DATAFLOW")
    bw_param_hls_pragmas.append("DATAFLOW")

    fw_param_signature.append(f"hls::stream<{element_name}>& in_x")
    fw_param_hls_pragmas.append(f"INTERFACE mode=axis port=in_x register_mode=reverse depth={nn_in_size}")

    fw_param_signature.append(f"hls::stream<{element_name}, {nn_out_size}>& out_y")
    fw_param_hls_pragmas.append(f"INTERFACE mode=axis port=out_y register_mode=forward depth={nn_out_size}")

    bw_param_signature.append(f"hls::stream<{element_name}, {nn_out_size}>& in_grad_y")
    bw_param_hls_pragmas.append(f"INTERFACE mode=axis port=in_grad_y register_mode=reverse depth={nn_out_size}")

    # params.append(f"hls::stream<{element_name}, {out_size}>& out_grad_x")
    for k, size in enumerate(Info.param_size):
        if size != None:
            fw_param_signature.append(f"cm_float param{param_suffix[k]}[{size}]")
            fw_param_hls_pragmas.append(f"INTERFACE mode=bram storage_type=rom_1p port=param latency=1")

            bw_param_signature.append(f"cm_float param{param_suffix[k]}[{size}]")
            bw_param_hls_pragmas.append(f"INTERFACE mode=bram storage_type=rom_1p port=param latency=1")

            bw_param_signature.append(f"cm_float grad{param_suffix[k]}[{size}]")
            bw_param_hls_pragmas.append(f"INTERFACE mode=bram storage_type=ram_s2p port=grad latency=1")

    for k, info in enumerate(Info.cache_info):
        if info != None:
            fw_param_signature.append(f"hls::stream<{info.element_name}>& {cache_name[k]}_o")
            fw_param_hls_pragmas.append(f"INTERFACE mode=fifo port=cache{k}_{info.size}_out latency=1 depth={nn_out_size}")
            bw_param_signature.append(f"hls::stream<{info.element_name}>& {cache_name[k]}_i")
            bw_param_hls_pragmas.append(f"INTERFACE mode=fifo port=cache{k}_{info.size}_in latency=1 depth={nn_out_size}")

    print(fw_param_signature)

def _gen_ip_info():
    _gen_param_name_suffix()
    _gen_cache_name()
    _gen_stream_names()
    _gen_param_info()

def _gen_ostream_defination(kth, names):
    return [(f"hls::stream<{element_name}, {Info.node_out_size[kth]}> {name};",
            f"#pragma HLS BIND_STORAGE variable={name} type=fifo")
            for name in names]

def _gen_fw_content():
    contents = []
    for k, info in enumerate(nn_structures):
        if info[0] == "Fork":
            d = _gen_ostream_defination(k, node_io[k].fo)
            for t in d:
                contents.append(t[0])
                contents.append(t[1])
                contents.append("")
            contents.append(f"// {k}: {info}")
            contents.append(f"StreamSplitter{len(node_io[k].fo)}<{Info.node_out_size[k]}>::forward(")
            contents.append(f"    {node_io[k].fi},")
            contents.append("    {});".format(',\n        '.join(node_io[k].fo)))
            contents.append("")

        elif info[0] == "ForkAgain":
            pass

        elif info[0] == "ForkEnd":
            d = _gen_ostream_defination(k, [node_io[k].fo])
            contents.append(d[0][0])
            contents.append(d[0][1])
            contents.append("")
            merged_nodes = [x - 1 for x in Info.fork_info[k].fork_nodes[1:]]
            lens = [str(Info.node_out_size[x]) for x in merged_nodes]
            contents.append(f"StreamCat{len(node_io[k].fi)}<{', '.join(lens)}>::forward(")
            for p in node_io[k].fi:
                contents.append(f"    {p},")
            contents.append(f"    {node_io[k].fo});")

        elif info[0] in ("Linear", "Tanh", "Exp"):
            d = _gen_ostream_defination(k, [node_io[k].fo])
            contents.append(d[0][0])
            contents.append(d[0][1])
            contents.append("")
            contents.append(f"{info[0]}<{', '.join(str(x) for x in info[1:])}>::forward(")
            if param_suffix[k] != None:
                contents.append(f"    param{param_suffix[k]},")
            contents.append(f"    {node_io[k].fi},")
            contents.append(f"    {node_io[k].fo},")
            contents.append(f"    {cache_name[k]}_o);")
            contents.append("")
        
        else:
            raise NameError(info)

    return "\n".join("    " + x for x in contents)

def _gen_fw_function():
    t = '\n'.join('#pragma HLS ' + p for p in fw_param_hls_pragmas)
    return "\n".join((
        f"void forward({', '.join(fw_param_signature)}) {{",
        '\n'.join('    #pragma HLS ' + p for p in fw_param_hls_pragmas),
        "",
        _gen_fw_content(),
        f"}}"
    ))


def _gen_bw_content():
    contents = []
    for k, info in enumerate(reversed(nn_structures)):
        k = len(nn_structures) - 1 - k
        if info[0] == "ForkEnd":
            d = _gen_ostream_defination(k, node_io[k].bo)
            for t in d:
                contents.append(t[0])
                contents.append(t[1])
                contents.append("")
            contents.append(f"StreamSplitter{len(node_io[k].bo)}<{Info.node_out_size[k]}>::forward(")
            contents.append(f"    {node_io[k].bi},")
            t = ',\n    '.join(node_io[k].bo)
            contents.append(f"    {t});")
            contents.append("")
        
        elif info[0] == "ForkAgain":
            pass

        elif info[0] == "Fork":
            d = _gen_ostream_defination(k, [node_io[k].bo])
            contents.append(d[0][0])
            contents.append(d[0][1])
            contents.append("")
            merged_nodes = [x - 1 for x in Info.fork_info[k].fork_nodes[1:]]
            lens = [Info.node_out_size[x] for x in merged_nodes]
            contents.append(f"StreamAdder2{len(node_io[k].bi)}<{', '.join(str(x) for x in lens)}>(")
            t = ',\n    '.join(node_io[k].bi)
            contents.append(f"    {t},")
            contents.append(f"    {node_io[k].bo});")

        elif info[0] in ("Linear", "Tanh", "Exp"):
            d = _gen_ostream_defination(k, [node_io[k].bo])
            contents.append(d[0][0])
            contents.append(d[0][1])
            contents.append("")
            contents.append(f"{info[0]}<{', '.join(str(x) for x in info[1:])}>::backward(")
            if param_suffix[k] != None:
                contents.append(f"    param{param_suffix[k]},")
                contents.append(f"    grad{param_suffix[k]},")
            contents.append(f"    {cache_name[k]}_i,")
            contents.append(f"    {node_io[k].bi},")
            contents.append(f"    {node_io[k].bo});")
            contents.append("")
    return "\n".join("    " + x for x in contents)

def _gen_bw_function():
    return "\n".join((
        f"void backward({', '.join(bw_param_signature)}) {{",
        '\n'.join('    #pragma HLS ' + p for p in bw_param_hls_pragmas),
        "",
        _gen_bw_content(),
        f"}}"
    ))

def gen_nn_ip_source(filename):
    _gen_ip_info()
    with open(filename, "w") as f:
        f.write("\n".join((
            '#include "global.hpp"',
            '#include "net/net.hpp"',
            '',
            _gen_fw_function(),
            '',
            _gen_bw_function()
            )))
