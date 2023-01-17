#include "../global.hpp"

void fifo_switch(hls::stream<cm_float>& fifo_i,
                 hls::stream<cm_float>& fifo_o,
                 bool sel) {
#pragma HLS interface mode = ap_fifo port = fifo_i
#pragma HLS interface mode = ap_fifo port = fifo_o
#pragma HLS interface mode = ap_none port = sel
#pragma HLS stable variable = sel
    cm_float x;
    while (fifo_i.read_nb(x)) {
        fifo_o.write_dep(x, sel);
    }
}