#include "global.hpp"
#include "net/net.hpp"

using namespace hlsnn;

$param_static_definitions;

$grad_static_definitions;

$cache_static_definitions;

void param_loader(
    hls::stream<cm_axis_data> &in,
    $param_signatures);

void grad_extractor(
    $grad_signatures,
    hls::stream<cm_axis_data> &out);

void top_forward(
    hls::stream<cm_axis_data> &axis_x,
    hls::stream<cm_axis_data> &axis_y,
    bool cache_en,
    $param_signatures,
    $cache_signatures);

void top_backward(
    hls::stream<cm_axis_data> &axis_grad_y,
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

MODEL_API void forward(bool cache_en, cm_float in_x[$nn_in_size], cm_float out_y[$nn_out_size]) {
    
    hls::stream<cm_axis_data> s_x;
    hls::stream<cm_axis_data> s_y;

    FloatBusCarrier::loadArrayToAxisBus<$nn_in_size>(s_x, in_x, true);
    top_forward(s_x, s_y, cache_en, $param_variables, $cache_variables);
    FloatBusCarrier::dumpArrayFromAxisBus<$nn_out_size>(s_y, out_y);
}

MODEL_API void backward(cm_float grad_y[$nn_out_size]) {
    hls::stream<cm_axis_data> s_grad;
    FloatBusCarrier::loadArrayToAxisBus<$nn_out_size>(s_grad, grad_y, true);
    top_backward(s_grad, $param_variables, $grad_variables, $cache_variables);
}
