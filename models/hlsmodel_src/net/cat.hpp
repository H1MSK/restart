#pragma once

#include "../global.hpp"


template <int len1, int len2>
struct Cat2 {
    static void forward(hls::stream<cm_float>& in1,
                        hls::stream<cm_float>& in2,
                        hls::stream<cm_float>& out) {
#pragma HLS INTERFACE mode=ap_ctrl_chain port=return
#pragma HLS INTERFACE mode=ap_fifo port=in1
#pragma HLS INTERFACE mode=ap_fifo port=in2
#pragma HLS INTERFACE mode=ap_fifo port=out
    c2f_1: for (int i = 0; i < len1; ++i) {
            cm_float x = in1.read();
            out.write(x);
        }
    c2f_2: for (int i = 0; i < len2; ++i) {
            cm_float x = in2.read();
            out.write(x);
        }
    }
    static void backward(hls::stream<cm_float>& in,
                         hls::stream<cm_float>& out1,
                         hls::stream<cm_float>& out2) {
#pragma HLS INTERFACE mode=ap_ctrl_chain port=return
#pragma HLS INTERFACE mode=ap_fifo port=in
#pragma HLS INTERFACE mode=ap_fifo port=out1
#pragma HLS INTERFACE mode=ap_fifo port=out2
    c2b_1: for (int i = 0; i < len1; ++i) {
            cm_float x = in.read();
            out1.write(x);
        }
    c2b_2: for (int i = 0; i < len2; ++i) {
            cm_float x = in.read();
            out2.write(x);
        }
    }
};

template <int len1, int len2, int len3>
struct Cat3 {
    static void forward(hls::stream<cm_float>& in1,
                        hls::stream<cm_float>& in2,
                        hls::stream<cm_float>& in3,
                        hls::stream<cm_float>& out) {
#pragma HLS INTERFACE mode=ap_ctrl_chain port=return
#pragma HLS INTERFACE mode=ap_fifo port=in1
#pragma HLS INTERFACE mode=ap_fifo port=in2
#pragma HLS INTERFACE mode=ap_fifo port=in3
#pragma HLS INTERFACE mode=ap_fifo port=out
    c3f_1: for (int i = 0; i < len1; ++i) {
            cm_float x = in1.read();
            out.write(x);
        }
    c3f_2: for (int i = 0; i < len2; ++i) {
            cm_float x = in2.read();
            out.write(x);
        }
    c3f_3: for (int i = 0; i < len3; ++i) {
            cm_float x = in3.read();
            out.write(x);
        }
    }
    static void backward(hls::stream<cm_float>& in,
                         hls::stream<cm_float>& out1,
                         hls::stream<cm_float>& out2,
                         hls::stream<cm_float>& out3) {
#pragma HLS INTERFACE mode=ap_ctrl_chain port=return
#pragma HLS INTERFACE mode=ap_fifo port=in
#pragma HLS INTERFACE mode=ap_fifo port=out1
#pragma HLS INTERFACE mode=ap_fifo port=out2
#pragma HLS INTERFACE mode=ap_fifo port=out3
    c3b_1: for (int i = 0; i < len1; ++i) {
            cm_float x = in.read();
            out1.write(x);
        }
    c3b_2: for (int i = 0; i < len2; ++i) {
            cm_float x = in.read();
            out2.write(x);
        }
    c3b_3: for (int i = 0; i < len3; ++i) {
            cm_float x = in.read();
            out3.write(x);
        }
    }
};
