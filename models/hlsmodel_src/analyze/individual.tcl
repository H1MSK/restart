open_project build
exec mkdir -p ip

# Linear<376, 64> forward
open_solution -flow_target vivado sol_linear376_64_f
add_files -cflags "-DNodeType=Linear<376,64>" ../top_pg.cpp
create_clock -period 500MHz
set_part xc7z020-clg400-2
set_top top_forward_p

csynth_design


# Linear<376, 64> backward
open_solution -flow_target vivado sol_linear376_64_b
add_files -cflags "-DNodeType=Linear<376,64>" ../top_pg.cpp
create_clock -period 500MHz
set_part xc7z020-clg400-2
set_top top_backward_p

csynth_design


# Linear<64, 64> forward
open_solution -flow_target vivado sol_linear64_64_f
add_files -cflags "-DNodeType=Linear<64,64>" ../top_pg.cpp
create_clock -period 500MHz
set_part xc7z020-clg400-2
set_top top_forward_p

csynth_design


# Linear<64, 64> backward
open_solution -flow_target vivado sol_linear64_64_b
add_files -cflags "-DNodeType=Linear<64,64>" ../top_pg.cpp
create_clock -period 500MHz
set_part xc7z020-clg400-2
set_top top_backward_p

csynth_design


# Linear<64, 17> forward
open_solution -flow_target vivado sol_linear64_17_f
add_files -cflags "-DNodeType=Linear<64,17>" ../top_pg.cpp
create_clock -period 500MHz
set_part xc7z020-clg400-2
set_top top_forward_p

csynth_design


# Linear<64, 17> backward
open_solution -flow_target vivado sol_linear64_17_b
add_files -cflags "-DNodeType=Linear<64,17>" ../top_pg.cpp
create_clock -period 500MHz
set_part xc7z020-clg400-2
set_top top_backward_p

csynth_design


# Tanh<64> forward
open_solution -flow_target vivado sol_tanh64_f
add_files -cflags "-DNodeType=Tanh<64>" ../top_g.cpp
create_clock -period 500MHz
set_part xc7z020-clg400-2
set_top top_forward

csynth_design


# Tanh<64> backward
open_solution -flow_target vivado sol_tanh64_b
add_files -cflags "-DNodeType=Tanh<64>" ../top_g.cpp
create_clock -period 500MHz
set_part xc7z020-clg400-2
set_top top_backward

csynth_design


# Exp<17> forward
open_solution -flow_target vivado sol_exp17_f
add_files -cflags "-DNodeType=Exp<17>" ../top_g.cpp
create_clock -period 500MHz
set_part xc7z020-clg400-2
set_top top_forward

csynth_design


# Exp<17> backward
open_solution -flow_target vivado sol_exp17_b
add_files -cflags "-DNodeType=Exp<17>" ../top_g.cpp
create_clock -period 500MHz
set_part xc7z020-clg400-2
set_top top_backward

csynth_design
cp build/sol_exp17_b/impl/export.zip ./ip/exp17_b.zip