module ap_controller(
    input ap_clk,
    input ap_rst_n,

    input start_trig,
    output finish,
    output idle,

    output ap_start,
    input ap_ready,
    input ap_done,
    input ap_idle
);
    reg start;
    wire next_start = start_trig | (start & ~ap_ready);
    assign finish = ap_done;
    assign idle = ap_idle;
    assign ap_start = next_start;
    always @(posedge ap_clk) begin
        if (~ap_rst_n) begin
            start <= 0;
        end else begin
            start <= next_start;
        end
    end

endmodule
