#ifndef PARSE_H_INCLUDED__
#define PARSE_H_INCLUDED__

#include <stdio.h>
#include <stdlib.h>

#include "command.h"
#include "program.h"

int parse_program(const char* ppath, struct program* out_p);

#endif