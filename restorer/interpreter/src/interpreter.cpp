#include "interpreter.h"

#include <map>
#include <vector>

#include <cstdio>
#include <cerrno>
#include <cassert>
#include <cstring>

#include <unistd.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <sys/socket.h>
#include <sys/wait.h>

#include "ipc.h"
#include "fd_utils.h"
#include "pid_utils.h"
#include "log.h"
#include "io_utils.h"
#include "command/command_print.h"

// TODO: that is temporary
#define FINI_SLEEP_TIME 200

static int interpreter_worker(int max_fd);
static int send_command(int sock_fd, const command*);

static void sigchld_handler(int sig)
{
    pid_t p;
    int status;
    while ((p = waitpid(-1, &status, WNOHANG)) != -1) {
    	log_info("Child dead [ %d ] catched", p);
    }
    (void) sig;
}

static int setup_child_handler()
{
	struct sigaction sa;
	memset(&sa, 0, sizeof(sa));
	sa.sa_handler = sigchld_handler;
	return sigaction(SIGCHLD, &sa, NULL);
}

int interpreter_run(const command* program, int len)
{
	// server socket fd for every interpreter-worker
	std::map<pid_t, int> server_socks; 
	// connection fd for every interpreter-worker
	std::map<pid_t, int> connections;
	// service file descriptors
	int srv_fd = -1;
	int conn_fd = -1;

	auto cleanup_fun = 
	[&srv_fd, &conn_fd, &server_socks, &connections](int ret_code) {
		for (const auto& p : server_socks)
			close(p.second);
		server_socks.clear();
		for (const auto& p : connections)
			close(p.second);
		connections.clear();
		close(srv_fd);
		close(conn_fd);
		return ret_code;
	};
	
	if (setup_child_handler()) {
		log_stderr("Can't setup child handler");
		return cleanup_fun(-1);
	}                             

	for(int i = 0; i < len; ++i) {
		const command& cmd = program[i];

		if (cmd.type == CMD_FORK_CHILD) {
			cmd_fork_child fork_cmd = *static_cast<cmd_fork_child*>(cmd.c);
			pid_t child = fork_cmd.child_pid;

			log_info("Got fork command; child = %d; parent = %d", 
				 child, cmd.owner);
			
			// opening socket for ipc with child interpreter proc
			srv_fd = socket_open(child);
			if (srv_fd < 0) {
				log_error("Can't open socket for pid %d", child);
				return cleanup_fun(-1);
			}

			if (cmd.owner != 0) {
				log_info("Forking child interpreter %d", child);
				pid_t pid = fork_pid(child);
				if (pid < 0) {
					log_error("Can't fork interpreter %d", child);
					return cleanup_fun(-1);
				} else if (pid == 0) {
					// closing not needed fds
					cleanup_fun(0);
					log_info("Running interpreter fun");
					int ret = interpreter_worker(fork_cmd.max_fd);
					log_info("Exiting...");
					return ret;
				}
			} else {
				log_info("Delegating fork of [ %d ] to it's owner [ %d ] through socket [ %d ]", 
				     child, cmd.owner, conn_fd);
				conn_fd = connections[cmd.owner];
				send_command(conn_fd, &cmd);
			}

			// in master interpreter; opening connection with newborn worker
			log_info("Accepting connection from [ %d ] ...", child);
			if ((conn_fd = accept(srv_fd, NULL, NULL)) < 0) {
				log_error("Can't open connection Master <-> %d", child);
				return cleanup_fun(-1);
			}
			log_info("Connection accepted: %d", conn_fd);

			server_socks[child] = srv_fd;
			connections[child] = conn_fd;
		} else {
			// just delegating command evaluation
			log_info("Sending command [ %d ] to [ %d ] through socket [ %d ]", 
				     cmd.type, cmd.owner, conn_fd);
			conn_fd = connections[cmd.owner];
			send_command(conn_fd, &cmd);
		}
	}
	
	log_info("All commands were sent");

	cleanup_fun(0);
	sleep(FINI_SLEEP_TIME);
	return 0;
}

static int send_command(int sock_fd, const command* cmd)
{
	if (io_write(sock_fd, 
		         static_cast<const char*>(static_cast<const void*>(&(cmd->type))), 
		         sizeof(cmd->type)) < 0) {
		log_error("Can't send command type via socket [%s]",
			         strerror(errno));
		return -1;
	}
	if (io_write(sock_fd, static_cast<const char*>(cmd->c), get_cmd_size(cmd->type)) < 0) {
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

static std::map<int, command_evaluator> evaluators = {
	{ CMD_SETSID,        eval_cmd_setsid },
	{ CMD_FORK_CHILD,    NULL }, // evaluated in main interpreter loop
	{ CMD_REG_OPEN,      eval_cmd_reg_open },
	{ CMD_CREATE_THREAD, eval_cmd_create_thread },
	{ CMD_DUPLICATE_FD,  eval_cmd_duplicate_fd },
	{ CMD_CLOSE_FD,      eval_cmd_close_fd },
	{ CMD_FINI,          NULL }, // evaluated in main loop too
	{ CMD_UNKNOWN,       NULL }
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
	int conn_fd; // socket connection fd
	auto cleanup_fun = [&conn_fd](int ret_code) {
			close(conn_fd);
			return ret_code;
	};

	if (setup_child_handler()) {
		log_stderr("Can't setup child handler");
		return cleanup_fun(-1);
	}

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
	int free_fd = max_fd + 1; // first free fd available for helper files during restore
	int mov_ret = move_fd(conn_fd, free_fd);
	if (mov_ret < 0) {
		log_error("Can't remap socket fd [%d]", mov_ret);
		return cleanup_fun(-1);
	}
	conn_fd = free_fd;
	free_fd += 1;

	char buf[5000];
	char cmd_buf[MAX_CMD_SIZE];
	while (true) {
		enum cmd_type cmd_type;
		log_info("Reading command from socket [ %d ]", conn_fd);
		if (io_read(conn_fd, (char*) &cmd_type, sizeof(enum cmd_type)) < 0
		    || io_read(conn_fd, cmd_buf, get_cmd_size(cmd_type)) < 0) {

			log_stderr("Can't read command from socket");
			return cleanup_fun(-1);
		}
		log_info("Got = %s", sprint_cmd(buf, cmd_type, cmd_buf));

		if (cmd_type == CMD_FORK_CHILD) {
			cmd_fork_child* c = (cmd_fork_child*) cmd_buf;
			log_info("Forking interpreter %d", c->child_pid);

			pid_t pid = fork_pid(c->child_pid);
			if (pid < 0) {
				log_error("Can't fork interpreter %d", c->child_pid);
				return cleanup_fun(-1);
			} else if (pid == 0) {
				cleanup_fun(0);
				log_info("Running interpreter procedure");
				if (interpreter_worker(c->max_fd) < 0) {
					log_error("Interpreter returned error");
					return -1;
				}
				return 0;
			}
		} else if (cmd_type == CMD_FINI) {
			log_info("Finilizing interpreter...");
			sleep(FINI_SLEEP_TIME);
			break;
		} else { 
		    // generic command evaluation
			if (evaluators[cmd_type](static_cast<void*>(cmd_buf)) < 0) {
				log_error("Command [%d] evaluation failed", cmd_type);
				return cleanup_fun(-1);
			}
		}
	}

	return cleanup_fun(0);
}

// ============================ command evaluators =============================

static int eval_cmd_setsid(void* cmd)
{
	cmd_setsid c = *static_cast<cmd_setsid*>(cmd);
	(void) c;

	log_info("Evaluating setsid...");
	if (setsid() < 0) {
		log_stderr("Can't setsid");
		return -1;
	}

	return 0;
}

static int eval_cmd_reg_open(void* cmd)
{
	cmd_reg_open* c = *static_cast<cmd_reg_open*>(cmd);
	int fd = open(c->path, c->flags, c->mode);
	if (fd < 0) {
		log_stderr("Can't open file");
		return -1;
	}
	log_info("opened reg file at [ %d ]; moving to [ %d ]", fd, c->fd);
	if (move_fd(fd, c->fd) < 0) {
		log_stderr("Can't move fd");
		return -1;
	}
	if (lseek(c->fd, c->offset, SEEK_SET) < 0) {
		log_stderr("Can't set offset");
		return -1;
	}
	return 0;
}

static int eval_cmd_duplicate_fd(void* cmd)
{
	cmd_duplicate_fd* c = *static_cast<cmd_duplicate_fd*>(cmd);
	if (dup2(c->old_fd, c->new_fd) < 0) {
		log_error("Can't dup fd [ %d ] to [ %d ] [ %s ]", 
			  c->old_fd, c->new_fd, strerror(errno));
		return -1;
	}
	return 0;
}

static int eval_cmd_close_fd(void* cmd)
{
	cmd_close_fd* c = *static_cast<cmd_close_fd*>(cmd);
	if (close(c->fd) < 0) {
		log_error("Can't close fd [ %d ] [ %s ]", c->fd, strerror(errno));
		return -1;
	}
	return 0;
}

static int eval_cmd_create_thread(void* cmd)
{
	cmd_create_thread c = *static_cast<cmd_create_thread*>(cmd);
	(void) c;

	log_info("Evaluating create thread... (TODO)");

	return 0;
}