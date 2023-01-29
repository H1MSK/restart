create_project sync_fifo_controller ./build_sync_fifo_controller -part xc7z020clg400-2

add_files ./sync_fifo_controller.v

ipx::package_project -import_files ./sync_fifo_controller.v -root_dir ./build/sync_fifo_controller -name sync_fifo_controller -vendor h1msk.cc -library fpga_nn.hls -taxonomy /UserIP

set_property display_name {Sync FIFO Controller} [ipx::current_core]

ipx::add_bus_interface FIFO_READ [ipx::current_core]
set_property abstraction_type_vlnv xilinx.com:interface:fifo_read_rtl:1.0 [ipx::get_bus_interfaces FIFO_READ -of_objects [ipx::current_core]]
set_property bus_type_vlnv xilinx.com:interface:fifo_read:1.0 [ipx::get_bus_interfaces FIFO_READ -of_objects [ipx::current_core]]
ipx::add_port_map RD_DATA [ipx::get_bus_interfaces FIFO_READ -of_objects [ipx::current_core]]
set_property physical_name fifo_rd_data [ipx::get_port_maps RD_DATA -of_objects [ipx::get_bus_interfaces FIFO_READ -of_objects [ipx::current_core]]]
ipx::add_port_map RD_EN [ipx::get_bus_interfaces FIFO_READ -of_objects [ipx::current_core]]
set_property physical_name fifo_rd_en [ipx::get_port_maps RD_EN -of_objects [ipx::get_bus_interfaces FIFO_READ -of_objects [ipx::current_core]]]
ipx::add_port_map EMPTY [ipx::get_bus_interfaces FIFO_READ -of_objects [ipx::current_core]]
set_property physical_name fifo_empty [ipx::get_port_maps EMPTY -of_objects [ipx::get_bus_interfaces FIFO_READ -of_objects [ipx::current_core]]]

ipx::add_bus_interface FIFO_WRITE [ipx::current_core]
set_property abstraction_type_vlnv xilinx.com:interface:fifo_write_rtl:1.0 [ipx::get_bus_interfaces FIFO_WRITE -of_objects [ipx::current_core]]
set_property bus_type_vlnv xilinx.com:interface:fifo_write:1.0 [ipx::get_bus_interfaces FIFO_WRITE -of_objects [ipx::current_core]]
ipx::add_port_map WR_DATA [ipx::get_bus_interfaces FIFO_WRITE -of_objects [ipx::current_core]]
set_property physical_name fifo_wr_data [ipx::get_port_maps WR_DATA -of_objects [ipx::get_bus_interfaces FIFO_WRITE -of_objects [ipx::current_core]]]
ipx::add_port_map WR_EN [ipx::get_bus_interfaces FIFO_WRITE -of_objects [ipx::current_core]]
set_property physical_name fifo_wr_en [ipx::get_port_maps WR_EN -of_objects [ipx::get_bus_interfaces FIFO_WRITE -of_objects [ipx::current_core]]]
ipx::add_port_map FULL [ipx::get_bus_interfaces FIFO_WRITE -of_objects [ipx::current_core]]
set_property physical_name fifo_full [ipx::get_port_maps FULL -of_objects [ipx::get_bus_interfaces FIFO_WRITE -of_objects [ipx::current_core]]]

ipx::add_bus_interface BRAM_PORT_R [ipx::current_core]
set_property abstraction_type_vlnv xilinx.com:interface:bram_rtl:1.0 [ipx::get_bus_interfaces BRAM_PORT_R -of_objects [ipx::current_core]]
set_property bus_type_vlnv xilinx.com:interface:bram:1.0 [ipx::get_bus_interfaces BRAM_PORT_R -of_objects [ipx::current_core]]
set_property interface_mode master [ipx::get_bus_interfaces BRAM_PORT_R -of_objects [ipx::current_core]]
ipx::add_port_map DIN [ipx::get_bus_interfaces BRAM_PORT_R -of_objects [ipx::current_core]]
set_property physical_name bram_dina [ipx::get_port_maps DIN -of_objects [ipx::get_bus_interfaces BRAM_PORT_R -of_objects [ipx::current_core]]]
ipx::add_port_map EN [ipx::get_bus_interfaces BRAM_PORT_R -of_objects [ipx::current_core]]
set_property physical_name bram_ena [ipx::get_port_maps EN -of_objects [ipx::get_bus_interfaces BRAM_PORT_R -of_objects [ipx::current_core]]]
ipx::add_port_map RST [ipx::get_bus_interfaces BRAM_PORT_R -of_objects [ipx::current_core]]
set_property physical_name bram_rsta [ipx::get_port_maps RST -of_objects [ipx::get_bus_interfaces BRAM_PORT_R -of_objects [ipx::current_core]]]
ipx::add_port_map CLK [ipx::get_bus_interfaces BRAM_PORT_R -of_objects [ipx::current_core]]
set_property physical_name bram_clka [ipx::get_port_maps CLK -of_objects [ipx::get_bus_interfaces BRAM_PORT_R -of_objects [ipx::current_core]]]
ipx::add_port_map WE [ipx::get_bus_interfaces BRAM_PORT_R -of_objects [ipx::current_core]]
set_property physical_name bram_wea [ipx::get_port_maps WE -of_objects [ipx::get_bus_interfaces BRAM_PORT_R -of_objects [ipx::current_core]]]
ipx::add_port_map ADDR [ipx::get_bus_interfaces BRAM_PORT_R -of_objects [ipx::current_core]]
set_property physical_name bram_addra [ipx::get_port_maps ADDR -of_objects [ipx::get_bus_interfaces BRAM_PORT_R -of_objects [ipx::current_core]]]

ipx::add_bus_interface BRAM_PORT_W [ipx::current_core]
set_property abstraction_type_vlnv xilinx.com:interface:bram_rtl:1.0 [ipx::get_bus_interfaces BRAM_PORT_W -of_objects [ipx::current_core]]
set_property bus_type_vlnv xilinx.com:interface:bram:1.0 [ipx::get_bus_interfaces BRAM_PORT_W -of_objects [ipx::current_core]]
set_property interface_mode master [ipx::get_bus_interfaces BRAM_PORT_W -of_objects [ipx::current_core]]
ipx::add_port_map EN [ipx::get_bus_interfaces BRAM_PORT_W -of_objects [ipx::current_core]]
set_property physical_name bram_enb [ipx::get_port_maps EN -of_objects [ipx::get_bus_interfaces BRAM_PORT_W -of_objects [ipx::current_core]]]
ipx::add_port_map DOUT [ipx::get_bus_interfaces BRAM_PORT_W -of_objects [ipx::current_core]]
set_property physical_name bram_doutb [ipx::get_port_maps DOUT -of_objects [ipx::get_bus_interfaces BRAM_PORT_W -of_objects [ipx::current_core]]]
ipx::add_port_map RST [ipx::get_bus_interfaces BRAM_PORT_W -of_objects [ipx::current_core]]
set_property physical_name bram_rstb [ipx::get_port_maps RST -of_objects [ipx::get_bus_interfaces BRAM_PORT_W -of_objects [ipx::current_core]]]
ipx::add_port_map CLK [ipx::get_bus_interfaces BRAM_PORT_W -of_objects [ipx::current_core]]
set_property physical_name bram_clkb [ipx::get_port_maps CLK -of_objects [ipx::get_bus_interfaces BRAM_PORT_W -of_objects [ipx::current_core]]]
ipx::add_port_map ADDR [ipx::get_bus_interfaces BRAM_PORT_W -of_objects [ipx::current_core]]
set_property physical_name bram_addrb [ipx::get_port_maps ADDR -of_objects [ipx::get_bus_interfaces BRAM_PORT_W -of_objects [ipx::current_core]]]

set_property value ACTIVE_HIGH [ipx::get_bus_parameters POLARITY -of_objects [ipx::get_bus_interfaces reset -of_objects [ipx::current_core]]]

ipx::create_xgui_files [ipx::current_core]
ipx::update_checksums [ipx::current_core]
ipx::check_integrity [ipx::current_core]
ipx::save_core [ipx::current_core]
ipx::unload_core ./build/sync_fifo_controller/component.xml

close_project

exit
