#include "global.hpp"

using namespace hlsnn;

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
    $param_signatures,
    $cache_signatures);

void top_backward(
    cm_float maxi_grad_y[$nn_out_size],
    $param_signatures,
    $grad_signatures,
    $cache_signatures);

$cache_static_definitions;
$param_static_definitions;
$grad_static_definitions;

MODEL_API void load_param(cm_float params[$all_param_count]) {
    param_loader(params, $param_variables);
}

MODEL_API void extract_grad(cm_float grads[$all_param_count]) {
    grad_extractor($grad_variables, grads);
}

MODEL_API void zero_grad() {
    $zero_grads;
}

int main() {
    cm_float params[$all_param_count];
    cm_float grads[$all_param_count];
    cm_float maxi_x[$nn_in_size] = {0};
    cm_float maxi_y[$nn_out_size] = {0};
    cm_float maxi_grad_y[$nn_out_size] = {0};

    for (int i = 0; i < $all_param_count; ++i) {
        params[i] = rand() / (float)(RAND_MAX) * 0.05f - 0.025f;
    }

    zero_grad();

    for (int i = 0; i < $nn_in_size; ++i) {
        maxi_x[i] = rand() / (float)(RAND_MAX) * 0.05f - 0.025f;
    }

    for (int i = 0; i < $nn_out_size; ++i) {
        maxi_grad_y[i] = rand() / (float)(RAND_MAX) * 0.05f - 0.025f;
    }

    load_param(params);

    top_forward(maxi_x, maxi_y, false,
        $param_variables,
        $cache_variables);

    top_forward(maxi_x, maxi_y, true,
        $param_variables,
        $cache_variables);
    top_backward(maxi_grad_y,
        $param_variables,
        $grad_variables,
        $cache_variables);

    extract_grad(grads);
}
