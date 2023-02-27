create_project bram_mux ./build_bram_mux -part xc7z020clg400-2

add_files ./bram_mux.v

ipx::package_project -import_files ./bram_mux.v -root_dir ./build/bram_mux -name bram_mux -vendor h1msk.cc -library fpga_nn.hls -taxonomy /UserIP

set_property display_name {BRAM Mux} [ipx::current_core]

ipx::create_xgui_files [ipx::current_core]
ipx::update_checksums [ipx::current_core]
ipx::check_integrity [ipx::current_core]
ipx::save_core [ipx::current_core]
ipx::unload_core ./build/bram_mux/component.xml
close_project

exit