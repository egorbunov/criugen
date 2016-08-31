#include <stdio.h>
#include <stdlib.h>

#include "parse.h"
#include "command.h"
#include "interpreter.h"

void print_usage(void)
{
	printf("USAGE: ./interpreter '/path/to/program.json'\n");
}

int main(int argc, char* argv[])
{
	command_vec program;
	struct command c;
	int i;

	if (argc < 2) {
		print_usage();
		return 0;
	}

	vec_init(&program);
	if (parse_program(argv[1], &program) < 0) {
		printf("Error: can't parse json file with program\n");
		return -1;		
	}

	vec_foreach(&program, c, i) {
		print_cmd(&c);
	}

	interpreter_run(&program);

	vec_foreach(&program, c, i) {
		free(c.c);
	}
	vec_deinit(&program);
	return 0;
}
