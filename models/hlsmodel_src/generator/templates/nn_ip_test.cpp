#include "global.hpp"
#include "net/functors.hpp"

using namespace hlsnn;

MODEL_API void load_param(cm_float params[$all_param_count]);

MODEL_API void extract_grad(cm_float grads[$all_param_count]);

MODEL_API void zero_grad();

MODEL_API void forward(bool cache_en, int n, cm_float in_x[$nn_in_size], cm_float out_y[$nn_out_size]);

MODEL_API void backward(int n, cm_float grad_y[$nn_out_size]);

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

    forward(false, 1, maxi_x, maxi_y);
    forward(true, 1, maxi_x, maxi_y);
    backward(1, maxi_grad_y);

    extract_grad(grads);
}
