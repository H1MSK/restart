# Create project and configure IP
create_project system ./build_system -part xc7z020clg400-2
set_property  ip_repo_paths  . [current_project]
update_ip_catalog -rebuild




# Create block design and add main IPs
create_bd_design "system"
startgroup
create_bd_cell -type ip -vlnv xilinx.com:hls:forward:1.0 forward
create_bd_cell -type ip -vlnv xilinx.com:hls:backward:1.0 backward
create_bd_cell -type ip -vlnv xilinx.com:hls:grad_extractor:1.0 grad_extractor
create_bd_cell -type ip -vlnv xilinx.com:hls:param_loader:1.0 param_loader
endgroup





# ZYNQ system
startgroup
create_bd_cell -type ip -vlnv xilinx.com:ip:processing_system7:5.5 processing_system7_0
set_property -dict [list CONFIG.PCW_FPGA0_PERIPHERAL_FREQMHZ {200} CONFIG.PCW_USE_S_AXI_HP0 {1} CONFIG.PCW_USE_S_AXI_HP1 {1} CONFIG.PCW_USE_S_AXI_HP2 {1} CONFIG.PCW_USE_FABRIC_INTERRUPT {1} CONFIG.PCW_S_AXI_HP0_DATA_WIDTH {32} CONFIG.PCW_S_AXI_HP1_DATA_WIDTH {32} CONFIG.PCW_S_AXI_HP2_DATA_WIDTH {32} CONFIG.PCW_IRQ_F2P_INTR {1} CONFIG.PCW_UIPARAM_DDR_PARTNO {MT41J256M16 RE-125} CONFIG.PCW_GPIO_EMIO_GPIO_ENABLE {1} CONFIG.PCW_GPIO_EMIO_GPIO_IO {32}] [get_bd_cells processing_system7_0]
endgroup





# Reset ip
startgroup
create_bd_cell -type ip -vlnv xilinx.com:ip:proc_sys_reset:5.0 proc_sys_reset_0
connect_bd_net [get_bd_pins proc_sys_reset_0/slowest_sync_clk] [get_bd_pins processing_system7_0/FCLK_CLK0]
connect_bd_net [get_bd_pins proc_sys_reset_0/ext_reset_in] [get_bd_pins processing_system7_0/FCLK_RESET0_N]
endgroup





# Clock & Reset
startgroup
apply_bd_automation -rule xilinx.com:bd_rule:processing_system7 -config {make_external "FIXED_IO, DDR" Master "Disable" Slave "Disable" }  [get_bd_cells processing_system7_0]
connect_bd_net [get_bd_pins processing_system7_0/FCLK_CLK0] [get_bd_pins param_loader/ap_clk]
connect_bd_net [get_bd_pins proc_sys_reset_0/peripheral_aresetn] [get_bd_pins param_loader/ap_rst_n]
connect_bd_net [get_bd_pins processing_system7_0/FCLK_CLK0] [get_bd_pins grad_extractor/ap_clk]
connect_bd_net [get_bd_pins proc_sys_reset_0/peripheral_aresetn] [get_bd_pins grad_extractor/ap_rst_n]
connect_bd_net [get_bd_pins processing_system7_0/FCLK_CLK0] [get_bd_pins forward/ap_clk]
connect_bd_net [get_bd_pins proc_sys_reset_0/peripheral_aresetn] [get_bd_pins forward/ap_rst_n]
connect_bd_net [get_bd_pins processing_system7_0/FCLK_CLK0] [get_bd_pins backward/ap_clk]
connect_bd_net [get_bd_pins proc_sys_reset_0/peripheral_aresetn] [get_bd_pins backward/ap_rst_n]
endgroup





# Control IP
startgroup
create_bd_cell -type ip -vlnv h1msk.cc:fpga_nn.hls:ap_controller:1.0 apcon_fw
connect_bd_intf_net [get_bd_intf_pins apcon_fw/ap_ctrl] [get_bd_intf_pins forward/ap_ctrl]
connect_bd_net [get_bd_pins apcon_fw/ap_clk] [get_bd_pins processing_system7_0/FCLK_CLK0]
connect_bd_net [get_bd_pins apcon_fw/ap_rst_n] [get_bd_pins proc_sys_reset_0/peripheral_aresetn]
create_bd_cell -type ip -vlnv h1msk.cc:fpga_nn.hls:ap_controller:1.0 apcon_bw
connect_bd_intf_net [get_bd_intf_pins apcon_bw/ap_ctrl] [get_bd_intf_pins backward/ap_ctrl]
connect_bd_net [get_bd_pins apcon_bw/ap_clk] [get_bd_pins processing_system7_0/FCLK_CLK0]
connect_bd_net [get_bd_pins apcon_bw/ap_rst_n] [get_bd_pins proc_sys_reset_0/peripheral_aresetn]
create_bd_cell -type ip -vlnv h1msk.cc:fpga_nn.hls:ap_controller:1.0 apcon_param
connect_bd_intf_net [get_bd_intf_pins apcon_param/ap_ctrl] [get_bd_intf_pins param_loader/ap_ctrl]
connect_bd_net [get_bd_pins apcon_param/ap_clk] [get_bd_pins processing_system7_0/FCLK_CLK0]
connect_bd_net [get_bd_pins apcon_param/ap_rst_n] [get_bd_pins proc_sys_reset_0/peripheral_aresetn]
create_bd_cell -type ip -vlnv h1msk.cc:fpga_nn.hls:ap_controller:1.0 apcon_grad
connect_bd_intf_net [get_bd_intf_pins apcon_grad/ap_ctrl] [get_bd_intf_pins grad_extractor/ap_ctrl]
connect_bd_net [get_bd_pins apcon_grad/ap_clk] [get_bd_pins processing_system7_0/FCLK_CLK0]
connect_bd_net [get_bd_pins apcon_grad/ap_rst_n] [get_bd_pins proc_sys_reset_0/peripheral_aresetn]
endgroup





# Create memories and their connections
startgroup
$memory_scripts
endgroup





# Memory reset signals
startgroup
create_bd_cell -type ip -vlnv xilinx.com:ip:xlconcat:2.1 concat_param_reset
set_property -dict [list CONFIG.NUM_PORTS {$param_count}] [get_bd_cells concat_param_reset]
$param_rsta_busy_out_scripts
create_bd_cell -type ip -vlnv xilinx.com:ip:util_reduced_logic:2.0 reduce_param_reset
set_property -dict [list CONFIG.C_SIZE {$param_count} CONFIG.C_OPERATION {or} CONFIG.LOGO_FILE {data/sym_orgate.png}] [get_bd_cells reduce_param_reset]
connect_bd_net [get_bd_pins reduce_param_reset/Op1] [get_bd_pins concat_param_reset/dout]

create_bd_cell -type ip -vlnv xilinx.com:ip:xlconcat:2.1 concat_grad_reset
set_property -dict [list CONFIG.NUM_PORTS {$param_count}] [get_bd_cells concat_grad_reset]
$grad_rsta_busy_out_scripts
create_bd_cell -type ip -vlnv xilinx.com:ip:util_reduced_logic:2.0 reduce_grad_reset
set_property -dict [list CONFIG.C_SIZE {$param_count} CONFIG.C_OPERATION {or} CONFIG.LOGO_FILE {data/sym_orgate.png}] [get_bd_cells reduce_grad_reset]
connect_bd_net [get_bd_pins reduce_grad_reset/Op1] [get_bd_pins concat_grad_reset/dout]
endgroup





# Create caches and their connections
startgroup
$cache_scripts
endgroup





# DMA for forward function
startgroup
create_bd_cell -type ip -vlnv xilinx.com:ip:axi_dma:7.1 axi_dma_fw
set_property -dict [list CONFIG.c_m_axi_s2mm_data_width.VALUE_SRC PROPAGATED CONFIG.c_single_interface.VALUE_SRC USER] [get_bd_cells axi_dma_fw]
set_property -dict [list CONFIG.c_include_sg {0} CONFIG.c_sg_include_stscntrl_strm {0} CONFIG.c_mm2s_burst_size {256} CONFIG.c_s2mm_burst_size {256} CONFIG.c_include_mm2s_dre {1} CONFIG.c_include_s2mm_dre {1}] [get_bd_cells axi_dma_fw]

connect_bd_net [get_bd_pins forward/out_y_TREADY] [get_bd_pins axi_dma_fw/s_axis_s2mm_tready]
connect_bd_net [get_bd_pins forward/ap_continue] [get_bd_pins axi_dma_fw/s_axis_s2mm_tready]
connect_bd_intf_net [get_bd_intf_pins axi_dma_fw/M_AXIS_MM2S] [get_bd_intf_pins forward/in_x]
connect_bd_intf_net [get_bd_intf_pins axi_dma_fw/S_AXIS_S2MM] [get_bd_intf_pins forward/out_y]
endgroup





# AXI Interconnect fw DMA <==> HP0
startgroup
apply_bd_automation -rule xilinx.com:bd_rule:axi4 -config { Clk_master {/processing_system7_0/FCLK_CLK0 (200 MHz)} Clk_slave {/processing_system7_0/FCLK_CLK0 (200 MHz)} Clk_xbar {/processing_system7_0/FCLK_CLK0 (200 MHz)} Master {/axi_dma_fw/M_AXI_MM2S} Slave {/processing_system7_0/S_AXI_HP0} ddr_seg {Auto} intc_ip {New AXI Interconnect} master_apm {0}}  [get_bd_intf_pins processing_system7_0/S_AXI_HP0]
set_property name axi_mem_intercon_fw [get_bd_cells axi_mem_intercon]
set_property -dict [list CONFIG.NUM_SI {2} CONFIG.NUM_MI {1}] [get_bd_cells axi_mem_intercon_fw]
connect_bd_intf_net [get_bd_intf_pins axi_dma_fw/M_AXI_S2MM] -boundary_type upper [get_bd_intf_pins axi_mem_intercon_fw/S01_AXI]
connect_bd_net [get_bd_pins axi_mem_intercon_fw/S01_ACLK] [get_bd_pins processing_system7_0/FCLK_CLK0]
connect_bd_net [get_bd_pins axi_mem_intercon_fw/S01_ARESETN] [get_bd_pins proc_sys_reset_0/peripheral_aresetn]
connect_bd_net [get_bd_pins axi_dma_fw/m_axi_s2mm_aclk] [get_bd_pins processing_system7_0/FCLK_CLK0]
assign_bd_address -target_address_space /axi_dma_fw/Data_S2MM [get_bd_addr_segs processing_system7_0/S_AXI_HP0/HP0_DDR_LOWOCM] -force
endgroup





# DMA for backward function
startgroup
create_bd_cell -type ip -vlnv xilinx.com:ip:axi_dma:7.1 axi_dma_bw
set_property -dict [list CONFIG.c_include_sg {0} CONFIG.c_sg_include_stscntrl_strm {0} CONFIG.c_include_s2mm {0} CONFIG.c_include_mm2s_dre {1}] [get_bd_cells axi_dma_bw]
connect_bd_intf_net [get_bd_intf_pins axi_dma_bw/M_AXIS_MM2S] [get_bd_intf_pins backward/in_grad_y]
endgroup





# AXI Interconnect bw DMA <==> HP1
startgroup
apply_bd_automation -rule xilinx.com:bd_rule:axi4 -config { Clk_master {Auto} Clk_slave {Auto} Clk_xbar {Auto} Master {/axi_dma_bw/M_AXI_MM2S} Slave {/processing_system7_0/S_AXI_HP1} ddr_seg {Auto} intc_ip {New AXI Interconnect} master_apm {0}}  [get_bd_intf_pins processing_system7_0/S_AXI_HP1]
set_property name axi_mem_intercon_bw [get_bd_cells axi_mem_intercon]
endgroup






# DMA for param loader and grad extractor
startgroup
create_bd_cell -type ip -vlnv xilinx.com:ip:axi_dma:7.1 axi_dma_pg
set_property -dict [list CONFIG.c_single_interface.VALUE_SRC USER] [get_bd_cells axi_dma_pg]
set_property -dict [list CONFIG.c_include_sg {0} CONFIG.c_sg_length_width {17} CONFIG.c_sg_include_stscntrl_strm {0} CONFIG.c_include_mm2s_dre {1} CONFIG.c_mm2s_burst_size {256} CONFIG.c_include_s2mm_dre {1} CONFIG.c_s2mm_burst_size {256}] [get_bd_cells axi_dma_pg]
connect_bd_intf_net [get_bd_intf_pins axi_dma_pg/M_AXIS_MM2S] [get_bd_intf_pins param_loader/in_r]
connect_bd_intf_net [get_bd_intf_pins axi_dma_pg/S_AXIS_S2MM] [get_bd_intf_pins grad_extractor/out_r]
endgroup




# AXI Interconnect gp DMA <==> HP2
startgroup
apply_bd_automation -rule xilinx.com:bd_rule:axi4 -config { Clk_master {Auto} Clk_slave {Auto} Clk_xbar {Auto} Master {/axi_dma_pg/M_AXI_MM2S} Slave {/processing_system7_0/S_AXI_HP2} ddr_seg {Auto} intc_ip {New AXI Interconnect} master_apm {0}}  [get_bd_intf_pins processing_system7_0/S_AXI_HP2]
set_property name axi_mem_intercon_pg [get_bd_cells axi_mem_intercon]
set_property -dict [list CONFIG.NUM_SI {2} CONFIG.NUM_MI {1}] [get_bd_cells axi_mem_intercon_pg]
connect_bd_intf_net [get_bd_intf_pins axi_dma_pg/M_AXI_S2MM] -boundary_type upper [get_bd_intf_pins axi_mem_intercon_pg/S01_AXI]
connect_bd_net [get_bd_pins axi_mem_intercon_pg/S01_ACLK] [get_bd_pins processing_system7_0/FCLK_CLK0]
connect_bd_net [get_bd_pins axi_mem_intercon_pg/S01_ARESETN] [get_bd_pins proc_sys_reset_0/peripheral_aresetn]
connect_bd_net [get_bd_pins axi_dma_pg/m_axi_s2mm_aclk] [get_bd_pins processing_system7_0/FCLK_CLK0]
assign_bd_address -target_address_space /axi_dma_pg/Data_S2MM [get_bd_addr_segs processing_system7_0/S_AXI_HP2/HP2_DDR_LOWOCM] -force
endgroup





# AXI Slave GP 0 to DMAs
apply_bd_automation -rule xilinx.com:bd_rule:axi4 -config { Clk_master {Auto} Clk_slave {Auto} Clk_xbar {Auto} Master {/processing_system7_0/M_AXI_GP0} Slave {/axi_dma_bw/S_AXI_LITE} ddr_seg {Auto} intc_ip {New AXI Interconnect} master_apm {0}}  [get_bd_intf_pins axi_dma_bw/S_AXI_LITE]
apply_bd_automation -rule xilinx.com:bd_rule:axi4 -config { Clk_master {Auto} Clk_slave {Auto} Clk_xbar {Auto} Master {/processing_system7_0/M_AXI_GP0} Slave {/axi_dma_fw/S_AXI_LITE} ddr_seg {Auto} intc_ip {New AXI Interconnect} master_apm {0}}  [get_bd_intf_pins axi_dma_fw/S_AXI_LITE]
apply_bd_automation -rule xilinx.com:bd_rule:axi4 -config { Clk_master {Auto} Clk_slave {Auto} Clk_xbar {Auto} Master {/processing_system7_0/M_AXI_GP0} Slave {/axi_dma_pg/S_AXI_LITE} ddr_seg {Auto} intc_ip {New AXI Interconnect} master_apm {0}}  [get_bd_intf_pins axi_dma_pg/S_AXI_LITE]





# GPIO Connection
startgroup
create_bd_cell -type ip -vlnv h1msk.cc:fpga_nn.hls:gpio_connection:1.0 gpio_connection
connect_bd_intf_net [get_bd_intf_pins processing_system7_0/GPIO_0] [get_bd_intf_pins gpio_connection/GPIO]
connect_bd_net [get_bd_pins gpio_connection/fw_start] [get_bd_pins apcon_fw/start_trig]
connect_bd_net [get_bd_pins gpio_connection/fw_idle] [get_bd_pins apcon_fw/idle]
connect_bd_net [get_bd_pins gpio_connection/fw_done] [get_bd_pins apcon_fw/finish]

connect_bd_net [get_bd_pins gpio_connection/bw_start] [get_bd_pins apcon_bw/start_trig]
connect_bd_net [get_bd_pins gpio_connection/bw_idle] [get_bd_pins apcon_bw/idle]
connect_bd_net [get_bd_pins gpio_connection/bw_done] [get_bd_pins apcon_bw/finish]

connect_bd_net [get_bd_pins gpio_connection/param_start] [get_bd_pins apcon_param/start_trig]
connect_bd_net [get_bd_pins gpio_connection/param_idle] [get_bd_pins apcon_param/idle]
connect_bd_net [get_bd_pins gpio_connection/param_done] [get_bd_pins apcon_param/finish]

connect_bd_net [get_bd_pins gpio_connection/grad_start] [get_bd_pins apcon_grad/start_trig]
connect_bd_net [get_bd_pins gpio_connection/grad_idle] [get_bd_pins apcon_grad/idle]
connect_bd_net [get_bd_pins gpio_connection/grad_done] [get_bd_pins apcon_grad/finish]

connect_bd_net [get_bd_pins forward/cache_en] [get_bd_pins gpio_connection/cache_en]
connect_bd_net [get_bd_pins gpio_connection/param_reset_busy] [get_bd_pins reduce_param_reset/Res]
connect_bd_net [get_bd_pins gpio_connection/grad_reset_busy] [get_bd_pins reduce_grad_reset/Res]
$bram_mux_sel_connections

$bram_rst_connections
endgroup





# Interrupts





regenerate_bd_layout

# Todo: Connect other ports

save_bd_design

generate_target all [get_files  ./build_system/system.srcs/sources_1/bd/system/system.bd]
make_wrapper -files [get_files ./build_system/system.srcs/sources_1/bd/system/system.bd] -top
add_files -norecurse ./build_system/system.gen/sources_1/bd/system/hdl/system_wrapper.v

reset_run synth_1
launch_runs synth_1
wait_on_runs synth_1

# Todo: synthesis, implement, export

exit
