#include "global.hpp"

void param_loader(
        hls::stream<cm_float>& in,
        $param_signatures) {
#pragma HLS INTERFACE mode=ap_ctrl_hs port=return
#pragma HLS INTERFACE mode=axis register_mode=reverse port=in
$param_pragmas

$param_readers
}

void grad_extractor(
        $grad_signatures,
        hls::stream<cm_float>& out) {
#pragma HLS INTERFACE mode=ap_ctrl_hs port=return
$grad_pragmas
#pragma HLS INTERFACE mode=axis register_mode=forward port=out

$grad_writers
}