#include "global.hpp"
#include "net/net.hpp"

using namespace hlsnn;

void top_forward(
    cm_float maxi_x[$nn_in_size],
    cm_float maxi_y[$nn_out_size],
    bool cache_en,
    $param_signatures,
    $cache_signatures) {
    #pragma HLS INTERFACE mode=ap_ctrl_hs port=return
    #pragma HLS DATAFLOW
    #pragma HLS INTERFACE mode=m_axi port=maxi_x depth=$nn_in_size
    #pragma HLS INTERFACE mode=m_axi port=maxi_y depth=$nn_out_size
    #pragma HLS INTERFACE mode=ap_none port=cache_en
    #pragma HLS STABLE variable=cache_en

    $param_rom1p_pragmas
    $cache_fifo_interface_pragmas

    hls::stream<cm_float, $nn_in_size> in_x;
    #pragma HLS BIND_STORAGE variable=in_x type=fifo
    hls::stream<cm_float, $nn_out_size> out_y;
    #pragma HLS BIND_STORAGE variable=out_y type=fifo

    Array2stream<$nn_in_size>::run(maxi_x, in_x);

    $fw_content

    Stream2array<$nn_out_size>::run(out_y, maxi_y);
}

void top_backward(
    cm_float maxi_grad_y[$nn_out_size],
    $param_signatures,
    $grad_signatures,
    $cache_signatures) {
    #pragma HLS INTERFACE mode=ap_ctrl_hs port=return
    #pragma HLS DATAFLOW
    #pragma HLS INTERFACE mode=m_axi port=maxi_grad_y depth=$nn_out_size
    $param_rom1p_pragmas
    $grad_rams2p_pragmas
    $cache_fifo_interface_pragmas

    hls::stream<cm_float, $nn_out_size> in_grad_y;
    #pragma HLS BIND_STORAGE variable=in_grad_y type=fifo

    Array2stream<$nn_out_size>::run(maxi_grad_y, in_grad_y);

    $bw_content
}

#ifndef HLS_BUILD_SIM

void nn_ip(
    cm_float maxi_x[$nn_in_size],
    cm_float maxi_y[$nn_out_size],
    cm_float maxi_grad_y[$nn_out_size],
    bool cache_en,
    $param_signatures,
    $grad_signatures) {
    #pragma HLS INTERFACE mode=ap_ctrl_hs port=return
    #pragma HLS DATAFLOW
    #pragma HLS INTERFACE mode=m_axi port=maxi_x depth=$nn_in_size
    #pragma HLS INTERFACE mode=m_axi port=maxi_y depth=$nn_out_size
    #pragma HLS INTERFACE mode=m_axi port=maxi_grad_y depth=$nn_out_size
    #pragma HLS INTERFACE mode=ap_none port=cache_en
    #pragma HLS STABLE variable=cache_en

    $param_rom2p_pragmas
    $grad_rams2p_pragmas

$cache_static_definitions;

    $cache_fifo_storage_pragmas

    top_forward(maxi_x, maxi_y, cache_en,
        $param_variables,
        $cache_variables);
    top_backward(maxi_grad_y,
        $param_variables,
        $grad_variables,
        $cache_variables);
}

#endif
