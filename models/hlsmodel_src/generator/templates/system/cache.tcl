# Controller
create_bd_cell -type ip -vlnv h1msk.cc:fpga_nn.hls:sync_fifo_controller:1.0 fifocon_$cache_name
set_property -dict [list CONFIG.SIZE {$cache_size} CONFIG.ADDR_WIDTH {$cache_addr_width}] [get_bd_cells fifocon_$cache_name]

# Memory
create_bd_cell -type ip -vlnv xilinx.com:ip:blk_mem_gen:8.4 mem_$cache_name
set_property -dict [list CONFIG.Memory_Type {Simple_Dual_Port_RAM} CONFIG.Enable_32bit_Address {false} CONFIG.Use_Byte_Write_Enable {false} CONFIG.Write_Depth_A {$cache_size} CONFIG.Operating_Mode_A {NO_CHANGE} CONFIG.Enable_B {Use_ENB_Pin} CONFIG.Register_PortA_Output_of_Memory_Primitives {false} CONFIG.Register_PortB_Output_of_Memory_Primitives {false} CONFIG.Use_RSTA_Pin {false} CONFIG.Use_RSTB_Pin {true} CONFIG.Assume_Synchronous_Clk {true} CONFIG.use_bram_block {Stand_Alone}] [get_bd_cells mem_$cache_name]

connect_bd_intf_net [get_bd_intf_pins fifocon_$cache_name/BRAM_PORT_R] [get_bd_intf_pins mem_$cache_name/BRAM_PORTA]
connect_bd_intf_net [get_bd_intf_pins fifocon_$cache_name/BRAM_PORT_W] [get_bd_intf_pins mem_$cache_name/BRAM_PORTB]
connect_bd_net [get_bd_pins mem_$cache_name/rstb_busy] [get_bd_pins fifocon_$cache_name/bram_rst_busy]

# Write adaptor
connect_bd_intf_net [get_bd_intf_pins forward/${cache_name}] [get_bd_intf_pins fifocon_$cache_name/FIFO_WRITE]

# Read adaptor
connect_bd_intf_net [get_bd_intf_pins backward/${cache_name}] [get_bd_intf_pins fifocon_$cache_name/FIFO_READ]

# Clk & Rst
connect_bd_net [get_bd_pins processing_system7_0/FCLK_CLK0] [get_bd_pins fifocon_$cache_name/clk]
connect_bd_net [get_bd_pins proc_sys_reset_0/peripheral_reset] [get_bd_pins fifocon_$cache_name/reset]

# Debug
connect_bd_net [get_bd_pins fifocon_$cache_name/cnt] [get_bd_pins cache_debug_mux/cnt_$cache_name]
