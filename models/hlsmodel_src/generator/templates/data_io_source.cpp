#include "global.hpp"
#include "net/functors.hpp"

using namespace hlsnn;

void param_loader(
    hls::stream<cm_axis_data> &in,
    $param_signatures) {
#pragma HLS INTERFACE mode=s_axilite port=return
#pragma HLS INTERFACE mode=axis port=in register_mode=reverse
$param_ram1p_pragmas

$param_loader_content
}

void grad_extractor(
    $grad_signatures,
    hls::stream<cm_axis_data> &out) {
#pragma HLS INTERFACE mode=s_axilite port=return
#pragma HLS INTERFACE mode=axis port=out register_mode=forward
$grad_ram1p_pragmas

$grad_extractor_content
}
