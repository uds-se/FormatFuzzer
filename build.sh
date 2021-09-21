#!/bin/bash

# Produce format-specific C++ code
./ffcompile templates/$1.bt $1.cpp
git checkout -- png.cpp

# Build format-specific executable
g++ -c -I . -std=c++17 -g -O3 -Wall fuzzer.cpp
g++ -c -I . -std=c++17 -g -O3 -Wall $1.cpp
g++ -O3 $1.o fuzzer.o -o $1-fuzzer -lz

# Build format-specific shared library
g++ -I . -std=c++17 -g -O3 -Wall -shared -fPIC $1.cpp fuzzer.cpp -o $1.so -lz
