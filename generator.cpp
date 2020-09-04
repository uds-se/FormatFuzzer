#include <cstdio>
#include <cstring>
#include <cassert>
#include "formatfuzzer.h"

int main(int argc, char** argv) {
	assert(argc == 3);
	setup_input(argv[1]);
	try {
		generate_file();
	} catch (...) {
		delete_globals();
		fprintf(stderr, "%s failed\n", get_bin_name(argv[0]));
		save_output(argv[2]);
		return -1;
	}
	save_output(argv[2]);
	fprintf(stderr, "%s finished\n", get_bin_name(argv[0]));
	return 0;
}
