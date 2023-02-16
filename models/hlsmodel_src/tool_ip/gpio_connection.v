module GPIO_Connection(
    output[31:0] GPIO_I,
    input[31:0] GPIO_O,
    input[31:0] GPIO_T,

    output fw_start,
    output fw_complete,
    input fw_finish,
    input fw_idle,

    output bw_start,
    output bw_complete,
    input bw_finish,
    input bw_idle,

    output param_start,
    output param_complete,
    input param_finish,
    input param_idle,

    output grad_start,
    output grad_complete,
    input grad_finish,
    input grad_idle,

    output system_reset,
    output param_reset,
    output grad_reset,

    input param_reset_busy,
    input grad_reset_busy,

    output cache_en,
    output bram_sel);

    // 0x00-0x03: forward
    assign fw_start = GPIO_O['h00];
    assign fw_complete = GPIO_O['h01];
    // assign GPIO_I['h02] = fw_finish;
    // assign GPIO_I['h03] = fw_idle;

    // 0x04-0x07: backward
    assign bw_start = GPIO_O['h04];
    assign bw_complete = GPIO_O['h05];
    // assign GPIO_I['h06] = bw_finish;
    // assign GPIO_I['h07] = bw_idle;

    // 0x08-0x0b: param loader
    assign param_start = GPIO_O['h08];
    assign param_complete = GPIO_O['h09];
    // assign GPIO_I['h0a] = param_finish;
    // assign GPIO_I['h0b] = param_idle;

    // 0x0c-0x0f: grad extractor
    assign grad_start = GPIO_O['h0c];
    assign grad_complete = GPIO_O['h0d];
    // assign GPIO_I['h0e] = grad_finish;
    // assign GPIO_I['h0f] = grad_idle;

    // 0x10-0x13: reset signals
    assign system_reset = GPIO_O['h10];
    assign param_reset = GPIO_O['h11];
    assign grad_reset = GPIO_O['h12];
    
    // 0x14-0x17: reset busy signals
    // assign GPIO_I['h14] = param_reset_busy;
    // assign GPIO_I['h15] = grad_reset_busy;

    assign cache_en = GPIO_O['h18];
    assign bram_sel = GPIO_O['h19];

    assign GPIO_I = {
        // 0x00-0x03: forward
        2'b11,
        fw_finish,
        fw_idle,

        // 0x04-0x07: backward
        2'b11,
        bw_finish,
        bw_idle,

        // 0x08-0x0b: param loader
        2'b11,
        param_finish,
        param_idle,

        // 0x0c-0x0f: grad extractor
        2'b11,
        grad_finish,
        grad_idle,

        // 0x10-0x13: reset signals
        4'b1111,

        // 0x14-0x17: reset busy signals
        param_reset_busy,
        grad_reset_busy,
        2'b11,

        // 0x18-0x1b:
        4'b1111,
        // 0x1c-0x1f: not used currently
        4'b1111
    };
endmodule
