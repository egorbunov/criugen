#ifndef PARSE_H_INCLUDED__
#define PARSE_H_INCLUDED__

#include <vector>

#include <cstdio>
#include <cstdlib>

#include "command/command.h"

/**
 * @param path to program file
 * @param program vector there commands will be added
 * @return non-negative value if all is ok; in case of no errors
 *         user must free all payload command data from commands
 *         in program (delete command->c).
 */
int parse_program(const char* ppath, std::vector<command>& program);

#endif
