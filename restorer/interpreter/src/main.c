#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <linux/limits.h>

#include <zlog.h>
#include <libgen.h>

#include "parse.h"
#include "command.h"
#include "interpreter.h"

// global logging category
zlog_category_t* g_log;

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
	if (zlog_init(buf)) {
		printf("Error initializing log\n");
		printf("Config file path: %s\n", buf);
		return -1;
	}
	g_log = zlog_get_category("interpreter_cat");
	if (!g_log) {
		printf("Error getting log category %s", "interpreter_cat");
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
	zlog_fini();

	return 0;
}
