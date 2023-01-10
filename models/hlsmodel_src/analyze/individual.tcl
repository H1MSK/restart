# Linear<376, 64> forward
open_project generated_linear_376_64_forward
open_solution -flow_target vivado sol
add_files -cflags "-DNodeType=Linear<376,64>" ../top_pg.cpp
create_clock -period 500MHz
set_part xc7z020-clg400-2
set_top top_forward_p

csynth_design
export_design -format ip_catalog -ipname linear_376_64_forward


# Linear<376, 64> backward
open_project generated_linear_376_64_backward
open_solution -flow_target vivado sol
add_files -cflags "-DNodeType=Linear<376,64>" ../top_pg.cpp
create_clock -period 500MHz
set_part xc7z020-clg400-2
set_top top_backward_p

csynth_design
export_design -format ip_catalog -ipname linear_376_64_backward


# Linear<64, 64> forward
open_project generated_linear_64_64_forward
open_solution -flow_target vivado sol
add_files -cflags "-DNodeType=Linear<64,64>" ../top_pg.cpp
create_clock -period 500MHz
set_part xc7z020-clg400-2
set_top top_forward_p

csynth_design
export_design -format ip_catalog -ipname linear_64_64_forward


# Linear<64, 64> backward
open_project generated_linear_64_64_backward
open_solution -flow_target vivado sol
add_files -cflags "-DNodeType=Linear<64,64>" ../top_pg.cpp
create_clock -period 500MHz
set_part xc7z020-clg400-2
set_top top_backward_p

csynth_design
export_design -format ip_catalog -ipname linear_64_64_backward


# Linear<64, 17> forward
open_project generated_linear_64_17_forward
open_solution -flow_target vivado sol
add_files -cflags "-DNodeType=Linear<64,17>" ../top_pg.cpp
create_clock -period 500MHz
set_part xc7z020-clg400-2
set_top top_forward_p

csynth_design
export_design -format ip_catalog -ipname linear_64_17_forward


# Linear<64, 17> backward
open_project generated_linear_64_17_backward
open_solution -flow_target vivado sol
add_files -cflags "-DNodeType=Linear<64,17>" ../top_pg.cpp
create_clock -period 500MHz
set_part xc7z020-clg400-2
set_top top_backward_p

csynth_design
export_design -format ip_catalog -ipname linear_64_17_backward


# Tanh<64> forward
open_project generated_tanh_64_forward
open_solution -flow_target vivado sol
add_files -cflags "-DNodeType=Tanh<64>" ../top_g.cpp
create_clock -period 500MHz
set_part xc7z020-clg400-2
set_top top_forward

csynth_design
export_design -format ip_catalog -ipname tanh_64_forward


# Tanh<64> backward
open_project generated_tanh_64_backward
open_solution -flow_target vivado sol
add_files -cflags "-DNodeType=Tanh<64>" ../top_g.cpp
create_clock -period 500MHz
set_part xc7z020-clg400-2
set_top top_backward

csynth_design
export_design -format ip_catalog -ipname tanh_64_backward


# Exp<17> forward
open_project generated_exp_17_forward
open_solution -flow_target vivado sol
add_files -cflags "-DNodeType=Exp<17>" ../top_g.cpp
create_clock -period 500MHz
set_part xc7z020-clg400-2
set_top top_forward

csynth_design
export_design -format ip_catalog -ipname exp_17_forward


# Exp<17> backward
open_project generated_exp_17_backward
open_solution -flow_target vivado sol
add_files -cflags "-DNodeType=Exp<17>" ../top_g.cpp
create_clock -period 500MHz
set_part xc7z020-clg400-2
set_top top_backward

csynth_design
export_design -format ip_catalog -ipname exp_17_backward
