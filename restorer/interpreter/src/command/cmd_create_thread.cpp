#include "command/cmd_create_thread.h"

#include "log.h"

using namespace log;

const char* cmd_create_thread::tag = "CREATE_THREAD";

int cmd_create_thread::execute() {
	log_error("Can't create thread; not supported...");
	return -1;
}
