#pragma once

#include <sstream>

#include "command.h"

/**
 * Command equivalent to syscall `setsid(pid)`
 */
struct cmd_setsid : command
{
private:
	const pid_t pid;

public:
	const static char* tag;

	cmd_setsid(pid_t pid): pid(pid)
	{}

	pid_t get_pid() {
		return pid;
	}

	pid_t get_owner() override 
	{
		return pid;
	}

	size_t get_size() override 
	{
		return sizeof(cmd_setsid);
	}

	std::string get_tag() override 
	{
		return tag;
	}

	std::string to_string() override
	{
		std::stringstream ss;
		ss << get_tag() << "(pid = " << pid << ")";
		return ss.str();
	}

	int execute() override;
};
