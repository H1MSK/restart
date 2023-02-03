#include "global.hpp"
#include "net/net.hpp"

$param_static_definitions;

$grad_static_definitions;

$cache_static_definitions;

void param_loader(
    hls::stream<cm_float>& in,
    $param_signatures);

void grad_extractor(
    $grad_signatures,
    hls::stream<cm_float>& out);

void top_forward(
    hls::stream<cm_float, $nn_in_size>& in_x,
    hls::stream<cm_float, $nn_out_size>& out_y,
    bool cache_en,
    $param_signatures,
    $cache_signatures);

void top_backward(
    hls::stream<cm_float, $nn_out_size>& in_grad_y,
    $param_signatures,
    $grad_signatures,
    $cache_signatures);

MODEL_API void load_param(cm_float params[$all_param_count]) {
    hls::stream<cm_float, $all_param_count> param_stream;
    Ram1p2Fifo<$all_param_count>::run(params, param_stream);
    param_loader(param_stream, $param_variables);
}

MODEL_API void extract_grad(cm_float grads[$all_param_count]) {
    hls::stream<cm_float, $all_param_count> grad_stream;
    grad_extractor($grad_variables, grad_stream);
    Fifo2Ram1p<$all_param_count>::run(grad_stream, grads);
}

MODEL_API void zero_grad() {
    $zero_grads;
}

MODEL_API void forward(bool cache_en, cm_float x[$nn_in_size], cm_float y[$nn_out_size]) {
    hls::stream<cm_float, $nn_in_size> in_x;
    hls::stream<cm_float, $nn_out_size> out_y;

    Ram1p2Fifo<$nn_in_size>::run(x, in_x);
    top_forward(in_x, out_y, cache_en, $param_variables, $cache_variables);
    Fifo2Ram1p<$nn_out_size>::run(out_y, y);
}

MODEL_API void backward(cm_float grad_y[$nn_out_size]) {
    hls::stream<cm_float, $nn_out_size> in_grad_y;

    Ram1p2Fifo<$nn_out_size>::run(grad_y, in_grad_y);

    top_backward(in_grad_y, $param_variables, $grad_variables, $cache_variables);
}
