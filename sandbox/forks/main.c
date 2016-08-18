#include <string.h>
#include <stdlib.h>
#include <errno.h>
#include <stdio.h>
#include <stdarg.h>
#include <stdint.h>

#include <inttypes.h>

#include <unistd.h>
#include <linux/sched.h>
#include <sys/wait.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

typedef void (*job_fun)();

int log_fd = -1;

void add_log(const char *format, ...);
void exit_err(const char *format, ...);
void wait_for_pids(pid_t* from, pid_t* to);
pid_t fork_job(job_fun fun, const char* tag);
pid_t daemonize();


void loop_job()
{
	uint64_t sum = 0;
	for (uint64_t i = 0; i < 10000000000; ++i)
	{
		sum += i;
	}
	add_log("Sum = %"PRId64, sum);
}

void sleep_job()
{
	sleep(10000);
}

void no_job()
{
	return;
}

#define stack_size 100000
char stack[stack_size];
int thread_job(void *arg)
{
	loop_job();
	return 0;
}

int main(int argc, char* argv[])
{
	pid_t pids[5];

	daemonize();
	
	if (argc > 1) {
		log_fd = open(argv[1], O_CREAT | O_TRUNC | O_RDWR, 0666);
		if (log_fd < 0) {
			exit(2);
		}
	}


	add_log("%d", getpid());

	pids[0] = fork_job(loop_job, "loop");
	pids[1] = fork_job(sleep_job, "sleep");
	pids[2] = fork_job(no_job, "exit at once");
	pids[3] = clone(thread_job, (void*) (stack + stack_size), CLONE_VM | CLONE_FS | CLONE_THREAD | CLONE_FILES | CLONE_SIGHAND | SIGCHLD, (void*) NULL);
	if (pids[3] < 0) {
		exit_err("Can't create thread");
	} else {
		add_log("Thread created: %d", pids[3]);
	}

	wait_for_pids(pids, pids + 1);

	return 0;
}

// ============== definitions ===============

pid_t fork_job(job_fun fun, const char* tag)
{
	pid_t pid;
	pid = fork();
	if (pid < 0) exit_err("Can't fork");
	if (pid == 0) {
		fun();
		exit(0);
	}
	add_log("Forked job: tag = [%s]; pid = %d", tag, pid);
	return pid;
}

void wait_for_pids(pid_t* from, pid_t* to)
{
	pid_t* cur = from;
	while (cur <= to) {
		add_log("Waiting for %d", *cur);
		if (waitpid(*cur, NULL, 0) < 0) {
			exit_err("Can't waitpid");
		}
		cur = cur + 1;
	}
}

void add_log(const char *format, ...)
{
	if (log_fd < 0) {
		return;
	}

	char msg[1000];
	int cnt;

	va_list args;
	va_start(args, format);

	cnt = vsprintf(msg, format, args);
	if (write(log_fd, msg, cnt) == -1 || write(log_fd, "\n", sizeof("\n")) == -1) {
		perror("Write failed");
		exit(1);
	}
}

void exit_err(const char *format, ...)
{
	if (log_fd < 0) {
		exit(1);
	}

	char msg[1000];
	int cnt;

	va_list args;
	va_start(args, format);

	cnt = vsprintf(msg, format, args);
	cnt += sprintf(msg + cnt, " [ %s ]\n", strerror(errno));
	if (write(log_fd, msg, cnt) == -1) {
		perror("Write failed");
		exit(1);
	}
	exit(1);
}

pid_t daemonize()
{
    pid_t pid;
    int fd;

    pid = fork();
    if (pid < 0) {
        exit_err("Can't daemonize");
    } else if (pid != 0) {
        exit(0);
    }
    if (setsid() < 0) {
        exit_err("Can't daemonize (setsid failed)");
    }
    if (chdir("/") < 0) {
        exit_err("Can't daemonize (chdir failed)");
    }
    fd = open("/dev/null", O_RDWR, 0);
    if (fd != -1) {
        if (dup2(fd, STDIN_FILENO) < 0) exit_err("dup stdin");
        if (dup2(fd, STDOUT_FILENO) < 0) exit_err("dup stdout");
        if (dup2(fd, STDERR_FILENO) < 0) exit_err("dup stderr");
        if (fd > 2 && close(fd) < 0) {
            exit_err("close fd err");
        }
    }
    umask(027);
    return 0;
}
