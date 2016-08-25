#include "parse.h"

#include "jsmn.h"

int parse_program(const char* ppath, struct program* out_p)
{
	jsmn_parser parser;
	jsmntok_t tokens[100]; // enough for tokens per command
	return 0;
} 