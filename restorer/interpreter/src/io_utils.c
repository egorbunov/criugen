#include "io_utils.h"

#include <limits.h>

#include <sys/types.h>
#include <unistd.h>

int io_read(int fd, char* buf, size_t count)
{
	ssize_t cnt;
	while (count != 0) {
		cnt = read(fd, buf, count);
		if (cnt <= 0 || cnt > SSIZE_MAX)
			return -1;
		buf += cnt;
		count -= cnt;
	}
	return 0;
}

int io_write(int fd, const char* buf, size_t count)
{
	ssize_t cnt;
	while (count != 0) {
		cnt = write(fd, buf, count);
		if (cnt <= 0)
			return -1;
		buf += cnt;
		count -= cnt;
	}
	return 0;
}