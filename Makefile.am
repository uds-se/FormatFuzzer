# FormatFuzzer Makefile. Edit these rules in `Makefile.am' only.

# By default, we build a `gif' fuzzer
bin_PROGRAMS = gif-fuzzer
gif_fuzzer_SOURCES = gif.cpp fuzzer.cpp

# Libraries to use (png needs -lz)
LIBS = -lz

# Where the .bt templates are
TEMPLATES = templates/

# The create script
FFCOMPILE = ./ffcompile

# Create a C++ file from template (say, 'gif.cpp' from template 'gif.bt')
%.cpp: $(TEMPLATES)%.bt
	$(FFCOMPILE) $< $@

# Keep generated .cpp files
.PRECIOUS: %.cpp

# How to create the fuzzer (say, 'gif-fuzzer')
%-fuzzer$(EXEEXT): %.o fuzzer.o
	@rm -f $@
	$(AM_V_CXXLD)$(CXXLINK) $+ $(LIBS)

# How to create the fuzzer as a shared library (say, 'gif.so')
%.so: %.cpp fuzzer.cpp
	@rm -f $@
	$(AM_V_CXXLD)$(CXXLINK) -shared -fPIC $+ $(LIBS)

# Create a random file (say, 'make random.gif')
random.%: %-fuzzer$(EXEEXT)
	./$< fuzz $@
