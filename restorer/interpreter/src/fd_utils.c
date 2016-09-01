#include "fd_utils.h"

#include <errno.h>

#include <fcntl.h>
#include <unistd.h>

int move_fd(int old_fd, int new_fd)
{
	int ret;
	if (ret = fcntl(new_fd, F_GETFD), ret > 0 || errno != EBADF) {
		return -1;
	}
	if (dup2(old_fd, new_fd) < 0 || close(old_fd) < 0) 
		return -1;
	return 0;
}
