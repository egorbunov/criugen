#ifndef PROGRAM_H_INCLUDED__
#define PROGRAM_H_INCLUDED__

#include "command.h"

enum cmd_type
{
	CMD_FORK_ROOT = 0,
	CMD_SETSID,
	CMD_FORK_CHILD,
	CMD_REG_OPEN,
	CMD_CLOSE_FD,
	CMD_DUPLICATE_FD,
	CMD_CREATE_THREAD,
	CMD_UNKNOWN
};

#define COMMAND_NUM 20

#define CMD_TAG_FORK_ROOT "FORK_ROOT"
#define CMD_TAG_SETSID "SETSID"
#define CMD_TAG_FORK_CHILD "FORK_CHILD"
#define CMD_TAG_REG_OPEN "REG_OPEN"
#define CMD_TAG_CLOSE_FD "CLOSE_FD"
#define CMD_TAG_DUP_FD "DUP_FD"
#define CMD_TAG_CREATE_THREAD "CREATE_THREAD"

struct command
{
	enum cmd_type type;
	void* c; // command
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

void prog_print(struct program*);

#endif