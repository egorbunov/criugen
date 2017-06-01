#include <stdio.h>
#include <unistd.h>

static int log_fd = -1;

void init_log(const char* log_filename) {
    log_fd = open(log_filename, O_CREAT | O_TRUNC | O_RDWR, 0666);
    if (log_fd < 0) {
        perror("Open log failed");
        exit(2);
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

void log_error(const char *format, ...)
{
    if (log_fd < 0) {
        return;
    }

    char msg[1000];
    int cnt;
    cnt = 0;

    va_list args;
    va_start(args, format);

    cnt += sprintf(msg + cnt, "ERROR: ");
    cnt += vsprintf(msg + cnt, format, args);
    cnt += sprintf(msg + cnt, "\n");
    if (write(log_fd, msg, cnt) == -1) {
        perror("Write failed");
        exit(1);
    }
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
    // umask(027);
    umask(011);
    return 0;
}

char* rand_string(char *str, size_t size)
{
    const char charset[] = "abcdefghijklmnopqrstuvwxyz1234567890";
    if (size) {
        --size;
        for (size_t n = 0; n < size; n++) {
            int key = rand() % (int) (sizeof charset - 1);
            str[n] = charset[key];
        }
        str[size] = '\0';
    }
    return str;
}

char* rand_tmpfile(char *str, size_t len) {
    const int prefixlen = 5;
    if (len < prefixlen + 1) {
        return NULL;
    }
    char* rnd_str = rand_string(str + prefixlen, len - prefixlen);
    sprintf(str, "/tmp/%s", rnd_str);
    return str;
}
