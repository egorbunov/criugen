#include "log.h"

static zlog_category_t* log_category;

int log_init(const char* zlog_conf_path)
{
	if (zlog_init(zlog_conf_path)) {
		return -1;
	}
	log_category = zlog_get_category("interpreter_cat");
	if (!log_category) {
		return -2;
	}
	return 0;
}

zlog_category_t* get_log_category()
{
	return log_category;
}

void log_fini(void)
{
	zlog_fini();
}
