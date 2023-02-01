#pragma once

#include "../global.hpp"

template <int len>
struct Fifo2Ram1p {
    static void run(hls::stream<cm_float>& in, cm_float out[len]) {
#pragma HLS INTERFACE mode=ap_ctrl_chain port=return
#pragma HLS INTERFACE mode=ap_fifo port=in
#pragma HLS INTERFACE mode=bram storage_type=ram_1p port=out
    f2r: for (int i = 0; i < len; ++i) {
            cm_float x = in.read();
            out[i] = x;
        }
    }
};

template <int len>
struct Ram1p2Fifo {
    static void run(cm_float in[len], hls::stream<cm_float>& out) {
#pragma HLS INTERFACE mode=ap_ctrl_chain port=return
#pragma HLS INTERFACE mode=bram storage_type=ram_1p port=in
#pragma HLS INTERFACE mode=ap_fifo port=out
    f2r: for (int i = 0; i < len; ++i) {
            out << in[i];
        }
    }
};
