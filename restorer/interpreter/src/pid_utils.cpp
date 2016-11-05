#include "pid_utils.h"

#include <string.h>
#include <errno.h>
#include <stdlib.h>

#include <unistd.h>
#include <sys/file.h>
#include <sys/stat.h>
#include <fcntl.h>

#include "log.h"

int fork_pid(pid_t pid)
{
	const char* pid_file = "/proc/sys/kernel/ns_last_pid";

	// TODO: do we need to save old value from pid file and restore it after forking?
	int fd = open(pid_file, O_RDWR | O_CREAT, 0644);
	if (fd < 0) {
		log::log_stderr("Can't open pid file");
		return -1;
	}
	
	if (flock(fd, LOCK_EX)) {
		log::log_stderr("Can't lock pid file");
		close(fd);
		return -1;
	}
	char buf[32];
	snprintf(buf, sizeof(buf), "%d", pid - 1);
	if (write(fd, buf, strlen(buf)) != (ssize_t) strlen(buf)) {
		log::log_stderr("Can't write pid file");
		close(fd);
		return -1;
	}
	int pipefd[2];
	if (pipe(pipefd) < 0) {
		log::log_stderr("Can't open pipe");
		close(fd);
		return -1;
	}
	// forking
	int ret = 0;
	pid_t new_pid = fork();
	if (new_pid < 0) {
		log::log_stderr("Can't fork");
		close(fd);
		close(pipefd[0]);
		close(pipefd[1]);
	} else if (new_pid != 0) {
		close(pipefd[0]);
		ret = new_pid;
		if (flock(fd, LOCK_UN)) {
			log::log_stderr("Can't unlock pid file");
			ret = -1;
		}
		close(fd);
		if (ret != -1 && new_pid != pid) {
			log::log_error("Forked [ %d ] instead of [ %d ]", new_pid, pid);
			ret = -1;
		}
		if (write(pipefd[1], &ret, sizeof(ret)) != sizeof(ret)) {
			log::log_stderr("Can't write to pipe");
			ret = -1;
		}
		close(pipefd[1]);
		return ret;
	} else {
		close(fd);
		close(pipefd[1]);
		if (read(pipefd[0], &ret, sizeof(ret)) != sizeof(ret))
			log::log_stderr("Can't read from pipe");
		if (ret < 0) {
			log::log_info("Exiting from child due to parent err");
			exit(1);
		}
		close(pipefd[0]);
		return 0;
	}
	return -1;
}