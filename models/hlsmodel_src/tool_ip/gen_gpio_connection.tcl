create_project gpio_connection ./build_gpio_connection -part xc7z020clg400-2

add_files ./gpio_connection.v

ipx::package_project -import_files ./gpio_connection.v -root_dir ./build/gpio_connection -name gpio_connection -vendor h1msk.cc -library fpga_nn.hls -taxonomy /UserIP

set_property display_name {GPIO Gonnection} [ipx::current_core]

ipx::remove_bus_interface grad_reset [ipx::current_core]
ipx::remove_bus_interface param_reset [ipx::current_core]

ipx::add_bus_interface GPIO [ipx::current_core]
set_property abstraction_type_vlnv xilinx.com:interface:gpio_rtl:1.0 [ipx::get_bus_interfaces GPIO -of_objects [ipx::current_core]]
set_property bus_type_vlnv xilinx.com:interface:gpio:1.0 [ipx::get_bus_interfaces GPIO -of_objects [ipx::current_core]]
set_property interface_mode mirroredMaster [ipx::get_bus_interfaces GPIO -of_objects [ipx::current_core]]
ipx::add_port_map TRI_O [ipx::get_bus_interfaces GPIO -of_objects [ipx::current_core]]
set_property physical_name GPIO_O [ipx::get_port_maps TRI_O -of_objects [ipx::get_bus_interfaces GPIO -of_objects [ipx::current_core]]]
ipx::add_port_map TRI_T [ipx::get_bus_interfaces GPIO -of_objects [ipx::current_core]]
set_property physical_name GPIO_T [ipx::get_port_maps TRI_T -of_objects [ipx::get_bus_interfaces GPIO -of_objects [ipx::current_core]]]
ipx::add_port_map TRI_I [ipx::get_bus_interfaces GPIO -of_objects [ipx::current_core]]
set_property physical_name GPIO_I [ipx::get_port_maps TRI_I -of_objects [ipx::get_bus_interfaces GPIO -of_objects [ipx::current_core]]]

ipx::add_bus_parameter POLARITY [ipx::get_bus_interfaces system_reset -of_objects [ipx::current_core]]
set_property value ACTIVE_HIGH [ipx::get_bus_parameters POLARITY -of_objects [ipx::get_bus_interfaces system_reset -of_objects [ipx::current_core]]]

ipx::create_xgui_files [ipx::current_core]
ipx::update_checksums [ipx::current_core]
ipx::check_integrity [ipx::current_core]
ipx::save_core [ipx::current_core]
ipx::unload_core ./build/gpio_connection/component.xml

close_project

exit
