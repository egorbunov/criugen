#ifndef PROGRAM_H_INCLUDED__
#define PROGRAM_H_INCLUDED__

#include "command.h"

struct command
{
	enum cmd_type type;
	void* payload;
};

struct program
{
	size_t size;
	size_t cap;
	struct command* commands;
};

#define cmd_foreach(p, cmd, i)\
	if ( (p)->size > 0 )\
		for ( (i) = 0;\
		      (i) < (p)->size && (((cmd) = (p)->commands[(i)]), 1);\
		      ++(i))

struct program* prog_create();

/**
 * Adds command to given program.
 * Steals ownership of passed struct command so it will be deleted
 * on program_delete call ==> allocate it on the heap!
 */
int prog_add_cmd(struct program*, struct command);

void prog_delete(struct program*);

#endif