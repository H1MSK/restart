create_project ap_fifo_r ./build_ap_fifo_r -part xc7z020clg400-2

add_files ./ap_fifo_r.v

ipx::package_project -import_files ./ap_fifo_r.v -root_dir ./build/ap_fifo_r -name ap_fifo_r -vendor h1msk.cc -library fpga_nn.hls -taxonomy /UserIP

set_property display_name {ap_fifo_r} [ipx::current_core]


ipx::add_bus_interface acc_fifo_s [ipx::current_core]
set_property abstraction_type_vlnv xilinx.com:interface:acc_fifo_read_rtl:1.0 [ipx::get_bus_interfaces acc_fifo_s -of_objects [ipx::current_core]]
set_property bus_type_vlnv xilinx.com:interface:acc_fifo_read:1.0 [ipx::get_bus_interfaces acc_fifo_s -of_objects [ipx::current_core]]
set_property interface_mode slave [ipx::get_bus_interfaces acc_fifo_s -of_objects [ipx::current_core]]
ipx::add_port_map RD_DATA [ipx::get_bus_interfaces acc_fifo_s -of_objects [ipx::current_core]]
set_property physical_name RD_DATA_s [ipx::get_port_maps RD_DATA -of_objects [ipx::get_bus_interfaces acc_fifo_s -of_objects [ipx::current_core]]]
ipx::add_port_map RD_EN [ipx::get_bus_interfaces acc_fifo_s -of_objects [ipx::current_core]]
set_property physical_name RD_EN_s [ipx::get_port_maps RD_EN -of_objects [ipx::get_bus_interfaces acc_fifo_s -of_objects [ipx::current_core]]]
ipx::add_port_map EMPTY_N [ipx::get_bus_interfaces acc_fifo_s -of_objects [ipx::current_core]]
set_property physical_name EMPTY_N_s [ipx::get_port_maps EMPTY_N -of_objects [ipx::get_bus_interfaces acc_fifo_s -of_objects [ipx::current_core]]]
ipx::add_bus_interface fifo_m [ipx::current_core]
set_property abstraction_type_vlnv xilinx.com:interface:fifo_read_rtl:1.0 [ipx::get_bus_interfaces fifo_m -of_objects [ipx::current_core]]
set_property bus_type_vlnv xilinx.com:interface:fifo_read:1.0 [ipx::get_bus_interfaces fifo_m -of_objects [ipx::current_core]]
set_property interface_mode master [ipx::get_bus_interfaces fifo_m -of_objects [ipx::current_core]]
ipx::add_port_map RD_DATA [ipx::get_bus_interfaces fifo_m -of_objects [ipx::current_core]]
set_property physical_name RD_DATA_m [ipx::get_port_maps RD_DATA -of_objects [ipx::get_bus_interfaces fifo_m -of_objects [ipx::current_core]]]
ipx::add_port_map RD_EN [ipx::get_bus_interfaces fifo_m -of_objects [ipx::current_core]]
set_property physical_name RD_EN_m [ipx::get_port_maps RD_EN -of_objects [ipx::get_bus_interfaces fifo_m -of_objects [ipx::current_core]]]
ipx::add_port_map EMPTY [ipx::get_bus_interfaces fifo_m -of_objects [ipx::current_core]]
set_property physical_name EMPTY_m [ipx::get_port_maps EMPTY -of_objects [ipx::get_bus_interfaces fifo_m -of_objects [ipx::current_core]]]

ipx::create_xgui_files [ipx::current_core]
ipx::update_checksums [ipx::current_core]
ipx::check_integrity [ipx::current_core]
ipx::save_core [ipx::current_core]
ipx::unload_core ./build/ap_fifo_r/component.xml
close_project

exit