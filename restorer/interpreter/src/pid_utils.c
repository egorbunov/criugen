#include "pid_utils.h"

#include <unistd.h>

int fork_pid(pid_t pid)
{
	(void) pid;
	return fork();
}