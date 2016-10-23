#ifndef COMMAND_PRINT_H_INCLUDED__
#define COMMAND_PRINT_H_INCLUDED__

#include "command.h"

/**
 * Print command into buffer
 * 
 * @param buffer to write stringified cmd into
 * @param type (id) of the command
 * @param command data
 * @return int as sprintf returns
 */
int sprint_cmd(char* buf, enum cmd_type type, const void* cmd);

/**
 * print cmd to console
 * 
 * @param cmd
 */
void print_cmd(const struct command* cmd);

#endif