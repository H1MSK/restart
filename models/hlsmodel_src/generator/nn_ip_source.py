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

    def __repr__(self) -> str:
        return f"NodeIo(fi={self.fi}, fo={self.fo}, bi={self.bi}, bo={self.bo})"

node_io: List[NodeIO] = []
param_suffix: List[str] = []
cache_name: List[str] = []
path_param_count: List[int] = []

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

def _fw_scan():
    global node_io
    global path_param_count

    current_input_name = "in_x"

    forkpath_names: List[List[str]] = []

    for kth, info in enumerate(nn_structures):
        path_param_count.append(0 if kth == 0 else path_param_count[kth - 1])
        if info[0] == "Fork":
            node_io[kth].fi = current_input_name
            node_io[kth].fo = tuple(f"fork{kth}_f{i}" for i in range(len(Info.fork_info[kth].fork_nodes) - 1)) # ignore ForkEnd
            current_input_name = node_io[kth].fo[0]
            forkpath_names.append([])
        elif info[0] == "ForkAgain":
            # No need to generate node
            node_io[kth].fi = node_io[kth].fo = None
            path_param_count[kth] = (0 if kth == 0 else path_param_count[Info.path_info[kth].fork_start])
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
            path_param_count[kth] += (1 if Info.param_size[kth] != None else 0)
            node_io[kth].fi = current_input_name
            out_name = f"{info[0].lower()}{kth}_fo"
            node_io[kth].fo = out_name
            current_input_name = out_name

    node_io[-1].fo = 'out_y'

def _bw_scan():
    global node_io

    current_input_name = "in_grad_y"
    forkpath_names: List[List[str]] = []

    for kth, info in enumerate(reversed(nn_structures)):
        kth = len(nn_structures) - 1 - kth
        if path_param_count[kth] == 0:
            if node_io[kth] != None:
                node_io[kth].bi = None
                node_io[kth].bo = None
            if info[0] == "ForkAgain":
                forkend_pos = Info.fork_info[Info.path_info[kth].fork_start].fork_nodes[-1]
                current_input_name = node_io[forkend_pos].bo[Info.path_info[kth].kth - 1]
            continue
        if info[0] == "ForkEnd":
            node_io[kth].bi = current_input_name
            node_io[kth].bo = tuple(f"fork{kth}_b{i}" for i in range(len(Info.fork_info[kth].fork_nodes) - 1))
            current_input_name = node_io[kth].bo[-1]
            forkpath_names.append([])
        elif info[0] == "ForkAgain":
            # No need to generate node
            node_io[kth].bi = node_io[kth].bo = None
            forkend_pos = Info.fork_info[Info.path_info[kth].fork_start].fork_nodes[-1]
            forkpath_names[-1].append(current_input_name)
            print(kth, Info.path_info[kth])
            current_input_name = node_io[forkend_pos].bo[Info.path_info[kth].kth - 1]
        elif info[0] == "Fork":
            forkpath_names[-1].append(current_input_name)
            node_io[kth].bi = forkpath_names[-1]
            forkpath_names.pop()
            out_name = f"forkend{kth}_bo"
            node_io[kth].bo = out_name
            current_input_name = out_name
        else:
            node_io[kth].bi = current_input_name
            if path_param_count[kth] > 1 or (path_param_count[kth] == 1 and Info.param_size[kth] == None):
                out_name = f"{info[0].lower()}{kth}_bo"
                node_io[kth].bo = out_name
                current_input_name = out_name
            else:
                node_io[kth].bo = None
                current_input_name = None

def _gen_stream_names():
    global node_io
    node_io = [NodeIO("", "", "", "") for info in nn_structures]
    _fw_scan()
    _bw_scan()
    print("\n".join(f"{k}: {repr(x)}" for k, x in enumerate(zip(nn_structures, path_param_count, node_io))))

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
            fw_param_hls_pragmas.append(f"INTERFACE mode=bram storage_type=rom_1p port=param{param_suffix[k]} latency=1")

            bw_param_signature.append(f"cm_float param{param_suffix[k]}[{size}]")
            bw_param_hls_pragmas.append(f"INTERFACE mode=bram storage_type=rom_1p port=param{param_suffix[k]} latency=1")

            bw_param_signature.append(f"cm_float grad{param_suffix[k]}[{size}]")
            bw_param_hls_pragmas.append(f"INTERFACE mode=bram storage_type=ram_s2p port=grad{param_suffix[k]} latency=1")

    for k, info in enumerate(Info.cache_info):
        if info != None:
            fw_param_signature.append(f"hls::stream<{info.element_name}>& {cache_name[k]}_o")
            fw_param_hls_pragmas.append(f"INTERFACE mode=ap_fifo port=cache{k}_{info.size}_o depth={nn_out_size}")
            bw_param_signature.append(f"hls::stream<{info.element_name}>& {cache_name[k]}_i")
            bw_param_hls_pragmas.append(f"INTERFACE mode=ap_fifo port=cache{k}_{info.size}_i depth={nn_out_size}")

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
        contents.append(f"// {k}: {info}")
        if info[0] == "Fork":
            if k + 1 != len(nn_structures):
                d = _gen_ostream_defination(k, node_io[k].fo)
                for t in d:
                    contents.append(t[0])
                    contents.append(t[1])
            contents.append(f"StreamSplitter{len(node_io[k].fo)}<{Info.node_out_size[k]}>::run(")
            contents.append(f"    {node_io[k].fi},")
            contents.append("    {});".format(',\n        '.join(node_io[k].fo)))
            contents.append("")

        elif info[0] == "ForkAgain":
            pass

        elif info[0] == "ForkEnd":
            if k + 1 != len(nn_structures):
                d = _gen_ostream_defination(k, [node_io[k].fo])
                contents.append(d[0][0])
                contents.append(d[0][1])
            merged_nodes = [x - 1 for x in Info.fork_info[k].fork_nodes[1:]]
            lens = [str(Info.node_out_size[x]) for x in merged_nodes]
            contents.append(f"StreamCat{len(node_io[k].fi)}<{', '.join(lens)}>::run(")
            for p in node_io[k].fi:
                contents.append(f"    {p},")
            contents.append(f"    {node_io[k].fo});")

        elif info[0] in ("Linear", "Tanh", "Exp"):
            if k + 1 != len(nn_structures):
                d = _gen_ostream_defination(k, [node_io[k].fo])
                contents.append(d[0][0])
                contents.append(d[0][1])
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
        f"void top_forward({', '.join(fw_param_signature)}) {{",
        '\n'.join('    #pragma HLS ' + p for p in fw_param_hls_pragmas),
        "",
        _gen_fw_content(),
        f"}}"
    ))


def _gen_bw_content():
    contents = []
    for k, info in enumerate(reversed(nn_structures)):
        k = len(nn_structures) - 1 - k
        contents.append(f"// {k}: {info}")
        if node_io[k] == None or node_io[k].bi == None:
            continue
        if info[0] == "ForkEnd":
            d = _gen_ostream_defination(k, node_io[k].bo)
            for t in d:
                contents.append(t[0])
                contents.append(t[1])
            contents.append(f"StreamSplitter{len(node_io[k].bo)}<{Info.node_out_size[k]}>::run(")
            contents.append(f"    {node_io[k].bi},")
            t = ',\n        '.join(node_io[k].bo)
            contents.append(f"    {t});")
            contents.append("")
        
        elif info[0] == "ForkAgain":
            pass

        elif info[0] == "Fork":
            d = _gen_ostream_defination(k, [node_io[k].bo])
            contents.append(d[0][0])
            contents.append(d[0][1])
            merged_nodes = [x - 1 for x in Info.fork_info[k].fork_nodes[:-1]]
            contents.append(f"StreamAdder{len(node_io[k].bi)}<{Info.node_in_size[k]}>::run(")
            t = ',\n        '.join(node_io[k].bi)
            contents.append(f"    {t},")
            contents.append(f"    {node_io[k].bo});")

        elif info[0] in ("Linear", "Tanh", "Exp"):
            if node_io[k].bo:
                d = _gen_ostream_defination(k, [node_io[k].bo])
                contents.append(d[0][0])
                contents.append(d[0][1])
            contents.append(f"{info[0]}<{', '.join(str(x) for x in info[1:])}>::backward(")
            if param_suffix[k] != None:
                contents.append(f"    param{param_suffix[k]},")
                contents.append(f"    grad{param_suffix[k]},")
            contents.append(f"    {cache_name[k]}_i,")
            if node_io[k].bo != None:
                contents.append(f"    {node_io[k].bi},")
                contents.append(f"    {node_io[k].bo});")
            else:
                contents.append(f"    {node_io[k].bi});")
            contents.append("")
    return "\n".join("    " + x for x in contents)

def _gen_bw_function():
    return "\n".join((
        f"void top_backward({', '.join(bw_param_signature)}) {{",
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
