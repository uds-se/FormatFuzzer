#!/bin/bash

./ffcompile templates/$1.bt $1.cpp
g++ -c -I . -std=c++17 -g -O3 -Wall fuzzer.cpp
g++ -c -I . -std=c++17 -g -O3 -Wall $1.cpp
g++ -O3 $1.o fuzzer.o -o $1-fuzzer -lz
