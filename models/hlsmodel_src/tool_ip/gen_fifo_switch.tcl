create_project fifo_switch ./build_fifo_switch -part xc7z020clg400-2

add_files ./fifo_switch.v

ipx::package_project -import_files ./fifo_switch.v -root_dir ./build/fifo_switch -name fifo_switch -vendor h1msk.cc -library fpga_nn.hls -taxonomy /UserIP

set_property display_name {FIFO Switch} [ipx::current_core]

ipx::add_bus_interface fifo_i [ipx::current_core]
set_property abstraction_type_vlnv xilinx.com:interface:acc_fifo_write_rtl:1.0 [ipx::get_bus_interfaces fifo_i -of_objects [ipx::current_core]]
set_property bus_type_vlnv xilinx.com:interface:acc_fifo_write:1.0 [ipx::get_bus_interfaces fifo_i -of_objects [ipx::current_core]]
ipx::add_port_map WR_DATA [ipx::get_bus_interfaces fifo_i -of_objects [ipx::current_core]]
set_property physical_name fifo_i_din [ipx::get_port_maps WR_DATA -of_objects [ipx::get_bus_interfaces fifo_i -of_objects [ipx::current_core]]]
ipx::add_port_map WR_EN [ipx::get_bus_interfaces fifo_i -of_objects [ipx::current_core]]
set_property physical_name fifo_i_write [ipx::get_port_maps WR_EN -of_objects [ipx::get_bus_interfaces fifo_i -of_objects [ipx::current_core]]]
ipx::add_port_map FULL_N [ipx::get_bus_interfaces fifo_i -of_objects [ipx::current_core]]
set_property physical_name fifo_i_full_n [ipx::get_port_maps FULL_N -of_objects [ipx::get_bus_interfaces fifo_i -of_objects [ipx::current_core]]]

ipx::add_bus_interface fifo_o [ipx::current_core]
set_property abstraction_type_vlnv xilinx.com:interface:acc_fifo_write_rtl:1.0 [ipx::get_bus_interfaces fifo_o -of_objects [ipx::current_core]]
set_property bus_type_vlnv xilinx.com:interface:acc_fifo_write:1.0 [ipx::get_bus_interfaces fifo_o -of_objects [ipx::current_core]]
set_property interface_mode master [ipx::get_bus_interfaces fifo_o -of_objects [ipx::current_core]]
ipx::add_port_map WR_DATA [ipx::get_bus_interfaces fifo_o -of_objects [ipx::current_core]]
set_property physical_name fifo_o_din [ipx::get_port_maps WR_DATA -of_objects [ipx::get_bus_interfaces fifo_o -of_objects [ipx::current_core]]]
ipx::add_port_map WR_EN [ipx::get_bus_interfaces fifo_o -of_objects [ipx::current_core]]
set_property physical_name fifo_o_write [ipx::get_port_maps WR_EN -of_objects [ipx::get_bus_interfaces fifo_o -of_objects [ipx::current_core]]]
ipx::add_port_map FULL_N [ipx::get_bus_interfaces fifo_o -of_objects [ipx::current_core]]
set_property physical_name fifo_o_full_n [ipx::get_port_maps FULL_N -of_objects [ipx::get_bus_interfaces fifo_o -of_objects [ipx::current_core]]]

ipx::create_xgui_files [ipx::current_core]
ipx::update_checksums [ipx::current_core]
ipx::check_integrity [ipx::current_core]
ipx::save_core [ipx::current_core]
ipx::unload_core ./build/fifo_switch/component.xml

close_project

exit
