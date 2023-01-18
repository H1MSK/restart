create_project system ./build_system -part xc7z020clg400-2
set_property  ip_repo_paths  . [current_project]

create_bd_design "system"

# Create hls ips
create_bd_cell -type ip -vlnv xilinx.com:hls:nn_ip:1.0 nn_ip
create_bd_cell -type ip -vlnv xilinx.com:hls:grad_extractor:1.0 grad_extractor
create_bd_cell -type ip -vlnv xilinx.com:hls:param_loader:1.0 param_loader

# Create memories and their connections
$memory_scripts

# DMA for forward function
create_bd_cell -type ip -vlnv xilinx.com:ip:axi_dma:7.1 axi_dma_fw
set_property -dict [list CONFIG.c_m_axi_s2mm_data_width.VALUE_SRC PROPAGATED CONFIG.c_single_interface.VALUE_SRC USER] [get_bd_cells axi_dma_fw]
set_property -dict [list CONFIG.c_include_sg {0} CONFIG.c_sg_include_stscntrl_strm {0} CONFIG.c_mm2s_burst_size {256} CONFIG.c_s2mm_burst_size {256} CONFIG.c_include_mm2s_dre {1} CONFIG.c_include_s2mm_dre {1}] [get_bd_cells axi_dma_fw]
connect_bd_intf_net [get_bd_intf_pins axi_dma_fw/M_AXIS_MM2S] [get_bd_intf_pins nn_ip/in_x]
connect_bd_intf_net [get_bd_intf_pins axi_dma_fw/S_AXIS_S2MM] [get_bd_intf_pins nn_ip/out_y]

# DMA for backward function
create_bd_cell -type ip -vlnv xilinx.com:ip:axi_dma:7.1 axi_dma_bw
set_property -dict [list CONFIG.c_include_sg {0} CONFIG.c_sg_include_stscntrl_strm {0} CONFIG.c_include_s2mm {0} CONFIG.c_include_mm2s_dre {1} CONFIG.c_include_s2mm_dre {1}] [get_bd_cells axi_dma_bw]
connect_bd_intf_net [get_bd_intf_pins axi_dma_bw/M_AXIS_MM2S] [get_bd_intf_pins nn_ip/in_grad_y]

# DMA for param loader and grad extractor
create_bd_cell -type ip -vlnv xilinx.com:ip:axi_dma:7.1 axi_dma_pg
set_property -dict [list CONFIG.c_single_interface.VALUE_SRC USER] [get_bd_cells axi_dma_pg]
set_property -dict [list CONFIG.c_include_sg {0} CONFIG.c_sg_length_width {17} CONFIG.c_sg_include_stscntrl_strm {0} CONFIG.c_include_mm2s_dre {1} CONFIG.c_mm2s_burst_size {256} CONFIG.c_include_s2mm_dre {1} CONFIG.c_s2mm_burst_size {256}] [get_bd_cells axi_dma_pg]
connect_bd_intf_net [get_bd_intf_pins axi_dma_pg/M_AXIS_MM2S] [get_bd_intf_pins param_loader/in_r]
connect_bd_intf_net [get_bd_intf_pins axi_dma_pg/S_AXIS_S2MM] [get_bd_intf_pins grad_extractor/out_r]




# AXI-GPIO out for grad reset, cache_en and param/grad mux sel
# 0: Grad reset
# 1: BRAM Mux sel
# 2: Cache en
create_bd_cell -type ip -vlnv xilinx.com:ip:axi_gpio:2.0 axi_gpio_out
set_property -dict [list CONFIG.C_GPIO_WIDTH {3} CONFIG.C_ALL_OUTPUTS {1}] [get_bd_cells axi_gpio_out]
create_bd_cell -type ip -vlnv xilinx.com:ip:xlslice:1.0 gpio_out_0
set_property -dict [list CONFIG.DIN_TO {0} CONFIG.DIN_FROM {0} CONFIG.DIN_WIDTH {3} CONFIG.DOUT_WIDTH {1}] [get_bd_cells gpio_out_0]
create_bd_cell -type ip -vlnv xilinx.com:ip:xlslice:1.0 gpio_out_1
set_property -dict [list CONFIG.DIN_TO {1} CONFIG.DIN_FROM {1} CONFIG.DIN_WIDTH {3} CONFIG.DOUT_WIDTH {1}] [get_bd_cells gpio_out_1]
create_bd_cell -type ip -vlnv xilinx.com:ip:xlslice:1.0 gpio_out_2
set_property -dict [list CONFIG.DIN_TO {2} CONFIG.DIN_FROM {2} CONFIG.DIN_WIDTH {3} CONFIG.DOUT_WIDTH {1}] [get_bd_cells gpio_out_2]
connect_bd_net [get_bd_pins axi_gpio_out/gpio_io_o] [get_bd_pins gpio_out_2/Din]
connect_bd_net [get_bd_pins axi_gpio_out/gpio_io_o] [get_bd_pins gpio_out_1/Din]
connect_bd_net [get_bd_pins axi_gpio_out/gpio_io_o] [get_bd_pins gpio_out_0/Din]

# Auto gen: GPIO O0 -> grad rst
#connect_bd_net [get_bd_pins gpio_out_0/Dout] [get_bd_pins ***/rsta]
$grad_rst_connections

# Auto gen: GPIO O1 -> BRAM Mux
$bram_mux_sel_connections

# GOIO O2 -> cache_en
connect_bd_net [get_bd_pins gpio_out_2/Dout] [get_bd_pins nn_ip/cache_en]


# AXI GPIO in
create_bd_cell -type ip -vlnv xilinx.com:ip:axi_gpio:2.0 axi_gpio_in
set_property -dict [list CONFIG.C_GPIO_WIDTH {10} CONFIG.C_ALL_INPUTS {1} CONFIG.C_INTERRUPT_PRESENT {1}] [get_bd_cells axi_gpio_in]
create_bd_cell -type ip -vlnv xilinx.com:ip:xlconcat:2.1 gpio_in_concat
set_property -dict [list CONFIG.NUM_PORTS {10}] [get_bd_cells gpio_in_concat]
connect_bd_net [get_bd_pins gpio_in_concat/dout] [get_bd_pins axi_gpio_in/gpio_io_i]

# RST Busy
# Concat
create_bd_cell -type ip -vlnv xilinx.com:ip:xlconcat:2.1 mem_grad_rst_busy_concat
set_property -dict [list CONFIG.NUM_PORTS {$param_count}] [get_bd_cells mem_grad_rst_busy_concat]
$grad_rst_busy_connections

# And
create_bd_cell -type ip -vlnv xilinx.com:ip:util_reduced_logic:2.0 mem_grad_rst_busy_and
set_property -dict [list CONFIG.C_SIZE {7}] [get_bd_cells mem_grad_rst_busy_and]
connect_bd_net [get_bd_pins mem_grad_rst_busy_concat/dout] [get_bd_pins mem_grad_rst_busy_and/Op1]


connect_bd_net [get_bd_pins nn_ip/ap_done] [get_bd_pins gpio_in_concat/In0]
connect_bd_net [get_bd_pins nn_ip/ap_ready] [get_bd_pins gpio_in_concat/In1]
connect_bd_net [get_bd_pins nn_ip/ap_idle] [get_bd_pins gpio_in_concat/In2]
connect_bd_net [get_bd_pins param_loader/ap_done] [get_bd_pins gpio_in_concat/In3]
connect_bd_net [get_bd_pins param_loader/ap_ready] [get_bd_pins gpio_in_concat/In4]
connect_bd_net [get_bd_pins param_loader/ap_idle] [get_bd_pins gpio_in_concat/In5]
connect_bd_net [get_bd_pins grad_extractor/ap_done] [get_bd_pins gpio_in_concat/In6]
connect_bd_net [get_bd_pins grad_extractor/ap_ready] [get_bd_pins gpio_in_concat/In7]
connect_bd_net [get_bd_pins grad_extractor/ap_idle] [get_bd_pins gpio_in_concat/In8]
connect_bd_net [get_bd_pins mem_grad_rst_busy_and/Res] [get_bd_pins gpio_in_concat/In9]

# ZYNQ system
create_bd_cell -type ip -vlnv xilinx.com:ip:processing_system7:5.5 processing_system7_0

exit
