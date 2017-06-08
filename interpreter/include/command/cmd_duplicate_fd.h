#pragma once

#include <sstream>

#include "command.h"

/**
 * Command equivalent to syscall `dup2(old_fd, new_fd)`
 */
struct cmd_duplicate_fd : command
{
private:
	const pid_t pid;
	const int old_fd;
	const int new_fd;

public:
	const static char* tag;

	cmd_duplicate_fd(pid_t pid, int old_fd, int new_fd)
	: pid(pid), old_fd(old_fd), new_fd(new_fd)
	{}

	pid_t get_pid() {
		return pid;
	}

	int get_old_fd() {
		return old_fd;
	}

	int get_new_fd() {
		return new_fd;
	}

	pid_t get_owner() override 
	{
		return pid;
	}
	
	size_t get_sizeof() override 
	{
		return sizeof(cmd_duplicate_fd);
	}

	std::string get_tag() override 
	{
		return tag;
	}
	
	std::string to_string() override
	{
		std::stringstream ss;
		ss << get_tag() << "(pid = " << pid
		                << ", old_fd = " << old_fd
		                << ", new_fd = " << new_fd << ")";
		return ss.str();
	}

	int execute() override;
};
