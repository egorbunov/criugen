#include "command/commands.h"

void* command_ptr_get(command* cmd)
{
	return static_cast<void*>(cmd);
	// if (cmd->get_tag() == cmd_setsid::tag) {
	// 	return static_cast<void*>(dynamic_cast<cmd_setsid*>(cmd));
	// } else if (cmd->get_tag() == cmd_close_fd::tag) {
	// 	return static_cast<void*>(dynamic_cast<cmd_close_fd*>(cmd));
	// } else if (cmd->get_tag() == cmd_reg_open::tag) {
	// 	return static_cast<void*>(dynamic_cast<cmd_reg_open*>(cmd));
	// } else if (cmd->get_tag() == cmd_fork_child::tag) {
	// 	return static_cast<void*>(dynamic_cast<cmd_fork_child*>(cmd));
	// } else if (cmd->get_tag() == cmd_fini::tag) {
	// 	return static_cast<void*>(dynamic_cast<cmd_fini*>(cmd));
	// } else if (cmd->get_tag() == cmd_create_thread::tag) {
	// 	return static_cast<void*>(dynamic_cast<cmd_create_thread*>(cmd));
	// } else if (cmd->get_tag() == cmd_duplicate_fd::tag) {
	// 	return static_cast<void*>(dynamic_cast<cmd_duplicate_fd*>(cmd));
	// } else {
	// 	return nullptr;
	// }
}

command* ptr_to_command(void* cmd_ptr)
{
	return static_cast<command*>(cmd_ptr);
}