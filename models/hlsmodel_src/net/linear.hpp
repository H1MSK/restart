#pragma once

#include "../global.hpp"

template <int In, int Out>
struct Linear {
    constexpr static int in_size = In;
    constexpr static int out_size = Out;
    constexpr static int param_size = in_size * out_size + out_size;
    constexpr static int cache_size = in_size;

    void forward(cm_float param[param_size],
                 hls::stream<cm_float>& in_x,
                 hls::stream<cm_float>& out_y,
                 hls::stream<cm_float>& cache) {
#pragma HLS INTERFACE mode = ap_ctrl_chain port = return
#pragma HLS INTERFACE mode = ap_memory port = param storage_type = rom_1p
#pragma HLS INTERFACE mode = ap_fifo port = in_x
#pragma HLS INTERFACE mode = ap_fifo port = out_y
#pragma HLS INTERFACE mode = ap_fifo port = cache
        cm_float x[in_size];
        const cm_float *const w = param;
        const cm_float *const b = param + in_size * out_size;
        for (int j = 0; j < in_size; ++j) {
            in_x >> x[j];
        }
        for (int i = 0; i < out_size; ++i) {
            cm_float y_i = b[i];
            for (int j = 0; j < in_size; ++j) {
                y_i += w[i * in_size + j] * x[j];
            }
            out_y << y_i;
        }
        for (int j = 0; j < in_size; ++j) {
            cache << x[j];
        }
    }

#if CM_WITH_BACKWARD
    void backward(cm_float param[param_size],
                  cm_float grad[param_size],
                  hls::stream<cm_float>& in_grad_y,
                  hls::stream<cm_float>& out_grad_x) {
#pragma HLS INTERFACE mode = ap_ctrl_chain port = return
#pragma HLS INTERFACE mode = ap_memory port = param storage_type = rom_1p
#pragma HLS INTERFACE mode = ap_memory port = grad storage_type = ram_s2p
#pragma HLS INTERFACE mode = ap_fifo port = in_grad_y
#pragma HLS INTERFACE mode = ap_fifo port = out_grad_x
        cm_float grad_y[out_size];
        const cm_float *const w = param;
        cm_float *const grad_w = grad;
        cm_float *const grad_b = grad + in_size * out_size;
        for (int i = 0; i < out_size; ++i) {
            grad_y[i] = in_grad_y.read();
        }
        for (int j = 0; j < in_size; ++j) {
            cm_float grad_x_j = 0;
            for (int i = 0; i < out_size; ++i) {
                grad_x_j += w[i * in_size + j] * grad_y[i];
            }
            out_grad_x << grad_x_j;
        }
        
        for (int j = 0; j < in_size; ++j) {
            cm_float cache_x_j = cache.read();
            for (int i = 0; i < out_size; ++i) {
                grad_w[i * in_size + j] += grad_y[i] * cache_x_j;
            }
        }
        for (int i = 0; i < out_size; ++i) {
            grad_b[i] += grad_y[i];
        }
    }
#endif
};
