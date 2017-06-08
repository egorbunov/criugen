#pragma once

#include <cstddef>

int io_read(int fd, char* buf, size_t count);

int io_write(int fd, const char* buf, size_t count);

template<typename T>
int io_read(int fd, T* t) {
	return io_read(fd, static_cast<char*>(static_cast<void*>(t)), sizeof(T));
}

template<typename T>
int io_write(int fd, const T& t) {
	return io_write(fd, static_cast<const char*>(static_cast<const void*>(&t)), sizeof(T));
}
