#include "global.hpp"

using namespace hlsnn;

void param_loader(
    cm_float in[$all_param_count],
    $param_signatures) {
#pragma HLS INTERFACE mode=s_axilite port=return
#pragma HLS INTERFACE mode=m_axi port=in
$param_ram1p_pragmas

$param_loader_content
}

void grad_extractor(
    $grad_signatures,
    cm_float out[$all_param_count]) {
#pragma HLS INTERFACE mode=s_axilite port=return
#pragma HLS INTERFACE mode=m_axi port=out
$grad_ram1p_pragmas

$grad_extractor_content
}