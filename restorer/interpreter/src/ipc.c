#include "ipc.h"

#include <stdio.h>

#include <sys/un.h>
#include <sys/socket.h>
#include <unistd.h>

static struct sockaddr_un get_socket_addr(pid_t pid)
{
	struct sockaddr_un addr;
	addr.sun_family = AF_UNIX;
	sprintf(addr.sun_path, "/tmp/restorer_helper_%d", pid);
	return addr;
}

int socket_open(pid_t pid)
{
	const int srv_backlog = 100;
	int fd;
	struct sockaddr_un addr;

	if ((fd = socket(AF_UNIX, SOCK_STREAM, 0)) < 0)
	    return -1;
	memset(&addr, 0, sizeof(struct sockaddr_un));
	addr = get_socket_addr(pid);
	if (access(addr.sun_path, F_OK) == 0)
		if (unlink(addr.sun_path) < 0)
			return -1;
	if (bind(fd, (struct sockaddr*) &addr, sizeof(struct sockaddr_un)) < 0)
		return -1;
	if (listen(fd, srv_backlog) < 0)
		return -1;
	return fd;
}

int socket_connect(pid_t pid)
{
	struct sockaddr_un addr;
	int fd;

	if ((fd = socket(AF_UNIX, SOCK_STREAM, 0)) < 0)
	    return -1;
	memset(&addr, 0, sizeof(struct sockaddr_un));
	addr = get_socket_addr(pid);
	if (connect(fd, (struct sockaddr*) &addr, sizeof(struct sockaddr_un)) < 0)
		return -1;
	return fd;
}
