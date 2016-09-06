#ifndef IO_UTILS_H_INCLUDED__
#define IO_UTILS_H_INCLUDED__

#include <stddef.h>

int io_read(int fd, char* buf, size_t count);

int io_write(int fd, const char* buf, size_t count);

#endif