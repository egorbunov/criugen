#include "command/command.h"

#include <map>
#include <string>

using std::string;
using std::map;

static map<cmd_type, string> cmd_tag_map = {
	{ CMD_FORK_CHILD,    "FORK_CHILD" },
	{ CMD_SETSID,        "SETSID" },
	{ CMD_REG_OPEN,      "REG_OPEN" },
	{ CMD_CLOSE_FD,      "CLOSE_FD" },
	{ CMD_DUPLICATE_FD,  "DUP_FD" },
	{ CMD_CREATE_THREAD, "CREATE_THREAD" },
	{ CMD_FINI,          "FINI_CMD" },
	{ CMD_UNKNOWN,       "UNKNOWN_COMMAND" }
};

static map<string, cmd_type> build_tag_cmd_map() {
	map<string, cmd_type> result;
	for (const auto& p : cmd_tag_map) {
		result[p.second] = p.first;
	}
	return result;
}

static map<string, cmd_type> tag_cmd_map = build_tag_cmd_map();

static map<cmd_type, size_t> cmd_size_map = {
	{ CMD_FORK_CHILD,    sizeof(cmd_fork_child) },
	{ CMD_SETSID,        sizeof(cmd_setsid) },
	{ CMD_REG_OPEN,      sizeof(cmd_reg_open) },
	{ CMD_CLOSE_FD,      sizeof(cmd_close_fd) },
	{ CMD_DUPLICATE_FD,  sizeof(cmd_duplicate_fd) },
	{ CMD_CREATE_THREAD, sizeof(cmd_create_thread) },
	{ CMD_FINI,          sizeof(cmd_fini) },
	{ CMD_UNKNOWN,       0 }
};

size_t get_cmd_number() 
{
	return cmd_tag_map.size();
}

const char* get_cmd_tag(enum cmd_type cmd_id) 
{
	auto it = cmd_tag_map.find(cmd_id);
	if (it == cmd_tag_map.end()) {
		return NULL;
	}
	return it->second.c_str();
}

int get_cmd_size(enum cmd_type cmd_id) 
{
	auto it = cmd_size_map.find(cmd_id);
	if (it == cmd_size_map.end()) {
		return -1;
	}
	return it->second;
}

enum cmd_type get_cmd_by_str(const char* str) {
	auto it = tag_cmd_map.find(str);
	if (it == tag_cmd_map.end()) {
		return CMD_UNKNOWN;
	}
	return it->second;
}