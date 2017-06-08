#include "command/cmd_reg_open.h"

#include "log.h"
#include "fd_utils.h"

#include <fcntl.h>
#include <unistd.h>

using namespace log;

const char* cmd_reg_open::tag = "REG_OPEN";

int cmd_reg_open::execute() {
	int file_fd = open(path, flags, mode);
	if (file_fd < 0) {
		log_stderr("Can't open file");
		return -1;
	}
	log_info("opened reg file at [ %d ]; moving to [ %d ]", file_fd, fd);
	int ret = move_fd(file_fd, fd);
	if (ret < 0) {
		log_stderr("Can't move fd [move_fd exit code = %d]", ret);
		return -1;
	}
	if (lseek(fd, offset, SEEK_SET) < 0) {
		log_stderr("Can't lseek");
		return -1;
	}
	return 0;
}
