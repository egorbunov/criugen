#include "interpreter.h"

#include <stdio.h>
#include <errno.h>
#include <assert.h>
#include <string.h>

#include <unistd.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <sys/socket.h>

#include "int_index.h"
#include "ipc.h"
#include "fd_utils.h"
#include "pid_utils.h"
#include "log.h"
#include "io_utils.h"

typedef int pipe_t[2];
typedef vec_t(pipe_t) vec_pipes;

static int command_sizes[COMMAND_NUM] = {
	[CMD_FORK_CHILD] = sizeof(struct cmd_fork_child),
	[CMD_SETSID] = sizeof(struct cmd_setsid),
	[CMD_REG_OPEN] = sizeof(struct cmd_reg_open),
	[CMD_CLOSE_FD] = sizeof(struct cmd_close_fd),
	[CMD_DUPLICATE_FD] = sizeof(struct cmd_duplicate_fd),
	[CMD_CREATE_THREAD] = sizeof(struct cmd_create_thread),
	[CMD_FINI] = sizeof(struct cmd_fini)
};

static int interpreter_worker(int max_fd);
static int send_command(int sock_fd, const struct command*);

/**
 * Master interpreter procedure, which responsible for
 * sending commands to interpreter-workers -- processes
 * from restoring process tree, who will evaluate commands
 * and restore themselves
 * @param  p command list
 */
int interpreter_run(const command_vec* p)
{
	int ret = 0;
	
	struct int_index pid_idx;  // pid -> id (0, ...)
	vec_int_t id_pid_map; // id -> pid
	vec_int_t server_socks; // socket fds
	vec_int_t connections; // connection fds
	
	int i;	
	struct command cmd;
	int srv_fd;
	int conn_fd;

	vec_init(&id_pid_map);
	vec_init(&server_socks);
	vec_init(&connections);

	vec_foreach(p, cmd, i) {
		int owner_id;

		if (cmd.owner != 0 && index_get(&pid_idx, cmd.owner, &owner_id) < 0) {
			log_error("Can't find cmd owner id, pid = %d", cmd.owner);
			ret = -1;
			goto exit;
		}

		if (cmd.type == CMD_FORK_CHILD) {
			pid_t child;
			int id;

			child = ((struct cmd_fork_child*) cmd.c)->child_pid;
			id = id_pid_map.length;

			log_info("Got fork command; child = %d; parent = %d", child, cmd.owner);
			
			// opening socket for ipc with child interpreter proc
			srv_fd = socket_open(child);
			if (srv_fd < 0) {
				log_error("Can't open socket for pid %d", child);
				ret = -1;
				goto exit;
			}

			if (cmd.owner == 0) {
				pid_t pid;
				log_info("Forking child interpreter %d", child);
				pid = fork_pid(child);
				if (pid < 0) {
					log_error("Can't fork interpreter %d", child);
					ret = -1;
					goto exit;
				} else if (pid == 0) {
					// closing not needed fds
					close(srv_fd);
					vec_foreach(&server_socks, srv_fd, i)
						close(srv_fd);
					vec_foreach(&connections, conn_fd, i)
						close(conn_fd);
					vec_clear(&server_socks);
					vec_clear(&connections);
					
					log_info("Running interpreter fun");
					ret = interpreter_worker(
						((struct cmd_fork_child*) cmd.c)->max_fd
					);

					goto exit;
				}
			} else {
				log_info("Delegating fork to owner [ %d ]", cmd.owner);
				conn_fd = connections.data[owner_id];
				send_command(conn_fd, &cmd);
			}
			// opening connection
			log_info("Accepting connection from [ %d ] ...", child);
			if ((conn_fd = accept(srv_fd, NULL, NULL)) < 0) {
				log_error("Can't open connection Master <-> %d", child);
				ret = -1;
				close(srv_fd);
				goto exit;
			}
			log_info("Connection accepted: %d", conn_fd);

			// storing connection and other stuff

			assert(id_pid_map.length == server_socks.length);
			assert(id_pid_map.length == connections.length);
			assert(id_pid_map.length == id);

			if (!index_put(&pid_idx, child, id)) {
				log_error("Can't update index");
				ret = -1;
				close(srv_fd);
				close(conn_fd);
				goto exit;
			}
			log_info("Add pid mapping [ %d -> %d ]", child, id);

			if (vec_push(&id_pid_map, child) < 0 ||
			    vec_push(&server_socks, srv_fd) < 0 ||
			    vec_push(&connections, conn_fd) < 0) 
			{
			    	log_error("Can't update vectors");
			    	ret = -1;
			    	close(srv_fd);
			    	close(conn_fd);
			    	goto exit;
			}
		} else {
			// just delegating command evaluation
			log_info("Sending command [ %d ] to [ %d (id = %d) ] through socket [ %d ]", 
				 cmd.type, cmd.owner, owner_id, conn_fd);
			conn_fd = connections.data[owner_id];
			send_command(conn_fd, &cmd);
		}
	}
	
	log_info("All commands were sent");

exit:
	vec_foreach(&server_socks, srv_fd, i) {
		close(srv_fd);
	}
	vec_foreach(&connections, conn_fd, i) {
		close(conn_fd);
	}
	vec_deinit(&id_pid_map);
	vec_deinit(&server_socks);
	vec_deinit(&connections);

	sleep(100);

	return ret;
}

static int send_command(int sock_fd, const struct command* cmd)
{
	if (io_write(sock_fd, (void*) &(cmd->type), sizeof(cmd->type)) < 0) {
		log_error("Can't send command type via socket [%s]",
			         strerror(errno));
		return -1;
	}
	if (io_write(sock_fd, cmd->c, command_sizes[cmd->type]) < 0) {
		log_error("Can't send command via socket [%s]",
			         strerror(errno));
		return -1;
	}
	return 0;
}


typedef int (*command_evaluator)(void* cmd);

static int eval_cmd_setsid(void* cmd);
static int eval_cmd_reg_open(void* cmd);
static int eval_cmd_duplicate_fd(void* cmd);
static int eval_cmd_close_fd(void* cmd);
static int eval_cmd_create_thread(void* cmd);

static command_evaluator evaluators[COMMAND_NUM] = {
	[CMD_SETSID] = eval_cmd_setsid,
	[CMD_FORK_CHILD] = NULL, // evaluated in main interpreter loop
	[CMD_REG_OPEN] = eval_cmd_reg_open,
	[CMD_CREATE_THREAD] = eval_cmd_create_thread,
	[CMD_DUPLICATE_FD] = eval_cmd_duplicate_fd,
	[CMD_CLOSE_FD] = eval_cmd_close_fd,
	[CMD_FINI] = NULL, // evaluated in main loop too
	[CMD_UNKNOWN] = NULL
};

/**
 * Main procedure for interpreter-worker (particular process from
 * process tree to restore). 
 * @param max_fd max used file descriptor for target process, so for 
 *               opening auxiliary files `max_fd + 1` and greater may
 *               be used
 */
static int interpreter_worker(int max_fd)
{
	int ret;
	int conn_fd; // socket connection fd
	int free_fd; // first free fd available for helper files during restore
	enum cmd_type cmd_type;
	char buf[5000];
	char cmd_buf[COMMAND_MAX_SIZE];

	free_fd = max_fd + 1;
	ret = 0;

	// connecting to socket to get commands
	log_info("Connecting to master socket...");
	conn_fd = socket_connect(getpid());
	log_info("Connected: %d", conn_fd);

	if (conn_fd < 0) {
		log_error("Can't connect to master socket from interpreter %d [%s]", 
			         getpid(), strerror(errno));
		return -1;
	}
	// remapping socket fd because we need 'clear' fdt for process restore
	if ((ret = move_fd(conn_fd, free_fd)) < 0) {
		log_error("Can't remap socket fd [%d]", ret);
		close(conn_fd);
		ret = -1;
		goto exit;
	}
	conn_fd = free_fd;
	free_fd += 1;

	(void) max_fd;

	while (true) {
		// reading command
		log_info("Reading command from socket [ %d ]", conn_fd);
		if ((ret = io_read(conn_fd, (char*) &cmd_type, sizeof(enum cmd_type))) < 0 ||
		    (ret = io_read(conn_fd, cmd_buf, command_sizes[cmd_type])) < 0) {
			log_stderr("Can't read command from socket");
			goto exit;
		}
		log_info("Got = %s", sprint_cmd(buf, cmd_type, cmd_buf));

		if (cmd_type == CMD_FORK_CHILD) {
			pid_t pid;
			struct cmd_fork_child* c = (struct cmd_fork_child*) cmd_buf;
			log_info("Forking interpreter %d", c->child_pid);

			pid = fork_pid(c->child_pid);
			if (pid < 0) {
				log_error("Can't fork interpreter %d", c->child_pid);
				ret = -1;
				goto exit;
			} else if (pid == 0) {
				// close(conn_fd);
				log_info("Running interpreter procedure");
				if (interpreter_worker(c->max_fd) < 0) {
					log_error("Interpreter returned error");
					return -1;
				}
				return 0;
			}
		} else if (cmd_type == CMD_FINI) {
			log_info("Finilizing interpreter...");
			close(conn_fd);
			sleep(100);
		} else {
			if ((ret = evaluators[cmd_type]((void*) cmd_buf)) < 0) {
				log_error("Command [%d] evaluation failed", cmd_type);
				goto exit;
			}
		}
	}

exit:
	close(conn_fd);
	return ret;
}

// ============================ command evaluators =============================

static int eval_cmd_setsid(void* cmd)
{
	struct cmd_setsid c = *((struct cmd_setsid*) cmd);
	(void) c;

	log_info("Evaluating setsid...");

	return 0;
}

static int eval_cmd_reg_open(void* cmd)
{
	struct cmd_reg_open* c = (struct cmd_reg_open*) cmd;
	int fd;

	fd = open(c->path, c->flags, c->mode);
	if (fd < 0) {
		log_stderr("Can't open file");
		return -1;
	}
	if (move_fd(fd, c->fd) < 0) {
		log_stderr("Can't move fd");
		return -1;
	}

	// todo LSEEK
	return 0;
}

static int eval_cmd_duplicate_fd(void* cmd)
{
	struct cmd_duplicate_fd* c = (struct cmd_duplicate_fd*) cmd;
	if (dup2(c->old_fd, c->new_fd) < 0) {
		log_error("Can't dup fd [ %d ] to [ %d ] [ %s ]", c->old_fd, c->new_fd, strerror(errno));
		return -1;
	}
	return 0;
}

static int eval_cmd_close_fd(void* cmd)
{
	struct cmd_close_fd* c = (struct cmd_close_fd*) cmd;
	if (close(c->fd) < 0) {
		log_error("Can't close fd [ %d ] [ %s ]", c->fd, strerror(errno));
		return -1;
	}
	return 0;
}

static int eval_cmd_create_thread(void* cmd)
{
	struct cmd_create_thread c = *((struct cmd_create_thread*) cmd);
	(void) c;

	log_info("Evaluating create thread... (TODO)");

	return 0;
}