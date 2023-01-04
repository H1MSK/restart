#pragma once

#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wunused-variable"
#pragma GCC diagnostic ignored "-Wsign-compare"
#include <hls_stream.h>
#pragma GCC diagnostic pop
#include <cstring>

#ifndef OBS_DIM
#define OBS_DIM         376
#endif

#ifndef ACT_DIM
#define ACT_DIM         8
#endif

#ifndef HIDDEN_WIDTH
#define HIDDEN_WIDTH    64
#endif

#ifndef ACT_CONTINUOUS
#define ACT_CONTINUOUS  1
#endif

using cm_float = float;

#include <hls_math.h>
