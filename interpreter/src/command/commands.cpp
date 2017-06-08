#include "command/commands.h"

#include <vector>
#include <algorithm>

namespace {
	size_t calc_cmd_max_size() {
		auto sizes = std::vector<size_t> { sizeof(cmd_close_fd), sizeof(cmd_create_thread), 
			                               sizeof(cmd_duplicate_fd), sizeof(cmd_fini), sizeof(cmd_fork_child),
			                               sizeof(cmd_reg_open), sizeof(cmd_setsid) } ;
		return *std::max_element(sizes.begin(), sizes.end());
	}
}

size_t command_max_size() {
	const static size_t max_size = calc_cmd_max_size();
	return max_size;
}

void* command_ptr_get(command* cmd)
{
	return static_cast<void*>(cmd);
}

command* ptr_to_command(void* cmd_ptr)
{
	return static_cast<command*>(cmd_ptr);
}
