#ifndef INTERPRETER_H_INCLUDED__
#define INTERPRETER_H_INCLUDED__

#include "command/command.h"

/**
 * Master interpreter procedure, which responsible for
 * sending commands to interpreter-workers -- processes
 * from restoring process tree, who will evaluate commands
 * and restore themselves
 * 
 * @param program array of commands to evaluate
 * @param len length of passed array
 * @return error code or 0 on success
 */
int interpreter_run(const command* program, int len);

#endif
