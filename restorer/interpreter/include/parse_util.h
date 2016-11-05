#pragma once

#include <istream>

/**
 * Reads characters to `c` from file and stops on first non-space one.
 * If that character is equal to given `ch` true is returned, else false
 */
bool read_check_char(std::istream& in, char ch, char* c);

/**
 * Reads one json object strating from opening '{' to closing '}'
 */
std::string read_one_json_object(std::istream& in);

/**
 * Parses file open flag
 */
int parse_open_flag(const char* str);