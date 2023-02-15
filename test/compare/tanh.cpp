#include "test.hpp"

int main() {
    srand(time(0));
    test<Tanh<32>, hlsnn::Tanh<32> >();
}
