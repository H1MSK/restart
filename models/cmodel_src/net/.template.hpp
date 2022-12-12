#pragma once

#include "../global.hpp"

// Y = X + P[0]
template <int vec_size>
struct Bias {
    constexpr static int in_size = vec_size;
    constexpr static int out_size = vec_size;
    constexpr static int param_size = 1;
    constexpr static int cache_size = 0;

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
        for (int i = 0; i < in_size; ++i) {
            cm_float x = in_x.read();
            out_y << (x + param[0]);
        }
#if CM_WITH_BACKWARD
        if (enable_grad) {
            ;
        }
#endif
    }

#if CM_WITH_BACKWARD
    void backward(hls::stream<cm_float>& in_grad_y,
                  hls::stream<cm_float>& out_grad_x) {
#pragma HLS INTERFACE type = ap_ctrl_chain port = return
#pragma HLS INTERFACE type = ap_fifo port = in_grad_y
#pragma HLS INTERFACE type = ap_fifo port = out_grad_x
        for (int i = 0; i < in_size; ++i) {
            cm_float gy = in_grad_y.read();
            grad[0] += gy;
            out_grad_x << gy;
        }
    }
#endif

    cm_float param[param_size];

#if CM_WITH_BACKWARD
    cm_float grad[param_size];
    // hls::stream<cm_float> cache;
#endif
};
