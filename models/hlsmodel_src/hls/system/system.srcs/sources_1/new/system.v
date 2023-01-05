`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 01/04/2023 09:06:09 AM
// Design Name: 
// Module Name: system
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////


module system(
    input ap_clk,
    input ap_rst,
    input ap_start,
    output ap_done,
    input ap_continue,
    output ap_idle,
    output ap_ready
    );
    linear64_64_f_0 u1(
        .ap_clk(ap_clk),
        .ap_rst(ap_rst),
        .ap_start(ap_start),
        .ap_done(ap_done),
        .ap_continue(ap_continue),
        .ap_idle(ap_idle),
        .ap_ready(ap_ready)
    );
endmodule
