// Fuzzer.cpp
// Main driver for FormatFuzzer

#include <cstdio>
#include <cstring>
#include <cassert>

#include "formatfuzzer.h"

int fuzz(int argc, char **argv)
{
	assert(argc == 3);
	setup_input(argv[1]);
	try
	{
		generate_file();
	}
	catch (...)
	{
		delete_globals();
		fprintf(stderr, "%s failed\n", get_bin_name(argv[0]));
		save_output(argv[2]);
		return -1;
	}
	save_output(argv[2]);
	fprintf(stderr, "%s finished\n", get_bin_name(argv[0]));
	return 0;
}

int parse(int argc, char **argv)
{
	assert(argc == 3);
	set_parser();
	setup_input(argv[1]);
	try
	{
		generate_file();
	}
	catch (...)
	{
		delete_globals();
		fprintf(stderr, "%s failed\n", get_bin_name(argv[0]));
		save_output(argv[2]);
		return -1;
	}
	save_output(argv[2]);
	fprintf(stderr, "%s finished\n", get_bin_name(argv[0]));
	return 0;
}

typedef struct
{
	const char *name;
	int (*fun)(int argc, char **argv);
} COMMAND;

COMMAND commands[] = {
	{"fuzz", fuzz},
	{"parse", parse},
};

static char *bin_name;

int help(int argc, char *argv[])
{
	fprintf(stderr, "%s: usage: %s COMMAND\n", bin_name, bin_name);
	fprintf(stderr, "where COMMAND is one of \n");
	for (int i = 0; i < sizeof(commands) / sizeof(COMMAND); i++)
		fprintf(stderr, "`%s' ", commands[i].name);
	fprintf(stderr, "\n");
	fprintf(stderr, "Use COMMAND --help to learn more\n");
	return 0;
}

// Dispatch commands
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