`timescale 1ns / 1ps

module fifo_switch#(
    parameter ADDR_WIDTH=32,
    parameter DATA_WIDTH=32,
    parameter WEN_WIDTH=DATA_WIDTH / 8 + (DATA_WIDTH & 7 ? 1 : 0)
)(
    input [ADDR_WIDTH-1:0]  P0_Addr,
    input                   P0_EN,
    input [DATA_WIDTH-1:0]  P0_Din,
    output [DATA_WIDTH-1:0] P0_Dout,
    input [WEN_WIDTH-1:0]   P0_WEN,
    input                   P0_Clk,
    input                   P0_Rst,
    
    input [ADDR_WIDTH-1:0]  P1_Addr,
    input                   P1_EN,
    input [DATA_WIDTH-1:0]  P1_Din,
    output [DATA_WIDTH-1:0] P1_Dout,
    input [WEN_WIDTH-1:0]   P1_WEN,
    input                   P1_Clk,
    input                   P1_Rst,


    output [ADDR_WIDTH-1:0] O_Addr,
    output                  O_EN,
    output [DATA_WIDTH-1:0] O_Din,
    input [DATA_WIDTH-1:0]  O_Dout,
    output [WEN_WIDTH-1:0]  O_WEN,
    output                  O_Clk,
    output                  O_Rst,
    
    input                   sel
);
    assign O_Addr = sel ? P1_Addr : P0_Addr;
    assign O_EN = sel ? P1_EN : P0_EN;
    assign O_Din = sel ? P1_Din : P0_Din;
    assign P0_Dout = sel ? 0 : O_Dout;
    assign P1_Dout = sel ? O_Dout : 0;
    assign O_WEN = sel ? P1_WEN : P0_WEN;
    assign O_Clk = sel ? P1_Clk : P0_Clk;
    assign O_Rst = sel ? P1_Rst : P0_Rst;
endmodule
