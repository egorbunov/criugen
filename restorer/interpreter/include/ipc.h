#pragma once

#include <sys/types.h>

/**
 * Opens socket with name generated for given pid
 * Logic is simple: returned socket fd should be used for
 * ipc between master interpreter process and process with that
 * pid
 * @return    fd of opened socket or -1 in case of error
 */
int socket_open(pid_t pid);

/**
 * Connects to socket, which was previously opened with
 * call to `socket_open(pid)`
 * @return     fd of socket or -1 in case of error
 */
int socket_connect(pid_t pid);