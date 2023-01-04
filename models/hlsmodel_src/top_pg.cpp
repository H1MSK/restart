#include "global.hpp"
#include "net/net.hpp"

#ifndef NodeType
using NodeType = Linear<376, 64>;
#endif

void top(hls::stream<cm_float>& in_x, hls::stream<cm_float>& out_y,
         hls::stream<cm_float>& in_grad_y, hls::stream<cm_float>& out_grad_x,
         cm_float param[NodeType::param_size],
         cm_float grad[NodeType::param_size], hls::stream<cm_float>& cache_out,
         hls::stream<cm_float>& cache_in) {
#pragma HLS INTERFACE mode=ap_ctrl_none port=return
#pragma HLS INTERFACE mode=ap_fifo port=in_x
#pragma HLS INTERFACE mode=ap_fifo port=out_y
#pragma HLS INTERFACE mode=ap_fifo port=in_grad_y
#pragma HLS INTERFACE mode=ap_fifo port=out_grad_x
#pragma HLS INTERFACE mode=ap_memory port=param storage_type=rom_2p
#pragma HLS INTERFACE mode=ap_memory port=grad storage_type=ram_t2p
#pragma HLS INTERFACE mode=ap_fifo port=cache_out
#pragma HLS INTERFACE mode=ap_fifo port=cache_in
    static NodeType node;
}
