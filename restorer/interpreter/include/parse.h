#ifndef PARSE_H_INCLUDED__
#define PARSE_H_INCLUDED__

#include <stdio.h>
#include <stdlib.h>

#include "command.h"

int parse_program(const char* ppath, command_vec* out_p);

#endif
