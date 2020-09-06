# Default targets
bin_PROGRAMS = PNG_generator PNG_parser
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