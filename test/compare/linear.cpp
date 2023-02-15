#include "test.hpp"

int main() {
    srand(time(0));
    test<Linear<32, 64>, hlsnn::Linear<32, 64>>();
}
