#pragma once

#include <sys/types.h>

/**
 * linux fork() extension to fork with particular pid
 */
int fork_pid(pid_t);
