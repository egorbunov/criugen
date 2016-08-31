#include "command.h"

#include <stdio.h>

void print_cmd(const struct command* c)
{
	printf("{\n");
	if (c->type == CMD_SETSID) {
		printf("\tcmd: %s,\n", CMD_TAG_SETSID);
		printf("\tpid: %d", ((struct cmd_setsid*) c->c)->pid);
	} else if (c->type == CMD_FORK_CHILD) {
		printf("\tcmd: %s,\n", CMD_TAG_FORK_CHILD);
		printf("\tpid: %d,\n", ((struct cmd_fork_child*) c->c)->pid);
		printf("\tchild_pid: %d,\n", ((struct cmd_fork_child*) c->c)->child_pid);
		printf("\tmax_fd: %d\n", ((struct cmd_fork_child*) c->c)->max_fd);
	} else if (c->type == CMD_REG_OPEN) {
		printf("\tcmd: %s,\n", CMD_TAG_REG_OPEN);
		printf("\tpid: %d,\n", ((struct cmd_reg_open*) c->c)->pid);
		printf("\tfd: %d,\n", ((struct cmd_reg_open*) c->c)->fd);
		printf("\tpath: %s,\n", ((struct cmd_reg_open*) c->c)->path);
		printf("\tflags: %d,\n", ((struct cmd_reg_open*) c->c)->flags);
		printf("\tmode: %d,\n", ((struct cmd_reg_open*) c->c)->mode);
		printf("\toffset: %d,\n", ((struct cmd_reg_open*) c->c)->offset);
	} else if (c->type == CMD_CLOSE_FD) {
		printf("\tcmd: %s,\n", CMD_TAG_CLOSE_FD);
		printf("\tpid: %d,\n", ((struct cmd_close_fd*) c->c)->pid);
		printf("\tfd: %d", ((struct cmd_close_fd*) c->c)->fd);
	} else if (c->type == CMD_DUPLICATE_FD) {
		printf("\tcmd: %s,\n", CMD_TAG_DUP_FD);
		printf("\tpid: %d,\n", ((struct cmd_duplicate_fd*) c->c)->pid);
		printf("\told_fd: %d,\n", ((struct cmd_duplicate_fd*) c->c)->old_fd);
		printf("\tnew_fd: %d,\n", ((struct cmd_duplicate_fd*) c->c)->new_fd);
	} else if (c->type == CMD_CREATE_THREAD) {
		printf("\tcmd: %s,\n", CMD_TAG_CREATE_THREAD);
		printf("\tpid: %d,\n", ((struct cmd_create_thread*) c->c)->pid);
		printf("\ttid: %d", ((struct cmd_create_thread*) c->c)->tid);
	}
	printf("\n}\n");
}
