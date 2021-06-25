# FormatFuzzer

`FormatFuzzer` is a framework for *high-efficiency, high-quality generation and parsing of binary inputs.*
It takes a *binary template* that describes the format of a binary input and generates an *executable* that produces and parses the given binary format.
From a binary template for GIF, for instance, `FormatFuzzer` produces a GIF generator - also known as *GIF fuzzer*.

The binary templates used by FormatFuzzer come from the [010 editor](https://www.sweetscape.com/010editor/).
There are more than [170 binary templates](https://www.sweetscape.com/010editor/templates.html), which either can be used directly for `FormatFuzzer` or adapted for its use.
Generators produced by `FormatFuzzer` are highly efficient, producing thousands of files with test inputs per second.

The project is still in an early stage. Current work includes

* creating `.bt` files that are optimized for input generation;
* adding more configuration options to control the fuzzer;
* extending binary templates with specific fuzzing targets;
and
* interfacing with other test generators for coverage-guided testing and other test strategies.

Contributors are welcome! Visit the [FormatFuzzer project page](https://github.com/uds-se/FormatFuzzer) for filing ideas and issues, or adding pull requests.


## Getting

FormatFuzzer is available from the [FormatFuzzer project page](https://github.com/uds-se/FormatFuzzer) by cloning its git repository:

```
git clone https://github.com/uds-se/FormatFuzzer.git
```
All further actions take place in its main folder:
```
cd FormatFuzzer
```

## Prerequisites

To run FormatFuzzer, you need the following:
* Python 3
* A C++ compiler with GNU libraries (notably `getopt_long()`) such as `clang` or `gcc`
* The Python packages `py010parser`, `six`, and `intervaltree`
* A `zlib` library (for decoding PNG files)

If you plan to edit the build and configuration scripts (`.ac` and `.am` files), you will also need
* GNU autoconf
* GNU automake

### Installing Everything on Linux (Debian Packages)

```
sudo apt install git g++ make automake python3-pip zlib1g-dev
pip3 install py010parser six intervaltree
```

### Installing Python packages

On all systems, using `pip`:
```
pip install py010parser
pip install six
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

Note: all building commands require you to be in the same folder as this `README` file. Building a fuzzer outside of this folder is not yet supported.

### Method 1: Using Make

There's a `Makefile` (source in `Makefile.am`) which automates all construction steps.
(Requires `GNU make`.)
First do
```
touch configure Makefile.in
```
then
```
./configure
```
and then
```
make gif-fuzzer
```
to create a GIF fuzzer.

This works for all file formats provided in `templates/`; if there is a file `templates/FOO.bt`, then `make FOO-fuzzer` will build a fuzzer.


### Method 2: Manual steps

If the above `make` method does not work, or if you want more control, you may have to proceed manually.

#### Step 1: Compiling Binary Template Files into C++ code

Run the `ffcompile` compiler to compile the binary template into C++ code. It takes two arguments: the `.bt` binary template, and a `.cpp` C++ file to be generated.
```
./ffcompile templates/gif.bt gif.cpp
```


#### Step 2: Compiling the C++ code

Use the following commands to create a fuzzer `gif-fuzzer`.
First, compile the generic command-line driver:

```
g++ -c -I . -std=c++17 -g -O3 -Wall fuzzer.cpp
```
(`-I .` denotes the location of the `bt.h` file; `-std=c++17` sets the C++ standard.)

Then, compile the binary parser/compiler:

```
g++ -c -I . -std=c++17 -g -O3 -Wall gif.cpp
```

Finally, link the binary parser/compiler with the command-line driver to obtain an executable. If you use any extra libraries (such as `-lz`), be sure to specify these here too.
```
g++ -O3 gif.o fuzzer.o -o gif-fuzzer -lz
```


## Running the Fuzzer

The generated fuzzer takes a _command_ as first argument, followed by options and arguments to that command.

The most important command is `fuzz`, for producing outputs.  Its arguments are files to be generated in the appropriate format.

Run the generator as
```
./gif-fuzzer fuzz output.gif
```
to create a random binary file `output.gif`, or
```
./gif-fuzzer fuzz out1.gif out2.gif out3.gif
```
to create three GIF files `out1.gif`, `out2.gif`, and `out3.gif`.

Note that the `gif.bt` template we provide has been augmented with special functions to make generation of valid files easier. If you use an original `.bt` template files without adaptations, you may get warnings during generation and create invalid files.


## Running Parsers

You can also run the fuzzer as a _parser_ for binary files, using the `parse` command. This is useful if you want to test the accuracy of the binary template, or if you want to mutate an input (see `Decision Files', below).

To run the parser, use
```
./gif-fuzzer parse input.gif
```
You will see error messages if `input.gif` cannot be successfully parsed.


## Decision Files

While parsing, you can also store all parsing decisions (i.e. which parsing alternatives were taken) in a _decision file_. This is a sequence of bytes enumerating the decisions taken.
Each byte stands for a single parsing decision. A byte value of `0` means that the first alternative was taken, a byte value of `1` means that the second alternative was taken, and so on.

You can generate such a decision file when parsing an input:
```
./gif-fuzzer parse --decisions input.dec input.gif
```
Here, `input.dec` stores the decisions made for parsing `input.gif'.

You can also use such a decision file when _generating_ inputs. The fuzzer will then take the exact same decisions as found during parsing. The following command generates a new GIF file using the decisions determined while parsing `input.gif':
```
./gif-fuzzer fuzz --decisions input.dec input2.gif
```
If everything works well, both files should be identical:
```
cmp input.gif input2.gif
```
By _mutating_ a decision file (e.g. replacing individual bytes), you can create inputs that are _similar_ to the original file parsed. This is useful for interfacing with specific testing strategies and fuzzers such as AFL, where you can use `gif-fuzzer` and the like as _translators_ from decision files to binary files and back: AFL would mutate decision files, and the program under test would run on the translated binary files. In contrast to mutating binary files directly (as AFL would normally do), this would have the advantage of always having valid inputs - and thus progressing much faster towards coverage.


## Creating and Customizing Binary Templates

To write your own `.bt` binary templates (and thus create a high-efficiency fuzzer/parser for this format), read the section [Introduction to Templates and Scripts](https://www.sweetscape.com/010editor/manual/IntroTempScripts.htm) from the [010 Editor Manual](https://www.sweetscape.com/010editor/manual/).

In many cases, a template of the format you are looking for (or a similar one) may already exist. Have a look at the 010 editor [binary template collection](https://www.sweetscape.com/010editor/templates.html) whether there is something that you can use or base your format on.

Note that the `.bt` files provided in the repository generally target _parsing_ files. They _can_ be used for _generating_ files, too; but they often lack exact information which parts of the input are required.

In this section, we discuss some of the ways in which you can customize `.bt` files to work well with `FormatFuzzer`.

For example, for the GIF format, the file [templates/gif-orig.bt](templates/gif-orig.bt) shows the original binary template, which was only designed for parsing, while the file [templates/gif.bt](templates/gif.bt) is a modified version which is capable of generating valid GIFs. Comparing the two files, we see that a small number changes was required to achieve this.

If you have created a `gif-fuzzer`, either by running `make gif-fuzzer` or by using the `ffcompile` tool, you have already obtained a C++ file `gif.cpp` which contains an implementation of the GIF generator and parser. This is useful to see how the changes you make to the binary template are translated into executable code. More details on the C++ code are presented on the next section.

The GIF binary template makes use of _lookahead_ functions `ReadUByte()` and `ReadUShort()` to look ahead at the values of the next bytes in the file before actually parsing them into a struct field. At generation time, we allow those functions to receive an additional argument specifying a set of good known values to pick for the bytes that we look ahead. In addition, we also allow specifying a global set of good known values to always use when calling a particular lookahead function, such as `ReadUByte()`. Those are stored in the `ReadUByteInitValues` vector.

By default, our translation procedure `ffcompile` tries to mine interesting values which have been used in comparisons against lookahead bytes and use them as a global set of known values. When running
```
./ffcompile templates/gif.bt gif.cpp
```
a printed message shows the lookahead functions identified, as well as the mined interesting values:
```
Finished creating cpp generator.

Lookahead functions found:

ReadUByte
ReadUShort

Mined interesting values:

GlobalColorTableFlag: ['1']
LocalColorTableFlag: ['1']
ReadUByte: ['0x3B', '0x2C']
ReadUShort: ['0xF921', '0xFE21', '0x0121', '0xFF21']
Signature: ['"GIF"']
```

For GIF generation, however, it is better to specify the set of good known values for `ReadUByte()` individually at each call to the function. So we define an empty array (size 0)
```
const local UBYTE ReadUByteInitValues[0];
```
to overwrite the set of global `ReadUByteInitValues` and for each call to `ReadUByte()`, we use an additional argument to specify the set of good values to use for that particular location.
The binary template language is also powerful enough to allow this choice to be made based on runtime conditions. For example, in the following code we show how the choice of appropriate values for a `ReadUByte()` call can depend on the current GIF version we are generating. A GIF version `89a` allows one extra possible value for the byte (0x21).
```
	if(GifHeader.Version == "89a")
		local UBYTE values[] = { 0x3B, 0x2C, 0x21 };
	else
		local UBYTE values[] = { 0x3B, 0x2C };

	while (ReadUByte(FTell(), values) != 0x3B) {
		...
	}
```

The remaining edits required for the GIF binary template are similar. For example, for each struct field can also specify a set of known good values. For example this specifies the correct values for the `Version` field: `87a` and `89a`.
```
	char	Version[3] = { {"87a"}, {"89a"} };
```


## Understanding the Generated C++ Code

For debugging purposes, as well as for understanding how to make appropriate changes to improve your generators and parsers, it may be useful to understand some inner workings of the generated C++ code.
Ideally, you should be able to edit the binary template files until they can be used to generate valid files with high probability, so you wouldn't have to edit the generated C++ code.

The C++ code creates a class for each `struct` and `union` defined in the binary template, as well as for native types, such as `int`.

At construction time, when initializing a variable, we can define a set of good known values that this variable can assume. For example, the constructor call
```
char_array_class cname(cname_element, { "IHDR", "tEXt", "PLTE", "cHRM", "sRGB", "iEXt", "zEXt", "tIME", "pHYs", "bKGD", "sBIT", "sPLT", "acTL", "fcTL", "fdAT", "IHDR", "IEND" });
```
would specify 17 good values to use for variable `cname`. But this is often not enough, since the choice of appropriate chunk types is context sensitive.
So we also allow specifying a set of good values at generation time when generating a new chunk.
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

All the random choices taken by the generator are done by calling the `rand_int()` method.
```
long long rand_int(unsigned long long x, std::function<long long (unsigned char*)> parse);
```
When running the program as a generator, this method samples an integer from 0 to x-1 by reading bytes from the random buffer.
When running the program as a parser, this method uses the `parse()` function to find out which random bytes must be present in the random buffer in order to generate the target file, and then writes those bytes to the random buffer.
The `parse` function receives as an argument the buffer at the current position of the file and must then return which value would have to be returned by the current call to `rand_int()` in order to generate this exact file configuration.


## Authors

FormatFuzzer was designed and written by Rafael Dutra &lt;rafael.dutra@cispa.de&gt;.

The concept of a fuzzer compiler was introduced by Rahul Gopinath &lt;rahul.gopinath@cispa.de&gt; and Andreas Zeller &lt;zeller@cispa.de&gt;.



## Copyright

FormatFuzzer is Copyright &copy; 2020 by CISPA Helmholtz Center for Information Security. The following licenses apply:

* _The FormatFuzzer code_ (notably, all C++ code and code related to its generation) is subject to the GNU GENERAL PUBLIC LICENSE, as found in [COPYING](COPYING).

* As an exception to the above, _C++ code generated by FormatFuzzer_ (i.e., fuzzers and parsers for specific formats) is in the public domain.

* _The original_ [pfp](https://github.com/d0c-s4vage/pfp) _code_, which FormatFuzzer is based upon, is subject to a MIT license, as found in [LICENSE-pfp](LICENSE-pfp).
