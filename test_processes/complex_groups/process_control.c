#include "process_control.h"

#include <unistd.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <signal.h>

#include <stdlib.h>
#include <string.h>
#include <stdio.h>

#include "io.h"
#include "log.h"
#include "socket.h"
#include "protocol.h"


typedef struct {
	int connected_pid;
	int sock_fd;
} connection;

static pthread_rwlock_t g_slave_connections_lock;
static char g_master_socket_name[100];

#define G_MAX_CONNECTIONS 1000

static int g_master_socket = 0;
static int g_root_master_conn = 0;
static size_t g_connections_cnt = 0;
// array with socket connections to slave processes
static connection g_slave_connections[G_MAX_CONNECTIONS];

static pthread_t g_listener_thread;
static pthread_t g_master_slave_thread;

static void* master_thread_fun(void*);
static void* master_slave_thread_fun(void*);

static int add_new_connection(int pid, int fd);

static int connect_to_master();
static void run_process_node(int);


int init_process_contol() {
	log_info("Initializing process control");

	memset(g_master_socket_name, 0, sizeof(g_master_socket_name));
	sprintf(g_master_socket_name, "/tmp/%d-master", getpid());

	// init rw lock
	if (pthread_rwlock_init(&g_slave_connections_lock, NULL) != 0) {
		log_sys_error("Can't initialize pthread rw lock");
		return -1;
	}

	g_master_socket = create_unix_server_sock(g_master_socket_name);
	if (g_master_socket < 0) {
		log_sys_error("Can't create master unix sk");
		return -1;
	}

	if (pthread_create(&g_listener_thread, NULL, master_thread_fun, NULL) != 0) {
		log_sys_error("Can't start listener thread");
		return -1;
	}

	// first we connecting to master (actually we connect this process to itself)
	g_root_master_conn = connect_to_master();


	if (pthread_create(&g_master_slave_thread, NULL, master_slave_thread_fun, &g_root_master_conn) != 0) {
		log_sys_error("Can't start master-slave thread");
		return -1;
	}

	log_info("Finish initialization of process control");
	return 0;
}

void deinit_process_contol() {
	int res = 0;

	log_info("Destroying process control");

	for (int i = 0; i < g_connections_cnt; ++i) {
		if (finalize_connection(g_slave_connections[i].sock_fd) < 0) {
			log_sys_error("Failed to fianlize (%d, %d)", g_slave_connections[i].connected_pid, g_slave_connections[i].sock_fd);
			res = -1;
		} else {
			g_slave_connections[i].connected_pid = -1; // mark as finalized
		}

		shutdown(g_slave_connections[i].sock_fd, SHUT_RDWR);
	}

	// if we close server socket before client sockets,
	// that would spoil other client sockets: TODO: is that because of unix domain socks?
	shutdown(g_master_socket, SHUT_RDWR);

	if (res < 0) {
		log_error("Failed to finalize all connections, killing all slaves!!!");
		for (int i = 0; i < g_connections_cnt; ++i) {
			int pid = g_slave_connections[i].connected_pid;
			if (pid < 0) continue;
			if (kill(pid, SIGKILL) < 0) {
				log_sys_error("Failed to kill slave %d", pid);
			}
		}
		exit(1);
	}

	log_info("Waiting for listener thread");
	pthread_join(g_listener_thread, NULL);
	log_info("Waiting for slave master");
	pthread_join(g_master_slave_thread, NULL);
	log_info("Destroying rwlock");
	pthread_rwlock_destroy(&g_slave_connections_lock);
}

static void close_all_connections_fds(void);
static int find_connection(int pid, connection* dst);

/**
 * @return pid of forked child be executor_pid process, negative in case of error
 */
int pc_fork(int executor_pid) {
	connection conn;
	int32_t executor_child_pid;
	int sock = 0;

	find_connection(executor_pid, &conn);
	if (conn.connected_pid < 0) {
		log_error("No such executor: [%d]", executor_pid);
		return -42;
	}
	sock = conn.sock_fd;

	if (send_fork_msg(sock) < 0) {
		log_sys_error("Can't send fork msg");
		return -1;
	}

	if (recv_response(sock, &executor_child_pid) < 0) {
		log_sys_error("Can't recv response");
		return -1;
	}

	return executor_child_pid;
}

/**
 * @param executor_pid -- pid of the process, which will execute setpgid(pid, pgid)
 * @return 0 on success (command was executed suuccesfully), 
 *         negative on failure (failure may occur on this side ot on the
 * 		   side of the executor)
 */
int pc_setpgid(int executor_pid, uint32_t pid, uint32_t pgid) {
	connection conn;
	int sock = 0;
	int32_t response = 0;

	find_connection(executor_pid, &conn);
	if (conn.connected_pid < 0) {
		log_error("No such executor!");
		return -42;
	}
	sock = conn.sock_fd;

	if (send_setpgid_msg(sock, construct_setpgid_msg(pid, pgid)) < 0) {
		log_sys_error("Can't send setpgid msg");
		return -1;
	}

	if (recv_response(sock, &response) < 0) {
		log_sys_error("Can't recv response");
		return -1;
	}

	return response;
}

/**
 * Send finish message to process with executor_pid
 */
int pc_finish(int executor_pid) {
	connection conn;
	int sock = 0;
	int32_t response = 0;

	find_connection(executor_pid, &conn);
	if (conn.connected_pid < 0) {
		log_error("No such executor!");
		return -42;
	}
	sock = conn.sock_fd;

	if (send_finsih_msg(sock) < 0) {
		log_sys_error("Can't send finish msg");
		return -1;
	}

	if (recv_response(sock, &response) < 0) {
		log_sys_error("Can't recv response");
		return -1;
	}

	return response;
}


// slave stuff

static int process_setpgid(int sock);
static int process_fork(int sock);

// process slave function
static void run_process_node(int master_conn_sock) {
	int res;
	message_type msg_type;

	while (1) {
		if (recv_msg_type(master_conn_sock, &msg_type) < 0) {
			log_sys_error("[slave] Can't recv message type");
			log_info("[slave] Exiting...");
			break;
		}

		res = 0;

		switch (msg_type) {
			case MSG_SETPGID: {
				log_info("[slave] Got setpgid request");
				res = process_setpgid(master_conn_sock);
				break;
			}
			case MSG_FORK: {
				log_info("[slave] Got fork request");
				res = process_fork(master_conn_sock);
				break;
			}
			case MSG_FINISH: {
				log_info("[slave] Got finish request");
				log_info("[slave] Finishing");
				res = 0;
				break;
			}
			default: {
				log_error("[slave] Got unknown command: %d", msg_type);
				res = -1;
				break;
			}
		}

		// sending response!
		if (send_response(master_conn_sock, res) < 0) {
			log_sys_error("[slave] Can't send response");
			log_info("[slave] Exiting");
			break;
		}

		if (msg_type == MSG_FINISH) {
			goto finish;
		}
	}

finish:
    log_info("[slave] Goodbye, master!");
	close(master_conn_sock);
	return;
}

static int connect_to_master() {
	int new_sock = create_unix_client_sock(g_master_socket_name); // do we need fence here?
	if (new_sock < 0) {
		log_sys_error("[slave] Can't create unix client sock");
		return -1;
	}

	if (perfom_handshake_client(new_sock) < 0) {
		log_sys_error("[slave] Handshake failed");
		close(new_sock);
		return -1;
	}

	return new_sock;
}

static int process_setpgid(int sock) {
	setpgid_msg m;
	int32_t res = 0;

	if (recv_setpgid_msg(sock, &m) < 0) {
		log_sys_error("[slave] Can't recv setpgid msg");
		res = -1;
	}

	if (setpgid(m.pid, m.pgid) < 0) {
		log_sys_error("[slave] Can't run command setpgid(%d, %d)", m.pid, m.pgid);
		res = -1;
	}

	return res;
}

static int process_fork(int sock) {
	int pipefd[2];
	int32_t child_pid;
	int32_t res = 0;

	if (pipe(pipefd) < 0) {
		log_sys_error("[slave] Can't create pipe");
		return -1;
	}

	child_pid = fork();
	if (child_pid < 0) {
		log_sys_error("[slave] Can't fork");
		res = -1;
	} else if (child_pid == 0) {
		close(pipefd[0]);

		int new_conn;
		// running new process node
		close(sock);
		close_all_connections_fds();
		// first we connecting to master
		new_conn = connect_to_master();
		if (new_conn < 0) {
			log_sys_error("[slave] Failed to connect to master");
			exit(1);
		}

		if (io_write_int32(pipefd[1], 0) < 0) {
			log_sys_error("[slave] Failed to write connect confirmation to parent");
		}
		close(pipefd[1]);

		run_process_node(new_conn);

		exit(0);
	} else {
		close(pipefd[1]);
	}

	// waiting for child to connect to master
	log_info("[slave] Waiting for new child to connect to master...");
	if (io_read_int32(pipefd[0], &res) < 0) {
		log_sys_error("[slave] Failed to read child connect confirmation");
	}
	close(pipefd[0]);

	res = child_pid;
	return res;
}

static void* master_thread_fun(void* arg) {
	(void) arg;
	int client_sock;
	int32_t client_pid;

	while (1) {
		log_info("[master] Accepting new connection...");
		client_sock = accept(g_master_socket, NULL, NULL);
		if (client_sock < 0) {
			log_sys_error("[master] Accept failed");
			break;
		}

		client_pid = handshake_peer_pid(client_sock);
		if (client_pid < 0) {
			log_error("[master] Handshake failed; Exiting.");
			finish_handshake_server(client_pid, -1);
			break;
		}
		// response if slave pid
		add_new_connection(client_pid, client_sock);

		if (finish_handshake_server(client_sock, 0) < 0) {
			log_sys_error("[master] Handshake failed! Bye.");
			break;
		}
	}


	close(g_master_socket);
	close_all_connections_fds();

	return NULL;
}

static void close_all_connections_fds(void) {
	pthread_rwlock_rdlock(&g_slave_connections_lock);

	for (int i = 0; i < g_connections_cnt; ++i) {
		close(g_slave_connections[i].sock_fd);
	}

	pthread_rwlock_unlock(&g_slave_connections_lock);
}

static int find_connection(int pid, connection* dst) {
	pthread_rwlock_rdlock(&g_slave_connections_lock);

	dst->connected_pid = -1;
	dst->sock_fd = -1;

	for (int i = 0; i < g_connections_cnt; ++i) {
		if (g_slave_connections[i].connected_pid == pid) {
			dst->connected_pid = g_slave_connections[i].connected_pid;
			dst->sock_fd = g_slave_connections[i].sock_fd;
			break;
		}
	}

	pthread_rwlock_unlock(&g_slave_connections_lock);

	return 0;
}

static void* master_slave_thread_fun(void* arg) {
	int conn_fd = *((int*) arg);
	run_process_node(conn_fd);
	return NULL;
}

static int add_new_connection(int pid, int fd) {
	if (g_connections_cnt >= G_MAX_CONNECTIONS) {
		log_error("Connections limit exceeded!");
		return -1;
	}

	if (pthread_rwlock_wrlock(&g_slave_connections_lock) != 0) {
		log_error("Can't lock connections lock");
		return -1;
	}

	g_slave_connections[g_connections_cnt] = (connection) {
		.connected_pid = pid,
		.sock_fd = fd
	};
	g_connections_cnt += 1;

	if (pthread_rwlock_unlock(&g_slave_connections_lock) != 0) {
		log_error("Can't unlock connections lock");
		return -1;
	}

	return 0;
}
