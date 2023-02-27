// Plain synchronous fifo implementation
// Sync clock and sync reset

module sync_fifo_controller#(
    parameter SIZE = 32,
    parameter DATA_WIDTH = 32,
    parameter ADDR_WIDTH = 5
)(
    // Control ports
    (* X_INTERFACE_INFO = "xilinx.com:signal:reset:1.0 reset RST" *)
    (* X_INTERFACE_PARAMETER = "POLARITY ACTIVE_HIGH" *)
    input                   reset,
    (* X_INTERFACE_INFO = "xilinx.com:signal:clock:1.0 clk CLK" *)
    (* X_INTERFACE_PARAMETER = "ASSOCIATED_RESET reset" *)
    input                   clk,

    // FIFO write interface
    (* X_INTERFACE_INFO = "xilinx.com:interface:acc_fifo_write:1.0 FIFO_WRITE WR_EN" *)
    input                   fifo_wr_en,
    (* X_INTERFACE_INFO = "xilinx.com:interface:acc_fifo_write:1.0 FIFO_WRITE FULL_N" *)
    output                  fifo_full_n,
    (* X_INTERFACE_INFO = "xilinx.com:interface:acc_fifo_write:1.0 FIFO_WRITE WR_DATA" *)
    input[DATA_WIDTH-1:0]   fifo_wr_data,

    // FIFO read interface
    (* X_INTERFACE_INFO = "xilinx.com:interface:acc_fifo_read:1.0 FIFO_READ RD_EN" *)
    input                   fifo_rd_en,
    (* X_INTERFACE_INFO = "xilinx.com:interface:acc_fifo_read:1.0 FIFO_READ RD_DATA" *)
    output[DATA_WIDTH-1:0]  fifo_rd_data,
    (* X_INTERFACE_INFO = "xilinx.com:interface:acc_fifo_read:1.0 FIFO_READ EMPTY_N" *)
    output                  fifo_empty_n,

    // FIFO control
    // output                  fifo_wr_err,
    // output                  fifo_rd_err,

    // BRAM Read port
    (* X_INTERFACE_INFO = "xilinx.com:interface:bram:1.0 BRAM_PORT_R ADDR" *)
    (* X_INTERFACE_PARAMETER = "MODE Master" *)
    output[ADDR_WIDTH-1:0]  bram_addra,
    (* X_INTERFACE_INFO = "xilinx.com:interface:bram:1.0 BRAM_PORT_R CLK" *)
    output                  bram_clka,
    (* X_INTERFACE_INFO = "xilinx.com:interface:bram:1.0 BRAM_PORT_R DIN" *)
    output[DATA_WIDTH-1:0]  bram_dina,
    (* X_INTERFACE_INFO = "xilinx.com:interface:bram:1.0 BRAM_PORT_R RST" *)
    output                  bram_rsta,
    (* X_INTERFACE_INFO = "xilinx.com:interface:bram:1.0 BRAM_PORT_R WE" *)
    output                  bram_wea,
    (* X_INTERFACE_INFO = "xilinx.com:interface:bram:1.0 BRAM_PORT_R EN" *)
    output                  bram_ena,

    // BRAM Write port
    (* X_INTERFACE_INFO = "xilinx.com:interface:bram:1.0 BRAM_PORT_W ADDR" *)
    (* X_INTERFACE_PARAMETER = "MODE Master" *)
    output[ADDR_WIDTH-1:0]  bram_addrb,
    (* X_INTERFACE_INFO = "xilinx.com:interface:bram:1.0 BRAM_PORT_W CLK" *)
    output                  bram_clkb,
    (* X_INTERFACE_INFO = "xilinx.com:interface:bram:1.0 BRAM_PORT_W RST" *)
    output                  bram_rstb,
    (* X_INTERFACE_INFO = "xilinx.com:interface:bram:1.0 BRAM_PORT_W DOUT" *)
    input[DATA_WIDTH-1:0]   bram_doutb,
    (* X_INTERFACE_INFO = "xilinx.com:interface:bram:1.0 BRAM_PORT_W EN" *)
    output                  bram_enb,
    
    input                   bram_rst_busy,

    output[ADDR_WIDTH:0]    cnt
);
    reg[ADDR_WIDTH-1:0]  read_addr;
    reg[ADDR_WIDTH-1:0]  write_addr;

    reg[ADDR_WIDTH:0]  data_cnt = 0;

    reg fifo_empty;
    reg fifo_full;

    wire next_fifo_full = (data_cnt == SIZE && ~fifo_rd_en || data_cnt == SIZE-1 && fifo_wr_en);
    wire next_fifo_empty = (data_cnt == 0 && ~fifo_wr_en || data_cnt == 1 && fifo_rd_en);

    assign fifo_empty_n = !fifo_empty;
    assign fifo_full_n = !fifo_full;
    
    wire internal_reset = reset | bram_rst_busy;
    
    assign bram_addra = write_addr;
    assign bram_clka = clk;
    assign bram_dina = fifo_wr_data;
    assign bram_rsta = reset;
    assign bram_ena = fifo_wr_en;
    assign bram_wea = 1;  // TODO: Check this implementation
    
    assign bram_addrb = read_addr;
    assign bram_clkb = clk;
    assign bram_rstb = reset;
    assign fifo_rd_data = bram_doutb;
    assign bram_enb = 1;

    // assign fifo_wr_err = (data_cnt == SIZE && fifo_wr_en);
    // assign fifo_rd_err = (data_cnt == 0 && fifo_rd_en);
    
    assign cnt = data_cnt;
    
    wire[ADDR_WIDTH-1:0] next_read_addr;
    wire[ADDR_WIDTH-1:0] next_write_addr;

    generate
        if ($clog2(SIZE) != $clog2(SIZE + 1)) begin
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
    else if (fifo_rd_en && ~fifo_empty)
        read_addr <= next_read_addr;

    // write data address
    always@(posedge clk)
    if (internal_reset)
        write_addr <= 0;
    else if (fifo_wr_en && ~fifo_full)
        write_addr <= next_write_addr;

    // full register
    always@(posedge clk)
    if (internal_reset)
        fifo_full <= 1;
    else
        fifo_full <= next_fifo_full;

    // empty register
    always@(posedge clk)
    if (internal_reset)
        fifo_empty <= 1;
    else
        fifo_empty <= next_fifo_empty;
    
    reg[ADDR_WIDTH:0]  next_data_cnt;
    
    always@(*) begin
        if (~fifo_full && fifo_wr_en && ~fifo_rd_en) next_data_cnt <= data_cnt + 1;
        else if (~fifo_empty && fifo_rd_en && ~fifo_wr_en) next_data_cnt <= data_cnt - 1;
        else next_data_cnt <= data_cnt;
    end

    // fifo data count
    always@(posedge clk)
    if (internal_reset)
        data_cnt <= 0;
    else
        data_cnt <= next_data_cnt;

endmodule
