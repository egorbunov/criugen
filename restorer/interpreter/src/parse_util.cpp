#include "parse_util.h"

#include <string>
#include <sstream>

#include <cstring>
#include <fcntl.h>

bool read_check_char(std::istream& in, char ch, char* c)
{
	*c = ' ';
	while (isspace(*c))
		*c = in.get();
	return *c == ch;
}

std::string read_one_json_object(std::istream& in)
{
	std::stringstream ss;
	char ch;
	if (!read_check_char(in, '{', &ch))
		return "";
	int balance = 1;
	ss << '{';
	while (balance != 0) {
		ch = in.get();
		if (ch == '{')
			balance += 1;
		else if (ch == '}')
			balance -= 1;
		else if (ch == EOF)
			return "";
		if (!isspace(ch))
			ss << ch;
	}
	return ss.str();
}

int parse_open_flag(const char* str)
{
	if (strncmp(str, "O_RDWR", strlen("O_RDWR")))
		return O_RDWR;
	if (strncmp(str, "O_LARGEFILE", strlen("O_LARGEFILE")))
		return 0; // TODO ?
	if (strncmp(str, "O_CREAT", strlen("O_CREAT")))
		return O_CREAT;
	if (strncmp(str, "O_EXCL", strlen("O_EXCL")))
		return O_EXCL;
	if (strncmp(str, "O_APPEND", strlen("O_APPEND")))
		return O_APPEND;
	if (strncmp(str, "O_WRONLY", strlen("O_WRONLY")))
		return O_WRONLY;
	if (strncmp(str, "O_RDONLY", strlen("O_RDONLY")))
		return O_RDONLY;
	if (strncmp(str, "O_TRUNC", strlen("O_TRUNC")))
		return O_TRUNC;
	return -1;
}