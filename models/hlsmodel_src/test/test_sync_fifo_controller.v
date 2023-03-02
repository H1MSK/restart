module test_sfc;
  localparam DATA_CNT = 31;
  localparam DATA_WIDTH = 24;
  localparam ADDR_WIDTH = $clog2(DATA_CNT);
  
  wire      [DATA_WIDTH-1:0] data;       //data to be written
  wire      [ADDR_WIDTH-1:0] read_addr;  //address for read operation
  wire      [ADDR_WIDTH-1:0] write_addr; //address for write operation
  wire                       we;         //write enable signal
  wire                       read_en;
  wire                       write_en;
  wire                       rst1;
  wire                       rst2;
  wire                       read_clk;   //clock signal for read operation
  wire                       write_clk;  //clock signal for write operation
  reg [DATA_WIDTH-1:0] q;                //read data
    
  reg [DATA_WIDTH-1:0] ram [DATA_CNT-1:0]; // ** is exponentiation

  reg rst_bsy_1;
  reg rst_bsy_2;

  always @(posedge write_clk) begin //WRITE
    if (rst1) begin
      for (integer i=0; i<DATA_CNT; i = i+1)
        ram[i] <= 0;
      rst_bsy_1 <= 1;
    end else begin
      rst_bsy_1 <= 0;
      if (we & write_en) begin
        ram[write_addr] <= data;
      end
    end
  end
    
  always @(posedge read_clk) begin //READ
    if (rst2) begin
      for (integer i=0; i<DATA_CNT; i = i+1)
        ram[i] <= 0;
      rst_bsy_2 <= 1;
    end else if (read_en) begin
      rst_bsy_2 <= 0;
      if (read_en) begin
        q <= ram[read_addr];
      end
    end
  end

  //  The following function calculates the address width based on specified RAM depth
  function integer clogb2;
    input integer depth;
      for (clogb2=0; depth>0; clogb2=clogb2+1)
        depth = depth >> 1;
  endfunction
  
  reg clk = 0;
  reg reset = 0;
  reg fifo_wr_en = 0;
  reg[DATA_WIDTH-1:0] fifo_wr_data = 0;
  wire fifo_full_n;

  reg fifo_rd_en = 0;
  wire[DATA_WIDTH-1:0] fifo_rd_data;
  wire fifo_empty_n;

  wire[ADDR_WIDTH:0] count;
  
  sync_fifo_controller#(
    .SIZE(DATA_CNT),
    .DATA_WIDTH(DATA_WIDTH),
    .ADDR_WIDTH(ADDR_WIDTH)
  ) uut(
    .reset(reset),
    .clk(clk),
    .fifo_wr_en(fifo_wr_en),
    .fifo_full_n(fifo_full_n),
    .fifo_wr_data(fifo_wr_data),
    .fifo_rd_en(fifo_rd_en),
    .fifo_rd_data(fifo_rd_data),
    .fifo_empty_n(fifo_empty_n),
    .bram_addra(write_addr),
    .bram_clka(write_clk),
    .bram_dina(data),
    .bram_rsta(rst1),
    .bram_wea(we),
    .bram_ena(write_en),

    .bram_addrb(read_addr),
    .bram_clkb(read_clk),
    .bram_rstb(rst2),
    .bram_doutb(q),
    .bram_enb(read_en),

    .bram_rst_busy(rst_bsy_2),

    .cnt(count)
  );

  initial begin
    clk = 0;
    while (1) begin
      clk = !clk;
      #1;
    end
  end

  initial begin
    reset = 1;
    #20;
    reset = 0;
  end

  integer x_w;
  initial begin
    #50;
    for (x_w = 0; x_w < DATA_CNT + 2; x_w = x_w + 1) begin
      #1;
      fifo_wr_data = x_w+1;
      fifo_wr_en = 1;
      #2;
      fifo_wr_data = 0;
      fifo_wr_en = 0;
      #17;
    end
    wait (count == 0);
    #4;
    for (x_w = DATA_CNT + 2; x_w < DATA_CNT + 6; x_w = x_w + 1) begin
      #1;
      fifo_wr_data = x_w+1;
      fifo_wr_en = 1;
      #2;
      fifo_wr_data = 0;
      fifo_wr_en = 0;
      #17;
    end
    #2;
    reset = 1;
    #30;
    reset = 0;
    #21;
    
    fifo_wr_data = 51;
    for (x_w = 0; x_w < DATA_CNT + 4; x_w = x_w + 1) begin
      fifo_wr_en = 1;
      #2;
      fifo_wr_data = x_w+52;
    end
    fifo_wr_en = 0;
    wait (count == 1);
    #1;
    for (x_w = DATA_CNT+4; x_w < DATA_CNT + 8; x_w = x_w + 1) begin
      fifo_wr_en = 1;
      #2;
      fifo_wr_data = x_w+52;
    end
    fifo_wr_en = 0;
  end

  integer x_r;
  initial begin
    wait (count == DATA_CNT);
    #4;
    for (x_r = 0; x_r < DATA_CNT + 6; x_r = x_r + 1) begin
      #1;
      fifo_rd_en = 1;
      if(fifo_rd_data != x_r + 1) $stop;
      #2;
      fifo_rd_en = 0;
      #17;
    end
    wait (count == DATA_CNT);
    #1;
    for (x_r = 0; x_r < DATA_CNT + 8; x_r = x_r + 1) begin
      fifo_rd_en = 1;
      if(fifo_rd_data != x_r + 51) $stop;
      #2;
    end
    fifo_rd_en = 0;
    #20;
    $finish;
  end

endmodule