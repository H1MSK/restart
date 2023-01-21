module ap_fifo_w#(
    parameter WIDTH = 32
)(
    input [WIDTH-1:0]   WR_DATA_s,
    output              FULL_N_s,
    input               WR_EN_s,
    output [WIDTH-1:0]  WR_DATA_m,
    input               FULL_m,
    output              WR_EN_m
);
    assign WR_DATA_m = WR_DATA_s;
    assign FULL_N_s = ~FULL_m;
    assign WR_EN_m = WR_EN_s;
endmodule