#ifndef LOG_H_INCLUDED__
#define LOG_H_INCLUDED__

#include <pthread.h>

#include "printers.h"

int init_log(int fd);
void deinit_log();


int __global_log_fd();
pthread_mutex_t* __global_log_fd_mutex();

#ifndef LOG_IMPORTANT

	#define log_info(format, args...) \
	    do { \
	    pthread_mutex_lock(__global_log_fd_mutex()); \
	    log_info_fd(__global_log_fd(), format, ##args); \
	    pthread_mutex_unlock(__global_log_fd_mutex()); \
	    } while (0)

	#define log_error(format, args...) \
	    do { \
	    pthread_mutex_lock(__global_log_fd_mutex()); \
	    log_error_fd(__global_log_fd(), format, ##args); \
	    pthread_mutex_unlock(__global_log_fd_mutex()); \
	    } while (0)

	#define log_sys_error(format, args...) \
	    do { \
	    pthread_mutex_lock(__global_log_fd_mutex()); \
	    log_sys_error_fd(__global_log_fd(), format, ##args); \
	    pthread_mutex_unlock(__global_log_fd_mutex()); \
	    } while (0)

	#define log_info(format, args...) \
	    do { \
	    pthread_mutex_lock(__global_log_fd_mutex()); \
	    log_info_fd(__global_log_fd(), format, ##args); \
	    pthread_mutex_unlock(__global_log_fd_mutex()); \
	    } while (0)

	#define log_line(format, args...) \
	    do { \
	    pthread_mutex_lock(__global_log_fd_mutex()); \
	    pref_suff_printf(__global_log_fd(), "", "\n", format, ##args); \
	    pthread_mutex_unlock(__global_log_fd_mutex()); \
	    } while (0)

#else

	#define log_info(format, args...) \
	    do { \
	    } while (0)

	#define log_error(format, args...) \
	    do { \
	    pthread_mutex_lock(__global_log_fd_mutex()); \
	    log_error_fd(__global_log_fd(), format, ##args); \
	    pthread_mutex_unlock(__global_log_fd_mutex()); \
	    } while (0)

	#define log_sys_error(format, args...) \
	    do { \
	    pthread_mutex_lock(__global_log_fd_mutex()); \
	    log_sys_error_fd(__global_log_fd(), format, ##args); \
	    pthread_mutex_unlock(__global_log_fd_mutex()); \
	    } while (0)
	    
	#define log_info(format, args...) \
	    do { \
	    } while (0)

	#define log_line(format, args...) \
	    do { \
	    } while (0)

#endif

#define log_important(format, args...) \
    do { \
    pthread_mutex_lock(__global_log_fd_mutex()); \
    pref_suff_printf(__global_log_fd(), "", "\n", format, ##args); \
    pthread_mutex_unlock(__global_log_fd_mutex()); \
    } while (0)





#endif
