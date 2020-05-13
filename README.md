# pfpg

`pfpg` is a python compiler for 010 binary templates, implemented on top of [pfp](https://github.com/d0c-s4vage/pfp).
`pfpg` compiles binary templates into C++ code that can be used for generating (or parsing) files that that conform to the template specification.



### Usage

```python3 create.py PNG.bt 2>png-generator.cpp
```

```g++ -g -O3 -Wall png-generator.cpp -o png-generator
./png-generator output.png
```
