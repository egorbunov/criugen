#ifndef LOG_H_INCLUDED__
#define LOG_H_INCLUDED__

#include <errno.h>
#include <string.h>

#include <zlog.h>

int log_init(const char* zlog_conf_path);
zlog_category_t* get_log_category();
void log_fini(void);

#define log_info(...) \
	zlog_info(get_log_category(), __VA_ARGS__)

#define log_error(...) \
	zlog_error(get_log_category(), __VA_ARGS__)

#define log_stderr(msg) \
	zlog_error(get_log_category(), "%s [ %s ]", msg, strerror(errno))

#endif