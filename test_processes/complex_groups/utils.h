#include <stdio.h>
#include <unistd.h>

pid_t daemonize()
{
    pid_t pid;
    int fd;

    pid = fork();
    if (pid < 0) {
        perror("Can't daemonize");
        exit(1);
    } else if (pid != 0) {
        exit(0);
    }
    if (setsid() < 0) {
        perror("Can't daemonize (setsid failed)");
        exit(1);
    }
    if (chdir("/") < 0) {
        perror("Can't daemonize (chdir failed)");
        exit(1);
    }
    fd = open("/dev/null", O_RDWR, 0);
    if (fd != -1) {
        if (dup2(fd, STDIN_FILENO) < 0) {
            perror("dup stdin");
            exit(1);
        }
        if (dup2(fd, STDOUT_FILENO) < 0) {
            perror("dup stdout");
            exit(1);
        }
        if (dup2(fd, STDERR_FILENO) < 0) {
            perror("dup stderr");
            exit(1);
        }
        if (fd > 2 && close(fd) < 0) {
            perror("close fd err");
            exit(1);
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

