module ap_fifo_r#(
    parameter WIDTH = 32
)(
    input [WIDTH-1:0]   RD_DATA_m,
    input               EMPTY_m,
    output              RD_EN_m,
    output [WIDTH-1:0]  RD_DATA_s,
    output              EMPTY_N_s,
    input               RD_EN_s
);
    assign RD_DATA_s = RD_DATA_m;
    assign EMPTY_N_s = ~EMPTY_m;
    assign RD_EN_m = RD_EN_s;
endmodule