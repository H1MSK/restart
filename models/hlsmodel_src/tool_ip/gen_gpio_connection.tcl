create_project gpio_connection ./build_gpio_connection -part xc7z020clg400-2

add_files ./gpio_connection.v

ipx::package_project -import_files ./gpio_connection.v -root_dir ./build/gpio_connection -name gpio_connection -vendor h1msk.cc -library fpga_nn.hls -taxonomy /UserIP

set_property display_name {GPIO Gonnection} [ipx::current_core]

ipx::create_xgui_files [ipx::current_core]
ipx::update_checksums [ipx::current_core]
ipx::check_integrity [ipx::current_core]
ipx::save_core [ipx::current_core]
ipx::unload_core ./build/gpio_connection/component.xml

close_project

exit
