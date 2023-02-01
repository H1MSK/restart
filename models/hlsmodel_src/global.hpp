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
#define $all_param_count             2

#define $zero_grads                 memset(grad1, 0, sizeof(grad1));memset(grad2, 0, sizeof(grad2))

#define $param_rom1p_pragmas
#define $param_rom2p_pragmas
#define $grad_rams2p_pragmas
#define $cache_fifo_interface_pragmas
#define $cache_fifo_storage_pragmas

#define $fw_content                 Linear<$nn_in_size, $nn_out_size>::forward(param1, in_x, out_y, cache1, cache_en);
#define $bw_content                 Linear<$nn_in_size, $nn_out_size>::backward_no(param1, grad1, cache1, in_grad_y);
#endif
