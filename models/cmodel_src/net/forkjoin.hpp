#pragma once

#include "../global.hpp"

template <int vec_size>
struct CopyFork {
    constexpr static int in_size = vec_size;
    constexpr static int out_size = vec_size;
    constexpr static int param_size = 0;
    constexpr static int cache_size = 0;

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

    void forward2(hls::stream<cm_float>& in_x,
                 hls::stream<cm_float>& out_y1,
                 hls::stream<cm_float>& out_y2,
                 bool enable_grad) {
#pragma HLS INTERFACE type = ap_ctrl_chain port = return
#pragma HLS INTERFACE type = ap_fifo port = in_x
#pragma HLS INTERFACE type = ap_fifo port = out_y1
#pragma HLS INTERFACE type = ap_fifo port = out_y2
#pragma HLS INTERFACE type = ap_none port = enable_grad
#pragma HLS STABLE variable = enable_grad
        CM_UNUSED(enable_grad);
        for (int i = 0; i < in_size; ++i) {
            cm_float x = in_x.read();
            out_y1 << x;
            out_y2 << x;
        }
    }

#if CM_WITH_BACKWARD
    void backward2(hls::stream<cm_float>& in_grad_y1,
                  hls::stream<cm_float>& in_grad_y2,
                  hls::stream<cm_float>& out_grad_x) {
#pragma HLS INTERFACE type = ap_ctrl_chain port = return
#pragma HLS INTERFACE type = ap_fifo port = in_grad_y
#pragma HLS INTERFACE type = ap_fifo port = out_grad_x
        for (int i = 0; i < in_size; ++i) {
            cm_float gy1 = in_grad_y1.read();
            cm_float gy2 = in_grad_y2.read();
            out_grad_x << (gy1 + gy2);
        }
    }
#endif
};

template <int In1Size, int In2Size>
struct VecCat {
    constexpr static int in_size = In1Size + In2Size;
    constexpr static int out_size = In1Size + In2Size;
    constexpr static int param_size = 0;
    constexpr static int cache_size = 0;

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

    void forward2(hls::stream<cm_float>& in_x1,
                 hls::stream<cm_float>& in_x2,
                 hls::stream<cm_float>& out_y,
                 bool enable_grad) {
#pragma HLS INTERFACE type = ap_ctrl_chain port = return
#pragma HLS INTERFACE type = ap_fifo port = in_x1
#pragma HLS INTERFACE type = ap_fifo port = in_x2
#pragma HLS INTERFACE type = ap_fifo port = out_y
#pragma HLS INTERFACE type = ap_none port = enable_grad
#pragma HLS STABLE variable = enable_grad
        CM_UNUSED(enable_grad);
        for (int i = 0; i < In1Size; ++i) {
            cm_float x = in_x1.read();
            out_y << x;
        }
        for (int i = 0; i < In2Size; ++i) {
            cm_float x = in_x2.read();
            out_y << x;
        }
    }

#if CM_WITH_BACKWARD
    void backward2(hls::stream<cm_float>& in_grad_y,
                  hls::stream<cm_float>& out_grad_x1,
                  hls::stream<cm_float>& out_grad_x2) {
#pragma HLS INTERFACE type = ap_ctrl_chain port = return
#pragma HLS INTERFACE type = ap_fifo port = in_grad_y
#pragma HLS INTERFACE type = ap_fifo port = out_grad_x1
#pragma HLS INTERFACE type = ap_fifo port = out_grad_x2
        for (int i = 0; i < In1Size; ++i) {
            cm_float grad_y_i = in_grad_y.read();
            out_grad_x1 << grad_y_i;
        }
        for (int i = 0; i < In2Size; ++i) {
            cm_float grad_y_i = in_grad_y.read();
            out_grad_x2 << grad_y_i;
        }
    }
    void backward2(hls::stream<cm_float>& in_grad_y) {
#pragma HLS INLINE
        CM_UNUSED(in_grad_y);
    }
#endif
};

template <typename Node1Type, typename Node2Type,
          typename ForkerType = CopyFork<Node1Type::in_size>,
          typename JoinerType = VecCat<Node1Type::out_size, Node2Type::out_size>>
struct ForkJoin {
    static_assert(Node1Type::in_size == Node2Type::in_size);
    constexpr static int in_size = Node1Type::in_size;
    constexpr static int out_size = JoinerType::out_size;
    constexpr static int param_size = Node1Type::param_size + Node2Type::param_size + JoinerType::param_size;
    constexpr static int cache_size = Node1Type::cache_size + Node2Type::cache_size + JoinerType::cache_size;

    void loadParam(hls::stream<cm_float>& in_param) {
#pragma HLS INLINE
        forker.loadParam(in_param);
        node1.loadParam(in_param);
        node2.loadParam(in_param);
        joiner.loadParam(in_param);
    }

#if CM_WITH_BACKWARD
    void dumpGradAndZero(hls::stream<cm_float>& out_grad) {
#pragma HLS INLINE
        forker.dumpGradAndZero(out_grad);
        node1.dumpGradAndZero(out_grad);
        node2.dumpGradAndZero(out_grad);
        joiner.dumpGradAndZero(out_grad);
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
#pragma HLS DATAFLOW
        hls::stream<cm_float> in_x1, in_x2;
        hls::stream<cm_float> out_y1, out_y2;

        forker.forward2(in_x, in_x1, in_x2, enable_grad);
        node1.forward(in_x1, out_y1, enable_grad);
        node2.forward(in_x2, out_y2, enable_grad);
        joiner.forward2(out_y1, out_y2, out_y, enable_grad);
    }

#if CM_WITH_BACKWARD
    void backward(hls::stream<cm_float>& in_grad_y,
                  hls::stream<cm_float>& out_grad_x) {
#pragma HLS INTERFACE type = ap_ctrl_chain port = return
#pragma HLS INTERFACE type = ap_fifo port = in_grad_y
#pragma HLS INTERFACE type = ap_fifo port = out_grad_x
#pragma HLS DATAFLOW
        hls::stream<cm_float> in_grad_y1, in_grad_y2;
        hls::stream<cm_float> out_grad_x1, out_grad_x2;
        joiner.backward2(in_grad_y, in_grad_y1, in_grad_y2);
        node1.backward(in_grad_y1, out_grad_x1);
        node2.backward(in_grad_y2, out_grad_x2);
        forker.backward2(out_grad_x1, out_grad_x2, out_grad_x);
    }
// This function is commented out. I don't know exactly the behave of
//  the if statement in HLS. If it will be precalculated and converted into
//  content in either branch in compiling, then dataflow will be applied as
//  my intention.
//     void backward(hls::stream<cm_float>& in_grad_y) {
// #pragma HLS INTERFACE type = ap_ctrl_chain port = return
// #pragma HLS INTERFACE type = ap_fifo port = in_grad_y
// #pragma HLS INTERFACE type = ap_fifo port = out_grad_x
// #pragma HLS DATAFLOW
//         hls::stream<cm_float> in_grad_y1, in_grad_y2;
//         hls::stream<cm_float> out_grad_x1, out_grad_x2;
//         joiner.backward2(in_grad_y, in_grad_y1, in_grad_y2);
//         if (ForkerType::param_size != 0) {
//             node1.backward(in_grad_y1, out_grad_x1);
//             node2.backward(in_grad_y2, out_grad_x2);
//             forker.backward2(out_grad_x1, out_grad_x2);
//         } else {
//             node1.backward(in_grad_y1);
//             node2.backward(in_grad_y2);
//         }
//     }
#endif

    ForkerType forker;
    Node1Type node1;
    Node2Type node2;
    JoinerType joiner;
};
