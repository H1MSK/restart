#pragma once

#include "../global.hpp"
#include "functors.hpp"

template <int In, int Out>
struct Linear {
    constexpr static int in_size = In;
    constexpr static int out_size = Out;
    constexpr static int param_size = in_size * out_size + out_size;
    constexpr static int cache_size = in_size;

    static void forward(cm_float param[param_size],
                        hls::stream<cm_float>& in_x,
                        hls::stream<cm_float>& out_y,
                        hls::stream<cm_float>& cache,
                        bool cache_en) {
#pragma HLS INTERFACE mode = ap_ctrl_chain port = return
#pragma HLS INTERFACE mode = bram port = param storage_type = rom_1p
#pragma HLS INTERFACE mode = ap_fifo port = in_x
#pragma HLS INTERFACE mode = ap_fifo port = out_y
#pragma HLS INTERFACE mode = ap_fifo port = cache
#pragma HLS INTERFACE mode = ap_none port = cache_en
#pragma HLS STABLE variable = cache_en
        const cm_float* const w = param;
        const cm_float* const b = param + in_size * out_size;

        // This method will cause memory dependency violation on y_i in lfc_cal_i,
        //   which will stop ii from decrease
        // cm_float x[in_size];
        // #pragma HLS BIND_STORAGE variable=x type=ram_s2p
        //
        // Fifo2Ram1p<in_size>::run(in_x, x);
        //
        // lfc_cal: for (int i = 0; i < out_size; ++i) {
        //     cm_float y_i = b[i];
        //     lfc_cal_i: for (int j = 0; j < in_size; ++j) {
        //         y_i += w[i * in_size + j] * x[j];
        //     }
        //     out_y << y_i;
        // }

        // This method will introduce 1-cycle latency on y because of its implementation
        //   need use bram as storage
        cm_float y[out_size] = {0};
        #pragma HLS BIND_STORAGE variable=y type=ram_s2p
        lfc_cal: for (int j = 0; j < in_size; ++j) {
            cm_float x_j = in_x.read();
            if (cache_en) cache << x_j;
            lfc_cal_i: for (int i = 0; i < out_size; ++i) {
                #pragma HLS PIPELINE II=1
                y[i] += w[i * in_size + j] * x_j;
            }
        }

        lfc_o: for (int i = 0; i < out_size; ++i) {
            out_y << y[i] + b[i];
        }
        
        // This method is ideal for me but the dependence will become true
        //   if clock speed is too fast, and all items will be read out before
        //   new items are written into the fifo
        // And, The dependence pragma seems to be ignored by vitis.
        // hls::stream<cm_float, out_size> loop_y;
        // #pragma HLS BIND_STORAGE variable=loop_y type=fifo impl=srl
        // lfc_i: for (int i = 0; i < out_size; ++i) {
        //     loop_y.write(b[i]);
        // }
        // lfc_cal2: for (int j = 0; j < in_size; ++j) {
        //     cm_float x_j = in_x.read();
        //     lfc_cal2_i: for (int i = 0; i < out_size; ++i) {
        //     #pragma HLS PIPELINE
        //     #pragma HLS DEPENDENCE variable=loop_y dependent=false
        //         cm_float y_i = loop_y.read();
        //         y_i += w[i * in_size + j] * x_j;
        //         loop_y.write(y_i);
        //     }
        // }
        // lfc2_o: for (int i = 0; i < out_size; ++i) {
        //     out_y << loop_y.read();
        // }
    }

    static void backward_output(cm_float param[param_size],
                                hls::stream<cm_float>& in_grad_y,
                                hls::stream<cm_float>& out_grad_x) {
#pragma HLS INTERFACE mode = ap_ctrl_chain port = return
#pragma HLS INTERFACE mode = bram port = param storage_type = rom_1p
#pragma HLS INTERFACE mode = ap_fifo port = in_grad_y
#pragma HLS INTERFACE mode = ap_fifo port = out_grad_x
        const cm_float* const w = param;
        cm_float grad_x_cache[in_size] = {0};
#pragma HLS BIND_STORAGE variable=grad_x_cache type=ram_s2p
    lbo_cal:
        for (int i = 0; i < out_size; ++i) {
            cm_float grad_y_i = in_grad_y.read();
        lbo_cal_i:
            for (int j = 0; j < in_size; ++j) {
#pragma HLS DEPENDENCE variable=grad_x_cache dependent=false
                grad_x_cache[j] += w[i * in_size + j] * grad_y_i;
            }
        }
    lbo_o:
        for (int j = 0; j < in_size; ++j) {
            out_grad_x << grad_x_cache[j];
        }
    }

    static void backward_param_calc(hls::stream<cm_float>& cache,
                                    hls::stream<cm_float>& in_grad_y,
                                    cm_float grad[param_size]) {
#pragma HLS INTERFACE mode = ap_ctrl_chain port = return
#pragma HLS INTERFACE mode = ap_fifo port = cache
#pragma HLS INTERFACE mode = ap_fifo port = in_grad_y
#pragma HLS INTERFACE mode = bram port = grad storage_type = ram_s2p

        cm_float* const grad_w = grad;
        cm_float* const grad_b = grad + in_size * out_size;

        cm_float cache_x[in_size];
#pragma HLS BIND_STORAGE variable=cache_x type=ram_s2p
//#pragma HLS ARRAY_PARTITION variable=cache_x type=complete
        Fifo2Ram1p<in_size>::run(cache, cache_x);

    lbw:
        for (int i = 0; i < out_size; ++i) {
#pragma HLS DEPENDENCE variable=grad dependent=false
            cm_float grad_y_i = in_grad_y.read();
        lbw_i:
            for (int j = 0; j < in_size; ++j) {
#pragma HLS DEPENDENCE variable=grad dependent=false
                grad_w[i * in_size + j] += grad_y_i * cache_x[j];
            }
            grad_b[i] += grad_y_i;
        }
    }

    static void backward(cm_float param[param_size],
                         cm_float grad[param_size],
                         hls::stream<cm_float>& cache,
                         hls::stream<cm_float>& in_grad_y,
                         hls::stream<cm_float>& out_grad_x) {
#pragma HLS INTERFACE mode = ap_ctrl_chain port = return
#pragma HLS INTERFACE mode = bram port = param storage_type = rom_1p
#pragma HLS INTERFACE mode = bram port = grad storage_type = ram_s2p
#pragma HLS INTERFACE mode = ap_fifo port = cache
#pragma HLS INTERFACE mode = ap_fifo port = in_grad_y
#pragma HLS INTERFACE mode = ap_fifo port = out_grad_x
#pragma HLS DATAFLOW

        hls::stream<cm_float, out_size> grad_y1;
        hls::stream<cm_float, out_size> grad_y2;

        StreamSplitter2<out_size>::run(in_grad_y, grad_y1, grad_y2);

        backward_output(param, grad_y1, out_grad_x);

        backward_param_calc(cache, grad_y2, grad);
    }

    static void backward_no(cm_float param[param_size],
                            cm_float grad[param_size],
                            hls::stream<cm_float>& cache,
                            hls::stream<cm_float>& in_grad_y) {
#pragma HLS INTERFACE mode = ap_ctrl_chain port = return
#pragma HLS INTERFACE mode = bram port = param storage_type = rom_1p
#pragma HLS INTERFACE mode = bram port = grad storage_type = ram_s2p
#pragma HLS INTERFACE mode = ap_fifo port = cache
#pragma HLS INTERFACE mode = ap_fifo port = in_grad_y
#pragma HLS DATAFLOW

        backward_param_calc(cache, in_grad_y, grad);
    }
};
