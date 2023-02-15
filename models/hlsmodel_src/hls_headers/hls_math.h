#pragma once
// Fake one

#include <cmath>
#include "../global.hpp"
namespace hls
{
using hlsnn::cm_float;
static inline cm_float exp(cm_float x) { return std::exp(x); }
static inline bool isinf(cm_float x) { return std::isinf(x); }
static inline cm_float tanh(cm_float x) { return std::tanh(x); }
static inline cm_float pown(cm_float x, int n) {
    cm_float y = 1;
    while (n) {
        if (n & 1) y *= x;
        x *= x;
        n >>= 1;
    }
    return y;
}
} // namespace hls
