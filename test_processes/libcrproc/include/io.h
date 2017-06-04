#ifndef IO_H_INCLUDED__
#define IO_H_INCLUDED__

#include <stdio.h>
#include <stdint.h>

int io_write(int fd, const char* bytes, size_t to_sent_cnt);
int io_read(int sock_fd, char* dst, size_t to_read_cnt);

int io_write_int32(int fd, int32_t val);
int io_read_int32(int fd, int32_t* val);

#endif
