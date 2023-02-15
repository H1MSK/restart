#include <cassert>
#include <cstdlib>
#include <ctime>

#include "../../models/cmodel_src/net/net.hpp"
#include "../../models/hlsmodel_src/net/net.hpp"

inline cm_float rand_float() {
    return rand() / (cm_float)RAND_MAX * 2.0 - 1.0;
}

template <typename OUT = Linear<32, 32>,
          typename OUT_HLS = hlsnn::Linear<32, 32>,
          bool has_param = (OUT::param_size != 0)>
inline void test() {
    OUT dut;

    static_assert(OUT::in_size == OUT_HLS::in_size);
    static_assert(OUT::out_size == OUT_HLS::out_size);
    static_assert(OUT::param_size == OUT_HLS::param_size);
    static_assert(OUT::cache_size == OUT_HLS::cache_size);

    if constexpr (has_param) {
        for (int i = 0; i < OUT::param_size; ++i) {
            dut.param[i] = rand_float();
        }
    }

    hls::stream<cm_float> xc, xh, yc, yh, ch, ch1, cc1, yc1, yh1, goc, goh;

    for (int i = 0; i < OUT::in_size; ++i) {
        cm_float x = rand_float();
        xc.write(x);
        xh.write(x);
    }

    dut.forward(xc, yc, true);
    if constexpr (has_param) {
        OUT_HLS::forward(dut.param, xh, yh, ch, true);
    }
    if constexpr (!has_param) {
        OUT_HLS::forward(xh, yh, ch, true);
    }

    for (int i = 0; i < OUT::out_size; ++i) {
        cm_float y1 = yc.read(), y2 = yh.read();
        assert(abs(y1 - y2) < 1e-5);
        yc1.write(y1);
        yh1.write(y2);
    }

    for (int i = 0; i < OUT::cache_size; ++i) {
        cm_float c1 = ch.read(), c2 = dut.cache.read();
        assert(abs(c1 - c2) < 1e-5);
        ch1.write(c1);
        cc1.write(c2);
    }
    for (int i = 0; i < OUT::cache_size; ++i) {
        cm_float c2 = cc1.read();
        dut.cache.write(c2);
    }
    if constexpr (has_param) {
        cm_float grads[OUT::param_size];
        memset(dut.grad, 0, sizeof(dut.grad));
        memset(grads, 0, sizeof(grads));
        dut.backward(yc1, goc);
        OUT_HLS::backward(dut.param, grads, ch1, yh1, goh);
        for (int i = 0; i < OUT::in_size; ++i) {
            assert(abs(goc.read() - goh.read()) < 1e-5);
        }
        for (int i = 0; i < OUT::param_size; ++i) {
            assert(abs(grads[i] - dut.grad[i]) < 1e-5);
        }
    }
    
    if constexpr (!has_param) {
        dut.backward(yc1, goc);
        OUT_HLS::backward(ch1, yh1, goh);
        for (int i = 0; i < OUT::in_size; ++i) {
            assert(abs(goc.read() - goh.read()) < 1e-5);
        }
    }
}
