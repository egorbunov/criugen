#ifndef PROTOCOL_H_INCLUDED__
#define PROTOCOL_H_INCLUDED__

#include <stdint.h>

#include "socket.h"

// messages

typedef enum {
	MSG_SETPGID,
	MSG_SETSID,
	MSG_FORK,
	MSG_FINISH
} message_type;


typedef struct {
	uint32_t pid;
	uint32_t pgid;
} setpgid_msg;


// constructors

setpgid_msg construct_setpgid_msg(uint32_t pid, uint32_t pgid);


// send command functions

int send_setpgid_msg(int socket_fd, setpgid_msg msg);

int send_fork_msg(int socket_fd);

int send_finsih_msg(int socket_fd);

int send_setsid_msg(int socket_fd);


// send response functions

int send_response(int socket_fd, int32_t response);


// read functions

int recv_response(int socket_fd, int32_t* response);

int recv_msg_type(int socket_fd, message_type* type_dst);

int recv_setpgid_msg(int socket_fd, setpgid_msg* dst);

// handshake

int perfom_handshake_client(int socket_fd);

/**
 * Invoked by server as first part of the handshake
 */
int handshake_peer_pid(int socket_fd);

/**
 * Second part of the handshake (invoked by server)
 */
int finish_handshake_server(int socket_fd, int res);


// initiated by server
int finalize_connection(int socket_fd);

#endif
