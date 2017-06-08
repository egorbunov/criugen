#include "command/cmd_close_fd.h"

#include "log.h"

#include <unistd.h>

using namespace log;

const char* cmd_close_fd::tag = "CLOSE_FD";

int cmd_close_fd::execute() {
	if (close(fd) < 0) {
		log_stderr("Can't close fd [ %d ]", fd);
		return -1;
	}
	return 0;
}
