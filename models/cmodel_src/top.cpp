#include <hls_stream.h>
#include "global.hpp"
#include "net/net.hpp"

class NetType;

void top(NN_OP op,
         hls::stream<cm_float> in_param,
         hls::stream<cm_float> out_grad,
         hls::stream<cm_float> in_x,
         hls::stream<cm_float> in_grad_y,
         hls::stream<cm_float> out_y
         ) {
    static NetType net;
    switch(op) {
        case NN_OP_LoadParam:
            net.loadParam(in_param);
            break;
        case NN_OP_DumpGradAndZero:
            net.dumpGradAndZero(out_grad);
            break;
        case NN_OP_Forward:
            net.
    }
}
