module GPIO_Connection(
    (* X_INTERFACE_INFO = "xilinx.com:interface:gpio_rtl:1.0 GPIO TRI_I" *)
    output[31:0] GPIO_I,
    (* X_INTERFACE_INFO = "xilinx.com:interface:gpio_rtl:1.0 GPIO TRI_O" *)
    input[31:0] GPIO_O,
    (* X_INTERFACE_INFO = "xilinx.com:interface:gpio_rtl:1.0 GPIO TRI_T" *)
    input[31:0] GPIO_T,

    input[15:0] cache_cnt,
    output[15:0] cache_sel,

    (* X_INTERFACE_INFO = "xilinx.com:signal:reset:1.0 system_reset RST" *)
    (* X_INTERFACE_PARAMETER = "POLARITY ACTIVE_HIGH" *)
    output system_reset,
    (* X_INTERFACE_INFO = "xilinx.com:signal:reset:1.0 param_reset RST" *)
    (* X_INTERFACE_PARAMETER = "POLARITY ACTIVE_HIGH" *)
    output param_reset,
    (* X_INTERFACE_INFO = "xilinx.com:signal:reset:1.0 grad_reset RST" *)
    (* X_INTERFACE_PARAMETER = "POLARITY ACTIVE_HIGH" *)
    output grad_reset,

    input param_reset_busy,
    input grad_reset_busy,

    output bram_sel);
    // 0x10-0x13: reset signals
    assign system_reset = GPIO_O['h10];
    assign param_reset = GPIO_O['h11];
    assign grad_reset = GPIO_O['h12];
    
    // 0x14-0x17: reset busy signals
    // assign GPIO_I['h14] = param_reset_busy;
    // assign GPIO_I['h15] = grad_reset_busy;

    assign bram_sel = GPIO_O['h19];
    
    assign cache_sel = GPIO_O['h0f:'h00];

    assign GPIO_I = {
        // 0x1c-0x1f: not used currently
        4'b1111,
        // 0x18-0x1b:
        4'b1111,
        // 0x14-0x17: reset busy signals
        2'b11,
        grad_reset_busy,
        param_reset_busy,
        // 0x10-0x13: reset signals
        4'b1111,
        // 0x00-0x0f: debug
        cache_cnt
    };
endmodule
