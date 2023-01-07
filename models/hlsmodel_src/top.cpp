#include "global.hpp"
#include "net/net.hpp"

void forward(hls::stream<cm_float>& in_x, hls::stream<cm_float, 35>& out_y, cm_float param1_24128o64[24128], cm_float param3_4160o64[4160], cm_float param5_65o1[65], cm_float param7_24128o64[24128], cm_float param9_4160o64[4160], cm_float param12_1105o17[1105], cm_float param14_1105o17[1105], hls::stream<cm_float>& cache1_376_o, hls::stream<cm_float>& cache2_64_o, hls::stream<cm_float>& cache3_64_o, hls::stream<cm_float>& cache4_64_o, hls::stream<cm_float>& cache5_64_o, hls::stream<cm_float>& cache7_376_o, hls::stream<cm_float>& cache8_64_o, hls::stream<cm_float>& cache9_64_o, hls::stream<cm_float>& cache10_64_o, hls::stream<cm_float>& cache12_64_o, hls::stream<cm_float>& cache14_64_o, hls::stream<cm_float>& cache15_17_o) {
    #pragma HLS INTERFACE mode=ap_ctrl_chain port=return
    #pragma HLS DATAFLOW
    #pragma HLS INTERFACE mode=axis port=in_x register_mode=reverse depth=376
    #pragma HLS INTERFACE mode=axis port=out_y register_mode=forward depth=35
    #pragma HLS INTERFACE mode=bram storage_type=rom_1p port=param latency=1
    #pragma HLS INTERFACE mode=bram storage_type=rom_1p port=param latency=1
    #pragma HLS INTERFACE mode=bram storage_type=rom_1p port=param latency=1
    #pragma HLS INTERFACE mode=bram storage_type=rom_1p port=param latency=1
    #pragma HLS INTERFACE mode=bram storage_type=rom_1p port=param latency=1
    #pragma HLS INTERFACE mode=bram storage_type=rom_1p port=param latency=1
    #pragma HLS INTERFACE mode=bram storage_type=rom_1p port=param latency=1
    #pragma HLS INTERFACE mode=fifo port=cache1_376_out latency=1 depth=35
    #pragma HLS INTERFACE mode=fifo port=cache2_64_out latency=1 depth=35
    #pragma HLS INTERFACE mode=fifo port=cache3_64_out latency=1 depth=35
    #pragma HLS INTERFACE mode=fifo port=cache4_64_out latency=1 depth=35
    #pragma HLS INTERFACE mode=fifo port=cache5_64_out latency=1 depth=35
    #pragma HLS INTERFACE mode=fifo port=cache7_376_out latency=1 depth=35
    #pragma HLS INTERFACE mode=fifo port=cache8_64_out latency=1 depth=35
    #pragma HLS INTERFACE mode=fifo port=cache9_64_out latency=1 depth=35
    #pragma HLS INTERFACE mode=fifo port=cache10_64_out latency=1 depth=35
    #pragma HLS INTERFACE mode=fifo port=cache12_64_out latency=1 depth=35
    #pragma HLS INTERFACE mode=fifo port=cache14_64_out latency=1 depth=35
    #pragma HLS INTERFACE mode=fifo port=cache15_17_out latency=1 depth=35

    hls::stream<cm_float, 376> fork0_f0;
    #pragma HLS BIND_STORAGE variable=fork0_f0 type=fifo
    
    hls::stream<cm_float, 376> fork0_f1;
    #pragma HLS BIND_STORAGE variable=fork0_f1 type=fifo
    
    // 0: ('Fork', 376)
    StreamSplitter2<376>::forward(
        in_x,
        fork0_f0,
        fork0_f1);
    
    hls::stream<cm_float, 64> linear1_fo;
    #pragma HLS BIND_STORAGE variable=linear1_fo type=fifo
    
    Linear<376, 64>::forward(
        param1_24128o64,
        fork0_f0,
        linear1_fo,
        cache1_376_o);
    
    hls::stream<cm_float, 64> tanh2_fo;
    #pragma HLS BIND_STORAGE variable=tanh2_fo type=fifo
    
    Tanh<64>::forward(
        linear1_fo,
        tanh2_fo,
        cache2_64_o);
    
    hls::stream<cm_float, 64> linear3_fo;
    #pragma HLS BIND_STORAGE variable=linear3_fo type=fifo
    
    Linear<64, 64>::forward(
        param3_4160o64,
        tanh2_fo,
        linear3_fo,
        cache3_64_o);
    
    hls::stream<cm_float, 64> tanh4_fo;
    #pragma HLS BIND_STORAGE variable=tanh4_fo type=fifo
    
    Tanh<64>::forward(
        linear3_fo,
        tanh4_fo,
        cache4_64_o);
    
    hls::stream<cm_float, 1> linear5_fo;
    #pragma HLS BIND_STORAGE variable=linear5_fo type=fifo
    
    Linear<64, 1>::forward(
        param5_65o1,
        tanh4_fo,
        linear5_fo,
        cache5_64_o);
    
    hls::stream<cm_float, 64> linear7_fo;
    #pragma HLS BIND_STORAGE variable=linear7_fo type=fifo
    
    Linear<376, 64>::forward(
        param7_24128o64,
        fork0_f1,
        linear7_fo,
        cache7_376_o);
    
    hls::stream<cm_float, 64> tanh8_fo;
    #pragma HLS BIND_STORAGE variable=tanh8_fo type=fifo
    
    Tanh<64>::forward(
        linear7_fo,
        tanh8_fo,
        cache8_64_o);
    
    hls::stream<cm_float, 64> linear9_fo;
    #pragma HLS BIND_STORAGE variable=linear9_fo type=fifo
    
    Linear<64, 64>::forward(
        param9_4160o64,
        tanh8_fo,
        linear9_fo,
        cache9_64_o);
    
    hls::stream<cm_float, 64> tanh10_fo;
    #pragma HLS BIND_STORAGE variable=tanh10_fo type=fifo
    
    Tanh<64>::forward(
        linear9_fo,
        tanh10_fo,
        cache10_64_o);
    
    hls::stream<cm_float, 64> fork11_f0;
    #pragma HLS BIND_STORAGE variable=fork11_f0 type=fifo
    
    hls::stream<cm_float, 64> fork11_f1;
    #pragma HLS BIND_STORAGE variable=fork11_f1 type=fifo
    
    // 11: ('Fork', 64)
    StreamSplitter2<64>::forward(
        tanh10_fo,
        fork11_f0,
        fork11_f1);
    
    hls::stream<cm_float, 17> linear12_fo;
    #pragma HLS BIND_STORAGE variable=linear12_fo type=fifo
    
    Linear<64, 17>::forward(
        param12_1105o17,
        fork11_f0,
        linear12_fo,
        cache12_64_o);
    
    hls::stream<cm_float, 17> linear14_fo;
    #pragma HLS BIND_STORAGE variable=linear14_fo type=fifo
    
    Linear<64, 17>::forward(
        param14_1105o17,
        fork11_f1,
        linear14_fo,
        cache14_64_o);
    
    hls::stream<cm_float, 17> exp15_fo;
    #pragma HLS BIND_STORAGE variable=exp15_fo type=fifo
    
    Exp<17>::forward(
        linear14_fo,
        exp15_fo,
        cache15_17_o);
    
    hls::stream<cm_float, 34> forkend16_fo;
    #pragma HLS BIND_STORAGE variable=forkend16_fo type=fifo
    
    StreamCat2<17, 17>::forward(
        linear12_fo,
        exp15_fo,
        forkend16_fo);
    hls::stream<cm_float, 35> forkend17_fo;
    #pragma HLS BIND_STORAGE variable=forkend17_fo type=fifo
    
    StreamCat2<1, 34>::forward(
        linear5_fo,
        forkend16_fo,
        forkend17_fo);
}

void backward(hls::stream<cm_float, 35>& in_grad_y, cm_float param1_24128o64[24128], cm_float grad1_24128o64[24128], cm_float param3_4160o64[4160], cm_float grad3_4160o64[4160], cm_float param5_65o1[65], cm_float grad5_65o1[65], cm_float param7_24128o64[24128], cm_float grad7_24128o64[24128], cm_float param9_4160o64[4160], cm_float grad9_4160o64[4160], cm_float param12_1105o17[1105], cm_float grad12_1105o17[1105], cm_float param14_1105o17[1105], cm_float grad14_1105o17[1105], hls::stream<cm_float>& cache1_376_i, hls::stream<cm_float>& cache2_64_i, hls::stream<cm_float>& cache3_64_i, hls::stream<cm_float>& cache4_64_i, hls::stream<cm_float>& cache5_64_i, hls::stream<cm_float>& cache7_376_i, hls::stream<cm_float>& cache8_64_i, hls::stream<cm_float>& cache9_64_i, hls::stream<cm_float>& cache10_64_i, hls::stream<cm_float>& cache12_64_i, hls::stream<cm_float>& cache14_64_i, hls::stream<cm_float>& cache15_17_i) {
    #pragma HLS INTERFACE mode=ap_ctrl_chain port=return
    #pragma HLS DATAFLOW
    #pragma HLS INTERFACE mode=axis port=in_grad_y register_mode=reverse depth=35
    #pragma HLS INTERFACE mode=bram storage_type=rom_1p port=param latency=1
    #pragma HLS INTERFACE mode=bram storage_type=ram_s2p port=grad latency=1
    #pragma HLS INTERFACE mode=bram storage_type=rom_1p port=param latency=1
    #pragma HLS INTERFACE mode=bram storage_type=ram_s2p port=grad latency=1
    #pragma HLS INTERFACE mode=bram storage_type=rom_1p port=param latency=1
    #pragma HLS INTERFACE mode=bram storage_type=ram_s2p port=grad latency=1
    #pragma HLS INTERFACE mode=bram storage_type=rom_1p port=param latency=1
    #pragma HLS INTERFACE mode=bram storage_type=ram_s2p port=grad latency=1
    #pragma HLS INTERFACE mode=bram storage_type=rom_1p port=param latency=1
    #pragma HLS INTERFACE mode=bram storage_type=ram_s2p port=grad latency=1
    #pragma HLS INTERFACE mode=bram storage_type=rom_1p port=param latency=1
    #pragma HLS INTERFACE mode=bram storage_type=ram_s2p port=grad latency=1
    #pragma HLS INTERFACE mode=bram storage_type=rom_1p port=param latency=1
    #pragma HLS INTERFACE mode=bram storage_type=ram_s2p port=grad latency=1
    #pragma HLS INTERFACE mode=fifo port=cache1_376_in latency=1 depth=35
    #pragma HLS INTERFACE mode=fifo port=cache2_64_in latency=1 depth=35
    #pragma HLS INTERFACE mode=fifo port=cache3_64_in latency=1 depth=35
    #pragma HLS INTERFACE mode=fifo port=cache4_64_in latency=1 depth=35
    #pragma HLS INTERFACE mode=fifo port=cache5_64_in latency=1 depth=35
    #pragma HLS INTERFACE mode=fifo port=cache7_376_in latency=1 depth=35
    #pragma HLS INTERFACE mode=fifo port=cache8_64_in latency=1 depth=35
    #pragma HLS INTERFACE mode=fifo port=cache9_64_in latency=1 depth=35
    #pragma HLS INTERFACE mode=fifo port=cache10_64_in latency=1 depth=35
    #pragma HLS INTERFACE mode=fifo port=cache12_64_in latency=1 depth=35
    #pragma HLS INTERFACE mode=fifo port=cache14_64_in latency=1 depth=35
    #pragma HLS INTERFACE mode=fifo port=cache15_17_in latency=1 depth=35

    hls::stream<cm_float, 35> fork17_b0;
    #pragma HLS BIND_STORAGE variable=fork17_b0 type=fifo
    
    hls::stream<cm_float, 35> fork17_b1;
    #pragma HLS BIND_STORAGE variable=fork17_b1 type=fifo
    
    StreamSplitter2<35>::forward(
        in_grad_y,
        fork17_b0,
    fork17_b1);
    
    hls::stream<cm_float, 34> fork16_b0;
    #pragma HLS BIND_STORAGE variable=fork16_b0 type=fifo
    
    hls::stream<cm_float, 34> fork16_b1;
    #pragma HLS BIND_STORAGE variable=fork16_b1 type=fifo
    
    StreamSplitter2<34>::forward(
        fork17_b0,
        fork16_b0,
    fork16_b1);
    
    hls::stream<cm_float, 17> exp15_bo;
    #pragma HLS BIND_STORAGE variable=exp15_bo type=fifo
    
    Exp<17>::backward(
        cache15_17_i,
        fork16_b0,
        exp15_bo);
    
    hls::stream<cm_float, 17> linear14_bo;
    #pragma HLS BIND_STORAGE variable=linear14_bo type=fifo
    
    Linear<64, 17>::backward(
        param14_1105o17,
        grad14_1105o17,
        cache14_64_i,
        exp15_bo,
        linear14_bo);
    
    hls::stream<cm_float, 17> linear12_bo;
    #pragma HLS BIND_STORAGE variable=linear12_bo type=fifo
    
    Linear<64, 17>::backward(
        param12_1105o17,
        grad12_1105o17,
        cache12_64_i,
        o,
        linear12_bo);
    
    hls::stream<cm_float, 64> forkend11_bo;
    #pragma HLS BIND_STORAGE variable=forkend11_bo type=fifo
    
    StreamAdder21<17, 17>(
        linear14_bo,
        forkend11_bo);
    hls::stream<cm_float, 64> tanh10_bo;
    #pragma HLS BIND_STORAGE variable=tanh10_bo type=fifo
    
    Tanh<64>::backward(
        cache10_64_i,
        forkend11_bo,
        tanh10_bo);
    
    hls::stream<cm_float, 64> linear9_bo;
    #pragma HLS BIND_STORAGE variable=linear9_bo type=fifo
    
    Linear<64, 64>::backward(
        param9_4160o64,
        grad9_4160o64,
        cache9_64_i,
        tanh10_bo,
        linear9_bo);
    
    hls::stream<cm_float, 64> tanh8_bo;
    #pragma HLS BIND_STORAGE variable=tanh8_bo type=fifo
    
    Tanh<64>::backward(
        cache8_64_i,
        linear9_bo,
        tanh8_bo);
    
    hls::stream<cm_float, 64> linear7_bo;
    #pragma HLS BIND_STORAGE variable=linear7_bo type=fifo
    
    Linear<376, 64>::backward(
        param7_24128o64,
        grad7_24128o64,
        cache7_376_i,
        tanh8_bo,
        linear7_bo);
    
    hls::stream<cm_float, 1> linear5_bo;
    #pragma HLS BIND_STORAGE variable=linear5_bo type=fifo
    
    Linear<64, 1>::backward(
        param5_65o1,
        grad5_65o1,
        cache5_64_i,
        o,
        linear5_bo);
    
    hls::stream<cm_float, 64> tanh4_bo;
    #pragma HLS BIND_STORAGE variable=tanh4_bo type=fifo
    
    Tanh<64>::backward(
        cache4_64_i,
        linear5_bo,
        tanh4_bo);
    
    hls::stream<cm_float, 64> linear3_bo;
    #pragma HLS BIND_STORAGE variable=linear3_bo type=fifo
    
    Linear<64, 64>::backward(
        param3_4160o64,
        grad3_4160o64,
        cache3_64_i,
        tanh4_bo,
        linear3_bo);
    
    hls::stream<cm_float, 64> tanh2_bo;
    #pragma HLS BIND_STORAGE variable=tanh2_bo type=fifo
    
    Tanh<64>::backward(
        cache2_64_i,
        linear3_bo,
        tanh2_bo);
    
    hls::stream<cm_float, 64> linear1_bo;
    #pragma HLS BIND_STORAGE variable=linear1_bo type=fifo
    
    Linear<376, 64>::backward(
        param1_24128o64,
        grad1_24128o64,
        cache1_376_i,
        tanh2_bo,
        linear1_bo);
    
    hls::stream<cm_float, 376> forkend0_bo;
    #pragma HLS BIND_STORAGE variable=forkend0_bo type=fifo
    
    StreamAdder21<1, 34>(
        linear7_bo,
        forkend0_bo);
}