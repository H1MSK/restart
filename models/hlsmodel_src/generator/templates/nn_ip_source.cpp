#include "global.hpp"
#include "net/net.hpp"

using namespace hlsnn;

void task_forward(hls::stream<cm_float, $nn_in_size>& in_x,
                  hls::stream<cm_float, $nn_out_size>& out_y,
                  bool cache_en,
                  $param_signatures,
                  $cache_signatures) {
    #pragma HLS INTERFACE mode=ap_ctrl_chain port=return
    #pragma HLS DATAFLOW
    #pragma HLS INTERFACE mode=ap_fifo port=in_x depth=$nn_in_size
    #pragma HLS INTERFACE mode=ap_fifo port=out_y depth=$nn_out_size
    #pragma HLS INTERFACE mode=ap_none port=cache_en
    #pragma HLS STABLE variable=cache_en

    $param_rom1p_pragmas
    $cache_fifo_interface_pragmas

    $fw_content
}

void top_forward(
    cm_float maxi_x[$nn_in_size],
    cm_float maxi_y[$nn_out_size],
    bool cache_en,
    int n,
    $param_signatures,
    $cache_signatures) {
    #pragma HLS INTERFACE mode=s_axilite port=return
    #pragma HLS INTERFACE mode=m_axi port=maxi_x depth=$nn_in_size
    #pragma HLS INTERFACE mode=m_axi port=maxi_y depth=$nn_out_size
    #pragma HLS INTERFACE mode=s_axilite port=cache_en
    #pragma HLS INTERFACE mode=s_axilite port=n

    $param_rom1p_pragmas
    $cache_fifo_interface_pragmas

    for (int i = 0; i < n; ++i) {
        #pragma HLS DATAFLOW
        hls::stream<cm_float, $nn_in_size> in_x;
        hls::stream<cm_float, $nn_out_size> out_y;
        Array2stream<$nn_in_size>::run(maxi_x + i * $nn_in_size, in_x);
        task_forward(in_x, out_y, cache_en, $param_variables, $cache_variables);
        Stream2array<$nn_out_size>::run(out_y, maxi_y + i * $nn_out_size);
    }
}

void task_backward(hls::stream<cm_float, $nn_out_size>& in_grad_y,
                   $param_signatures,
                   $grad_signatures,
                   $cache_signatures) {
    #pragma HLS INTERFACE mode=ap_ctrl_chain port=return
    #pragma HLS DATAFLOW
    #pragma HLS INTERFACE mode=ap_fifo port=in_grad_y depth=$nn_out_size
    $param_rom1p_pragmas
    $grad_rams2p_pragmas
    $cache_fifo_interface_pragmas
    $bw_content
}

void top_backward(
    cm_float maxi_grad_y[$nn_out_size],
    int n,
    $param_signatures,
    $grad_signatures,
    $cache_signatures) {
    #pragma HLS INTERFACE mode=s_axilite port=return
    #pragma HLS INTERFACE mode=m_axi port=maxi_grad_y depth=$nn_out_size
    #pragma HLS INTERFACE mode=s_axilite port=n
    $param_rom1p_pragmas
    $grad_rams2p_pragmas
    $cache_fifo_interface_pragmas

    for (int i = 0; i < n; ++i) {
        #pragma HLS DATAFLOW
        hls::stream<cm_float, $nn_out_size> in_grad_y;
        Array2stream<$nn_out_size>::run(maxi_grad_y + i * $nn_out_size, in_grad_y);
        task_backward(in_grad_y, $param_variables, $grad_variables,
                      $cache_variables);
    }
}
