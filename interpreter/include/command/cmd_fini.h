#pragma once

#include <sstream>

#include "command.h"


struct cmd_fini : command
{
private:
	const pid_t pid;

public:
	const static char* tag;

	cmd_fini(pid_t pid): pid(pid)
	{}

	pid_t get_pid() {
		return pid;
	}

	pid_t get_owner() override 
	{
		return pid;
	}
	
	size_t get_sizeof() override 
	{
		return sizeof(cmd_fini);
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