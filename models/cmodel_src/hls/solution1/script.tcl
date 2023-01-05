############################################################
## This file is generated automatically by Vitis HLS.
## Please DO NOT edit it.
## Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
############################################################
open_project hls
set_top unitop
add_files unitop.cpp
open_solution "solution1" -flow_target vivado
set_part {xc7z020-clg400-2}
create_clock -period 500MHz -name default
source "./hls/solution1/directives.tcl"
#csim_design
csynth_design
#cosim_design
export_design -format ip_catalog
