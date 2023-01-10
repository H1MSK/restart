#pragma once

#include "../global.hpp"

// Y = exp(X)
template <int vec_size>
struct Tanh {
    constexpr static int in_size = vec_size;
    constexpr static int out_size = vec_size;
    constexpr static int param_size = 0;
    constexpr static int cache_size = vec_size;

    static void forward(hls::stream<cm_float>& in_x,
                        hls::stream<cm_float>& out_y,
                        hls::stream<cm_float>& cache) {
#pragma HLS INTERFACE mode = ap_ctrl_none port = return
#pragma HLS INTERFACE mode = ap_fifo port = in_x
#pragma HLS INTERFACE mode = ap_fifo port = out_y
#pragma HLS INTERFACE mode = ap_fifo port = cache
        tf: for (int i = 0; i < vec_size; ++i) {
            cm_float x = in_x.read();
            cm_float tanhx;
            cm_float ex = hls::exp(x);
            cm_float enx = hls::exp(-x);
            if (ex > 1e5f) tanhx = 1;
            else if (ex < 1e-5f) tanhx = -1;
            else tanhx = (ex - enx) / (ex + enx);
//             cm_float tanhx = std::tanh(x);
            out_y << tanhx;
            cache << tanhx;
        }
    }

    static void backward(hls::stream<cm_float>& cache,
                         hls::stream<cm_float>& in_grad_y,
                         hls::stream<cm_float>& out_grad_x) {
#pragma HLS INTERFACE mode = ap_ctrl_chain port = return
#pragma HLS INTERFACE mode = ap_fifo port = cache
#pragma HLS INTERFACE mode = ap_fifo port = in_grad_y
#pragma HLS INTERFACE mode = ap_fifo port = out_grad_x
        tb: for (int i = 0; i < vec_size; ++i) {
            cm_float grad_y_i = in_grad_y.read();
            cm_float cache_y_i = cache.read();
            out_grad_x << grad_y_i * (1 - hls::pown(cache_y_i, 2));
        }
    }
};
