echo -e "\033[32mGenerating functions, tcls and directives for NN...\033[0m"
python generator generated.nn.cpp generated.nn.tcl generated.fw_directives.tcl generated.bw_directives.tcl generated.data_io.cpp generated.data_io.tcl generated.system.tcl

echo -e "\033[32mGenerating IPs to be used in system...\033[0m"
echo -e "\033[32mThis will take some time...\033[0m"
echo -e "\033[32m(The output will seem to be messy since there are 4 jobs outputing to the\033[0m"
echo -e "\033[32m console simultaneously. Please refer to build_*.log to check each output)\033[0m"
sleep 1s
vitis_hls generated.nn.tcl -l build_nn.log &
vitis_hls generated.data_io.tcl -l build_data_io.log &
cd tool_ip && ./gen.sh && cd .. &
wait

vivado -mode tcl -source generated.system.tcl
