create_project bram_mux ./build_bram_mux -part xc7z020clg400-2

add_files ./bram_mux.v

ipx::package_project -import_files ./bram_mux.v -root_dir ./build/bram_mux -name bram_mux -vendor h1msk.cc -library fpga_nn.hls -taxonomy /UserIP

set_property display_name {BRAM Mux} [ipx::current_core]

ipx::add_bus_interface P0 [ipx::current_core]
set_property interface_mode slave [ipx::get_bus_interfaces P0 -of_objects [ipx::current_core]]
set_property abstraction_type_vlnv xilinx.com:interface:bram_rtl:1.0 [ipx::get_bus_interfaces P0 -of_objects [ipx::current_core]]
set_property bus_type_vlnv xilinx.com:interface:bram:1.0 [ipx::get_bus_interfaces P0 -of_objects [ipx::current_core]]
ipx::add_port_map RST [ipx::get_bus_interfaces P0 -of_objects [ipx::current_core]]
set_property physical_name P0_Rst [ipx::get_port_maps RST -of_objects [ipx::get_bus_interfaces P0 -of_objects [ipx::current_core]]]
ipx::add_port_map CLK [ipx::get_bus_interfaces P0 -of_objects [ipx::current_core]]
set_property physical_name P0_Clk [ipx::get_port_maps CLK -of_objects [ipx::get_bus_interfaces P0 -of_objects [ipx::current_core]]]
ipx::add_port_map DIN [ipx::get_bus_interfaces P0 -of_objects [ipx::current_core]]
set_property physical_name P0_Din [ipx::get_port_maps DIN -of_objects [ipx::get_bus_interfaces P0 -of_objects [ipx::current_core]]]
ipx::add_port_map EN [ipx::get_bus_interfaces P0 -of_objects [ipx::current_core]]
set_property physical_name P0_EN [ipx::get_port_maps EN -of_objects [ipx::get_bus_interfaces P0 -of_objects [ipx::current_core]]]
ipx::add_port_map DOUT [ipx::get_bus_interfaces P0 -of_objects [ipx::current_core]]
set_property physical_name P0_Dout [ipx::get_port_maps DOUT -of_objects [ipx::get_bus_interfaces P0 -of_objects [ipx::current_core]]]
ipx::add_port_map WE [ipx::get_bus_interfaces P0 -of_objects [ipx::current_core]]
set_property physical_name P0_WEN [ipx::get_port_maps WE -of_objects [ipx::get_bus_interfaces P0 -of_objects [ipx::current_core]]]
ipx::add_port_map ADDR [ipx::get_bus_interfaces P0 -of_objects [ipx::current_core]]
set_property physical_name P0_Addr [ipx::get_port_maps ADDR -of_objects [ipx::get_bus_interfaces P0 -of_objects [ipx::current_core]]]

ipx::add_bus_interface P1 [ipx::current_core]
set_property interface_mode slave [ipx::get_bus_interfaces P1 -of_objects [ipx::current_core]]
set_property abstraction_type_vlnv xilinx.com:interface:bram_rtl:1.0 [ipx::get_bus_interfaces P1 -of_objects [ipx::current_core]]
set_property bus_type_vlnv xilinx.com:interface:bram:1.0 [ipx::get_bus_interfaces P1 -of_objects [ipx::current_core]]
ipx::add_port_map RST [ipx::get_bus_interfaces P1 -of_objects [ipx::current_core]]
set_property physical_name P1_Rst [ipx::get_port_maps RST -of_objects [ipx::get_bus_interfaces P1 -of_objects [ipx::current_core]]]
ipx::add_port_map CLK [ipx::get_bus_interfaces P1 -of_objects [ipx::current_core]]
set_property physical_name P1_Clk [ipx::get_port_maps CLK -of_objects [ipx::get_bus_interfaces P1 -of_objects [ipx::current_core]]]
ipx::add_port_map DIN [ipx::get_bus_interfaces P1 -of_objects [ipx::current_core]]
set_property physical_name P1_Din [ipx::get_port_maps DIN -of_objects [ipx::get_bus_interfaces P1 -of_objects [ipx::current_core]]]
ipx::add_port_map EN [ipx::get_bus_interfaces P1 -of_objects [ipx::current_core]]
set_property physical_name P1_EN [ipx::get_port_maps EN -of_objects [ipx::get_bus_interfaces P1 -of_objects [ipx::current_core]]]
ipx::add_port_map DOUT [ipx::get_bus_interfaces P1 -of_objects [ipx::current_core]]
set_property physical_name P1_Dout [ipx::get_port_maps DOUT -of_objects [ipx::get_bus_interfaces P1 -of_objects [ipx::current_core]]]
ipx::add_port_map WE [ipx::get_bus_interfaces P1 -of_objects [ipx::current_core]]
set_property physical_name P1_WEN [ipx::get_port_maps WE -of_objects [ipx::get_bus_interfaces P1 -of_objects [ipx::current_core]]]
ipx::add_port_map ADDR [ipx::get_bus_interfaces P1 -of_objects [ipx::current_core]]
set_property physical_name P1_Addr [ipx::get_port_maps ADDR -of_objects [ipx::get_bus_interfaces P1 -of_objects [ipx::current_core]]]

ipx::add_bus_interface O [ipx::current_core]
set_property interface_mode master [ipx::get_bus_interfaces O -of_objects [ipx::current_core]]
set_property abstraction_type_vlnv xilinx.com:interface:bram_rtl:1.0 [ipx::get_bus_interfaces O -of_objects [ipx::current_core]]
set_property bus_type_vlnv xilinx.com:interface:bram:1.0 [ipx::get_bus_interfaces O -of_objects [ipx::current_core]]
ipx::add_port_map RST [ipx::get_bus_interfaces O -of_objects [ipx::current_core]]
set_property physical_name O_Rst [ipx::get_port_maps RST -of_objects [ipx::get_bus_interfaces O -of_objects [ipx::current_core]]]
ipx::add_port_map CLK [ipx::get_bus_interfaces O -of_objects [ipx::current_core]]
set_property physical_name O_Clk [ipx::get_port_maps CLK -of_objects [ipx::get_bus_interfaces O -of_objects [ipx::current_core]]]
ipx::add_port_map DIN [ipx::get_bus_interfaces O -of_objects [ipx::current_core]]
set_property physical_name O_Din [ipx::get_port_maps DIN -of_objects [ipx::get_bus_interfaces O -of_objects [ipx::current_core]]]
ipx::add_port_map EN [ipx::get_bus_interfaces O -of_objects [ipx::current_core]]
set_property physical_name O_EN [ipx::get_port_maps EN -of_objects [ipx::get_bus_interfaces O -of_objects [ipx::current_core]]]
ipx::add_port_map DOUT [ipx::get_bus_interfaces O -of_objects [ipx::current_core]]
set_property physical_name O_Dout [ipx::get_port_maps DOUT -of_objects [ipx::get_bus_interfaces O -of_objects [ipx::current_core]]]
ipx::add_port_map WE [ipx::get_bus_interfaces O -of_objects [ipx::current_core]]
set_property physical_name O_WEN [ipx::get_port_maps WE -of_objects [ipx::get_bus_interfaces O -of_objects [ipx::current_core]]]
ipx::add_port_map ADDR [ipx::get_bus_interfaces O -of_objects [ipx::current_core]]
set_property physical_name O_Addr [ipx::get_port_maps ADDR -of_objects [ipx::get_bus_interfaces O -of_objects [ipx::current_core]]]

ipx::create_xgui_files [ipx::current_core]
ipx::update_checksums [ipx::current_core]
ipx::check_integrity [ipx::current_core]
ipx::save_core [ipx::current_core]
ipx::unload_core ./build/bram_mux/component.xml
close_project

exit