#pragma once

#include "../global.hpp"

// Y = exp(X)
template <int vec_size>
struct Exp {
    constexpr static int in_size = vec_size;
    constexpr static int out_size = vec_size;
    constexpr static int param_size = 0;
    constexpr static int cache_size = vec_size;

    static void forward(hls::stream<cm_float>& in_x,
                        hls::stream<cm_float>& out_y,
                        hls::stream<cm_float>& cache,
                        bool cache_en) {
#pragma HLS INTERFACE mode = ap_ctrl_none port = return
#pragma HLS INTERFACE mode = ap_fifo port = in_x
#pragma HLS INTERFACE mode = ap_fifo port = out_y
#pragma HLS INTERFACE mode = ap_fifo port = cache
#pragma HLS INTERFACE mode = ap_none port = cache_en
#pragma HLS STABLE variable = cache_en
        ef: for (int i = 0; i < in_size; ++i) {
            cm_float x = in_x.read();
            cm_float ex = hls::exp(x);
            out_y << ex;
            if (cache_en) cache << ex;
        }
    }

    static void backward(hls::stream<cm_float>& cache,
                         hls::stream<cm_float>& in_grad_y,
                         hls::stream<cm_float>& out_grad_x) {
#pragma HLS INTERFACE mode = ap_ctrl_chain port = return
#pragma HLS INTERFACE mode = ap_fifo port = cache
#pragma HLS INTERFACE mode = ap_fifo port = in_grad_y
#pragma HLS INTERFACE mode = ap_fifo port = out_grad_x
        eb: for (int i = 0; i < in_size; ++i) {
            cm_float grad_y_i = in_grad_y.read();
            cm_float cache_y_i = cache.read();
            out_grad_x << grad_y_i * cache_y_i;
        }
    }
};
