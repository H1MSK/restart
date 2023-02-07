#pragma once

#include "../global.hpp"

template <int len>
struct Stream2array {
    static void run(hls::stream<cm_float>& in, cm_float out[len]) {
    f2r: for (int i = 0; i < len; ++i) {
            cm_float x = in.read();
            out[i] = x;
        }
    }
};

template <int len>
struct Array2stream {
    static void run(cm_float in[len], hls::stream<cm_float>& out) {
    f2r: for (int i = 0; i < len; ++i) {
            out << in[i];
        }
    }
};
