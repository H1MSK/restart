#include "global.hpp"
#include "net/net.hpp"

using namespace hlsnn;

template<int len>
void dump_from_axis(hls::stream<cm_axis_data> &axis, hls::stream<cm_float, len> &fifo/*, bool *need_stop, bool *complete*/) {
    int i;
    for (i = 0; i < len; ++i) {
        cm_axis_data tmp;
        axis.read(tmp);
        fifo.write(FloatBusCarrier::unpack(tmp));
        // if (tmp.last) {
        //     *need_stop = true;
        //     break;
        // }
    }
    // *complete = (i == len);
}

template<int len>
void load_to_axis(hls::stream<cm_axis_data> &axis, hls::stream<cm_float, len> &fifo, bool isLast) {
    for (int j = len - 1; j >= 0; --j) {
        axis.write(FloatBusCarrier::pack(fifo.read(), isLast && j == 0));
    }
}

void task_forward(hls::stream<cm_float, $nn_in_size>& in_x,
                  hls::stream<cm_float, $nn_out_size>& out_y,
                  bool cache_en,
                  $param_signatures,
                  $cache_signatures) {
    #pragma HLS INTERFACE mode=ap_ctrl_chain port=return
    #pragma HLS DATAFLOW
    #pragma HLS INTERFACE mode=ap_fifo port=in_x depth=$nn_in_size
    #pragma HLS INTERFACE mode=ap_fifo port=out_y depth=$nn_out_size
    #pragma HLS INTERFACE mode=ap_none port=cache_en
    #pragma HLS STABLE variable=cache_en

    $param_rom1p_pragmas
    $cache_fifo_interface_pragmas

    $fw_content
}

void top_forward(hls::stream<cm_axis_data>& axis_x,
                 hls::stream<cm_axis_data>& axis_y,
                 int n,
                 bool cache_en,
                 $param_signatures,
                 $cache_signatures) {
    #pragma HLS INTERFACE mode=s_axilite port=return
    #pragma HLS INTERFACE mode=axis port=axis_x register_mode=reverse
    #pragma HLS INTERFACE mode=axis port=axis_y register_mode=forward
    #pragma HLS INTERFACE mode=s_axilite port=cache_en
    #pragma HLS INTERFACE mode=s_axilite port=n

    $param_rom1p_pragmas
    $cache_fifo_interface_pragmas

    for (int i = 0; i < n; ++i) {
        #pragma HLS DATAFLOW
        hls::stream<cm_float, $nn_in_size> in_x;
        hls::stream<cm_float, $nn_out_size> out_y;
        dump_from_axis(axis_x, in_x);
        task_forward(in_x, out_y, cache_en, $param_variables, $cache_variables);
        load_to_axis(axis_y, out_y, false);
    }
    axis_y.write(cm_axis_data {
        .data = 0,
        .keep = 0,
        .strb = 0,
        .user = 0,
        .last = 1,
        .id = 0,
        .dest = 0
    });
}

void task_backward(hls::stream<cm_float, $nn_out_size>& in_grad_y,
                   $param_signatures,
                   $grad_signatures,
                   $cache_signatures) {
    #pragma HLS INTERFACE mode=ap_ctrl_chain port=return
    #pragma HLS DATAFLOW
    #pragma HLS INTERFACE mode=ap_fifo port=in_grad_y depth=$nn_out_size
    $param_rom1p_pragmas
    $grad_rams2p_pragmas
    $cache_fifo_interface_pragmas

    $bw_content
}

void top_backward(hls::stream<cm_axis_data>& axis_grad_y,
                  int n,
                  $param_signatures,
                  $grad_signatures,
                  $cache_signatures) {
    #pragma HLS INTERFACE mode=s_axilite port=return
    // #pragma HLS DATAFLOW
    #pragma HLS INTERFACE mode=s_axilite port=n
    #pragma HLS INTERFACE mode=axis port=axis_grad_y register_mode=reverse
    $param_rom1p_pragmas
    $grad_rams2p_pragmas
    $cache_fifo_interface_pragmas

    for (int i = 0; i < n; ++i) {
        #pragma HLS DATAFLOW
        hls::stream<cm_float, $nn_out_size> in_grad_y;
        dump_from_axis(axis_grad_y, in_grad_y);
        task_backward(in_grad_y, $param_variables, $grad_variables,
                      $cache_variables);
    }
}
