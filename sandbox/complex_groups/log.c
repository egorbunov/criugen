#include "log.h"

int __global_log_fd_val = -1;
pthread_mutex_t __global_log_fd_mutex_val;

int init_log(int fd) {
    __global_log_fd_val = fd;
    if (pthread_mutex_init(&__global_log_fd_mutex_val, NULL) != 0) {
    	return -1;
    }
    return 0;
}

void deinit_log() {
	close(__global_log_fd_val);
	pthread_mutex_destroy(&__global_log_fd_mutex_val);
}

int __global_log_fd() {
	return __global_log_fd_val;
}

pthread_mutex_t* __global_log_fd_mutex() {
	return &__global_log_fd_mutex_val;
}
