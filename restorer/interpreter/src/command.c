#include "command.h"

#include <stdio.h>

static void sprint_cmd_setsid(char* buf, const void* cmd)
{
	struct cmd_setsid* c = (struct cmd_setsid*) cmd;
	sprintf(buf, "{ cmd: %s, pid: %d }", CMD_TAG_SETSID, c->pid);
}

static void sprint_cmd_fork_child(char* buf, const void* cmd)
{
	struct cmd_fork_child* c = (struct cmd_fork_child*) cmd;
	sprintf(buf, "{ cmd: %s, pid: %d, child_pid: %d, max_fd: %d }", 
		     CMD_TAG_FORK_CHILD, c->pid, c->child_pid, c->max_fd);
}

static void sprint_cmd_reg_open(char* buf, const void* cmd)
{
	struct cmd_reg_open* c = (struct cmd_reg_open*) cmd;
	sprintf(buf, "{ cmd: %s, pid: %d, fd: %d, path: %s, "\
	              "flags: %d, mode: %d, offset: %d",
	             CMD_TAG_REG_OPEN, c->pid, c->fd, c->path,
	             c->flags, c->mode, c->offset);
}

static void sprint_cmd_close_fd(char* buf, const void* cmd)
{
	struct cmd_close_fd* c = (struct cmd_close_fd*) cmd;
	sprintf(buf, "{ cmd: %s, pid: %d, fd: %d }", 
		     CMD_TAG_CLOSE_FD, c->pid, c->fd);
}

static void sprint_cmd_duplicate_fd(char* buf, const void* cmd)
{
	struct cmd_duplicate_fd* c = (struct cmd_duplicate_fd*) cmd;
	sprintf(buf, "{ cmd: %s, pid: %d, old_fd: %d, new_fd: %d }", 
		     CMD_TAG_DUP_FD, c->pid, c->old_fd, c->new_fd);
}

static void sprint_cmd_create_thread(char* buf, const void* cmd)
{
	struct cmd_create_thread* c = (struct cmd_create_thread*) cmd;
	sprintf(buf, "{ cmd: %s, pid: %d, tid: %d }", 
		     CMD_TAG_CREATE_THREAD, c->pid, c->tid);
}

static void sprint_cmd_fini(char* buf, const void* cmd)
{
	struct cmd_fini* c = (struct cmd_fini*) cmd;
	sprintf(buf, "{ cmd: %s, pid: %d }", CMD_TAG_FINI, c->pid);
}

typedef void (*cmd_printer)(char*, const void*);

static cmd_printer command_printers[COMMAND_NUM] = {
	[CMD_FORK_CHILD] = sprint_cmd_fork_child,
	[CMD_SETSID] = sprint_cmd_setsid,
	[CMD_REG_OPEN] = sprint_cmd_reg_open,
	[CMD_CLOSE_FD] = sprint_cmd_close_fd,
	[CMD_DUPLICATE_FD] = sprint_cmd_duplicate_fd,
	[CMD_CREATE_THREAD] = sprint_cmd_create_thread,
	[CMD_FINI] = sprint_cmd_fini
};

char* sprint_cmd(char* buf, enum cmd_type type, void* cmd)
{
	command_printers[type](buf, cmd);
	return buf;
}

void print_cmd(const struct command* c)
{
	char buf[4000];
	command_printers[c->type](buf, c->c);
	printf("%s", buf);
}