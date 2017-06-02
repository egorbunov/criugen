#include <string.h>
#include <stdlib.h>
#include <errno.h>
#include <stdio.h>
#include <stdarg.h>
#include <stdint.h>

#include <inttypes.h>

#include <unistd.h>
#include <linux/sched.h>
#include <sys/wait.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <time.h>


#include <sys/mman.h>

#include <pthread.h>

#include "utils.h"

void run(void);

int main(int argc, char* argv[])
{
	srand(time(NULL));
	if (argc > 1) {
		init_log(argv[1]);
	} else {
		printf("%s\n", "No log file specified, continue without logging.");
	}
	daemonize();
	add_log("%d", getpid());

	run();
	

	sleep(100);
	return 0;
}

void run(void) {
	// forking first child
	int child_1_pid;
	int child_2_pid;
	int root_pid;
	int root_pgid;
	int res;
	// at first we fork not to be session leader
	res = fork();
	if (res < 0) {
		log_error("fork, %s", strerror(errno));
		exit(1);
	}
	if (res != 0) {
		sleep(100);
		return;
	}

	// not session leader continues here


	root_pid = getpid();
	root_pgid = getpgid(0);
	if (root_pgid != root_pid) {
		if (setpgid(0, 0) < 0) {
			log_error("setpgid root init [%s]", strerror(errno));
			exit(1);
		}
		root_pgid = root_pid;
	}

	child_1_pid = fork();
	if (child_1_pid < 0) {
		perror("fork");
		exit(1);
	}
	if (child_1_pid == 0) {
		sleep(100);
		return;
	}
	if (setpgid(child_1_pid, child_1_pid) < 0) {
		log_error("%s, [%s]", "setpgid child 1", strerror(errno));
		exit(1);
	}

	child_2_pid = fork();
	if (child_2_pid < 0) {
		perror("fork");
		exit(1);
	}
	if (child_2_pid == 0) {
		add_log("init = %d", getpgid(0));
		add_log("child 2 pid = %d", getpid());
		while (getpgid(0) != getpid()) {
			// pass
		}
		exit(0);	
	}

	if (setpgid(child_2_pid, child_1_pid) < 0) {
		log_error("%s, [%s]", "setpgid child2 to child 1 group", strerror(errno));
		exit(1);
	}
	add_log("setting child 1 group to: %d", root_pgid);
	if (setpgid(child_1_pid, root_pgid) < 0) {
		log_error("%s, [%s]", "setpgid child 1 to root group", strerror(errno));
		exit(1);
	}
	add_log("setting root group to: %d", child_1_pid);
	if (setpgid(0, child_1_pid) < 0) {
		log_error("%s, [%s]", "setpgid root to group child 1", strerror(errno));
		exit(1);
	}
	add_log("setting group of child 2 to: %d", child_2_pid);
	if (setpgid(child_2_pid, child_2_pid) < 0) { // just to 
		log_error("%s, [%s]", "setpgid child 2 to finish", strerror(errno));
		exit(1);
	}

	add_log("gid of %d = %d", getpid(), getpgid(0));
	add_log("gid of %d = %d", child_1_pid, getpgid(child_1_pid));

	add_log("waiting for %d", child_2_pid);
	if (waitpid(child_2_pid, NULL, 0) < 0) {
		log_error("wait; %s", strerror(errno));
	}
	add_log("FINISH");
	wait(NULL);

	return;
}
