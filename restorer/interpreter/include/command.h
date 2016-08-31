#ifndef COMMAND_H_INCLUDED__
#define COMMAND_H_INCLUDED__

#include <sys/types.h>
#include <linux/limits.h>

#include "vec.h"

// commands

struct cmd_setsid
{
	pid_t pid;
};

struct cmd_fork_child
{
	pid_t pid;
	pid_t child_pid;
	int max_fd; // largest file descriptor opened in process
	            // we need it because we want to establish IPC
	            // with pipes and pipes must be opened at some fd
};

struct cmd_create_thread
{
	pid_t pid;
	pid_t tid;
};

struct cmd_reg_open
{
	pid_t pid;
	char path[PATH_MAX];
	int flags;
	mode_t mode;
	int offset;
	int fd;
};

struct cmd_close_fd
{
	pid_t pid;
	int fd;
};

struct cmd_duplicate_fd
{
	pid_t pid;
	int old_fd;
	int new_fd;
};

// commands utils and wrapper for IPC

#define COMMAND_NUM 20

#define CMD_TAG_FORK_ROOT "FORK_ROOT"
#define CMD_TAG_SETSID "SETSID"
#define CMD_TAG_FORK_CHILD "FORK_CHILD"
#define CMD_TAG_REG_OPEN "REG_OPEN"
#define CMD_TAG_CLOSE_FD "CLOSE_FD"
#define CMD_TAG_DUP_FD "DUP_FD"
#define CMD_TAG_CREATE_THREAD "CREATE_THREAD"

enum cmd_type
{
	CMD_FORK_CHILD = 0,
	CMD_SETSID,
	CMD_REG_OPEN,
	CMD_CLOSE_FD,
	CMD_DUPLICATE_FD,
	CMD_CREATE_THREAD,
	CMD_UNKNOWN
};

struct command
{
	enum cmd_type type;
	void* c; // command
};

typedef vec_t(struct command) command_vec;


void print_cmd(const struct command* cmd);



#endif
