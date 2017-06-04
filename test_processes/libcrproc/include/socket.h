#ifndef SOCKET_H_INCLUDED__
#define SOCKET_H_INCLUDED__

#include <stdio.h>


/**
  socket_name is truncated in case it is too big for address len
**/
int create_unix_server_sock(const char* socket_name);

int create_unix_client_sock(const char* server_socket_name);

int socket_send(int sock_fd, const char* bytes, size_t to_sent_cnt);

int socket_read(int sock_fd, char* dst, size_t to_read_cnt);

#endif
