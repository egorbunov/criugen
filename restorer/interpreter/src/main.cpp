#include <stdio.h>
#include <stdlib.h>
#include <string.h>
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
	command_vec program;
	struct command c;
	int i;
   	char buf[PATH_MAX];

	if (argc < 2) {
		print_usage();
		return 0;
	}

	// init logging
	sprintf(buf, "%s/zlog.conf", dirname(argv[0]));
	if (log_init(buf)) {
		printf("Error initializing log\n");
		printf("Config file path: %s\n", buf);
		return -1;
	}
	
	// parsing program and starting interpreter...
	vec_init(&program);
	if (parse_program(argv[1], &program) < 0) {
		printf("Error: can't parse json file with program\n");
		return -1;		
	}

	interpreter_run(&program);

	// finalizing
	vec_foreach(&program, c, i) {
		free(c.c);
	}
	vec_deinit(&program);

	log_fini();

	return 0;
}
