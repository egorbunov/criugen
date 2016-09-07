#include "fd_utils.h"

#include <errno.h>

#include <fcntl.h>
#include <unistd.h>


int move_fd(int old_fd, int new_fd)
{
	if (old_fd == new_fd)
		return 0;
	if (fcntl(new_fd, F_GETFD) > 0 || errno != EBADF)
		return -1;
	if (dup2(old_fd, new_fd) < 0 || close(old_fd) < 0) 
		return -2;
	return 0;	
}
