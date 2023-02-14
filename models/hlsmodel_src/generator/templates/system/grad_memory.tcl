create_bd_cell -type ip -vlnv xilinx.com:ip:blk_mem_gen:8.4 $mem_name
set_property -dict [list CONFIG.Memory_Type {True_Dual_Port_RAM} CONFIG.Assume_Synchronous_Clk {true} CONFIG.Enable_32bit_Address {true} CONFIG.Use_Byte_Write_Enable {true} CONFIG.Byte_Size {8} CONFIG.Write_Depth_A {$mem_depth} CONFIG.Write_Width_A {$mem_bitwidth} CONFIG.Read_Width_A {$mem_bitwidth} CONFIG.Write_Width_B {$mem_bitwidth} CONFIG.Read_Width_B {$mem_bitwidth} CONFIG.Register_PortA_Output_of_Memory_Primitives {false} CONFIG.Register_PortB_Output_of_Memory_Primitives {false} CONFIG.Use_RSTA_Pin {true} CONFIG.Use_RSTB_Pin {true} CONFIG.use_bram_block {Stand_Alone} CONFIG.EN_SAFETY_CKT {true}] [get_bd_cells $mem_name]

create_bd_cell -type ip -vlnv h1msk.cc:fpga_nn.hls:bram_mux:1.0 $mux_name

connect_bd_intf_net [get_bd_intf_pins $instance/$porta] [get_bd_intf_pins $mux_name/P0]
connect_bd_intf_net [get_bd_intf_pins backward/$portb] [get_bd_intf_pins $mux_name/P1]
connect_bd_intf_net [get_bd_intf_pins $mux_name/O] [get_bd_intf_pins $mem_name/BRAM_PORTB]

connect_bd_intf_net [get_bd_intf_pins backward/$porta] [get_bd_intf_pins $mem_name/BRAM_PORTA]
