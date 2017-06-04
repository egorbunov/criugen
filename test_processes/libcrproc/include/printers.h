#ifndef PRINTERS_H_INCLUDED__
#define PRINTERS_H_INCLUDED__

#include <stdio.h>
#include <unistd.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/syscall.h>

#define pref_suff_printf(fd, pref, suff, format, args...) dprintf(fd, pref format suff, ##args)

#define write_logf(fd, log_type, format, args...) \
    pref_suff_printf(fd, "[pid = %d | tid = %ld] %s: ", "\n", \
    	format, getpid(), syscall(__NR_gettid), log_type, ##args)

#define write_suff_logf(fd, log_type, suffix, format, args...) \
    pref_suff_printf(fd, "[pid = %d | tid = %ld] %s: ", " [%s]\n", \
    	format, getpid(), syscall(__NR_gettid), log_type, ##args, suffix)

#define log_info_fd(fd, format, args...) \
    do { \
    if (fd < 0) { \
    } else { \
    	write_logf(fd, "INFO", format, ##args); \
    } \
    } while(0)

#define log_error_fd(fd, format, args...) \
    do { \
    if (fd < 0) { \
    } else { \
    	write_logf(fd, "ERROR", format, ##args); \
    } \
    } while(0)

#define log_sys_error_fd(fd, format, args...) \
    do { \
    if (fd < 0) { \
    } else { \
    	write_suff_logf(fd, "ERROR", strerror(errno), format, ##args); \
    } \
    } while(0)


#endif