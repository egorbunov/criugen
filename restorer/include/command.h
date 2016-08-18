#pragma once

#include <string>

#include <sys/types.h>

/**
 * Every command, passed to interpreter, has it's executor -- 
 * process (or thread, maybe), which is responsible for execution.
 * That executor (or helper) acts like context for command evaluation.
 * For now it seems that it's enough to treat every process in restored 
 * process tree as such executors (at the very end of the restore stage
 * that processes should morph into target processes with right VM and 
 * all that). Also initial interpreter process may act like executor.
 *
 * So executors are:
 *     - initial interpreter process (identified by -1; OK?)
 *     - every process created with `fork_child_cmd` command or `init_cmd` and
 *       identified by `pid`.
 *
 * Command execution should fail if there is no executor with specified id.
 */
struct command
{
	pid_t executor;
}

/**
 * Command, which must be executed firstly.
 * It's purpose is to spawn root process of process tree.
 * `executor` argument is ignored so command must be executed by initial 
 * interpreter process.
 */
struct init_cmd : command
{
	pid_t pid;
}

struct fork_child_cmd : command
{
	pid_t pid; // new child pid (executor becomes it's parent)
}

struct create_thread_cmd : command
{
	pid_t tid;
}

struct open_reg_file_cmd : command
{
	std::string file_path;
	int flags;
	int offset;
	int fd; // after open, regular file must be placed at specified fd
}

struct close_file_cmd : command
{
	int fd;
}