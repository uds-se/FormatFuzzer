// Fuzzer.cpp
// Main driver for FormatFuzzer

#include <cstdio>
#include <cstring>
#include <cassert>
#include <getopt.h>
#include <stdint.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <fcntl.h>

#include "config.h"
#include "formatfuzzer.h"

static const char *bin_name = "formatfuzzer";

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
		int c = getopt_long(argc, argv, "d:",
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
			return 0;

		case 'd':
			decision_source = optarg;
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

#define MAX_RAND_SIZE 65536

int test(int argc, char *argv[])
{
	print_errors = true;
	int rand_fd = open("/dev/urandom", O_RDONLY);
	unsigned char data[MAX_RAND_SIZE];
	ssize_t r = read(rand_fd, data, MAX_RAND_SIZE);
	assert(r == MAX_RAND_SIZE);
	unsigned char contents[65536];
	unsigned char* file = NULL;
	size_t file_size;
	unsigned char* rand = NULL;
	size_t rand_size;
	size_t new_file_size;
	int generated = 0;
	int i;
	uint64_t start = get_cur_time_us();
	for (i = 0; i < 10000; ++i)
	{
		ssize_t r = read(rand_fd, data, 4096);
		assert(r == 4096);
		file_size = afl_pre_save_handler(data, MAX_RAND_SIZE, &file);
		if (file_size && file) {
			generated += 1;
			bool parsed = afl_post_load_handler(file, file_size, &rand, &rand_size);
			assert(file_size <= 65536);
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
	if (i != 10000) {
		write_file("r0", data, MAX_RAND_SIZE);
		write_file("f0", contents, file_size);
		write_file("r1", rand, rand_size);
		if (file)
			write_file("f1", file, new_file_size);
	}
	uint64_t end = get_cur_time_us();
	double time = (end - start) / 1.0e6;
	printf("Tested %d files from %d attempts in %f s.\n", generated, i, time);
	return 0;
}

int benchmark(int argc, char *argv[])
{
	int rand_fd = open("/dev/urandom", O_RDONLY);
	unsigned char data[MAX_RAND_SIZE];
	ssize_t r = read(rand_fd, data, MAX_RAND_SIZE);
	assert(r == MAX_RAND_SIZE);
	unsigned char* new_data = NULL;
	int generated = 0;
	uint64_t total_bytes = 0;
	int i;
	uint64_t start = get_cur_time_us();
	for (i = 0; i < 10000; ++i)
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
