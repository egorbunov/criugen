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

int log_fd = -1;

void add_log(const char *format, ...);
void exit_err(const char *format, ...);
pid_t daemonize();

int main(int argc, char* argv[])
{
	int fdp, fdc;
	pid_t chld;
 //        int pipefd[2];

	// if (pipe2(pipefd, 0) < 0) {
	// 	printf("Can't open pipe");
 //                exit(1);
 //        }


	if (argc != 3) {
		printf("Specify file name and log file name (not relative ;))\n");
		exit(0);
	}

	log_fd = open(argv[1], O_CREAT | O_TRUNC | O_RDWR, 0666);
	if (log_fd < 0) {
		exit(2);
	}

	daemonize();

	add_log("%d", getpid());

	fdp = open(argv[2], O_RDWR);
	if (fdp < 0) exit(1);
	chld = fork();
	if (chld < 0) exit(1);
	if (chld == 0) {
		close(fdp);
		fdc = open(argv[2], O_RDWR);
		if (fdc < 0) exit(1);
		sleep(50);
		exit(0);
	}
	wait(NULL);
	exit(0);
	return 0;
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
