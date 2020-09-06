# Default targets
bin_PROGRAMS = PNG_generator PNG_parser
PNG_generator_SOURCES = PNG.cpp generator.cpp
PNG_parser_SOURCES = PNG.cpp parser.cpp
PNG_generator_LDADD = -lz
PNG_parser_LDADD = -lz

# C++ flags
CXXFLAGS = -std=c++11

# Where the .bt templates are
TEMPLATES = templates/

# The create script
CREATE = $(PYTHON) create.py

%.cpp: $(TEMPLATES)%.bt
	$(CREATE) $< $@