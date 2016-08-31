#ifndef COMMAND_H_INCLUDED__
#define COMMAND_H_INCLUDED__

#include <sys/types.h>
#include <linux/limits.h>

struct cmd_fork_root
{
	pid_t pid;
};

struct cmd_setsid
{
	pid_t pid;
};

struct cmd_fork_child
{
	pid_t pid;
	pid_t child_pid;
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

#endif