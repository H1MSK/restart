#pragma once

#include "../global.hpp"

template <int In, int Out>
struct Linear {
    constexpr static int in_size = In;
    constexpr static int out_size = Out;
    constexpr static int param_size = in_size * out_size + out_size;
    constexpr static int cache_size = in_size;

#ifndef __SYNTHESIS__
    std::string cache_name;
    Linear() : cache_name("cl"+std::to_string(In)+"x"+std::to_string(Out)), cache(cache_name.c_str()) {}
#else
#endif

    void loadParam(hls::stream<cm_float>& in_param) {
#pragma HLS INLINE
        for (int i = 0; i < param_size; ++i)
            in_param >> param[i];
    }

#if CM_WITH_BACKWARD
    void dumpGradAndZero(hls::stream<cm_float>& out_grad) {
#pragma HLS INLINE
        for (int i = 0; i < param_size; ++i)
            out_grad << grad[i];
        if (param_size)
            memset(grad, 0, sizeof(grad));
    }
#endif

    void forward(hls::stream<cm_float>& in_x,
                 hls::stream<cm_float>& out_y,
                 bool enable_grad) {
#pragma HLS INTERFACE type = ap_ctrl_chain port = return
#pragma HLS INTERFACE type = ap_fifo port = in_x
#pragma HLS INTERFACE type = ap_fifo port = out_y
#pragma HLS INTERFACE type = ap_none port = enable_grad
#pragma HLS STABLE variable = enable_grad
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
#if CM_WITH_BACKWARD
        if (enable_grad) {
            for (int j = 0; j < in_size; ++j) {
                cache << x[j];
            }
        }
#endif
        if(enable_grad) CM_PRINT("F:Linear%dx%d:%d\n", in_size, out_size, (int)cache.size());
    }

#if CM_WITH_BACKWARD
    void backward(hls::stream<cm_float>& in_grad_y,
                  hls::stream<cm_float>& out_grad_x) {
#pragma HLS INTERFACE type = ap_ctrl_chain port = return
#pragma HLS INTERFACE type = ap_fifo port = in_grad_y
#pragma HLS INTERFACE type = ap_fifo port = out_grad_x
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
        CM_PRINT("B:Linear%dx%d:%d\n", in_size, out_size, (int)cache.size());
    }
    void backward(hls::stream<cm_float>& in_grad_y) {
#pragma HLS INTERFACE type = ap_ctrl_chain port = return
#pragma HLS INTERFACE type = ap_fifo port = in_grad_y
        cm_float grad_y[out_size];
        cm_float *const grad_w = grad;
        cm_float *const grad_b = grad + in_size * out_size;
        for (int i = 0; i < out_size; ++i) {
            grad_y[i] = in_grad_y.read();
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
        CM_PRINT("B:Linear%dx%d:%d\n", in_size, out_size, (int)cache.size());
    }
#endif

    cm_float param[param_size];

#if CM_WITH_BACKWARD
    cm_float grad[param_size];
    hls::stream<cm_float> cache;
#endif
};
