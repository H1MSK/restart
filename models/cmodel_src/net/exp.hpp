#pragma once

#include "../global.hpp"

// Y = exp(X)
template <int vec_size>
struct Exp {
    constexpr static int in_size = vec_size;
    constexpr static int out_size = vec_size;
    constexpr static int param_size = 0;
    constexpr static int cache_size = vec_size;

#ifndef __SYNTHESIS__
    std::string cache_name;
    Exp() : cache_name("ce"+std::to_string(vec_size)), cache(cache_name.c_str()) {}
#else
#endif

    void loadParam(hls::stream<cm_float>& in_param) {
#pragma HLS INLINE
        CM_UNUSED(in_param);
    }

#if CM_WITH_BACKWARD
    void dumpGradAndZero(hls::stream<cm_float>& out_grad) {
#pragma HLS INLINE
        CM_UNUSED(out_grad);
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
            cm_float ex = hls::exp(x);
            out_y << ex;
#if CM_WITH_BACKWARD
            if (enable_grad) cache << ex;
#endif
        }
        if(enable_grad) CM_PRINT("F:Exp%d:%d\n", vec_size, (int)cache.size());
    }

#if CM_WITH_BACKWARD
    void backward(hls::stream<cm_float>& in_grad_y,
                  hls::stream<cm_float>& out_grad_x) {
#pragma HLS INTERFACE type = ap_ctrl_chain port = return
#pragma HLS INTERFACE type = ap_fifo port = in_grad_y
#pragma HLS INTERFACE type = ap_fifo port = out_grad_x
        for (int i = 0; i < in_size; ++i) {
            cm_float grad_y_i = in_grad_y.read();
            cm_float cache_y_i = cache.read();
            out_grad_x << grad_y_i * cache_y_i;
        }
        CM_PRINT("B:Exp%d:%d\n", vec_size, (int)cache.size());
    }
    void backward(hls::stream<cm_float>& in_grad_y) {
#pragma HLS INLINE
        CM_PRINT("B:Exp%d:%d\n", vec_size, (int)cache.size());
        CM_UNUSED(in_grad_y);
    }
#endif
#if CM_WITH_BACKWARD
    hls::stream<cm_float> cache;
#endif
};
