# pfpg

`pfpg` is a python compiler for 010 binary templates, implemented on top of [pfp](https://github.com/d0c-s4vage/pfp).
`pfpg` compiles binary templates into C++ code that can be used for generating (or parsing) files that that conform to the template specification.


### Requirements

Supported Operating System : Linux (tested on Ubuntu 20.04)

```
sudo apt install libboost1.71-dev
```

### How to support new binary file formats

Run the compiler to compile the binary template into C++ code.
```
python3 create.py PNG.bt png-generator.cpp
```
Fix any issues that may prevent the python compiler from finishing by fixing bugs in the python compiler or modifying the original binary template for easier compilation.


After successfully generating the C++ code, try compiling the code.
```
g++ -g -O3 -Wall png-generator.cpp -o png-generator -lz
```
Fix any issues that may prevent the C++ code from compiling.

After the code compiles, try out running the generator.
```
./png-generator output.png
```
You can edit the C++ code to improve the generator until it successfully generates well-formated files with high probability.
