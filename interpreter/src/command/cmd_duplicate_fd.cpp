#include "command/cmd_duplicate_fd.h"

#include "log.h"

#include <unistd.h>

using namespace log;

const char* cmd_duplicate_fd::tag = "DUP_FD";

int cmd_duplicate_fd::execute() {
	if (dup2(old_fd, new_fd) < 0) {
		log_stderr("Can't dup fd [ %d ] to [ %d ]", old_fd, new_fd);
		return -1;
	}
	return 0;
}
