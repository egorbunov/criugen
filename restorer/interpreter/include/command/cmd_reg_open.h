#pragma once

#include <sstream>
#include <cstring>
#include <cassert>

#include <sys/types.h>
#include <linux/limits.h>

#include "command.h"

/**
 * This command contains regular file state, needed for it's restoring.
 */
struct cmd_reg_open : command
{
private:
	const pid_t pid;
	char path[PATH_MAX];
	const int flags;
	const mode_t mode;
	const int offset;
	const int fd;

public:
	const static char* tag;

	cmd_reg_open(pid_t pid, 
		         const char* path, 
		         int flags, 
		         mode_t mode, 
		         int offset, 
		         int fd)
	: pid(pid), flags(flags), mode(mode), offset(offset), fd(fd) 
	{	
		assert(strlen(path) < PATH_MAX);
		strncpy(this->path, path, sizeof(this->path));
	}

	pid_t get_pid() {
		return pid;
	}

	const char* get_path() {
		return path;
	}

	int get_flags() {
		return flags;
	}

	mode_t get_mode() {
		return mode;
	}

	int get_offset() {
		return offset;
	}

	int get_fd() {
		return fd;
	}

	pid_t get_owner() override 
	{
		return pid;
	}
	
	size_t get_size() override 
	{
		return sizeof(cmd_reg_open);
	}

	std::string get_tag() override 
	{
		return tag;
	}
	
	std::string to_string() override
	{
		std::stringstream ss;
		ss << get_tag() << "(pid = " << pid
		                << ", flags = " << flags
		                << ", mode = " << mode
		                << ", offset = " << offset
		                << ", fd = " << fd << ")";
		return ss.str();
	}

	int execute() override;
};
