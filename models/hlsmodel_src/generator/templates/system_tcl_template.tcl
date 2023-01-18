create_project test ./test -part xc7z020clg400-2
set_property  ip_repo_paths  . [current_project]
update_ip_catalog
create_ip -name forward -vendor xilinx.com -library hls -version 1.0 -module_name nn_forward
create_ip -name backward -vendor xilinx.com -library hls -version 1.0 -module_name nn_backward

$mems

$fifos

$connections
