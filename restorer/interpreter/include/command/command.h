#ifndef COMMAND_H_INCLUDED__
#define COMMAND_H_INCLUDED__

#include <sys/types.h>
#include <linux/limits.h>

/**
 * Command ID
 */
enum cmd_type
{
	CMD_FORK_CHILD = 0,
	CMD_SETSID,
	CMD_REG_OPEN,
	CMD_CLOSE_FD,
	CMD_DUPLICATE_FD,
	CMD_CREATE_THREAD,
	CMD_FINI,
	CMD_UNKNOWN
};

#define MAX_CMD_SIZE 300

/**
 * Command wrapper used for uniform command access.
 *
 * No inheritance and other stuff used due to C language
 * in mind
 */
struct command
{
	enum cmd_type type;
	pid_t owner; // command runner (interpreter) pid
	void* c; // command
};


/**
 * Command equivalent to setsid() system call
 */
struct cmd_setsid
{
	pid_t pid;
};

/**
 * Command intended to describe fork system call, when
 * child process with pid `child_pid` forks from it's
 * parent with child `pid`
 */
struct cmd_fork_child
{
	pid_t pid;
	pid_t child_pid;

	/**
	 * largest file descriptor was opened in a process (with child_pid);
	 * we need it because we want to open servie file descriptors 
	 * while restoring
	 */
	int max_fd; 
};

/**
 * Command describes thread creation with particular thread id `tid`
 * in a process with pid `pid`.
 */
struct cmd_create_thread
{
	pid_t pid;
	pid_t tid;
};

/**
 * This command contains regular file state, needed for it's restoring.
 * So it just stores process pid `pid`, where given file must
 * be opened.
 */
struct cmd_reg_open
{
	pid_t pid;
	char path[PATH_MAX];
	int flags;
	mode_t mode;
	int offset;
	int fd;
};

/**
 * Command equivalent to syscall `close(fd)`
 */
struct cmd_close_fd
{
	pid_t pid;
	int fd;
};

/**
 * Command equivalent to syscall `dup2(old_fd, new_fd)`
 */
struct cmd_duplicate_fd
{
	pid_t pid;
	int old_fd;
	int new_fd;
};

/**
 * Command, which designates the end of command stream,
 * menaning that restorer process, which got such command,
 * done all it's restoring job (which is described by commands =))
 */
struct cmd_fini
{
	pid_t pid;
};

/**
 * @return number of commands registered
 */
size_t get_cmd_number();

/**
 * @param command type
 * @return tag for command with given id; static string
 */
const char* get_cmd_tag(enum cmd_type cmd_id);

/**
 * If given string equal to any cmd tag, that command is returned
 * @param str (tag)
 * @return cmd id
 */
enum cmd_type get_cmd_by_str(const char* str);

/**
 * @param command id
 * @return sizeof for command with specified id of -1 if no such
 */
int get_cmd_size(enum cmd_type cmd_id);


#endif
