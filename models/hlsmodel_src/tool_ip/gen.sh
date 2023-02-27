# No need to parallel since all of the sources are small, and generating these ip is fast compare to nn ip
vivado -mode tcl -source gen_bram_mux.tcl -nojournal -log ../build_bram_mux.log
vivado -mode tcl -source gen_gpio_connection.tcl -nojournal -log ../build_gpio_connection.log
vivado -mode tcl -source gen_sync_fifo_controller.tcl -nojournal -log ../build_sync_fifo_controller.log
