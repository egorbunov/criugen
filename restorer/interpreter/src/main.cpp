#include <vector>

#include <cstdio>
#include <cstdlib>
#include <cstring>

#include <libgen.h>

#include <linux/limits.h>
#include <unistd.h>

#include "parse.h"
#include "command/command.h"
#include "interpreter.h"
#include "log.h"

void print_usage(void)
{
	printf("USAGE: ./interpreter '/path/to/program.json'\n");
}

int main(int argc, char* argv[])
{
	if (argc < 2) {
		print_usage();
		return 0;
	}

	// init logging
   	char buf[PATH_MAX];
	sprintf(buf, "%s/zlog.conf", dirname(argv[0]));
	if (log_init(buf)) {
		printf("Error initializing log\n");
		printf("Config file path: %s\n", buf);
		return -1;
	}
	
	// parsing program and starting interpreter...
	std::vector<command> program;
	int ret = parse_program(argv[1], program);
	if (ret < 0) {
		printf("Error: can't parse json file with program\n");
		return -1;
	}

	interpreter_run(&program[0], program.size());

	// clean program
	for (auto& c : program) {
		free(c.c);
	}

	log_fini();

	return 0;
}
