#pragma once

#include "../global.hpp"

template <int In, int Out>
struct Linear {
    constexpr static int in_size = In;
    constexpr static int out_size = Out;
    constexpr static int param_size = in_size * out_size + out_size;
    constexpr static int cache_size = in_size;

    static void forward(cm_float param[param_size], hls::stream<cm_float>& in_x,
                        hls::stream<cm_float>& out_y,
                        hls::stream<cm_float>& cache) {
#pragma HLS INTERFACE mode = ap_ctrl_chain port = return
#pragma HLS INTERFACE mode = ap_memory port = param storage_type = rom_1p
#pragma HLS INTERFACE mode = ap_fifo port = in_x
#pragma HLS INTERFACE mode = ap_fifo port = out_y
#pragma HLS INTERFACE mode = ap_fifo port = cache
#pragma HLS INLINE
        cm_float x[in_size];
        const cm_float* const w = param;
        const cm_float* const b = param + in_size * out_size;
        lfi: for (int j = 0; j < in_size; ++j) {
            cm_float t;
            in_x >> t;
            x[j] = t;
            cache << t;
        }
        lfc: for (int i = 0; i < out_size; ++i) {
            cm_float y_i = b[i];
#pragma HLS BIND_OP variable = y_i op = fadd impl = fabric
            for (int j = 0; j < in_size; ++j) {
                y_i += w[i * in_size + j] * x[j];
            }
            out_y << y_i;
        }
        //        for (int j = 0; j < in_size; ++j) {
        //            cache << x[j];
        //        }
    }

    static void backward(cm_float param[param_size], cm_float grad[param_size],
                         hls::stream<cm_float>& cache,
                         hls::stream<cm_float>& in_grad_y,
                         hls::stream<cm_float>& out_grad_x) {
#pragma HLS INTERFACE mode = ap_ctrl_chain port = return
#pragma HLS INTERFACE mode = ap_memory port = param storage_type = rom_1p
#pragma HLS INTERFACE mode = ap_memory port = grad storage_type = ram_s2p
#pragma HLS INTERFACE mode = ap_fifo port = cache
#pragma HLS INTERFACE mode = ap_fifo port = in_grad_y
#pragma HLS INTERFACE mode = ap_fifo port = out_grad_x
#pragma HLS INLINE
        cm_float grad_y1[out_size];
        cm_float grad_y2[out_size];
        const cm_float* const w = param;
        cm_float* const grad_w = grad;
        cm_float* const grad_b = grad + in_size * out_size;
        lbwi: for (int i = 0; i < out_size; ++i) {
            cm_float gy = in_grad_y.read();
            grad_y1[i] = gy;
            grad_y2[i] = gy;
            grad_b[i] += gy;
        }
        lbwo: for (int j = 0; j < in_size; ++j) {
            cm_float grad_x_j = 0;
            for (int i = 0; i < out_size; ++i) {
                grad_x_j += w[i * in_size + j] * grad_y1[i];
            }
            out_grad_x << grad_x_j;
        }

        lbw: for (int j = 0; j < in_size; ++j) {
            cm_float cache_x_j = cache.read();
            for (int i = 0; i < out_size; ++i) {
                grad_w[i * in_size + j] += grad_y2[i] * cache_x_j;
            }
        }
    }

    static void backward(cm_float param[param_size], cm_float grad[param_size],
                         hls::stream<cm_float>& cache,
                         hls::stream<cm_float>& in_grad_y) {
#pragma HLS INTERFACE mode = ap_ctrl_chain port = return
#pragma HLS INTERFACE mode = ap_memory port = param storage_type = rom_1p
#pragma HLS INTERFACE mode = ap_memory port = grad storage_type = ram_s2p
#pragma HLS INTERFACE mode = ap_fifo port = cache
#pragma HLS INTERFACE mode = ap_fifo port = in_grad_y
#pragma HLS INLINE
        cm_float grad_y[out_size];
        const cm_float* const w = param;
        cm_float* const grad_w = grad;
        cm_float* const grad_b = grad + in_size * out_size;
        lbi: for (int i = 0; i < out_size; ++i) {
            cm_float gy = in_grad_y.read();
            grad_y[i] = gy;
            grad_b[i] += gy;
        }

        lb: for (int j = 0; j < in_size; ++j) {
            cm_float cache_x_j = cache.read();
            for (int i = 0; i < out_size; ++i) {
                grad_w[i * in_size + j] += grad_y[i] * cache_x_j;
            }
        }
    }
};
