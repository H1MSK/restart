#pragma once

#include "../global.hpp"

namespace hlsnn {

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

struct FloatBusCarrier {
    static_assert(cm_float_bitwidth == 32,
                  "Please change the type of i in View to match the bitwidth "
                  "of cm_float");
    union View {
        cm_float f;
        int i;
    };
    template <int len>
    static void loadArrayToAxisBus(hls::stream<cm_axis_data>& bus,
                                   cm_float arr[len],
                                   bool isLast) {
        for (int i = 0; i < len - 1; ++i) {
            #pragma HLS PIPELINE II = 1
            bus.write(pack(arr[i], false));
        }
        bus.write(pack(arr[len - 1], isLast));
    }
    template <int len>
    static void dumpArrayFromAxisBus(hls::stream<cm_axis_data>& bus,
                                     cm_float arr[len]) {
        for (int i = 0; i < len; ++i) {
            #pragma HLS PIPELINE II = 1
            arr[i] = unpack(bus.read());
        }
    }
    template <int len>
    static void loadFifoToAxisBus(hls::stream<cm_axis_data>& bus,
                                  hls::stream<cm_float, len>& fifo,
                                  bool isLast) {
        for (int i = 0; i < len - 1; ++i) {
            #pragma HLS PIPELINE II = 1
            bus.write(pack(fifo.read(), false));
        }
        bus.write(pack(fifo.read(), isLast));
    }
    template <int len>
    static void dumpFifoFromAxisBus(hls::stream<cm_axis_data>& bus,
                                    hls::stream<cm_float, len>& fifo) {
        for (int i = 0; i < len; ++i) {
            #pragma HLS PIPELINE II = 1
            fifo << unpack(bus.read());
        }
    }
    static cm_axis_data pack(cm_float x, bool isLast) {
        return cm_axis_data {
            .data = (View{.f = x}.i),
            .keep = 0xFFFFFFFFUL,
            .strb = 0xFFFFFFFFUL,
            .user = 0,
            .last = isLast,
            .id = 0,
            .dest = 0};
    }
    static cm_float unpack(const cm_axis_data& i) {
        return View{.i = int(i.data)}.f;
    }
};

}  // namespace hlsnn
