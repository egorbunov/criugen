#include "io.h"

#include <stdlib.h>

#include <unistd.h>


int io_write(int fd, const char* bytes, size_t to_sent_cnt) {
	int res = 0;

	while (to_sent_cnt != 0) {
		res = write(fd, (void*) bytes, to_sent_cnt);
		if (res < 0) {
			return res;
		}
		to_sent_cnt -= res;
		bytes += res;
	}
	return 0;
}

int io_read(int fd, char* dst, size_t to_read_cnt) {
	int res = 0;

	while (to_read_cnt != 0) {
		res = read(fd, (void*) dst, to_read_cnt);
		if (res < 0) {
			return res;
		}
		dst += res;
		to_read_cnt -= res;
	}

	return 0;
}

int io_write_int32(int fd, int32_t val) {
	return io_write(fd, (char*) &val, sizeof(int32_t));
}

int io_read_int32(int fd, int32_t* val) {
	return io_read(fd, (char*) val, sizeof(int32_t));
}
