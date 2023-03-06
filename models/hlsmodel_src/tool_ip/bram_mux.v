`timescale 1ns / 1ps

module bram_mux#(
    parameter ADDR_WIDTH=32,
    parameter DATA_WIDTH=32,
    parameter WEN_WIDTH=DATA_WIDTH / 8 + (DATA_WIDTH & 7 ? 1 : 0)
)(
    (* X_INTERFACE_INFO = "xilinx.com:interface:bram:1.0 P0 ADDR" *)
    (* X_INTERFACE_PARAMETER = "MASTER_TYPE BRAM_CTRL" *)
    input [ADDR_WIDTH-1:0]  P0_Addr,
    (* X_INTERFACE_INFO = "xilinx.com:interface:bram:1.0 P0 EN" *)
    input                   P0_EN,
    (* X_INTERFACE_INFO = "xilinx.com:interface:bram:1.0 P0 DIN" *)
    input [DATA_WIDTH-1:0]  P0_Din,
    (* X_INTERFACE_INFO = "xilinx.com:interface:bram:1.0 P0 DOUT" *)
    output [DATA_WIDTH-1:0] P0_Dout,
    (* X_INTERFACE_INFO = "xilinx.com:interface:bram:1.0 P0 WE" *)
    input [WEN_WIDTH-1:0]   P0_WEN,
    (* X_INTERFACE_INFO = "xilinx.com:interface:bram:1.0 P0 CLK" *)
    input                   P0_Clk,
    (* X_INTERFACE_INFO = "xilinx.com:interface:bram:1.0 P0 RST" *)
    input                   P0_Rst,
    
    (* X_INTERFACE_INFO = "xilinx.com:interface:bram:1.0 P1 ADDR" *)
    (* X_INTERFACE_PARAMETER = "MASTER_TYPE BRAM_CTRL" *)
    input [ADDR_WIDTH-1:0]  P1_Addr,
    (* X_INTERFACE_INFO = "xilinx.com:interface:bram:1.0 P1 EN" *)
    input                   P1_EN,
    (* X_INTERFACE_INFO = "xilinx.com:interface:bram:1.0 P1 DIN" *)
    input [DATA_WIDTH-1:0]  P1_Din,
    (* X_INTERFACE_INFO = "xilinx.com:interface:bram:1.0 P1 DOUT" *)
    output [DATA_WIDTH-1:0] P1_Dout,
    (* X_INTERFACE_INFO = "xilinx.com:interface:bram:1.0 P1 WE" *)
    input [WEN_WIDTH-1:0]   P1_WEN,
    (* X_INTERFACE_INFO = "xilinx.com:interface:bram:1.0 P1 CLK" *)
    input                   P1_Clk,
    (* X_INTERFACE_INFO = "xilinx.com:interface:bram:1.0 P1 RST" *)
    input                   P1_Rst,


    (* X_INTERFACE_INFO = "xilinx.com:interface:bram:1.0 O ADDR" *)
    output [ADDR_WIDTH-1:0] O_Addr,
    (* X_INTERFACE_INFO = "xilinx.com:interface:bram:1.0 O EN" *)
    output                  O_EN,
    (* X_INTERFACE_INFO = "xilinx.com:interface:bram:1.0 O DIN" *)
    output [DATA_WIDTH-1:0] O_Din,
    (* X_INTERFACE_INFO = "xilinx.com:interface:bram:1.0 O DOUT" *)
    input [DATA_WIDTH-1:0]  O_Dout,
    (* X_INTERFACE_INFO = "xilinx.com:interface:bram:1.0 O WE" *)
    output [WEN_WIDTH-1:0]  O_WEN,
    (* X_INTERFACE_INFO = "xilinx.com:interface:bram:1.0 O CLK" *)
    output                  O_Clk,
    (* X_INTERFACE_INFO = "xilinx.com:interface:bram:1.0 O RST" *)
    output                  O_Rst,
    
    input                   sel,
    (* X_INTERFACE_INFO = "xilinx.com:signal:reset:1.0 inj_rst RST" *)
    (* X_INTERFACE_PARAMETER = "POLARITY ACTIVE_HIGH" *)
    input                   inj_rst
);
    assign O_Addr = sel ? P1_Addr : P0_Addr;
    assign O_EN = inj_rst ? 1 : (sel ? P1_EN : P0_EN);
    assign O_Din = sel ? P1_Din : P0_Din;
    assign P0_Dout = sel ? 0 : O_Dout;
    assign P1_Dout = sel ? O_Dout : 0;
    assign O_WEN = sel ? P1_WEN : P0_WEN;
    assign O_Clk = sel ? P1_Clk : P0_Clk;
    assign O_Rst = inj_rst ? 1 : (sel ? P1_Rst : P0_Rst);
endmodule
