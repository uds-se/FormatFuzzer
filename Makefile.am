# FormatFuzzer Makefile. Edit these rules in `Makefile.am' only.

# By default, we build a `png' fuzzer
bin_PROGRAMS = png-fuzzer
png_fuzzer_SOURCES = png.cpp fuzzer.cpp

# Libraries to use
LIBS = -lz

# Where the .bt templates are
TEMPLATES = templates/

# The create script
FFCOMPILE = $(PYTHON) ./ffcompile

# Create a C++ file from template
%.cpp: $(TEMPLATES)%.bt
	$(FFCOMPILE) $< $@

# How to create the fuzzer
%-fuzzer$(EXEEXT): %.o fuzzer.o
	@rm -f $@
	$(AM_V_CXXLD)$(CXXLINK) $+ $(LIBS)

# Create a random file
random.%: %-fuzzer$(EXEEXT)
	./$< fuzz /dev/urandom $@