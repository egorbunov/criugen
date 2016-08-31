#include <stdio.h>
#include <stdlib.h>

#include "parse.h"
#include "program.h"

void print_usage(void)
{
	printf("USAGE: ./interpreter '/path/to/program.json'\n");
}

int main(int argc, char* argv[])
{
	struct program* p;

	if (argc < 2) {
		print_usage();
		return 0;
	}

	p = prog_create();
	if (parse_program(argv[1], p) < 0) {
		printf("Error: can't parse json file with program\n");
		return -1;		
	}
	prog_print(p);
	prog_delete(p);
	return 0;
}