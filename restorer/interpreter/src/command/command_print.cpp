#include "command/command_print.h"

#include <cstdio>
#include <map>

#include "command/command.h"

static int sprint_cmd_setsid(char* buf, const void* cmd, const char*);
static int sprint_cmd_fork_child(char* buf, const void* cmd, const char*);
static int sprint_cmd_reg_open(char* buf, const void* cmd, const char*);
static int sprint_cmd_close_fd(char* buf, const void* cmd, const char*);
static int sprint_cmd_duplicate_fd(char* buf, const void* cmd, const char*);
static int sprint_cmd_create_thread(char* buf, const void* cmd, const char*);
static int sprint_cmd_fini(char* buf, const void* cmd, const char*);

typedef int (*cmd_printer)(char*, const void*, const char*);

static std::map<int, cmd_printer> command_printers = {
	{ CMD_FORK_CHILD,    sprint_cmd_fork_child },
	{ CMD_SETSID,        sprint_cmd_setsid },
	{ CMD_REG_OPEN,      sprint_cmd_reg_open },
	{ CMD_CLOSE_FD,      sprint_cmd_close_fd },
	{ CMD_DUPLICATE_FD,  sprint_cmd_duplicate_fd },
	{ CMD_CREATE_THREAD, sprint_cmd_create_thread },
	{ CMD_FINI,          sprint_cmd_fini }
};

// ======== public interface =========

int sprint_cmd(char* buf, enum cmd_type type, const void* cmd)
{
	return command_printers[type](buf, cmd, get_cmd_tag(type));
}

void print_cmd(const struct command* c)
{
	char buf[4000];
	sprint_cmd(buf, c->type, c->c);
	printf("%s", buf);
}

// ========= implementation details ===========

static int sprint_cmd_setsid(char* buf, const void* cmd, const char* tag)
{
	struct cmd_setsid* c = (struct cmd_setsid*) cmd;
	return sprintf(buf, "{ cmd: %s, pid: %d }", tag, c->pid);
}

static int sprint_cmd_fork_child(char* buf, const void* cmd, const char* tag)
{
	struct cmd_fork_child* c = (struct cmd_fork_child*) cmd;
	return sprintf(buf, "{ cmd: %s, pid: %d, child_pid: %d, max_fd: %d }", 
		     tag, c->pid, c->child_pid, c->max_fd);
}

static int sprint_cmd_reg_open(char* buf, const void* cmd, const char* tag)
{
	struct cmd_reg_open* c = (struct cmd_reg_open*) cmd;
	return sprintf(buf, "{ cmd: %s, pid: %d, fd: %d, path: %s, "\
	              "flags: %d, mode: %d, offset: %d",
	             tag, c->pid, c->fd, c->path,
	             c->flags, c->mode, c->offset);
}

static int sprint_cmd_close_fd(char* buf, const void* cmd, const char* tag)
{
	struct cmd_close_fd* c = (struct cmd_close_fd*) cmd;
	return sprintf(buf, "{ cmd: %s, pid: %d, fd: %d }", 
		     tag, c->pid, c->fd);
}

static int sprint_cmd_duplicate_fd(char* buf, const void* cmd, const char* tag)
{
	struct cmd_duplicate_fd* c = (struct cmd_duplicate_fd*) cmd;
	return sprintf(buf, "{ cmd: %s, pid: %d, old_fd: %d, new_fd: %d }", 
		     tag, c->pid, c->old_fd, c->new_fd);
}

static int sprint_cmd_create_thread(char* buf, const void* cmd, const char* tag)
{
	struct cmd_create_thread* c = (struct cmd_create_thread*) cmd;
	return sprintf(buf, "{ cmd: %s, pid: %d, tid: %d }", 
		     tag, c->pid, c->tid);
}

static int sprint_cmd_fini(char* buf, const void* cmd, const char* tag)
{
	struct cmd_fini* c = (struct cmd_fini*) cmd;
	return sprintf(buf, "{ cmd: %s, pid: %d }", tag, c->pid);
}

