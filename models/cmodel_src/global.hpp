#pragma once

#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wunused-variable"
#pragma GCC diagnostic ignored "-Wsign-compare"
#include <hls_stream.h>
#pragma GCC diagnostic pop

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

#ifndef CM_WITH_BACKWARD
#define CM_WITH_BACKWARD 1
#endif

#ifndef __SYNTHESIS__
#   if defined(WIN32)
#       define CM_API extern "C" __declspec(dllexport)
#   elif defined(__linux__)
#       define CM_API extern "C" __attribute__((visibility("default")))
#   endif
#else
#   define CM_API
#endif

enum NN_OP {
    NN_OP_None              = 0x00,
    NN_OP_LoadParam         = 0x01,
    NN_OP_DumpGradAndZero   = 0x02,
    NN_OP_Forward           = 0x10,
    NN_OP_ForwardWithCache  = 0x20,
    NN_OP_Backward          = 0x40,
};

using cm_float = float;

#include <hls_math.h>

#define CM_UNUSED(x)            ((void)(x))

#ifdef __SYNTHESIS__
#   define CM_PRINT(...)
#else
#   ifdef DEBUG
#       define CM_PRINT(...)    printf(__VA_ARGS__)
#   else
#       define CM_PRINT(...)
#   endif
#endif
