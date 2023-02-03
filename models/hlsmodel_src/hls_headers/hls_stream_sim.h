#pragma once
#include <deque>

namespace hls
{

template<typename Type, int depth = 0>
class stream;

template<typename Type, int depth>
class stream : public stream<Type, 0> {
 public:
    stream() = default;
    stream(const stream<Type, depth>& oth) = default;
    stream(stream<Type, depth>&& oth) = default;
};

template<typename Type>
class stream<Type, 0> {
 public:
    stream() = default;
    stream(const stream<Type, 0>& oth) = default;
    stream(stream<Type, 0>&& oth) = default;

    Type read() {
        Type x = data.front();
        data.pop_front();
        return x;
    }

    void write(Type x) {
        data.push_back(x);
    }

    void operator << (Type x) { write(x); }

 private:
    std::deque<Type> data;
};

} // namespace hls
