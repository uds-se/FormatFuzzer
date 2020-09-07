# FormatFuzzer

`FormatFuzzer` is a framework for *high-efficiency, high-quality generation and parsing of binary inputs.*
It takes a *binary template* that describes the format of a binary input and generates an *executable* that produces and parses the given binary format.
From a binary template for PNG, for instance, `FormatFuzzer` produces a PNG generator - also known as *PNG fuzzer*.

The binary templates used by FormatFuzzer come from the [010 editor](https://www.sweetscape.com/010editor/).
There are more than [170 binary templates](https://www.sweetscape.com/010editor/templates.html), which either can be used directly for `FormatFuzzer` or adapted for its use.
Generators produced by `FormatFuzzer` are highly efficient, producing thousands of files with test inputs per second.

This project is in its very early stage - contributors (notably for adapting and writing `.bt' files) are welcome!


## Installing

You need the following:
* Python 3
* A C++ compiler
* The Python packages `py010parser` and `intervaltree`
* A `zlib` library (for decoding PNG files)


### Installing Python packages

On all systems, using `pip`:
```
pip install py010parser
pip install intervaltree
```

### Installing zlib

For the PNG examples, you need a `zlib` library (`-lz`).

On Linux, using `apt`:
```
sudo apt install zlib1g-dev
```
On a Mac, you need to install `XCode'; then run this command:
```
xcode-select --install
```

## Building

Note: all building commands require you to be in the same folder as this `README' file. Building outside of this folder is not yet supported.

### Method 1: Using Make

There's a `Makefile` (source in `Makefile.am`) which automates all construction steps.
(Requires `GNU make`.)
First do
```
./configure
```
and then
```
make png-fuzzer
```
to create a PNG fuzzer.

This works for all file formats provided in `templates/`; if there is a file `templates/FOO.bt`, then `make FOO-fuzzer` will work.


### Method 2: Manual steps

If the above `make` method does not work, or if you want more control, you may have to proceed manually.

#### Compiling Binary Template Files into C++ code

Run the `ffcompile` compiler to compile the binary template into C++ code:
```
./ffcompile templates/png.bt png.cpp
```


#### Compiling the C++ code

Use the following commands to create a fuzzer `png-fuzzer`=.
First, compile the generic command-line driver:

```
g++ -c -I . -std=c++11 -g -O3 -Wall fuzzer.cpp
```
(`-I .` denotes the location of the `bt.h` file; `-std=c++11` sets the C++ standard.)

Then, compile the binary parser/compiler:

```
g++ -c -I . -std=c++11 -g -O3 -Wall png.cpp
```

Finally, link the binary parser/compiler with the command-line driver to obtain an executable:
```
g++ -O3 png.o generator.o -o png-fuzzer -lz
```


## Running the Fuzzer

The generator receives as input a list of files to be generated in the appropriate format.

Run the generator as
```
./png-fuzzer fuzz output.png
```
to create a random binary file `output.png'.

Note that during creation, you may encounter warnings about CRC mismatches. To resolve these, you need to extend the `.bt' file.


## Running Parsers

You can also run the fuzzer as a _parser_ for binary files. This is useful if you want to test the accuracy of the binary template, or if you want to mutate an input (see `Decision Files', below).

To run the parser, user
```
./png-fuzzer parse input.png
```
You will see error messages if `input.png' cannot be successfully parsed.


## Decision Files

While parsing, you can also store all parsing decisions (i.e.\ which parsing alternatives were taken) in a _decision file_. This is a sequence of bytes enumerating the decisions taken (byte value of `0' = first alternative was taken, byte value of `1' = second alternative was taken, and so on).

You can generate such a decision file when parsing an input:
```
./png-fuzzer parse --decisions input.dec input.png
```
Here, `input.dec' represents the decisions made for parsing `input.png'.

You can also use such a decision file when _generating_ inputs. The fuzzer will then take the exact same decisions as found during parsing. The following command generates a new PNG file using the decisions determined while parsing `input.png':
```
./png-fuzzer fuzz --decisions input.dec input2.png
```
If everything works well, both files should be similar:
```
cmp input.png input2.png
```
By _mutating_ a decision file (e.g. replacing individual bytes), you can create inputs that are similar to the original file parsed. This is useful for interfacing with specific testing strategies and fuzzers such as AFL.


## Creating and Customizing Binary Templates

To write your own binary template (and thus create a high-efficiency fuzzer/parser for this format), first have a look at the 010 editor [binary template collection](https://www.sweetscape.com/010editor/templates.html) whether there is something that you can use or base your format on.
To write your own `.bt` binary template, read the section [Introduction to Templates and Scripts](https://www.sweetscape.com/010editor/manual/IntroTempScripts.htm) from the [010 Editor Manual](https://www.sweetscape.com/010editor/manual/).

TODO: Have a few words here on the limitations of `FormatFuzzer` - what does one need to keep in mind when creating/customizing a `.bt` file?


## Customizing Generators and Parsers

If the files produced by the generator are still not valid, you can edit the C++ code to improve the generator until it successfully generates well-formatted files with high probability.

The difference between the files `synthesized/PNG.cpp` and `generators/PNG.cpp` shows what changes were added to the PNG generator in order to produce valid files.

FIXME: These files do not exist; instead, I see `synthesized/PNG.cpp` and `generators/PNG.cpp`. Do you expect people to edit the generated `.cpp` files? (Editing `.bt` files would be much preferred.)

TODO: Can I place the extra C++ code (say, for generating picture bits) into the `.bt' file?

TODO: Have a way to express changes to `.cpp` files that are not overwritten as one re-generates them from `.bt` files.

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

TODO: Can't I express such context (notably, the first and last chunk) in the `.bt` file?

TODO: Maybe have a walkthrough-style tutorial listing the changes to be made

All the random choices taken by the generator are done by calling the `rand_int()` method.
```
long long rand_int(unsigned long long x, std::function<long long (unsigned char*)> parse);
```
When running the program as a generator, this method samples an integer from 0 to x-1 by reading bytes from the random buffer.
When running the program as a parser, this method uses the `parse()` function to find out which random bytes must be present in the random buffer in order to generate the target file, and then writes those bytes to the random buffer.
The `parse` function receives as an argument the buffer at the current position of the file and must then return which value would have to be returned by the current call to `rand_int()` in order to generate this exact file configuration.

