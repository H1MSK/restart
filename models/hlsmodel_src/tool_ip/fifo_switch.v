`timescale 1ns / 1ps

module fifo_switch#(
    parameter DATA_WIDTH=32
)(
    input[DATA_WIDTH-1:0]   fifo_i_din,
    output                  fifo_i_full_n,
    input                   fifo_i_write,
    
    output[DATA_WIDTH-1:0]  fifo_o_din,
    input                   fifo_o_full_n,
    output                  fifo_o_write,

    input                   fifo_en
);
    assign fifo_o_din = fifo_i_din;
    assign fifo_i_full_n = fifo_o_full_n;
    assign fifo_o_write = fifo_en & fifo_i_write;
endmodule
