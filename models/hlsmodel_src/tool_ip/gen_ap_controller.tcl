create_project ap_controller ./build_ap_controller -part xc7z020clg400-2

add_files ./ap_controller.v

ipx::package_project -import_files ./ap_controller.v -root_dir ./build/ap_controller -name ap_controller -vendor h1msk.cc -library fpga_nn.hls -taxonomy /UserIP

set_property display_name {AP Controller} [ipx::current_core]

ipx::infer_bus_interfaces xilinx.com:signal:clock_rtl:1.0 [ipx::current_core]
ipx::infer_bus_interfaces xilinx.com:signal:reset_rtl:1.0 [ipx::current_core]
ipx::add_bus_interface ap_ctrl [ipx::current_core]
set_property abstraction_type_vlnv xilinx.com:interface:acc_handshake_rtl:1.0 [ipx::get_bus_interfaces ap_ctrl -of_objects [ipx::current_core]]
set_property bus_type_vlnv xilinx.com:interface:acc_handshake:1.0 [ipx::get_bus_interfaces ap_ctrl -of_objects [ipx::current_core]]
set_property interface_mode master [ipx::get_bus_interfaces ap_ctrl -of_objects [ipx::current_core]]
ipx::add_port_map ap_start [ipx::get_bus_interfaces ap_ctrl -of_objects [ipx::current_core]]
set_property physical_name ap_start [ipx::get_port_maps ap_start -of_objects [ipx::get_bus_interfaces ap_ctrl -of_objects [ipx::current_core]]]
ipx::add_port_map ap_idle [ipx::get_bus_interfaces ap_ctrl -of_objects [ipx::current_core]]
set_property physical_name ap_idle [ipx::get_port_maps ap_idle -of_objects [ipx::get_bus_interfaces ap_ctrl -of_objects [ipx::current_core]]]
ipx::add_port_map ap_ready [ipx::get_bus_interfaces ap_ctrl -of_objects [ipx::current_core]]
set_property physical_name ap_ready [ipx::get_port_maps ap_ready -of_objects [ipx::get_bus_interfaces ap_ctrl -of_objects [ipx::current_core]]]
ipx::add_port_map ap_done [ipx::get_bus_interfaces ap_ctrl -of_objects [ipx::current_core]]
set_property physical_name ap_done [ipx::get_port_maps ap_done -of_objects [ipx::get_bus_interfaces ap_ctrl -of_objects [ipx::current_core]]]

ipx::merge_project_changes ports [ipx::current_core]

ipx::create_xgui_files [ipx::current_core]
ipx::update_checksums [ipx::current_core]
ipx::check_integrity [ipx::current_core]
ipx::save_core [ipx::current_core]
ipx::unload_core ./build/ap_controller/component.xml

close_project

exit
