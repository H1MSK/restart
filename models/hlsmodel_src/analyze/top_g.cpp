#include "global.hpp"
#include "net/net.hpp"

#ifndef NodeType
using NodeType = Tanh<64>;
#endif

void top_forward(hls::stream<cm_float>& in_x, hls::stream<cm_float>& out_y,
                 hls::stream<cm_float>& cache_out, bool cache_en) {
#pragma HLS INTERFACE mode = ap_ctrl_chain port = return
#pragma HLS INTERFACE mode = ap_fifo port = in_x
#pragma HLS INTERFACE mode = ap_fifo port = out_y
#pragma HLS INTERFACE mode = ap_fifo port = cache_out
#pragma HLS INTERFACE mode = ap_none port = cache_en
#pragma HLS STABLE variable = cache_en
#pragma HLS DATAFLOW
    NodeType::forward(in_x, out_y, cache_out, cache_en);
}

void top_backward(hls::stream<cm_float>& in_grad_y,
                  hls::stream<cm_float>& out_grad_x,
                  hls::stream<cm_float>& cache_in) {
#pragma HLS INTERFACE mode = ap_ctrl_chain port = return
#pragma HLS INTERFACE mode = ap_fifo port = in_grad_y
#pragma HLS INTERFACE mode = ap_fifo port = out_grad_x
#pragma HLS INTERFACE mode = ap_fifo port = cache_in
#pragma HLS DATAFLOW
    NodeType::backward(cache_in, in_grad_y, out_grad_x);
}
