#include "test.hpp"

int main() {
    srand(time(0));
    test<Exp<32>, hlsnn::Exp<32> >();
}
