#include "global.hpp"
using namespace hlsnn;

void cache_writter(
    int pos, cm_float val,
    $cache_signatures) {
    #pragma HLS INTERFACE mode=s_axilite port=return
    #pragma HLS INTERFACE mode=s_axilite port=pos
    #pragma HLS INTERFACE mode=s_axilite port=val
    $cache_fifo_interface_pragmas

    switch (pos) {
    $cache_writter_cases
    default:
        break;
    }
}

void cache_reader(
    int pos, cm_float* val,
    $cache_signatures) {
    #pragma HLS INTERFACE mode=s_axilite port=return
    #pragma HLS INTERFACE mode=s_axilite port=pos
    #pragma HLS INTERFACE mode=s_axilite port=val
    $cache_fifo_interface_pragmas

    switch (pos) {
    $cache_reader_cases
    default:
        break;
    }
}

void cache_monitor(
    $cache_monitor_inputs,
    $cache_monitor_outputs
) {
    #pragma HLS INTERFACE mode=s_axilite port=return
    $cache_monitor_pragmas

    $cache_monitor_content
}
