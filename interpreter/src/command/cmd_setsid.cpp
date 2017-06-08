#include "command/cmd_setsid.h"

#include "log.h"

#include <unistd.h>

using namespace log;

const char* cmd_setsid::tag = "SETSID";

int cmd_setsid::execute() {
	if (setsid() < 0) {
		log_stderr("Can't setsid");
		return -1;
	}
	return 0;
}
