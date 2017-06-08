#pragma once

#include <ostream>
#include <string>

#include <sys/types.h>

#define MAX_CMD_SIZE 5000

struct command
{
	/**
	 * @return Pid of interpreter-process to execute that command
	 */
	virtual pid_t get_owner() = 0;

	virtual std::string to_string() = 0;

	/**
	 * @return sizeof of the command structure
	 */
	virtual size_t get_sizeof() = 0;

	/**
	 * @return command name (tag)
	 */
	virtual std::string get_tag() = 0;

	/**
	 * runs command execution
	 * @return exit code: negative number in case of error, positive else
	 */
	virtual int execute() = 0;

	virtual ~command() {};
};
