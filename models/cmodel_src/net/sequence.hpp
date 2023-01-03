#pragma once

#include "../global.hpp"

template <typename... Types>
struct Sequence;

template <typename FirstType>
struct Sequence<FirstType> {
    constexpr static int in_size = FirstType::in_size;
    constexpr static int out_size = FirstType::out_size;
    constexpr static int param_size = FirstType::param_size;
    constexpr static int cache_size = FirstType::cache_size;

    void loadParam(hls::stream<cm_float>& in_param) {
#pragma HLS INLINE
        first.loadParam(in_param);
    }

#if CM_WITH_BACKWARD
    void dumpGradAndZero(hls::stream<cm_float>& out_grad) {
#pragma HLS INLINE
        first.dumpGradAndZero(out_grad);
    }
#endif

    void forward(hls::stream<cm_float>& in_x,
                 hls::stream<cm_float>& out_y,
                 bool enable_grad) {
#pragma HLS INLINE
        first.forward(in_x, out_y, enable_grad);
    }

#if CM_WITH_BACKWARD
    void backward(hls::stream<cm_float>& in_grad_y,
                  hls::stream<cm_float>& out_grad_x) {
#pragma HLS INLINE
        first.backward(in_grad_y, out_grad_x);
    }
    void backward(hls::stream<cm_float>& in_grad_y) {
#pragma HLS INLINE
        first.backward(in_grad_y);
    }
#endif
    FirstType first;
};

template <typename FirstType, typename... OtherTypes>
struct Sequence<FirstType, OtherTypes...> {
    using SeqNext = Sequence<OtherTypes...>;
    constexpr static int in_size = FirstType::in_size;
    constexpr static int out_size = SeqNext::out_size;
    constexpr static int param_size = FirstType::param_size + SeqNext::param_size;
    constexpr static int cache_size = FirstType::cache_size + SeqNext::cache_size;

    static_assert(FirstType::out_size == SeqNext::in_size);

    void loadParam(hls::stream<cm_float>& in_param) {
#pragma HLS INLINE
        first.loadParam(in_param);
        next.loadParam(in_param);
    }

#if CM_WITH_BACKWARD
    void dumpGradAndZero(hls::stream<cm_float>& out_grad) {
#pragma HLS INLINE
        first.dumpGradAndZero(out_grad);
        next.dumpGradAndZero(out_grad);
    }
#endif

    void forward(hls::stream<cm_float>& in_x,
                 hls::stream<cm_float>& out_y,
                 bool enable_grad) {
#pragma HLS INTERFACE mode = ap_ctrl_chain port = return
#pragma HLS INTERFACE mode = ap_fifo port = in_x
#pragma HLS INTERFACE mode = ap_fifo port = out_y
#pragma HLS INTERFACE mode = ap_none port = enable_grad
#pragma HLS STABLE variable = enable_grad
//#pragma HLS DATAFLOW
        hls::stream<cm_float, FirstType::out_size> mid;
        first.forward(in_x, mid, enable_grad);
        next.forward(mid, out_y, enable_grad);
    }

#if CM_WITH_BACKWARD
    void backward(hls::stream<cm_float>& in_grad_y,
                  hls::stream<cm_float>& out_grad_x) {
#pragma HLS INTERFACE mode = ap_ctrl_chain port = return
#pragma HLS INTERFACE mode = ap_fifo port = in_grad_y
#pragma HLS INTERFACE mode = ap_fifo port = out_grad_x
//#pragma HLS DATAFLOW
        hls::stream<cm_float, FirstType::out_size> mid;
        next.backward(in_grad_y, mid);
        first.backward(mid, out_grad_x);
    }
    void backward(hls::stream<cm_float>& in_grad_y) {
#pragma HLS INTERFACE mode = ap_ctrl_chain port = return
#pragma HLS INTERFACE mode = ap_fifo port = in_grad_y
//#pragma HLS DATAFLOW
        hls::stream<cm_float, FirstType::out_size> mid;
        next.backward(in_grad_y, mid);
        first.backward(mid);
    }
#endif

    FirstType first;
    SeqNext next;
};
