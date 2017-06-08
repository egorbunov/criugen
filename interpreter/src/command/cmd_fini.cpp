#include "command/cmd_fini.h"

#include <unistd.h>

#include "log.h"

using namespace log;

const char* cmd_fini::tag = "FINI_CMD";

int cmd_fini::execute() {
	log_info("Sleeping...");
	sleep(10);
	return 0;
}
