#include "global.hpp"
#include "net/net.hpp"

void top_forward(
    hls::stream<cm_float, $nn_in_size>& in_x,
    hls::stream<cm_float, $nn_out_size>& out_y,
    bool cache_en,
    $param_signatures,
    $cache_signatures) {
    #pragma HLS INTERFACE mode=ap_ctrl_chain port=return
    #pragma HLS DATAFLOW
    #pragma HLS INTERFACE mode=axis port=in_x register_mode=reverse depth=376
    #pragma HLS INTERFACE mode=axis port=out_y register_mode=forward depth=35
    #pragma HLS INTERFACE mode=ap_none port=cache_en
    #pragma HLS STABLE variable=cache_en
    $param_rom1p_pragmas
    $cache_fifo_interface_pragmas

    $fw_content
}

void top_backward(
    hls::stream<cm_float, $nn_out_size>& in_grad_y,
    $param_signatures,
    $grad_signatures,
    $cache_signatures) {
    #pragma HLS INTERFACE mode=ap_ctrl_hs port=return
    #pragma HLS DATAFLOW
    #pragma HLS INTERFACE mode=axis port=in_grad_y register_mode=reverse depth=35
    $param_rom1p_pragmas
    $grad_rams2p_pragmas
    $cache_fifo_interface_pragmas

    $bw_content
}

#ifndef NO_NN_IP_FUNC

void nn_ip(
    hls::stream<cm_float, $nn_in_size>& in_x,
    hls::stream<cm_float, $nn_out_size>& out_y,
    hls::stream<cm_float, $nn_out_size>& in_grad_y,
    bool cache_en,
    $param_signatures,
    $grad_signatures) {
    #pragma HLS INTERFACE mode=ap_ctrl_hs port=return
    #pragma HLS DATAFLOW
    #pragma HLS INTERFACE mode=axis port=in_x register_mode=reverse depth=376
    #pragma HLS INTERFACE mode=axis port=out_y register_mode=forward depth=35
    #pragma HLS INTERFACE mode=axis port=in_grad_y register_mode=reverse depth=35
    #pragma HLS INTERFACE mode=ap_none port=cache_en
    #pragma HLS STABLE variable=cache_en

    $param_rom2p_pragmas
    $grad_rams2p_pragmas

$cache_static_definitions;

    $cache_fifo_storage_pragmas

    top_forward(in_x, out_y, cache_en,
        $param_variables,
        $cache_variables);
    top_backward(in_grad_y,
        $param_variables,
        $grad_variables,
        $cache_variables);
}

#endif
