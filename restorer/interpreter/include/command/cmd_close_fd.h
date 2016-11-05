#pragma once

#include <sstream>

#include "command.h"

/**
 * Command equivalent to syscall `close(fd)`
 */
struct cmd_close_fd : command
{
private:
	const pid_t pid;
	const int fd;

public:
	const static char* tag;

	cmd_close_fd(pid_t pid, int fd): pid(pid), fd(fd)
	{}

	pid_t get_pid() {
		return pid;
	}

	pid_t get_fd() {
		return fd;
	}

	pid_t get_owner() override 
	{
		return pid;
	}

	size_t get_size() override 
	{
		return sizeof(cmd_close_fd);
	}

	std::string get_tag() override 
	{
		return tag;
	}

	std::string to_string() override
	{
		std::stringstream ss;
		ss << get_tag() << "(pid=" << pid << ", " << "fd = " << fd << ")";
		return ss.str();
	}

	int execute() override;
};
