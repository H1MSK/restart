#pragma once

#include "../global.hpp"

template <int len>
struct StreamSplitter2 {
    static void forward(hls::stream<cm_float>& in,
                        hls::stream<cm_float>& out1,
                        hls::stream<cm_float>& out2) {
        #pragma HLS INTERFACE mode=ap_ctrl_none port=return
        #pragma HLS INTERFACE mode=ap_fifo port=in
        #pragma HLS INTERFACE mode=ap_fifo port=out1
        #pragma HLS INTERFACE mode=ap_fifo port=out2
        for (int i = 0; i < len; ++i) {
            cm_float x = in.read();
            out1.write(x);
            out2.write(x);
        }
    }
};

template <int len1, int len2>
struct StreamCat2 {
    static void forward(hls::stream<cm_float>& in1,
                        hls::stream<cm_float>& in2,
                        hls::stream<cm_float>& out) {
        #pragma HLS INTERFACE mode=ap_ctrl_none port=return
        #pragma HLS INTERFACE mode=ap_fifo port=in1
        #pragma HLS INTERFACE mode=ap_fifo port=in2
        #pragma HLS INTERFACE mode=ap_fifo port=out
        for (int i = 0; i < len1; ++i) {
            cm_float x = in1.read();
            out.write(x);
        }
        for (int i = 0; i < len2; ++i) {
            cm_float x = in2.read();
            out.write(x);
        }
    }
};

template <int len>
struct StreamAdder2 {
    static void forward(hls::stream<cm_float>& in1,
                        hls::stream<cm_float>& in2,
                        hls::stream<cm_float>& out) {
        #pragma HLS INTERFACE mode=ap_ctrl_none port=return
        #pragma HLS INTERFACE mode=ap_fifo port=in1
        #pragma HLS INTERFACE mode=ap_fifo port=in2
        #pragma HLS INTERFACE mode=ap_fifo port=out
        for (int i = 0; i < len; ++i) {
            cm_float x = in1.read();
            cm_float y = in2.read();
            out.write(x + y);
        }
    }
};
