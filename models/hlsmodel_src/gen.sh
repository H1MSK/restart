echo -e "\033[32mGenerating functions, tcls and directives for NN...\033[0m"
python generator

echo -e "\033[32mGenerating IPs to be used in system...\033[0m"
echo -e "\033[32mThis will take some time...\033[0m"
echo -e "\033[32mThe output will seem to be messy since there are several jobs outputing to the console simultaneously.\033[0m"
echo -e "\033[32mPlease refer to build_*.log to check each output.\033[0m"
sleep 1s
vitis_hls generated.nn.tcl -l build_nn.log &
vitis_hls generated.data_io.tcl -l build_data_io.log &
cd tool_ip && ./gen.sh && cd .. &
wait

echo -e "\033[32mGenerating system...\033[0m"
echo -e "\033[32mThis will take some time...\033[0m"
vivado -mode tcl -source generated.system.tcl
echo -e "\033[32mFinished!\033[0m"
