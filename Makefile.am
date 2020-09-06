# FormatFuzzer Makefile. Edit these rules in `Makefile.am' only.

# Default targets
bin_PROGRAMS = PNG-generator PNG-parser
PNG_generator_SOURCES = PNG.cpp generator.cpp
PNG_parser_SOURCES = PNG.cpp parser.cpp

# Libraries to use
LIBS = -lz

# C++ flags
CXXFLAGS = -std=c++11

# Where the .bt templates are
TEMPLATES = templates/

# The create script
CREATE = $(PYTHON) create.py

# Create a C++ file from template
%.cpp: $(TEMPLATES)%.bt
	$(CREATE) $< $@

# How to create a generator
%-generator$(EXEEXT): %.o generator.o
	@rm -f $@
	$(AM_V_CXXLD)$(CXXLINK) $+ $(LIBS)

# How to create a parser
%-parser$(EXEEXT): %.o parser.o
	@rm -f $@
	$(AM_V_CXXLD)$(CXXLINK) $+ $(LIBS)

# Create a random file
random.%: %-generator$(EXEEXT)
	./$< /dev/urandom $@