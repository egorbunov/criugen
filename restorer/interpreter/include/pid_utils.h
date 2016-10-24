#ifndef PID_UTILS_H_INCLUDED__
#define PID_UTILS_H_INCLUDED__

#include <sys/types.h>

/**
 * linux fork() extension to fork with particular pid
 */
int fork_pid(pid_t);

#endif