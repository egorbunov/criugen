#pragma once

#include <stddef.h>

template<T>
int io_read(int fd, T* t);

template<T>
int io_write(int fd, const T& t);

int io_read(int fd, char* buf, size_t count);

int io_write(int fd, const char* buf, size_t count);
