// Fuzzer.cpp
// Main driver for FormatFuzzer

#include <unordered_map>
#include <stdlib.h>
#include <cstdio>
#include <cstring>
#include <cassert>
#include <getopt.h>
#include <stdint.h>
#include <climits>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <fcntl.h>

#include "config.h"
#include "formatfuzzer.h"

static const char *bin_name = "formatfuzzer";

extern bool get_parse_tree;

// Each command comes as if it were invoked from the command line

// fuzz - generate random inputs
int fuzz(int argc, char **argv)
{
	const char *decision_source = "/dev/urandom";

	// Process options
	while (1)
	{
		static struct option long_options[] =
			{
				{"help", no_argument, 0, 'h'},
				{"decisions", required_argument, 0, 'd'},
				{0, 0, 0, 0}};
		int option_index = 0;
		int c = getopt_long(argc, argv, "d:p",
							long_options, &option_index);

		// Detect the end of the options.
		if (c == -1)
			break;

		switch (c)
		{
		case 'h':
		case '?':
			fprintf(stderr, "fuzz: usage: fuzz [--decisions SOURCE] [FILES...|-]\n");
			fprintf(stderr, "Outputs random data to given FILES (or `-' for standard output).\n");
			fprintf(stderr, "Options:\n");
			fprintf(stderr, "--decisions SOURCE: Use SOURCE for generation decisions (default %s)\n", decision_source);
			fprintf(stderr, "-p: print parse tree\n");
			return 0;

		case 'd':
			decision_source = optarg;
			break;
		case 'p':
			get_parse_tree = true;
			break;
		}
	}
    
    if (optind >= argc) {
		fprintf(stderr, "%s: missing output files. (Use '-' for standard output)\n", bin_name);
        return 1;
    }

	// Main function
	int errors = 0;
	for (int arg = optind; arg < argc; arg++)
	{
		char *out = argv[arg];
		bool success = false;
		setup_input(decision_source);
		try
		{
			generate_file();
			success = true;
		}
		catch (int status)
		{
			delete_globals();
			if (status == 0)
				success = true;
		}
		catch (...)
		{
			delete_globals();
		}
		save_output(out);
		if (success)
			fprintf(stderr, "%s: %s created\n", bin_name, out);
		else
		{
			fprintf(stderr, "%s: %s failed\n", bin_name, out);
			errors++;
		}
	}

	return errors;
}

// fuzz - parse existing files
int parse(int argc, char **argv)
{
	const char *decision_sink = 0;

	// Process options
	while (1)
	{
		static struct option long_options[] =
			{
				{"help", no_argument, 0, 'h'},
				{"decisions", required_argument, 0, 'd'},
				{0, 0, 0, 0}};
		int option_index = 0;
		int c = getopt_long(argc, argv, "d:",
							long_options, &option_index);

		// Detect the end of the options.
		if (c == -1)
			break;

		switch (c)
		{
		case 'h':
		case '?':
			fprintf(stderr, "parse: usage: parse [--decisions SINK] [FILES...|-]\n");
			fprintf(stderr, "Parses given FILES (or `-' for standard input).\n");
			fprintf(stderr, "Options:\n");
			fprintf(stderr, "--decisions SINK: Save parsing decisions in SINK (default: none)\n");
			return 0;

		case 'd':
			decision_sink = optarg;
			break;
		}
	}
    
    if (optind >= argc) {
		fprintf(stderr, "%s: missing input files. (Use '-' for standard input.)\n", bin_name);
        return 1;
    }

	int errors = 0;
	for (int arg = optind; arg < argc; arg++)
	{
		char *in = argv[arg];
		bool success = false;

		set_parser();
		setup_input(in);
		try
		{
			generate_file();
			success = true;
		}
		catch (int status)
		{
			delete_globals();
			if (status == 0)
				success = true;
		}
		catch (...)
		{
			delete_globals();
		}
		if (success)
			fprintf(stderr, "%s: %s parsed\n", bin_name, in);
		else
		{
			fprintf(stderr, "%s: %s failed\n", bin_name, in);
			errors++;
		}

		if (decision_sink)
			save_output(decision_sink);
	}

	return errors;
}

extern "C" size_t afl_pre_save_handler(unsigned char* data, size_t size, unsigned char** new_data);
extern "C" int afl_post_load_handler(unsigned char* data, size_t size, unsigned char** new_data, size_t* new_size);
extern bool print_errors;
extern std::unordered_map<std::string, std::string> variable_types;

unsigned copy_rand(unsigned char *dest);

extern const char* chunk_name;

extern bool get_chunk;
extern bool smart_mutation;
extern unsigned chunk_start;
extern unsigned chunk_end;
extern unsigned rand_start;
extern unsigned rand_end;
extern bool is_optional;
extern bool is_delete;
extern bool following_is_optional;


/* Get unix time in microseconds */

static uint64_t get_cur_time_us(void) {

  struct timeval  tv;
  struct timezone tz;

  gettimeofday(&tv, &tz);

  return (tv.tv_sec * 1000000ULL) + tv.tv_usec;

}

void write_file(const char* filename, unsigned char* data, size_t size) {
	printf("Saving file %s\n", filename);
	int file_fd = open(filename, O_CREAT | O_WRONLY | O_TRUNC, S_IRUSR | S_IWUSR | S_IRGRP | S_IWGRP | S_IROTH);
	ssize_t res = write(file_fd, data, size);
	assert((size_t) res == size);
	close(file_fd);
}

// smart_replace - apply a smart replacement
int smart_replace(int argc, char **argv)
{
	char *file_t = NULL;
	int start_t = -1;
	int end_t = -1;
	bool optional_t = false;
	const char* chunk_t;
	char *file_s = NULL;
	int start_s = -1;
	int end_s = -1;
	bool optional_s = false;
	const char* chunk_s;

	bool success = false;

	unsigned char *rand_t = new unsigned char[MAX_RAND_SIZE];
	unsigned char *rand_s = new unsigned char[MAX_RAND_SIZE];
	unsigned len_t;
	// Process options
	while (1)
	{
		static struct option long_options[] =
			{
				{"help", no_argument, 0, 'h'},
				{"targetfile", required_argument, 0, 1},
				{"targetstart", required_argument, 0, 2},
				{"targetend", required_argument, 0, 3},
				{"sourcefile", required_argument, 0, 4},
				{"sourcestart", required_argument, 0, 5},
				{"sourceend", required_argument, 0, 6},
				{0, 0, 0, 0}};
		int option_index = 0;
		int c = getopt_long(argc, argv, "",
							long_options, &option_index);

		// Detect the end of the options.
		if (c == -1)
			break;

		switch (c)
		{
		case 'h':
		case '?':
			fprintf(stderr, R"(replace: Smart Replacement
replace --targetfile file_t --targetstart start_t --targetend end_t
        --sourcefile file_s --sourcestart start_s --sourceend end_s OUTFILE
			
Apply a smart mutation which replaces one chunk from file_t (byte range
[start_t, end_t]) with another chunk from file_s (byte range [start_s, end_s]).
The resulting file should be similar to file_t, except with the source chunk
from file_s copied into the appropriate position of the target chunk from
file_t.  Moreover, the mutation is smarter than simple memmove() operations,
which should allow it to fix constraints implemented in the binary template,
such as lenght fields and checksums.  Command returns 0 if mutation worked as
expected or nonzero if it didn't work as expected.  This happens when the chunk
from file_s doesn't fit well in file_t because it required a larger or smaller
number of decision bytes in file_t than it did in file_s.
)");
			return 0;

		case 1:
			file_t = optarg;
			break;
		case 2:
			start_t = strtol(optarg, NULL, 0);
			break;
		case 3:
			end_t = strtol(optarg, NULL, 0);
			break;
		case 4:
			file_s = optarg;
			break;
		case 5:
			start_s = strtol(optarg, NULL, 0);
			break;
		case 6:
			end_s = strtol(optarg, NULL, 0);
			break;
		}
	}
    
	if (optind >= argc) {
		fprintf(stderr, "%s: missing output file.\n", bin_name);
		return -2;
	}
	if (!file_t || start_t == -1 || end_t == -1) {
		fprintf(stderr, "%s: missing required arguments for target file.\n", bin_name);
		return -2;
	}
	if (!file_s || start_s == -1 || end_s == -1) {
		fprintf(stderr, "%s: missing required arguments for source file.\n", bin_name);
		return -2;
	}

	// Main function
	char *out = argv[optind];

	printf("Parsing file %s\n\n", file_s);
	success = false;

	get_chunk = true;
	chunk_start = start_s;
	chunk_end = end_s;
	rand_start = rand_end = UINT_MAX;
	set_parser();
	setup_input(file_s);
	try
	{
		generate_file();
		success = true;
	}
	catch (int status)
	{
		delete_globals();
		if (status == 0)
			success = true;
	}
	catch (...)
	{
		delete_globals();
	}
	if (!success)
	{
		fprintf(stderr, "%s: Parsing %s failed\n", bin_name, file_s);
		return -2;
	}
	if (rand_start == UINT_MAX) {
		fprintf(stderr, "%s: Unable to find chunk in file %s\n", bin_name, file_s);
		return -2;
	}
	copy_rand(rand_s);
	start_s = rand_start;
	end_s = rand_end;
	optional_s = is_optional;
	chunk_s = chunk_name;


	printf("\nParsing file %s\n\n", file_t);
	success = false;

	get_chunk = true;
	chunk_start = start_t;
	chunk_end = end_t;
	rand_start = rand_end = UINT_MAX;
	set_parser();
	setup_input(file_t);
	try
	{
		generate_file();
		success = true;
	}
	catch (int status)
	{
		delete_globals();
		if (status == 0)
			success = true;
	}
	catch (...)
	{
		delete_globals();
	}
	if (!success)
	{
		fprintf(stderr, "%s: Parsing %s failed\n", bin_name, file_t);
		return -2;
	}
	if (end_t != -1 && rand_start == UINT_MAX) {
		fprintf(stderr, "%s: Unable to find chunk in file %s\n", bin_name, file_t);
		return -2;
	}
	len_t = copy_rand(rand_t);
	start_t = rand_start;
	end_t = rand_end;
	optional_t = is_optional;
	chunk_t = chunk_name;

	if (optional_t && !optional_s) {
		fprintf(stderr, "%s: Trying to copy non-optional chunk from file %s into optional chunk from file %s\n", bin_name, file_s, file_t);
		return -2;
	}
	if (!optional_t && optional_s) {
		fprintf(stderr, "%s: Trying to copy optional chunk from file %s into non-optional chunk from file %s\n", bin_name, file_s, file_t);
		return -2;
	}
	if (!optional_t && !optional_s && variable_types[chunk_t] != variable_types[chunk_s]) {
		fprintf(stderr, "%s: Trying to replace non-optional chunks of different types: %s, %s\n", bin_name, variable_types[chunk_t].c_str(), variable_types[chunk_s].c_str());
		return -2;
	}

	printf("\nGenerating file %s\n\n", out);

	unsigned rand_size = len_t + (end_s - start_s) - (end_t - start_t);
	assert(rand_size <= MAX_RAND_SIZE);
	memmove(rand_t + start_t + end_s + 1 - start_s, rand_t + end_t + 1, len_t - (end_t + 1));
	memcpy(rand_t + start_t, rand_s + start_s, end_s + 1 - start_s);

	get_chunk = false;
	smart_mutation = true;
	unsigned rand_end0 = rand_end = start_t + end_s - start_s;
	set_generator();

	unsigned char* file = NULL;
	unsigned file_size = afl_pre_save_handler(rand_t, MAX_RAND_SIZE, &file);
	if (!file || !file_size) {
		printf("Failed to generate mutated file!\n");
		return -2;
	}
	save_output(out);
	if (rand_end0 < rand_end)
		fprintf(stderr, "Warning: Consumed %u more decision bytes than expected while generating chunk.\n", rand_end - rand_end0);
	if (rand_end0 > rand_end)
		fprintf(stderr, "Warning: Consumed %u less decision bytes than expected while generating chunk.\n", rand_end0 - rand_end);
	fprintf(stderr, "%s: %s created\n", bin_name, out);

	delete[] rand_t;
	delete[] rand_s;
	return (rand_end > rand_end0) - (rand_end < rand_end0);
}





// smart_delete - apply a smart deletion
int smart_delete(int argc, char **argv)
{
	char *file_t = NULL;
	int start_t = -1;
	int end_t = -1;
	bool optional_t = false;

	bool success = false;

	unsigned char *rand_t = new unsigned char[MAX_RAND_SIZE];
	unsigned len_t;
	// Process options
	while (1)
	{
		static struct option long_options[] =
			{
				{"help", no_argument, 0, 'h'},
				{"targetfile", required_argument, 0, 1},
				{"targetstart", required_argument, 0, 2},
				{"targetend", required_argument, 0, 3},
				{0, 0, 0, 0}};
		int option_index = 0;
		int c = getopt_long(argc, argv, "",
							long_options, &option_index);

		// Detect the end of the options.
		if (c == -1)
			break;

		switch (c)
		{
		case 'h':
		case '?':
			fprintf(stderr, R"(delete: Smart Deletion
delete --targetfile file_t --targetstart start_t --targetend end_t OUTFILE

Apply a smart deletion operation, removing one chunk from file_t (byte range
[start_t, end_t]).  This can only be applied if the chunk is optional and the
following chunk is also optional.  A chunk is optional if there are calls to
FEof() and/or lookahead functions such as ReadBytes() right before the start
of the chunk.  This smart deletion should also fix constraints implemented in
the binary template (such as length fields).
)");
			return 0;

		case 1:
			file_t = optarg;
			break;
		case 2:
			start_t = strtol(optarg, NULL, 0);
			break;
		case 3:
			end_t = strtol(optarg, NULL, 0);
			break;
		}
	}
    
	if (optind >= argc) {
		fprintf(stderr, "%s: missing output file.\n", bin_name);
		return -2;
	}
	if (!file_t || start_t == -1 || end_t == -1) {
		fprintf(stderr, "%s: missing required arguments for target file.\n", bin_name);
		return -2;
	}

	// Main function
	char *out = argv[optind];


	printf("\nParsing file %s\n\n", file_t);
	success = false;
	is_delete = true;

	get_chunk = true;
	chunk_start = start_t;
	chunk_end = end_t;
	rand_start = rand_end = UINT_MAX;
	set_parser();
	setup_input(file_t);
	try
	{
		generate_file();
		success = true;
	}
	catch (int status)
	{
		delete_globals();
		if (status == 0)
			success = true;
	}
	catch (...)
	{
		delete_globals();
	}
	if (!success)
	{
		fprintf(stderr, "%s: Parsing %s failed\n", bin_name, file_t);
		return -2;
	}
	if (end_t != -1 && rand_start == UINT_MAX) {
		fprintf(stderr, "%s: Unable to find chunk in file %s\n", bin_name, file_t);
		return -2;
	}
	len_t = copy_rand(rand_t);
	start_t = rand_start;
	end_t = rand_end;
	optional_t = is_optional;

	if (!optional_t) {
		fprintf(stderr, "%s: The target chunk is not optional.\n", bin_name);
		return -2;
	}
	if (!following_is_optional) {
		fprintf(stderr, "%s: The target chunk is not followed by an optional chunk.\n", bin_name);
		return -2;
	}

	printf("\nGenerating file %s\n\n", out);

	memmove(rand_t + start_t, rand_t + end_t + 1, len_t - (end_t + 1));

	get_chunk = false;
	set_generator();

	unsigned char* file = NULL;
	unsigned file_size = afl_pre_save_handler(rand_t, MAX_RAND_SIZE, &file);
	if (!file || !file_size) {
		printf("Failed to generate mutated file!\n");
		return -2;
	}
	save_output(out);
	fprintf(stderr, "%s: %s created\n", bin_name, out);

	delete[] rand_t;
	return 0;
}





// smart_insert - apply a smart insertion
int smart_insert(int argc, char **argv)
{
	char *file_t = NULL;
	int start_t = -1;
	char *file_s = NULL;
	int start_s = -1;
	int end_s = -1;
	bool optional_s = false;

	bool success = false;

	unsigned char *rand_t = new unsigned char[MAX_RAND_SIZE];
	unsigned char *rand_s = new unsigned char[MAX_RAND_SIZE];
	unsigned len_t;
	// Process options
	while (1)
	{
		static struct option long_options[] =
			{
				{"help", no_argument, 0, 'h'},
				{"targetfile", required_argument, 0, 1},
				{"targetstart", required_argument, 0, 2},
				{"sourcefile", required_argument, 0, 4},
				{"sourcestart", required_argument, 0, 5},
				{"sourceend", required_argument, 0, 6},
				{0, 0, 0, 0}};
		int option_index = 0;
		int c = getopt_long(argc, argv, "",
							long_options, &option_index);

		// Detect the end of the options.
		if (c == -1)
			break;

		switch (c)
		{
		case 'h':
		case '?':
			fprintf(stderr, R"(insert: Smart Insertion
insert --targetfile file_t --targetstart start_t
       --sourcefile file_s --sourcestart start_s --sourceend end_s OUTFILE

Apply a smart insertion operation, inserting one chunk from file_s (byte range
[start_s, end_s]) into file_t, with the first byte at start_t.  This can only
be applied if file_t originally had an optional chunk starting at start_t or
if start_t was the position right after the end of an appendable chunk.  A
chunk is optional if there are calls to FEof() and/or lookahead functions such
as ReadBytes() right before the start of the chunk.  A chunk is appendable if
there are calls to FEof() and/or lookahead functions such as ReadBytes() right
before the end of the chunk.  The source chunk from file_s must also be
optional.  This smart addition should also fix constraints implemented in the
binary template (such as length fields).  Command returns 0 if mutation worked
as expected or nonzero if it didn't work as expected.  This happens when the
chunk from file_s doesn't fit well in file_t because it required a larger or
smaller number of decision bytes in file_t than it did in file_s.
)");
			return 0;

		case 1:
			file_t = optarg;
			break;
		case 2:
			start_t = strtol(optarg, NULL, 0);
			break;
		case 4:
			file_s = optarg;
			break;
		case 5:
			start_s = strtol(optarg, NULL, 0);
			break;
		case 6:
			end_s = strtol(optarg, NULL, 0);
			break;
		}
	}
    
	if (optind >= argc) {
		fprintf(stderr, "%s: missing output file.\n", bin_name);
		return -2;
	}
	if (!file_t || start_t == -1) {
		fprintf(stderr, "%s: missing required arguments for target file.\n", bin_name);
		return -2;
	}
	if (!file_s || start_s == -1 || end_s == -1) {
		fprintf(stderr, "%s: missing required arguments for source file.\n", bin_name);
		return -2;
	}

	// Main function
	char *out = argv[optind];

	printf("Parsing file %s\n\n", file_s);
	success = false;

	get_chunk = true;
	chunk_start = start_s;
	chunk_end = end_s;
	rand_start = rand_end = UINT_MAX;
	set_parser();
	setup_input(file_s);
	try
	{
		generate_file();
		success = true;
	}
	catch (int status)
	{
		delete_globals();
		if (status == 0)
			success = true;
	}
	catch (...)
	{
		delete_globals();
	}
	if (!success)
	{
		fprintf(stderr, "%s: Parsing %s failed\n", bin_name, file_s);
		return -2;
	}
	if (rand_start == UINT_MAX) {
		fprintf(stderr, "%s: Unable to find chunk in file %s\n", bin_name, file_s);
		return -2;
	}
	copy_rand(rand_s);
	start_s = rand_start;
	end_s = rand_end;
	optional_s = is_optional;


	printf("\nParsing file %s\n\n", file_t);
	success = false;

	get_chunk = true;
	chunk_start = start_t;
	chunk_end = -1;
	rand_start = rand_end = UINT_MAX;
	set_parser();
	setup_input(file_t);
	try
	{
		generate_file();
		success = true;
	}
	catch (int status)
	{
		delete_globals();
		if (status == 0)
			success = true;
	}
	catch (...)
	{
		delete_globals();
	}
	if (!success)
	{
		fprintf(stderr, "%s: Parsing %s failed\n", bin_name, file_t);
		return -2;
	}
	len_t = copy_rand(rand_t);
	start_t = rand_start;

	if (rand_start == UINT_MAX) {
		fprintf(stderr, "%s: Invalid position for insertion into file %s.\n", bin_name, file_t);
		fprintf(stderr, "Insertion can only happen at the start of an optional chunk or after the end of an appendable chunk/file.\n");
		return -2;
	}
	if (!optional_s) {
		fprintf(stderr, "%s: Trying to insert non-optional chunk from file %s.\n", bin_name, file_s);
		return -2;
	}
	
	printf("\nGenerating file %s\n\n", out);

	unsigned rand_size = len_t + (end_s + 1 - start_s);
	assert(rand_size <= MAX_RAND_SIZE);
	memmove(rand_t + start_t + end_s + 1 - start_s, rand_t + start_t, len_t - start_t);
	memcpy(rand_t + start_t, rand_s + start_s, end_s + 1 - start_s);

	get_chunk = false;
	smart_mutation = true;
	is_optional = true;
	unsigned rand_end0 = rand_end = start_t + end_s - start_s;
	set_generator();

	unsigned char* file = NULL;
	unsigned file_size = afl_pre_save_handler(rand_t, MAX_RAND_SIZE, &file);
	if (!file || !file_size) {
		printf("Failed to generate mutated file!\n");
		return -2;
	}
	save_output(out);
	if (rand_end0 < rand_end)
		fprintf(stderr, "Warning: Consumed %u more decision bytes than expected while generating chunk.\n", rand_end - rand_end0);
	if (rand_end0 > rand_end)
		fprintf(stderr, "Warning: Consumed %u less decision bytes than expected while generating chunk.\n", rand_end0 - rand_end);
	fprintf(stderr, "%s: %s created\n", bin_name, out);

	delete[] rand_t;
	delete[] rand_s;
	return (rand_end > rand_end0) - (rand_end < rand_end0);
}






int test(int argc, char *argv[])
{
	print_errors = true;
	int rand_fd = open("/dev/urandom", O_RDONLY);
	unsigned char *data = new unsigned char[MAX_RAND_SIZE];
	ssize_t r = read(rand_fd, data, MAX_RAND_SIZE);
	if (r != MAX_RAND_SIZE)
		printf("Read only %ld bytes from /dev/urandom\n", r);
	unsigned char *contents = new unsigned char[MAX_FILE_SIZE];
	unsigned char* file = NULL;
	size_t file_size;
	unsigned char* rand = NULL;
	size_t rand_size;
	size_t new_file_size;
	int generated = 0;
	int i;
	int iterations = 10000;
	uint64_t start = get_cur_time_us();
	for (i = 0; i < iterations; ++i)
	{
		ssize_t r = read(rand_fd, data, 4096);
		assert(r == 4096);
		file_size = afl_pre_save_handler(data, MAX_RAND_SIZE, &file);
		if (file_size && file) {
			generated += 1;
			bool parsed = afl_post_load_handler(file, file_size, &rand, &rand_size);
			assert(file_size <= MAX_FILE_SIZE);
			memcpy(contents, file, file_size);
			memset(file, 0, file_size);
			file = NULL;
			if (!parsed) {
				printf("Failed to parse!\n");
				break;
			}
			new_file_size = afl_pre_save_handler(rand, rand_size, &file);
			if (!file || !file_size) {
				printf("Failed to re-generate!\n");
				break;
			}
			if (file_size != new_file_size || memcmp(contents, file, file_size)) {
				printf("Re-generated file different from original file!\n");
				break;
			}
		}
	}
	if (i != iterations) {
		write_file("r0", data, MAX_RAND_SIZE);
		write_file("f0", contents, file_size);
		write_file("r1", rand, rand_size);
		if (file)
			write_file("f1", file, new_file_size);
	}
	uint64_t end = get_cur_time_us();
	double time = (end - start) / 1.0e6;
	printf("Tested %d files from %d attempts in %f s.\n", generated, i, time);
	delete[] data;
	delete[] contents;
	return 0;
}

int benchmark(int argc, char *argv[])
{
	int rand_fd = open("/dev/urandom", O_RDONLY);
	unsigned char *data =  new unsigned char[MAX_RAND_SIZE];
	ssize_t r = read(rand_fd, data, MAX_RAND_SIZE);
	if (r != MAX_RAND_SIZE)
		printf("Read only %ld bytes from /dev/urandom\n", r);
	unsigned char* new_data = NULL;
	int generated = 0;
	uint64_t total_bytes = 0;
	int i;
	int iterations = 10000;
	uint64_t start = get_cur_time_us();
	for (i = 0; i < iterations; ++i)
	{
		ssize_t r = read(rand_fd, data, 4096);
		assert(r == 4096);
		size_t new_size = afl_pre_save_handler(data, MAX_RAND_SIZE, &new_data);
		if (new_size && new_data) {
			generated += 1;
			total_bytes += new_size;
		}
	}
	uint64_t end = get_cur_time_us();
	double time = (end - start) / 1.0e6;
	printf("Generated %d files from %d attempts in %f s.\n", generated, i, time);
	if (generated)
		printf("Average file size %lu bytes.\n", total_bytes / generated);
	printf("Speed %f / s.\n", generated / time);
	delete[] data;
	return 0;
}

int version(int argc, char *argv[])
{
	fprintf(stderr, "This is %s\n", PACKAGE_STRING);
	return 0;
}

// Dispatch commands
typedef struct
{
	const char *name;
	int (*fun)(int argc, char **argv);
	const char *desc;
} COMMAND;

COMMAND commands[] = {
	{"fuzz", fuzz, "Generate random inputs"},
	{"parse", parse, "Parse inputs"},
	{"replace", smart_replace, "Apply a smart replacement"},
	{"delete", smart_delete, "Apply a smart deletion"},
	{"insert", smart_insert, "Apply a smart insertion"},
	{"test", test, "Test if fuzzer is working properly (sanity checks)"},
	{"benchmark", benchmark, "Benchmark fuzzing"},
	{"version", version, "Show version"},
};

int help(int argc, char *argv[])
{
	version(argc, argv);
	fprintf(stderr, "%s: usage: %s COMMAND [OPTIONS...] [ARGS...]\n", bin_name, bin_name);
	fprintf(stderr, "Commands:\n");
	for (unsigned i = 0; i < sizeof(commands) / sizeof(COMMAND); i++)
		fprintf(stderr, "%-10s - %s\n", commands[i].name, commands[i].desc);
	fprintf(stderr, "Use COMMAND --help to learn more\n");
	return 0;
}

int main(int argc, char **argv)
{
	bin_name = get_bin_name(argv[0]);
	if (argc <= 1)
		return help(argc, argv);

	char *cmd = argv[1];
	for (unsigned i = 0; i < sizeof(commands) / sizeof(COMMAND); i++)
	{
		if (strcmp(cmd, commands[i].name) == 0)
			return (*commands[i].fun)(argc - 1, argv + 1);
	}

	// Invalid command
	help(argc, argv);
	return -1;
}
