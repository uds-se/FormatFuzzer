// Fuzzer.cpp
// Main driver for FormatFuzzer

#include <cstdio>
#include <cstring>
#include <cassert>
#include <getopt.h>

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
		int c = getopt_long(argc, argv, "r:",
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

	// Main function
	setup_input(decision_source);
	int errors = 0;
	for (int arg = optind; arg < argc; arg++)
	{
		char *out = argv[arg];
		bool success = false;
		try
		{
			generate_file();
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
		int c = getopt_long(argc, argv, "r:",
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

	int errors = 0;
	for (int arg = optind; arg < argc; arg++)
	{
		char *in = argv[arg];
		bool success = true;

		set_parser();
		setup_input(in);
		try
		{
			generate_file();
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
	{"version", version, "Show version"},
};

int help(int argc, char *argv[])
{
	version(argc, argv);
	fprintf(stderr, "%s: usage: %s COMMAND [OPTIONS...] [ARGS...]\n", bin_name, bin_name);
	fprintf(stderr, "Commands:\n");
	for (int i = 0; i < sizeof(commands) / sizeof(COMMAND); i++)
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
	for (int i = 0; i < sizeof(commands) / sizeof(COMMAND); i++)
	{
		if (strcmp(cmd, commands[i].name) == 0)
			return (*commands[i].fun)(argc - 1, argv + 1);
	}

	// Invalid command
	help(argc, argv);
	return -1;
}