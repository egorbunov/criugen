#include "command/command.h"

#include <map>
#include <string>

using std::string;
using std::map;

static map<int, string> cmd_tag_map = {
	{ CMD_FORK_CHILD,    "FORK_CHILD" },
	{ CMD_SETSID,        "SETSID" },
	{ CMD_REG_OPEN,      "REG_OPEN" },
	{ CMD_CLOSE_FD,      "CLOSE_FD" },
	{ CMD_DUPLICATE_FD,  "DUP_FD" },
	{ CMD_CREATE_THREAD, "CREATE_THREAD" },
	{ CMD_FINI,          "FINI_CMD" },
	{ CMD_UNKNOWN,       "UNKNOWN_COMMAND" }
};

static map<int, size_t> cmd_size_map = {
	{ CMD_FORK_CHILD,    sizeof(cmd_fork_child) },
	{ CMD_SETSID,        sizeof(cmd_setsid) },
	{ CMD_REG_OPEN,      sizeof(cmd_reg_open) },
	{ CMD_CLOSE_FD,      sizeof(cmd_close_fd) },
	{ CMD_DUPLICATE_FD,  sizeof(cmd_duplicate_fd) },
	{ CMD_CREATE_THREAD, sizeof(cmd_create_thread) },
	{ CMD_FINI,          sizeof(cmd_fini) },
	{ CMD_UNKNOWN,       0 }
}

/**
 * Here all registered procedures are stored
 */
static map<string, map<int, int_ret_fun>> procedure_registry;

size_t get_cmd_number() 
{
	return cmd_tag_map.size();
}

const char* get_cmd_tag(int cmd_id) 
{
	auto it = cmd_tag_map.find(cmd_id);
	if (it == cmd_tag_map.end()) {
		return NULL;
	}
	return it->second.c_str();
}

int get_cmd_size(int cmd_id) 
{
	auto it = cmd_size_map.find(cmd_id);
	if (it == cmd_size_map.end()) {
		return -1;
	}
	return it->second;
}

bool register_procedure_for_cmd(const char* tag, 
	                            int cmd_id, 
	                            int_ret_fun fun) 
{
	auto map_it = procedure_registry.
				  	insert({ tag, map<int, int_ret_fun>() }).first;
	auto fun_map = map_it->second;
	auto res = fun_map.insert({ cmd_id, fun });
	if (res.second == false) {
		// procedure already registered, replacing
		res.first->second = fun;
		return false;
	}
	return true;
}

int_ret_fun get_procedure_for_cmd(const char* tag, int cmd_id) 
{
	auto map_it = procedure_registry.find(tag);
	if (map_it == procedure_registry.end()) {
		return NULL;
	}
	auto it = map_it->second.find(cmd_id);
	if (it == map_it->second.end()) {
		return NULL;
	}
	return it->second;
}