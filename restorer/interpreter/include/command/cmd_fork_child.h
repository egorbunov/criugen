#pragma once

#include <sstream>

#include "command.h"

/**
 * Command intended to describe fork system call, when
 * child process with pid `child_pid` forks from it's
 * parent with pid `pid`
 */
struct cmd_fork_child : command 
{
private:
	const pid_t pid;
	const pid_t child_pid;

	/**
	 * largest file descriptor was opened in a process (with child_pid);
	 * we need it because we want to open servie file descriptors 
	 * while restoring
	 */
	int max_fd;

public:
	const static char* tag;

	cmd_fork_child(pid_t pid, pid_t child_pid, int max_fd)
	: pid(pid), child_pid(child_pid), max_fd(max_fd) 
	{}

	pid_t get_pid() {
		return pid;
	}

	pid_t get_child_pid() {
		return child_pid;
	}

	int get_max_fd() {
		return max_fd;
	}

	pid_t get_owner() override 
	{
		return pid;
	}
	
	size_t get_size() override 
	{
		return sizeof(cmd_fork_child);
	}

	std::string get_tag() override 
	{
		return tag;
	}
	
	std::string to_string() override
	{
		std::stringstream ss;
		ss << get_tag() << "(pid = " << pid
		                << ", child_pid = " << child_pid
		                << ", max_fd = " << max_fd << ")";
		return ss.str();
	}

	int execute() override;
};