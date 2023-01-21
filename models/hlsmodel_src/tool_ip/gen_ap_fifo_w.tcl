create_project ap_fifo_w ./build_ap_fifo_w -part xc7z020clg400-2

add_files ./ap_fifo_w.v

ipx::package_project -import_files ./ap_fifo_w.v -root_dir ./build/ap_fifo_w -name ap_fifo_w -vendor h1msk.cc -library fpga_nn.hls -taxonomy /UserIP

set_property display_name {ap_fifo_w} [ipx::current_core]


ipx::add_bus_interface acc_fifo_s [ipx::current_core]
set_property abstraction_type_vlnv xilinx.com:interface:acc_fifo_write_rtl:1.0 [ipx::get_bus_interfaces acc_fifo_s -of_objects [ipx::current_core]]
set_property bus_type_vlnv xilinx.com:interface:acc_fifo_write:1.0 [ipx::get_bus_interfaces acc_fifo_s -of_objects [ipx::current_core]]
ipx::add_port_map WR_DATA [ipx::get_bus_interfaces acc_fifo_s -of_objects [ipx::current_core]]
set_property physical_name WR_DATA_s [ipx::get_port_maps WR_DATA -of_objects [ipx::get_bus_interfaces acc_fifo_s -of_objects [ipx::current_core]]]
ipx::add_port_map WR_EN [ipx::get_bus_interfaces acc_fifo_s -of_objects [ipx::current_core]]
set_property physical_name WR_EN_s [ipx::get_port_maps WR_EN -of_objects [ipx::get_bus_interfaces acc_fifo_s -of_objects [ipx::current_core]]]
ipx::add_port_map FULL_N [ipx::get_bus_interfaces acc_fifo_s -of_objects [ipx::current_core]]
set_property physical_name FULL_N_s [ipx::get_port_maps FULL_N -of_objects [ipx::get_bus_interfaces acc_fifo_s -of_objects [ipx::current_core]]]
ipx::add_bus_interface fifo_m [ipx::current_core]
set_property abstraction_type_vlnv xilinx.com:interface:fifo_write_rtl:1.0 [ipx::get_bus_interfaces fifo_m -of_objects [ipx::current_core]]
set_property bus_type_vlnv xilinx.com:interface:fifo_write:1.0 [ipx::get_bus_interfaces fifo_m -of_objects [ipx::current_core]]
set_property interface_mode master [ipx::get_bus_interfaces fifo_m -of_objects [ipx::current_core]]
ipx::add_port_map WR_DATA [ipx::get_bus_interfaces fifo_m -of_objects [ipx::current_core]]
set_property physical_name WR_DATA_m [ipx::get_port_maps WR_DATA -of_objects [ipx::get_bus_interfaces fifo_m -of_objects [ipx::current_core]]]
ipx::add_port_map WR_EN [ipx::get_bus_interfaces fifo_m -of_objects [ipx::current_core]]
set_property physical_name WR_EN_m [ipx::get_port_maps WR_EN -of_objects [ipx::get_bus_interfaces fifo_m -of_objects [ipx::current_core]]]
ipx::add_port_map FULL [ipx::get_bus_interfaces fifo_m -of_objects [ipx::current_core]]
set_property physical_name FULL_m [ipx::get_port_maps FULL -of_objects [ipx::get_bus_interfaces fifo_m -of_objects [ipx::current_core]]]

ipx::create_xgui_files [ipx::current_core]
ipx::update_checksums [ipx::current_core]
ipx::check_integrity [ipx::current_core]
ipx::save_core [ipx::current_core]
ipx::unload_core ./build/ap_fifo_w/component.xml
close_project

exit