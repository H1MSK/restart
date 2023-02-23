#include "global.hpp"
#include "net/net.hpp"

using namespace hlsnn;

$param_static_definitions;

$grad_static_definitions;

$cache_static_definitions;

// TODO: use task_forward and task_backward

void param_loader(
    hls::stream<cm_axis_data> &in,
    $param_signatures);

void grad_extractor(
    $grad_signatures,
    hls::stream<cm_axis_data> &out);

void top_forward(hls::stream<cm_axis_data>& axis_x,
                 hls::stream<cm_axis_data>& axis_y,
                 int n,
                 bool cache_en,
                 $param_signatures,
                 $cache_signatures);

void top_backward(hls::stream<cm_axis_data>& axis_grad_y,
                  int n,
                  $param_signatures,
                  $grad_signatures,
                  $cache_signatures);

MODEL_API void load_param(cm_float params[$all_param_count]) {
    hls::stream<cm_axis_data> in;
    FloatBusCarrier::loadArrayToAxisBus<$all_param_count>(in, params, true);
    param_loader(in, $param_variables);
}

MODEL_API void extract_grad(cm_float grads[$all_param_count]) {
    hls::stream<cm_axis_data> out;
    grad_extractor($grad_variables, out);
    FloatBusCarrier::dumpArrayFromAxisBus<$all_param_count>(out, grads);
}

MODEL_API void zero_grad() {
    $zero_grads;
}

MODEL_API void forward(bool cache_en, int n, cm_float in_x[$nn_in_size], cm_float out_y[$nn_out_size]) {
    
    hls::stream<cm_axis_data> s_x;
    hls::stream<cm_axis_data> s_y;

    for (int i = 0; i < n; ++i) {
        FloatBusCarrier::loadArrayToAxisBus<$nn_in_size>(s_x, in_x, i + 1 == n);
    }
    top_forward(s_x, s_y, 1, cache_en, $param_variables, $cache_variables);
    for (int i = 0; i < n; ++i) {
        FloatBusCarrier::dumpArrayFromAxisBus<$nn_out_size>(s_y, out_y);
    }
}

MODEL_API void backward(int n, cm_float grad_y[$nn_out_size]) {
    hls::stream<cm_axis_data> s_grad;

    for (int i = 0; i < n; ++i) {
        FloatBusCarrier::loadArrayToAxisBus<$nn_out_size>(s_grad, grad_y, i + 1 == n);
    }
    top_backward(s_grad, 1, $param_variables, $grad_variables, $cache_variables);
}
