set -e
g++ -o linear linear.cpp -g -I ../../models/hlsmodel_src/hls_headers/ -std=c++1z && echo "Linear compiled." && ./linear && sleep 1s && ./linear && sleep 1s && ./linear && echo "Linear done." && rm ./linear &
g++ -o tanh tanh.cpp -g -I ../../models/hlsmodel_src/hls_headers/ -std=c++1z && echo "Tanh compiled." && ./tanh && sleep 1s && ./tanh && sleep 1s && ./tanh && echo "Tanh done." && rm ./tanh &
g++ -o exp exp.cpp -g -I ../../models/hlsmodel_src/hls_headers/ -std=c++1z && echo "exp compiled." && ./exp && sleep 1s && ./exp && sleep 1s && ./exp && echo "exp done." && rm ./exp &
wait

echo "All done."
