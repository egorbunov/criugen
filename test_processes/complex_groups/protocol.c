#include "protocol.h"

#include <unistd.h>

#include <stdint.h>

#include "socket.h"


setpgid_msg construct_setpgid_msg(uint32_t pid, uint32_t pgid) {
	return (setpgid_msg) { 
		.pid = pid, 
		.pgid = pgid 
	};
}

// send functions
static int send_msg_of_type(int socket_fd, message_type type, char* msg, size_t size) {
	int res;

	res = socket_send(socket_fd, (char*) &type, sizeof(message_type));
	if (res < 0) {
		return res;
	}
	return socket_send(socket_fd, msg, size);
}


// no serialization beacuse we want to use it on the same machine	
int send_setpgid_msg(int socket_fd, setpgid_msg msg) {
	return send_msg_of_type(socket_fd, MSG_SETPGID, (char*) &msg, sizeof(msg));
}

int send_fork_msg(int socket_fd) {
	return send_msg_of_type(socket_fd, MSG_FORK, NULL, 0);
}

int send_finsih_msg(int socket_fd) {
	return send_msg_of_type(socket_fd, MSG_FINISH, NULL, 0);
}

static int send_int32(int socket_fd, int32_t response) {
	return socket_send(socket_fd, (char*) &response, sizeof(int32_t));
}

static int recv_int32(int socket_fd, int32_t* response) {
	return socket_read(socket_fd, (char*) response, sizeof(int32_t));
}

int send_response(int socket_fd, int32_t response) {
	return send_int32(socket_fd, response);
}

// read functions

int recv_response(int socket_fd, int32_t* response) {
	return recv_int32(socket_fd, response);
}

int recv_msg_type(int socket_fd, message_type* type_dst) {
	return socket_read(socket_fd, (char*) type_dst, sizeof(message_type));
}

int recv_setpgid_msg(int socket_fd, setpgid_msg* dst) {
	return socket_read(socket_fd, (char*) dst, sizeof(setpgid_msg));
}

int perfom_handshake_client(int socket_fd) {
	int32_t my_pid = getpid();
	int32_t res = 0;

	if (my_pid < 0) {
		return my_pid;
	}

	if (send_int32(socket_fd, my_pid) < 0) {
		return -1;
	}

	if (recv_response(socket_fd, &res) < 0) {
		return -1;
	}

	return res;
}

int handshake_peer_pid(int socket_fd) {
	int32_t peer_pid;

	if (recv_int32(socket_fd, &peer_pid) < 0) {
		return -1;
	}

	return peer_pid;
}

int finish_handshake_server(int socket_fd, int32_t res) {
	if (send_response(socket_fd, res) < 0) {
		return -1;
	}
	return 0;
}

int finalize_connection(int socket_fd) {
	int res;

	if (send_finsih_msg(socket_fd) < 0) {
		return -1;
	}

	if (recv_response(socket_fd, &res) < 0) {
		return -1;
	}

	return 0;
}