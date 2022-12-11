#pragma once
// Fake one

#include <cmath>
#include "../global.hpp"
namespace hls
{
static inline cm_float exp(cm_float x) { return std::exp(x); }
static inline bool isinf(cm_float x) { return std::isinf(x); }
} // namespace hls