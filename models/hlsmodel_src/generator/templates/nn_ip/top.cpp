void nn_ip(hls::stream<cm_float>& in_x, hls::stream<cm_float, 35>& out_y, hls::stream<cm_float, 35>& in_grad_y, bool cache_en, $param_signatures, $grad_signatures) {
    #pragma HLS INTERFACE mode=ap_ctrl_hs port=return
    #pragma HLS DATAFLOW
    #pragma HLS INTERFACE mode=axis port=in_x register_mode=reverse depth=376
    #pragma HLS INTERFACE mode=axis port=out_y register_mode=forward depth=35
    #pragma HLS INTERFACE mode=axis port=in_grad_y register_mode=reverse depth=35
    #pragma HLS INTERFACE mode=ap_none port=cache_en
    #pragma HLS STABLE variable=cache_en

$param_hls_pragmas
$grad_hls_pragmas

$cache_definitions

    $forward_func(in_x, out_y, cache_en,
        $params,
        $caches);
    $backward_func(in_grad_y,
        $params,
        $grads,
        $caches);
}