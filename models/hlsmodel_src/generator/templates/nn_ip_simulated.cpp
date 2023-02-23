#include "global.hpp"
#include "net/net.hpp"

using namespace hlsnn;

$param_static_definitions;

$grad_static_definitions;

$cache_static_definitions;

// TODO: use task_forward and task_backward

void param_loader(
    cm_float in[$all_param_count],
    $param_signatures);

void grad_extractor(
    $grad_signatures,
    cm_float out[$all_param_count]);

void top_forward(
    cm_float maxi_x[$nn_in_size],
    cm_float maxi_y[$nn_out_size],
    bool cache_en,
    int n,
    $param_signatures,
    $cache_signatures);

void top_backward(
    cm_float maxi_grad_y[$nn_out_size],
    int n,
    $param_signatures,
    $grad_signatures,
    $cache_signatures);

MODEL_API void load_param(cm_float params[$all_param_count]) {
    param_loader(params, $param_variables);
}

MODEL_API void extract_grad(cm_float grads[$all_param_count]) {
    grad_extractor($grad_variables, grads);
}

MODEL_API void zero_grad() {
    $zero_grads;
}

MODEL_API void forward(bool cache_en, int n, cm_float in_x[$nn_in_size], cm_float out_y[$nn_out_size]) {
    top_forward(in_x, out_y, cache_en, n, $param_variables, $cache_variables);
}

MODEL_API void backward(int n, cm_float grad_y[$nn_out_size]) {
    top_backward(grad_y, n, $param_variables, $grad_variables, $cache_variables);
}
