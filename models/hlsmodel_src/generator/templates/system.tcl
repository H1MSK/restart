# Create project and configure IP
if {[file exists ./build_system]} {
    puts "Using current system project"
    open_project ./build_system/system.xpr
} else {
    create_project system ./build_system -part xc7z020clg400-2
}





set_property  ip_repo_paths  . [current_project]
update_ip_catalog -rebuild




# Create block design and add main IPs
if {[catch {open_bd_design ./build_system/system.srcs/sources_1/bd/system/system.bd} errmsg]} {
    create_bd_design "system"
} else {
    delete_bd_objs [get_bd_cell *] [get_bd_net *] [get_bd_intf_nets *] [get_bd_intf_ports *]
}





startgroup
create_bd_cell -type ip -vlnv xilinx.com:hls:forward:1.0 forward
create_bd_cell -type ip -vlnv xilinx.com:hls:backward:1.0 backward
create_bd_cell -type ip -vlnv xilinx.com:hls:grad_extractor:1.0 grad_extractor
create_bd_cell -type ip -vlnv xilinx.com:hls:param_loader:1.0 param_loader
endgroup





# ZYNQ system
startgroup
create_bd_cell -type ip -vlnv xilinx.com:ip:processing_system7:5.5 processing_system7_0
set_property -dict [list CONFIG.PCW_FPGA0_PERIPHERAL_FREQMHZ {$system_clk_mhz} CONFIG.PCW_USE_S_AXI_HP0 {1} CONFIG.PCW_USE_S_AXI_HP1 {1} CONFIG.PCW_USE_S_AXI_HP2 {1} CONFIG.PCW_USE_S_AXI_HP3 {1} CONFIG.PCW_USE_FABRIC_INTERRUPT {1} CONFIG.PCW_S_AXI_HP0_DATA_WIDTH {64} CONFIG.PCW_S_AXI_HP1_DATA_WIDTH {64} CONFIG.PCW_S_AXI_HP2_DATA_WIDTH {64} CONFIG.PCW_S_AXI_HP3_DATA_WIDTH {64} CONFIG.PCW_IRQ_F2P_INTR {1} CONFIG.PCW_UIPARAM_DDR_PARTNO {MT41J256M16 RE-125} CONFIG.PCW_GPIO_EMIO_GPIO_ENABLE {1} CONFIG.PCW_GPIO_EMIO_GPIO_IO {32} CONFIG.PCW_PRESET_BANK1_VOLTAGE {LVCMOS 1.8V}] [get_bd_cells processing_system7_0]
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





# AXI Interconnect IP gmem <==> HP Slave
startgroup
apply_bd_automation -rule xilinx.com:bd_rule:axi4 -config { Clk_master {/processing_system7_0/FCLK_CLK0} Clk_slave {Auto} Clk_xbar {Auto} Master {/forward/m_axi_gmem} Slave {/processing_system7_0/S_AXI_HP0} ddr_seg {Auto} intc_ip {New AXI Interconnect} master_apm {0}}  [get_bd_intf_pins processing_system7_0/S_AXI_HP0]
set_property name axi_mem_intercon_fw [get_bd_cells axi_mem_intercon]
delete_bd_objs [get_bd_addr_segs forward/Data_m_axi_gmem/*]

apply_bd_automation -rule xilinx.com:bd_rule:axi4 -config { Clk_master {/processing_system7_0/FCLK_CLK0} Clk_slave {Auto} Clk_xbar {Auto} Master {/backward/m_axi_gmem} Slave {/processing_system7_0/S_AXI_HP1} ddr_seg {Auto} intc_ip {New AXI Interconnect} master_apm {0}}  [get_bd_intf_pins processing_system7_0/S_AXI_HP1]
set_property name axi_mem_intercon_bw [get_bd_cells axi_mem_intercon]
delete_bd_objs [get_bd_addr_segs backward/Data_m_axi_gmem/*]

apply_bd_automation -rule xilinx.com:bd_rule:axi4 -config { Clk_master {/processing_system7_0/FCLK_CLK0} Clk_slave {Auto} Clk_xbar {Auto} Master {/param_loader/m_axi_gmem} Slave {/processing_system7_0/S_AXI_HP2} ddr_seg {Auto} intc_ip {New AXI Interconnect} master_apm {0}}  [get_bd_intf_pins processing_system7_0/S_AXI_HP2]
set_property name axi_mem_intercon_pa [get_bd_cells axi_mem_intercon]
delete_bd_objs [get_bd_addr_segs param_loader/Data_m_axi_gmem/*]

apply_bd_automation -rule xilinx.com:bd_rule:axi4 -config { Clk_master {/processing_system7_0/FCLK_CLK0} Clk_slave {Auto} Clk_xbar {Auto} Master {/grad_extractor/m_axi_gmem} Slave {/processing_system7_0/S_AXI_HP3} ddr_seg {Auto} intc_ip {New AXI Interconnect} master_apm {0}}  [get_bd_intf_pins processing_system7_0/S_AXI_HP3]
set_property name axi_mem_intercon_gr [get_bd_cells axi_mem_intercon]
delete_bd_objs [get_bd_addr_segs grad_extractor/Data_m_axi_gmem/*]

assign_bd_address -target_address_space /forward/Data_m_axi_gmem [get_bd_addr_segs processing_system7_0/S_AXI_HP0/HP0_DDR_LOWOCM] -force
assign_bd_address -target_address_space /backward/Data_m_axi_gmem [get_bd_addr_segs processing_system7_0/S_AXI_HP1/HP1_DDR_LOWOCM] -force
assign_bd_address -target_address_space /param_loader/Data_m_axi_gmem [get_bd_addr_segs processing_system7_0/S_AXI_HP2/HP2_DDR_LOWOCM] -force
assign_bd_address -target_address_space /grad_extractor/Data_m_axi_gmem [get_bd_addr_segs processing_system7_0/S_AXI_HP3/HP3_DDR_LOWOCM] -force
endgroup




# AXI Slave GP 0 to DMAs
startgroup
apply_bd_automation -rule xilinx.com:bd_rule:axi4 -config { Clk_master {Auto} Clk_slave {/processing_system7_0/FCLK_CLK0} Clk_xbar {Auto} Master {/processing_system7_0/M_AXI_GP0} Slave {/forward/s_axi_control} ddr_seg {0x4000_0000} intc_ip {New AXI Interconnect} master_apm {0}}  [get_bd_intf_pins forward/s_axi_control]
apply_bd_automation -rule xilinx.com:bd_rule:axi4 -config { Clk_master {Auto} Clk_slave {/processing_system7_0/FCLK_CLK0} Clk_xbar {Auto} Master {/processing_system7_0/M_AXI_GP0} Slave {/backward/s_axi_control} ddr_seg {0x4001_0000} intc_ip {New AXI Interconnect} master_apm {0}}  [get_bd_intf_pins backward/s_axi_control]
apply_bd_automation -rule xilinx.com:bd_rule:axi4 -config { Clk_master {Auto} Clk_slave {/processing_system7_0/FCLK_CLK0} Clk_xbar {Auto} Master {/processing_system7_0/M_AXI_GP0} Slave {/param_loader/s_axi_control} ddr_seg {0x4002_0000} intc_ip {New AXI Interconnect} master_apm {0}}  [get_bd_intf_pins param_loader/s_axi_control]
apply_bd_automation -rule xilinx.com:bd_rule:axi4 -config { Clk_master {Auto} Clk_slave {/processing_system7_0/FCLK_CLK0} Clk_xbar {Auto} Master {/processing_system7_0/M_AXI_GP0} Slave {/grad_extractor/s_axi_control} ddr_seg {0x4003_0000} intc_ip {New AXI Interconnect} master_apm {0}}  [get_bd_intf_pins grad_extractor/s_axi_control]
endgroup





# GPIO Connection
startgroup
create_bd_cell -type ip -vlnv h1msk.cc:fpga_nn.hls:gpio_connection:1.0 gpio_connection
connect_bd_intf_net [get_bd_intf_pins processing_system7_0/GPIO_0] [get_bd_intf_pins gpio_connection/GPIO]

# connect_bd_net [get_bd_pins forward/cache_en] [get_bd_pins gpio_connection/cache_en]
connect_bd_net [get_bd_pins gpio_connection/param_reset_busy] [get_bd_pins reduce_param_reset/Res]
connect_bd_net [get_bd_pins gpio_connection/grad_reset_busy] [get_bd_pins reduce_grad_reset/Res]

connect_bd_net [get_bd_pins gpio_connection/system_reset] [get_bd_pins proc_sys_reset_0/aux_reset_in]

$param_mux_sel_connections
$grad_mux_sel_connections

$param_rst_connections
$grad_rst_connections
endgroup





# Interrupts
startgroup
create_bd_cell -type ip -vlnv xilinx.com:ip:xlconcat:2.1 concat_ip_intr
set_property -dict [list CONFIG.NUM_PORTS {4}] [get_bd_cells concat_ip_intr]
connect_bd_net [get_bd_pins forward/interrupt] [get_bd_pins concat_ip_intr/In0]
connect_bd_net [get_bd_pins backward/interrupt] [get_bd_pins concat_ip_intr/In1]
connect_bd_net [get_bd_pins param_loader/interrupt] [get_bd_pins concat_ip_intr/In2]
connect_bd_net [get_bd_pins grad_extractor/interrupt] [get_bd_pins concat_ip_intr/In3]
endgroup

startgroup
create_bd_cell -type ip -vlnv xilinx.com:ip:axi_intc:4.1 axi_intc_ip
connect_bd_net [get_bd_pins concat_ip_intr/dout] [get_bd_pins axi_intc_ip/intr]
connect_bd_net [get_bd_pins axi_intc_ip/irq] [get_bd_pins processing_system7_0/IRQ_F2P]
apply_bd_automation -rule xilinx.com:bd_rule:axi4 -config { Clk_master {/processing_system7_0/FCLK_CLK0} Clk_slave {/processing_system7_0/FCLK_CLK0} Clk_xbar {/processing_system7_0/FCLK_CLK0} Master {/processing_system7_0/M_AXI_GP0} Slave {/axi_intc_ip/s_axi} ddr_seg {0x4010_0000} intc_ip {/ps7_0_axi_periph} master_apm {0}}  [get_bd_intf_pins axi_intc_ip/s_axi]
endgroup





regenerate_bd_layout

# Todo: Connect other ports

save_bd_design

generate_target all [get_files  ./build_system/system.srcs/sources_1/bd/system/system.bd]
make_wrapper -files [get_files ./build_system/system.srcs/sources_1/bd/system/system.bd] -top
add_files -norecurse ./build_system/system.gen/sources_1/bd/system/hdl/system_wrapper.v

reset_run impl_1
reset_run synth_1
launch_runs impl_1 -to_step write_bitstream -jobs 4

# Todo: synthesis, implement, export

exit
