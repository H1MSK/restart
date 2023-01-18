create_project test ./test -part xc7z020clg400-2
set_property  ip_repo_paths  . [current_project]
update_ip_catalog
create_ip -name forward -vendor xilinx.com -library hls -version 1.0 -module_name nn_forward
create_ip -name backward -vendor xilinx.com -library hls -version 1.0 -module_name nn_backward

create_ip -name blk_mem_gen -vendor xilinx.com -library ip -version 8.4 -module_name mem_param1
set_property -dict [list CONFIG.Component_Name {mem_param1} CONFIG.Memory_Type {True_Dual_Port_RAM} CONFIG.Enable_32bit_Address {true} CONFIG.Use_Byte_Write_Enable {true} CONFIG.Byte_Size {8} CONFIG.Assume_Synchronous_Clk {true} CONFIG.Write_Width_A {32} CONFIG.Write_Depth_A {24128} CONFIG.Read_Width_A {32} CONFIG.Operating_Mode_A {WRITE_FIRST} CONFIG.Write_Width_B {32} CONFIG.Read_Width_B {32} CONFIG.Enable_B {Use_ENB_Pin} CONFIG.Register_PortA_Output_of_Memory_Primitives {false} CONFIG.Register_PortB_Output_of_Memory_Primitives {false} CONFIG.Use_RSTA_Pin {true} CONFIG.Use_RSTB_Pin {false} CONFIG.Port_B_Clock {100} CONFIG.Port_B_Write_Rate {50} CONFIG.Port_B_Enable_Rate {100} CONFIG.EN_SAFETY_CKT {true}] [get_ips mem_param1]


create_ip -name fifo_generator -vendor xilinx.com -library ip -version 13.2 -module_name fifo_cache1
set_property -dict [list CONFIG.Component_Name {fifo_cache1} CONFIG.Performance_Options {Standard_FIFO} CONFIG.Input_Data_Width {32} CONFIG.Input_Depth {32768} CONFIG.Output_Data_Width {32} CONFIG.Output_Depth {32768} CONFIG.Use_Extra_Logic {false} CONFIG.Data_Count_Width {15} CONFIG.Write_Data_Count_Width {15} CONFIG.Read_Data_Count_Width {15} CONFIG.Full_Threshold_Assert_Value {32766} CONFIG.Full_Threshold_Negate_Value {32765} CONFIG.Empty_Threshold_Assert_Value {2} CONFIG.Empty_Threshold_Negate_Value {3}] [get_ips fifo_cache1]
