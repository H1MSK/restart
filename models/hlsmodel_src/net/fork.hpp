#pragma once

#include "../global.hpp"

namespace hlsnn {

template <int len>
struct Fork2 {
    static void forward(hls::stream<cm_float>& in,
                        hls::stream<cm_float>& out1,
                        hls::stream<cm_float>& out2) {
#pragma HLS INTERFACE mode=ap_ctrl_chain port=return
#pragma HLS INTERFACE mode=ap_fifo port=in
#pragma HLS INTERFACE mode=ap_fifo port=out1
#pragma HLS INTERFACE mode=ap_fifo port=out2
    f2f: for (int i = 0; i < len; ++i) {
            cm_float x = in.read();
            out1.write(x);
            out2.write(x);
        }
    }
    static void backward(hls::stream<cm_float>& in1,
                         hls::stream<cm_float>& in2,
                         hls::stream<cm_float>& out) {
#pragma HLS INTERFACE mode=ap_ctrl_chain port=return
#pragma HLS INTERFACE mode=ap_fifo port=in1
#pragma HLS INTERFACE mode=ap_fifo port=in2
#pragma HLS INTERFACE mode=ap_fifo port=out
    f2b: for (int i = 0; i < len; ++i) {
            cm_float x = in1.read();
            cm_float y = in2.read();
            out.write(x + y);
        }
    }
};

template <int len>
struct Fork3 {
    static void forward(hls::stream<cm_float>& in,
                        hls::stream<cm_float>& out1,
                        hls::stream<cm_float>& out2,
                        hls::stream<cm_float>& out3) {
#pragma HLS INTERFACE mode=ap_ctrl_chain port=return
#pragma HLS INTERFACE mode=ap_fifo port=in
#pragma HLS INTERFACE mode=ap_fifo port=out1
#pragma HLS INTERFACE mode=ap_fifo port=out2
#pragma HLS INTERFACE mode=ap_fifo port=out3
    f3f: for (int i = 0; i < len; ++i) {
            cm_float x = in.read();
            out1.write(x);
            out2.write(x);
            out3.write(x);
        }
    }
    static void backward(hls::stream<cm_float>& in1,
                         hls::stream<cm_float>& in2,
                         hls::stream<cm_float>& in3,
                         hls::stream<cm_float>& out) {
#pragma HLS INTERFACE mode=ap_ctrl_chain port=return
#pragma HLS INTERFACE mode=ap_fifo port=in1
#pragma HLS INTERFACE mode=ap_fifo port=in2
#pragma HLS INTERFACE mode=ap_fifo port=in3
#pragma HLS INTERFACE mode=ap_fifo port=out
    f3b: for (int i = 0; i < len; ++i) {
            cm_float x1 = in1.read();
            cm_float x2 = in2.read();
            cm_float x3 = in3.read();
            out.write(x1 + x2 + x3);
        }
    }
};

}  //namespace hlsnn
