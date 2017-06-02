#include "socket.h"

#include <stdio.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>
#include <sys/un.h>

#include "io.h"


int create_unix_server_sock(const char* socket_name) {
	const int srv_backlog = 5;
	int socket_fd = 0;
	struct sockaddr_un addr;
	int res = 0;

	socket_fd = socket(AF_UNIX, SOCK_STREAM, 0);
	if (socket_fd < 0) {
	    return socket_fd;
	}

	memset(&addr, 0, sizeof(struct sockaddr_un));
	addr.sun_family = AF_UNIX;
	sprintf(addr.sun_path, "%s", socket_name);
	
	if (access(addr.sun_path, F_OK) == 0) {
		if ((res = unlink(addr.sun_path)) < 0) {
			return res;
		}
	}
	if ((res = bind(socket_fd, (struct sockaddr*) &addr, sizeof(struct sockaddr_un))) < 0) {
		return res;
	}
	if ((res = listen(socket_fd, srv_backlog)) < 0) {
		return res;
	}

	return socket_fd;
}

int create_unix_client_sock(const char* server_socket_name) {
	int socket_fd = 0;
	struct sockaddr_un addr;
	int res = 0;

	socket_fd = socket(AF_UNIX, SOCK_STREAM, 0);
	if (socket_fd < 0) {
	    return socket_fd;
	}

	memset(&addr, 0, sizeof(struct sockaddr_un));
	addr.sun_family = AF_UNIX;
	sprintf(addr.sun_path, "%s", server_socket_name);

	if ((res = connect(socket_fd, (struct sockaddr*) &addr, sizeof(struct sockaddr_un))) < 0) {
		return res;
	}

	return socket_fd;
}

int socket_send(int sock_fd, const char* bytes, size_t to_sent_cnt) {
	return io_write(sock_fd, bytes, to_sent_cnt);  // remember about MSG_NOSIGNAL
}

int socket_read(int sock_fd, char* dst, size_t to_read_cnt) {
	return io_read(sock_fd, dst, to_read_cnt);
}
