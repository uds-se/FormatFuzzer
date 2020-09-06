# FormatFuzzer

`FormatFuzzer` is a framework for *high-efficiency, high-quality generation and parsing of binary inputs.*
It takes a *binary template* that describes the format of a binary input and generates an *executable* that produces and parses the given binary format.
From a binary template for PNG, for instance, `FormatFuzzer` produces a PNG generator - also known as *PNG fuzzer*.
There are more than 170 binary templates available, which either can be used directly for `FormatFuzzer` or adapted with little effort.
The generator is highly efficient, producing thousands of files with test inputs per second.

## Installing

You need the following:
* Python 3
* A C++ compiler
* The Python packages `py010parser` and `intervaltree`
* A `zlib` library


### Installing Python packages

On all systems, using `pip`:
```
pip install py010parser
pip install intervaltree
```

### Installing zlib

You need a `zlib` library (`-lz`).

On Linux, using `apt`:
```
sudo apt install zlib1g-dev
```
On a Mac:
```
xcode-select --install
```

## Running

### Compiling Binary Template Files into C++ code

Run the compiler to compile the binary template into C++ code.
```
python3 create.py templates/PNG.bt PNG.cpp
```


TODO: I get
```
py010parser.plyparser.ParseError: /var/folders/n2/xd9445p97rb3xh7m1dfx8_4h0006ts/T/tmpay54rg_1:1:1: before: /
```
and thus used `synthesized/PNG.cpp` for the remaining steps.


### Compiling the C++ code

Use the following commands to create both a producer `PNG-generator` and a parser `PNG-parser`.

```
g++ -c -I . -std=c++11 -g -O3 -Wall PNG.cpp
g++ -c -I . -std=c++11 -g -O3 -Wall generator.cpp
g++ -O3 PNG.o generator.o -o PNG-generator -lz
g++ -c -I . -std=c++11 -g -O3 -Wall parser.cpp
g++ -O3 PNG.o parser.o -o PNG-parser -lz
```
(`-I .` denotes the location of the `bt.h` file; `-std=c++11` sets the C++ standard.)

TODO: Having a `Makefile` (with automake?) or similar may ease things, as one could simply write `make PNG-generator` or `make PNG-parser`, fetching the `.bt` file from `.` or `templates/`


### Running the generated producers and parsers

Run the generator as
```
./PNG-generator /dev/urandom output.png
```

Coming from `synthesized/PNG.cpp`, I get
```
Warning: *ERROR: CRC Mismatch @ chunk[0]; in data: 00000010; expected: b255b6e1
*ERROR: CRC Mismatch @ chunk[0]; in data: 00000010; expected: b255b6e1
Array length too large: -694336420, replaced with 5
Warning: *ERROR: CRC Mismatch @ chunk[1]; in data: 0000000c; expected: 2702739a
*ERROR: CRC Mismatch @ chunk[1]; in data: 0000000c; expected: 2702739a
Warning: *ERROR: CRC Mismatch @ chunk[2]; in data: 0000000b; expected: 05da1e5c
*ERROR: CRC Mismatch @ chunk[2]; in data: 0000000b; expected: 05da1e5c
Warning: *ERROR: CRC Mismatch @ chunk[3]; in data: 00000071; expected: 18e4dcb5
*ERROR: CRC Mismatch @ chunk[3]; in data: 00000071; expected: 18e4dcb5
Warning: *ERROR: CRC Mismatch @ chunk[4]; in data: 00000001; expected: 0473eaf1
*ERROR: CRC Mismatch @ chunk[4]; in data: 00000001; expected: 0473eaf1
Warning: *ERROR: CRC Mismatch @ chunk[5]; in data: 00000003; expected: 819d96ba
*ERROR: CRC Mismatch @ chunk[5]; in data: 00000003; expected: 819d96ba
Warning: *ERROR: CRC Mismatch @ chunk[6]; in data: 00000004; expected: 74993bc3
*ERROR: CRC Mismatch @ chunk[6]; in data: 00000004; expected: 74993bc3
Warning: *ERROR: CRC Mismatch @ chunk[7]; in data: 00000004; expected: 6cfb87ab
*ERROR: CRC Mismatch @ chunk[7]; in data: 00000004; expected: 6cfb87ab
Warning: *ERROR: Chunk IHDR must be first chunk.
*ERROR: Chunk IHDR must be first chunk.
Warning: *ERROR: Chunk IEND must be last chunk.
*ERROR: Chunk IEND must be last chunk.
PNG-generator finished
```

TODO: The source of randomness should come as an option (`--random SOURCE`?), with `/dev/urandom' being the default.

TODO: There should be ways to generate several outputs (say, by supplying several files)

TODO: Using `-` as output (or no arg at all) should write output to `stdout`





# Original instructions

`FormatFuzzer` works as a python compiler for 010Editor [binary templates](https://www.sweetscape.com/010editor/templates.html), implemented on top of [pfp](https://github.com/d0c-s4vage/pfp).
`FormatFuzzer` compiles binary templates into C++ code that can be used for generating (or parsing) files that conform to the template specification.

The generator receives as an input the source of randomness used for taking random decisions and produces as output a binary file in the appropriate format.
The parser takes as input the binary file and computes not only the parse tree of the target file, but also an appropriate source of random bytes that could be used by the generator to produce this exact file.

### Requirements

Tested on Linux (Ubuntu 20.04)


### How to support new binary file formats

Run the compiler to compile the binary template into C++ code.
```
python3 create.py templates/PNG.bt PNG.cpp
```
Fix any issues that may prevent the python compiler from finishing by fixing bugs in the python compiler or modifying the original binary template for easier compilation.


After successfully generating the C++ code, try compiling the code.
```
g++ -c -I . -std=c++11 -g -O3 -Wall PNG.cpp
g++ -c -I . -std=c++11 -g -O3 -Wall generator.cpp
g++ -O3 PNG.o generator.o -o PNG-generator -lz
g++ -c -I . -std=c++11 -g -O3 -Wall parser.cpp
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

If the files produced by the generator are still not valid, you can edit the C++ code to improve the generator until it successfully generates well-formatted files with high probability.
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

