#pragma once

#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wunused-variable"
#pragma GCC diagnostic ignored "-Wsign-compare"
#pragma GCC diagnostic ignored "-Wdeprecated-copy"
#include <hls_stream.h>
#pragma GCC diagnostic pop
#include <cstring>

namespace hlsnn {
using cm_float = float;
}  //namespace hlsnn

#include <hls_math.h>
#include <ap_int.h>

#define UNUSED(x)       ((void)(x))

#ifndef __SYNTHESIS__
#   if defined(WIN32)
#       define MODEL_API extern "C" __declspec(dllexport)
#   elif defined(__linux__)
#       define MODEL_API extern "C" __attribute__((visibility("default")))
#   endif
#else
#   define MODEL_API
#endif

#ifdef INTELLISENSE
#define $param_static_definitions   static cm_float param1[12];static cm_float param2[1]
#define $param_signatures           cm_float param1[12], cm_float param2[1]
#define $param_variables            param1, param2
#define $grad_static_definitions    static cm_float grad1[12];static cm_float grad2[1]
#define $grad_signatures            cm_float grad1[12], cm_float grad2[1]
#define $grad_variables             grad1, grad2
#define $cache_static_definitions   static hls::stream<cm_float, 5> cache1;static hls::stream<cm_float, 1> cache2
#define $cache_signatures           hls::stream<cm_float, 5>& cache1, hls::stream<cm_float, 1>& cache2
#define $cache_variables            cache1, cache2
#define $nn_in_size                 5
#define $nn_out_size                2
#define $all_param_count            13

#define $zero_grads                 memset(grad1, 0, sizeof(grad1));memset(grad2, 0, sizeof(grad2))

#define $param_ram1p_pragmas
#define $grad_ram1p_pragmas
#define $param_rom1p_pragmas
#define $param_rom2p_pragmas
#define $grad_rams2p_pragmas
#define $cache_fifo_interface_pragmas
#define $cache_fifo_storage_pragmas

#define $fw_content                 Linear<$nn_in_size, $nn_out_size>::forward(param1, in_x, out_y, cache1, cache_en);
#define $bw_content                 Linear<$nn_in_size, $nn_out_size>::backward_no(param1, grad1, cache1, in_grad_y);

#define $param_loader_content       int x = 0; for(int i = 0; i < 12; ++i) param1[i] = in[x++]; for (int i = 0; i < 1; ++i) param2[i] = in[x++];
#define $grad_extractor_content     int x = 0; for(int i = 0; i < 12; ++i) out[x++] = grad1[i]; for (int i = 0; i < 1; ++i) out[x++] = grad2[i];

#define $cache_writter_cases        case 1: cache1 << val; break; case 2: cache2 << val; break;
#define $cache_reader_cases         case 1: *val = cache1.read(); break; case 2: *val = cache2.read(); break;

// TODO: change type of generated inputs to ap_uint
#define $cache_monitor_inputs       ap_uint<3> in_size1, ap_uint<1> in_size2
#define $cache_monitor_outputs      int *out_size1, int *out_size2
#define $cache_monitor_pragmas
#define $cache_monitor_content

#endif
