#include "global.hpp"
#include "net/net.hpp"

using namespace hlsnn;

void top_forward(
    hls::stream<cm_axis_data> &axis_x,
    hls::stream<cm_axis_data> &axis_y,
    bool cache_en,
    $param_signatures,
    $cache_signatures) {
    #pragma HLS INTERFACE mode=s_axilite port=return
    #pragma HLS DATAFLOW
    #pragma HLS INTERFACE mode=axis port=axis_x register_mode=reverse
    #pragma HLS INTERFACE mode=axis port=axis_y register_mode=forward
    #pragma HLS INTERFACE mode=ap_none port=cache_en
    #pragma HLS STABLE variable=cache_en

    $param_rom1p_pragmas
    $cache_fifo_interface_pragmas

    hls::stream<cm_float, $nn_in_size> in_x;
    hls::stream<cm_float, $nn_out_size> out_y;
    FloatBusCarrier::dumpFifoFromAxisBus(axis_x, in_x);

    $fw_content

    FloatBusCarrier::loadFifoToAxisBus(axis_y, out_y, true);
}

void top_backward(
    hls::stream<cm_axis_data> &axis_grad_y,
    $param_signatures,
    $grad_signatures,
    $cache_signatures) {
    #pragma HLS INTERFACE mode=s_axilite port=return
    #pragma HLS DATAFLOW
    #pragma HLS INTERFACE mode=axis port=axis_grad_y register_mode=reverse
    $param_rom1p_pragmas
    $grad_rams2p_pragmas
    $cache_fifo_interface_pragmas

    hls::stream<cm_float, $nn_out_size> in_grad_y;
    FloatBusCarrier::dumpFifoFromAxisBus(axis_grad_y, in_grad_y);

    $bw_content
}
