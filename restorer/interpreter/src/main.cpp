#include <vector>
#include <iostream>
#include <fstream>

#include <cstdio>
#include <cstdlib>
#include <cstring>

#include <libgen.h>

#include <linux/limits.h>
#include <unistd.h>

#include "log.h"
#include "parse.h"
#include "restorer.h"

void print_usage(void)
{
	printf("USAGE: ./interpreter '/path/to/program.json' -l 'path/to/log.file'\n");
}

int main(int argc, char* argv[])
{
	std::string log_file = "";
	std::string program_file = "";

	for (int i = 1; i < argc; ++i) {
		if (strcmp("-l", argv[i]) == 0) {
			if (++i == argc) {
				std::cout << "ERROR: no log file specified after key '-l'!" << std::endl;
				print_usage();
				return -1;
			}
			log_file = argv[i];
		} else {
			program_file = argv[i];
		}
	}

	if (program_file.empty() || log_file.empty()) {
		std::cout << "ERROR: bad args!" << std::endl;
		print_usage();
		return -1;
	}

	log::log_setup(log_file);
	std::ifstream in(program_file);
	std::vector<std::shared_ptr<command>> program;
	if (parse_program(in, program) < 0) {
		std::cout << "ERROR: Can't parse program!" << std::endl;
		return -1;
	}

	restorer r(program);
	r.run();
	
	return 0;
}
