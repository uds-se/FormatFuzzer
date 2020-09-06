# FormatFuzzer Makefile. Edit these rules in `Makefile.am' only.

# By default, we build a `png' generator and parser
bin_PROGRAMS = png-generator png-parser
png_generator_SOURCES = png.cpp generator.cpp
png_parser_SOURCES = png.cpp parser.cpp

# Libraries to use
LIBS = -lz

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