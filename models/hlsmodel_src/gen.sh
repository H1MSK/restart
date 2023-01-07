echo -e "\033[32mGenerating top function, tcl and directives...\033[0m"
python generator generated.top.cpp generated.top_build.tcl generated.top_directives.tcl

echo -e "\033[32mSynthesis IP to be used in system...\033[0m"
echo -e "\033[32mThis will take some time...\033[0m"
sleep 1s
vitis_hls generated.top_build.tcl
