#include "interpreter.h"

#include <stdio.h>
#include <errno.h>
#include <assert.h>
#include <string.h>

#include <unistd.h>
#include <sys/socket.h>

#include <zlog.h>

#include "int_index.h"
#include "ipc.h"
#include "fd_utils.h"
#include "pid_utils.h"

typedef int pipe_t[2];
typedef vec_t(pipe_t) vec_pipes;

// logging
extern zlog_category_t* g_log;

static int command_sizes[COMMAND_NUM] = {
	[CMD_FORK_CHILD] = sizeof(struct cmd_fork_child),
	[CMD_SETSID] = sizeof(struct cmd_setsid),
	[CMD_REG_OPEN] = sizeof(struct cmd_reg_open),
	[CMD_CLOSE_FD] = sizeof(struct cmd_close_fd),
	[CMD_DUPLICATE_FD] = sizeof(struct cmd_duplicate_fd),
	[CMD_CREATE_THREAD] = sizeof(struct cmd_create_thread)
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
	pid_t child;
	pid_t pid;
	int id, owner_id;
	int srv_fd;
	int conn_fd;

	vec_init(&id_pid_map);
	vec_init(&server_socks);
	vec_init(&connections);

	vec_foreach(p, cmd, i) {
		if (cmd.owner != 0 && index_get(&pid_idx, cmd.owner, &owner_id) < 0) {
			zlog_info(g_log, "Can't find cmd owner id, pid = %d", cmd.owner);
			ret = -1;
			goto exit;
		}

		if (cmd.type == CMD_FORK_CHILD) {
			child = ((struct cmd_fork_child*) cmd.c)->child_pid;
			id = id_pid_map.length;
			
			// opening socket for ipc with child interpreter proc
			srv_fd = socket_open(child);
			if (srv_fd < 0) {
				zlog_info(g_log, "Can't open socket for pid %d", child);
				ret = -1;
				goto exit;
			}

			if (cmd.owner == 0) {
				pid = fork_pid(child);
				if (pid < 0) {
					zlog_info(g_log, "Can't fork interpreter %d", child);
					ret = -1;
					goto exit;
				} else if (pid == 0) {
					// closing not needed fds
					vec_foreach(&server_socks, srv_fd, i)
						close(srv_fd);
					vec_foreach(&connections, conn_fd, i)
						close(conn_fd);
					vec_clear(&server_socks);
					vec_clear(&connections);
					
					zlog_info(g_log, "Running interpreter fun");
					ret = interpreter_worker(
						((struct cmd_fork_child*) cmd.c)->max_fd
					);

					goto exit;
				}
			} else {
				conn_fd = connections.data[owner_id];
				send_command(conn_fd, &cmd);
			}
			// opening connection
			zlog_info(g_log, "Accepting connection...");
			if ((conn_fd = accept(srv_fd, NULL, NULL)) < 0) {
				zlog_info(g_log, "Can't open connection Master <-> %d", child);
				ret = -1;
				close(srv_fd);
				goto exit;
			}
			// storing connection and other stuff
			if (!index_put(&pid_idx, child, id) ||
			    vec_push(&server_socks, srv_fd) < 0 ||
			    vec_push(&connections, conn_fd) < 0) 
			{
			    	zlog_info(g_log, "Can't update vectors");
			    	ret = -1;
			    	close(srv_fd);
			    	close(conn_fd);
			    	goto exit;
			}
		} else {
			// just delegating command evaluation
			conn_fd = connections.data[owner_id];
			send_command(conn_fd, &cmd);
		}
	}
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
	return ret;
}
/**

 * Main procedure for interpreter-worker (particular process from
 * process tree to restore). 
 * @param max_fd max used file descriptor for target process, so for 
 *               opening auxiliary files `max_fd + 1` and greater may
 *               be used
 */
static int interpreter_worker(int max_fd)
{
	int conn_fd;
	int free_fd;

	free_fd = max_fd + 1;
	conn_fd = socket_connect(getpid());
	// connecting to socket to get commands
	if (conn_fd < 0) {
		zlog_info(g_log, "Can't connect to master socket from interpreter %d [%s]", 
			         getpid(), strerror(errno));
		return -1;
	}
	// remapping socket fd because we need fds for process restore
	if (move_fd(conn_fd, free_fd) < 0) {
		zlog_info(g_log, "Can't remap socket fd");
		close(conn_fd);
		return -1;
	}
	conn_fd = free_fd;
	free_fd += 1;

	sleep(100);
	return 0;
}

static int send_command(int sock_fd, const struct command* cmd)
{
	if (send(sock_fd, (void*) &(cmd->type), sizeof(cmd->type), 0) < 0) {
		zlog_info(g_log, "Can't send command type via socket [%s]",
			         strerror(errno));
		return -1;
	}
	if (send(sock_fd, cmd->c, command_sizes[cmd->type], 0) < 0) {
		zlog_info(g_log, "Can't send command via socket [%s]",
			         strerror(errno));
		return -1;
	}
	return 0;
}
