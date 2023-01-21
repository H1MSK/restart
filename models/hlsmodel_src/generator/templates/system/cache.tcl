# Create FIFO
create_bd_cell -type ip -vlnv xilinx.com:ip:fifo_generator:13.2 fifo_$cache_name
set_property -dict [list CONFIG.Input_Data_Width {32} CONFIG.Input_Depth {$cache_size_upscale} CONFIG.Output_Data_Width {32}] [get_bd_cells fifo_$cache_name]

# Write adaptor
create_bd_cell -type ip -vlnv h1msk.cc:fpga_nn.hls:ap_fifo_w:1.0 fifo_${cache_name}_w
connect_bd_intf_net [get_bd_intf_pins forward/${cache_name}_o] [get_bd_intf_pins fifo_${cache_name}_w/acc_fifo_s]
connect_bd_intf_net [get_bd_intf_pins fifo_${cache_name}_w/fifo_m] [get_bd_intf_pins fifo_$cache_name/FIFO_WRITE]

# Read adaptor
create_bd_cell -type ip -vlnv h1msk.cc:fpga_nn.hls:ap_fifo_r:1.0 fifo_${cache_name}_r
connect_bd_intf_net [get_bd_intf_pins backward/${cache_name}_i] [get_bd_intf_pins fifo_${cache_name}_r/acc_fifo_s]
connect_bd_intf_net [get_bd_intf_pins fifo_${cache_name}_r/fifo_m] [get_bd_intf_pins fifo_$cache_name/FIFO_READ]

# Clk & Rst
connect_bd_net [get_bd_pins processing_system7_0/FCLK_CLK0] [get_bd_pins fifo_$cache_name/clk]
connect_bd_net [get_bd_pins proc_sys_reset_0/peripheral_reset] [get_bd_pins fifo_$cache_name/srst]
