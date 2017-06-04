#ifndef CR_ENV_H_INCLUDED__
#define CR_ENV_H_INCLUDED__

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

#include "log.h"
#include "utils.h"

/**
 * Daemonizes and initializes log file from arguments
**/
void init_restorable_process_tree(int argc, char* argv[]) {
	int log_fd = 0;
	char* log_file = "log.txt";

	if (argc <= 1) {
		printf("%s\n", "No log file specified, will use `log.txt' in current working dir");
	} else {
		log_file = argv[1];
	}

	log_fd = open(log_file, O_CREAT | O_TRUNC | O_RDWR, 0666);
    if (log_fd < 0) {
        perror("Open log failed");
        exit(2);
    }
	init_log(log_fd);

	srand(time(NULL));
	daemonize();
	log_important("%d", getpid());
}

void ready_to_dump() {
	log_important("FINISH");
}

void deinit_cr() {
	deinit_log();
}

#endif