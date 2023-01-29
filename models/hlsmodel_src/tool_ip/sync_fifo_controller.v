// Plain synchronous fifo implementation
// Sync clock and sync reset

module sync_fifo_controller#(
    parameter SIZE = 32,
    parameter DATA_WIDTH = 32,
    parameter ADDR_WIDTH = $clog2(SIZE-1)+1
)(
    // Control ports
    input                   reset,
    input                   clk,

    // FIFO write interface
    input                   fifo_wr_en,
    output reg              fifo_full,
    input[DATA_WIDTH-1:0]   fifo_wr_data,

    // FIFO read interface
    input                   fifo_rd_en,
    output[DATA_WIDTH-1:0]  fifo_rd_data,
    output reg              fifo_empty,

    // FIFO control
    output                  fifo_wr_err,
    output                  fifo_rd_err,

    // BRAM Read port
    output[ADDR_WIDTH-1:0]  bram_addra,
    output                  bram_clka,
    output                  bram_rsta,
    output[DATA_WIDTH-1:0]  bram_dina,
    output                  bram_ena,
    output                  bram_wea,

    // BRAM Write port
    output[ADDR_WIDTH-1:0]  bram_addrb,
    output                  bram_clkb,
    output                  bram_rstb,
    input[DATA_WIDTH-1:0]   bram_doutb,
    output                  bram_enb,
    
    input                   bram_rst_busy
);
    reg[ADDR_WIDTH-1:0]  read_addr;
    reg[ADDR_WIDTH-1:0]  write_addr;

    reg[ADDR_WIDTH:0]  data_cnt;

    wire next_fifo_full = (data_cnt == SIZE);
    wire next_fifo_empty = (data_cnt == 0);
    
    wire internal_reset = reset | bram_rst_busy;
    
    assign bram_addra = write_addr;
    assign bram_clka = clk;
    assign bram_rsta = reset;
    assign bram_dina = fifo_wr_data;
    assign bram_ena = fifo_wr_en;
    assign bram_wea = 1;  // TODO: Check this implementation
    
    assign bram_addrb = read_addr;
    assign bram_clkb = clk;
    assign bram_rstb = reset;
    assign fifo_rd_data = bram_doutb;
    assign bram_enb = 1;

    assign fifo_wr_err = (data_cnt == SIZE && fifo_wr_en);
    assign fifo_rd_err = (data_cnt == 0 && fifo_rd_en);
    
    wire[ADDR_WIDTH-1:0] next_read_addr;
    wire[ADDR_WIDTH-1:0] next_write_addr;

    generate
        if ($clog2(SIZE) != $clog2(SIZE - 1)) begin
            assign next_read_addr = read_addr + 1;
            assign next_write_addr = write_addr + 1;
        end else begin
            wire[ADDR_WIDTH-1:0] rdaddress_add_1 = read_addr + 1;
            wire[ADDR_WIDTH-1:0] wraddress_add_1 = write_addr + 1;
            assign next_read_addr = rdaddress_add_1 == SIZE ? 0 : rdaddress_add_1;
            assign next_write_addr = wraddress_add_1 == SIZE ? 0 : wraddress_add_1;
        end
    endgenerate

    // read data address
    always@(posedge clk)
    if (internal_reset)
        read_addr <= 0;
    else if (fifo_rd_en && ~next_fifo_empty)
        read_addr <= next_read_addr;

    // write data address
    always@(posedge clk)
    if (internal_reset)
        write_addr <= 0;
    else if (fifo_wr_en && ~next_fifo_full)
        write_addr <= next_read_addr;

    // full register
    always@(posedge clk)
    if (internal_reset)
        fifo_full <= 0;
    else
        fifo_full <= next_fifo_full;

    // empty register
    always@(posedge clk)
    if (internal_reset)
        fifo_empty <= 1;
    else
        fifo_empty <= next_fifo_empty;

    // fifo data count
    always@(posedge clk)
    if (internal_reset)
        data_cnt <= 0;
    else if (fifo_wr_en && ~fifo_rd_en && ~next_fifo_full)
        data_cnt <= data_cnt + 1;
    else if (fifo_rd_en && ~fifo_wr_en && ~next_fifo_empty)
        data_cnt <= data_cnt - 1;
    else
        data_cnt <= data_cnt;

endmodule
