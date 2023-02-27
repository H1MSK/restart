create_project sync_fifo_controller ./build_sync_fifo_controller -part xc7z020clg400-2

add_files ./sync_fifo_controller.v

ipx::package_project -import_files ./sync_fifo_controller.v -root_dir ./build/sync_fifo_controller -name sync_fifo_controller -vendor h1msk.cc -library fpga_nn.hls -taxonomy /UserIP

set_property display_name {Sync FIFO Controller} [ipx::current_core]

ipx::create_xgui_files [ipx::current_core]
ipx::update_checksums [ipx::current_core]
ipx::check_integrity [ipx::current_core]
ipx::save_core [ipx::current_core]
ipx::unload_core ./build/sync_fifo_controller/component.xml

close_project

exit
