set -e

rm -rf build_grad_extractor/ build_forward/ build_backward/ build_param_loader/

cd tool_ip/
./clean.sh

cd ..
./gen.sh
