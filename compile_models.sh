mkdir -p models/build
cd models/build
cmake ../cmodel_src
make -j4
cd ../..
