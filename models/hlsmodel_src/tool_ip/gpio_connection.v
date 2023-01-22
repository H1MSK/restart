module GPIO_Connection(
    output[31:0] GPIO_I,
    input[31:0] GPIO_O,
    input[31:0] GPIO_T,
    output fw_start,
    input fw_done,
    input fw_idle,
    output bw_start,
    input bw_done,
    input bw_idle,
    output param_start,
    input param_done,
    input param_idle,
    output grad_start,
    input grad_done,
    input grad_idle,
    output param_reset,
    input param_reset_busy,
    output grad_reset,
    input grad_reset_busy,
    output cache_en,
    output bram_sel
);
    // assign GPIO_I = ~0;

    assign fw_start = GPIO_O['h00];
    // assign GPIO_I['h01] = fw_done;
    // assign GPIO_I['h02] = fw_idle;

    assign bw_start = GPIO_O['h04];
    // assign GPIO_I['h05] = bw_done;
    // assign GPIO_I['h06] = bw_idle;

    assign param_start = GPIO_O['h08];
    // assign GPIO_I['h09] = param_done;
    // assign GPIO_I['h0a] = param_idle;

    assign grad_start = GPIO_O['h0c];
    // assign GPIO_I['h0d] = grad_done;
    // assign GPIO_I['h0e] = grad_idle;

    assign param_reset = GPIO_O['h10];
    // assign GPIO_I['h11] = param_reset_busy;
    
    assign grad_reset = GPIO_O['h14];
    // assign GPIO_I['h15] = grad_reset_busy;

    assign cache_en = GPIO_O['h18];
    assign grad_sel = GPIO_O['h19];

    assign GPIO_I = {
        1'b1,
        fw_done,            // 0x01
        fw_idle,
        2'b11,
        bw_done,            // 0x05
        bw_idle,
        2'b11,
        param_done,         // 0x09
        param_idle,
        2'b11,
        grad_done,          // 0x0d
        grad_idle,
        2'b11,
        param_reset_busy,   // 0x11
        3'b111,
        grad_reset_busy,    // 0x15
        10'b1111111111
    };
    // assign fw_start = GPIO_O['h00];
    // assign bw_start = GPIO_O['h04];
    // assign param_start = GPIO_O['h08];
    // assign grad_start = GPIO_O['h0c];
endmodule
