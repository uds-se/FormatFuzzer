# FormatFuzzer

`FormatFuzzer` is a framework for producing efficient generators and parsers for various binary file formats.
`FormatFuzzer` works as a python compiler for 010Editor [binary templates](https://www.sweetscape.com/010editor/templates.html), implemented on top of [pfp](https://github.com/d0c-s4vage/pfp).
`FormatFuzzer` compiles binary templates into C++ code that can be used for generating (or parsing) files that that conform to the template specification.

The generator receives as an input the source of randomness used for taking random decisions and produces as output a binary file in the appropriate format.
The parser takes as input the binary file and computes not only the parse tree of the target file, but also an appropriate source of random bytes that could be used by the generator to produce this exact file.

### Requirements

Tested on Linux (Ubuntu 20.04)

```
sudo apt install zlib1g-dev
```

### How to support new binary file formats

Run the compiler to compile the binary template into C++ code.
```
python3 create.py templates/PNG.bt PNG.cpp
```
Fix any issues that may prevent the python compiler from finishing by fixing bugs in the python compiler or modifying the original binary template for easier compilation.


After successfully generating the C++ code, try compiling the code.
```
g++ -g -O3 -Wall -c PNG.cpp
g++ -g -O3 -Wall -c generator.cpp
g++ -O3 PNG.o generator.o -o PNG-generator -lz
g++ -g -O3 -Wall -c parser.cpp
g++ -O3 PNG.o parser.o -o PNG-parser -lz
```
Fix any issues that may prevent the C++ code from compiling.

After the code compiles, try out running the generator.
```
./PNG-generator /dev/urandom output.png
```
The first argument to the generator is the file to read the source of randomness from and the second argument is the file where the output will be stored.

You can run the parser with:
```
./PNG-parser output.png rand
```
The first argument to the parser is the input file and the second argument is where to store the source of random bytes that could be used to generate this file.
By default, the parser computes the parse tree of the file according to the binary template.

If the files produced by the generator are still not valid, you can edit the C++ code to improve the generator until it successfully generates well-formated files with high probability.
The difference between the files `synthesized/PNG.bt` and `generators/PNG.bt` shows what changes were added to the PNG generator in order to produce valid files.

When initializing a variable, we can define a set of good known values that this variable can assume. For example, the constructor call
```
char_array_class cname(cname_element, { "IHDR", "tEXt", "PLTE", "cHRM", "sRGB", "iEXt", "zEXt", "tIME", "pHYs", "bKGD", "sBIT", "sPLT", "acTL", "fcTL", "fdAT", "IHDR", "IEND" });
```
would specify 17 good values to use for variable `cname`. But in the case of PNG, the choice of appropriate chunk types is context sensitive, so it is better to specify the set of good values at generation time when generating a new chunk.
For example, this call could be used to generate an instance of `chunk` for the first chunk, which must have type IHDR.
```
GENERATE(chunk, ::g->chunk.generate({ "IHDR" }, false));
```
When generating the second chunk, we might use this long list of possible chunks that can come between the IHDR chunk and the PLTE chunk:
```
GENERATE(chunk, ::g->chunk.generate({ "iCCP", "sRGB", "sBIT", "gAMA", "cHRM", "pHYs", "sPLT", "tIME", "zTXt", "tEXt", "iTXt", "eXIf", "oFFs", "pCAL", "sCAL", "acTL", "fcTL", "fdAT", "fRAc", "gIFg", "gIFt", "gIFx", "sTER" }, true));
```
The generator will then uniformly pick one of the good known values to use for the new instance. We also allow the choice of an evil value which is not one of the good known values with small probability 1/128.
This feature can be enabled or disabled any time by using the method `set_evil_bit`.

All the random choices taken by the generator are done by calling the `rand_int` method.
```
long long rand_int(unsigned long long x, std::function<long long (unsigned char*)> parse);
```
When running the program as a generator, this method samples an integer from 0 to x-1 by reading bytes from the random buffer.
When running the program as a parser, this method uses the `parse` function to find out which random bytes must be present in the random buffer in order to generate the target file, and then writes those bytes to the random buffer.
The `parse` function receives as an argument the buffer at the current position of the file and must then return which value would have to be returned by the current call to `rand_int` in order to generate this exact file configuration.

