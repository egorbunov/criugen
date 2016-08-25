#include "program.h"

#include <stdlib.h>

struct program* prog_create()
{
	struct program* p;
	p = (struct program*) malloc(sizeof(struct program));
	if (!p)
		return NULL;
	*p = (struct program) {
		.size = 0,
		.cap = 2,
		.commands = (struct command*) malloc(sizeof(struct command) * p->cap)
	};
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
		free(c.payload);
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
	tmp = (struct command*) realloc(p->commands, p->cap * 2);
	if (!tmp) {
		return -1;
	}
	p->commands = tmp;
	p->cap *= 2;
	p->commands[p->size] = c;
	p->size += 1;
	return 0;
}

