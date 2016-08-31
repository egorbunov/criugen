#include "program.h"

#include <stdlib.h>
#include <stdio.h>

struct program* prog_create()
{
	struct program* p;
	p = (struct program*) malloc(sizeof(struct program));
	if (!p)
		return NULL;
	p->size = 0;
	p->cap = 2;
	p->commands = (struct command*) malloc(sizeof(struct command) * p->cap);
	if (!p->commands) {
		free(p);
		return NULL;
	}
	return p;
}

void prog_delete(struct program* p)
{
	size_t i = 0;
	struct command c;

	cmd_foreach(p, c, i) {
		free(c.c);
	}
	free(p);
}

int prog_add_cmd(struct program* p, struct command c)
{
	struct command* tmp = NULL;
	if (p->size < p->cap) {
		p->commands[p->size] = c;
		p->size += 1;
		return 0;
	}
	tmp = (struct command*) realloc(p->commands, sizeof(struct command) * p->cap * 2);
	if (!tmp) {
		return -1;
	}
	p->commands = tmp;
	p->cap *= 2;
	p->commands[p->size] = c;
	p->size += 1;
	return 0;
}

void prog_print(struct program* p)
{
	size_t i = 0;
	struct command c;

	cmd_foreach(p, c, i) {
		printf("%zu: {\n", i);
		if (c.type == CMD_FORK_ROOT) {
			printf("\tcmd: %s,\n", CMD_TAG_FORK_ROOT);
			printf("\tpid: %d", ((struct cmd_fork_root*) c.c)->pid);
		} else if (c.type == CMD_SETSID) {
			printf("\tcmd: %s,\n", CMD_TAG_SETSID);
			printf("\tpid: %d", ((struct cmd_setsid*) c.c)->pid);
		} else if (c.type == CMD_FORK_CHILD) {
			printf("\tcmd: %s,\n", CMD_TAG_FORK_CHILD);
			printf("\tpid: %d,\n", ((struct cmd_fork_child*) c.c)->pid);
			printf("\tchild_pid: %d\n", ((struct cmd_fork_child*) c.c)->child_pid);
		} else if (c.type == CMD_REG_OPEN) {
			printf("\tcmd: %s,\n", CMD_TAG_REG_OPEN);
			printf("\tpid: %d,\n", ((struct cmd_reg_open*) c.c)->pid);
			printf("\tfd: %d,\n", ((struct cmd_reg_open*) c.c)->fd);
			printf("\tpath: %s,\n", ((struct cmd_reg_open*) c.c)->path);
			printf("\tflags: %d,\n", ((struct cmd_reg_open*) c.c)->flags);
			printf("\tmode: %d,\n", ((struct cmd_reg_open*) c.c)->mode);
			printf("\toffset: %d,\n", ((struct cmd_reg_open*) c.c)->offset);
		} else if (c.type == CMD_CLOSE_FD) {
			printf("\tcmd: %s,\n", CMD_TAG_CLOSE_FD);
			printf("\tpid: %d,\n", ((struct cmd_close_fd*) c.c)->pid);
			printf("\tfd: %d", ((struct cmd_close_fd*) c.c)->fd);
		} else if (c.type == CMD_DUPLICATE_FD) {
			printf("\tcmd: %s,\n", CMD_TAG_DUP_FD);
			printf("\tpid: %d,\n", ((struct cmd_duplicate_fd*) c.c)->pid);
			printf("\told_fd: %d,\n", ((struct cmd_duplicate_fd*) c.c)->old_fd);
			printf("\tnew_fd: %d,\n", ((struct cmd_duplicate_fd*) c.c)->new_fd);
		} else if (c.type == CMD_CREATE_THREAD) {
			printf("\tcmd: %s,\n", CMD_TAG_CREATE_THREAD);
			printf("\tpid: %d,\n", ((struct cmd_create_thread*) c.c)->pid);
			printf("\ttid: %d", ((struct cmd_create_thread*) c.c)->tid);
		}
		printf("\n}\n");
	}
}

