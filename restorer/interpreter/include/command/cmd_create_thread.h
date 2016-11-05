#pragma once

#include <sstream>

#include "command.h"

/**
 * Command describes thread creation with particular thread id `tid`
 * in a process with pid `pid`.
 */
struct cmd_create_thread : command
{
private:
	const pid_t pid;
	const pid_t tid;

public:
	const static char* tag;

	cmd_create_thread(pid_t pid, pid_t tid): pid(pid), tid(tid)
	{}

	pid_t get_pid() {
		return pid;
	}

	pid_t get_tid() {
		return tid;
	}

	pid_t get_owner() override 
	{
		return pid;
	}
	
	size_t get_size() override 
	{
		return sizeof(cmd_create_thread);
	}

	std::string get_tag() override 
	{
		return tag;
	}
	
	std::string to_string() override
	{
		std::stringstream ss;
		ss << get_tag() << "(pid = " << pid << ", tid = " << tid << ")";
		return ss.str();
	}

	int execute() override;
};
