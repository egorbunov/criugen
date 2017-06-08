#include "parse.h"

#include <string>
#include <sstream>
#include <iterator>
#include <memory>

#include "json11.hpp"

#include "command/commands.h"
#include "parse_util.h"
#include "log.h"

static cmd_setsid* parse_cmd_setsid(const json11::Json&);
static cmd_close_fd* parse_cmd_close_fd(const json11::Json&);
static cmd_reg_open* parse_cmd_reg_open(const json11::Json&);
static cmd_fork_child* parse_cmd_fork_child(const json11::Json&);
static cmd_fini* parse_cmd_fini(const json11::Json&);
static cmd_create_thread* parse_create_thread(const json11::Json&);
static cmd_duplicate_fd* parse_duplicate_fd(const json11::Json&);

int parse_program(std::istream &in, std::vector<std::unique_ptr<command>>& program)
{
	std::string program_str(std::istreambuf_iterator<char>(in), {});
	std::string err;
	auto arr = json11::Json::parse(program_str, err);
	if (!err.empty() || !arr.is_array()) {
		log::log_error("Not array or error");
		return -1;
	}

	for (auto &cmd_json : arr.array_items()) {
		if (!cmd_json["#command"].is_string()) {
			log::log_error("No command field");
			return -1;
		}
		auto cmd_tag = cmd_json["#command"];
		command* cmd = nullptr;
		if (cmd_tag == cmd_setsid::tag) {
			cmd = parse_cmd_setsid(cmd_json);
		} else if (cmd_tag == cmd_close_fd::tag) {
			cmd = parse_cmd_close_fd(cmd_json);
		} else if (cmd_tag == cmd_reg_open::tag) {
			cmd = parse_cmd_reg_open(cmd_json);
		} else if (cmd_tag == cmd_fork_child::tag) {
			cmd = parse_cmd_fork_child(cmd_json);
		} else if (cmd_tag == cmd_fini::tag) {
			cmd = parse_cmd_fini(cmd_json);
		} else if (cmd_tag == cmd_create_thread::tag) {
			cmd = parse_create_thread(cmd_json);
		} else if (cmd_tag == cmd_duplicate_fd::tag) {
			cmd = parse_duplicate_fd(cmd_json);
		}
		if (cmd == nullptr) {
			log::log_error("Command not parsed");
			return -1;
		}
		program.push_back(std::unique_ptr<command>(cmd));
	}
	return 0;
}

static cmd_setsid* parse_cmd_setsid(const json11::Json& json) {
	if (!json["pid"].is_number()) {
		return nullptr;
	}
	return new cmd_setsid { json["pid"].int_value() };
}

static cmd_close_fd* parse_cmd_close_fd(const json11::Json& json) {
	if (!json["pid"].is_number() ||
		!json["fd"].is_number()) {
		return nullptr;
	}
	return new cmd_close_fd { json["pid"].int_value(), json["fd"].int_value() };
}

static cmd_reg_open* parse_cmd_reg_open(const json11::Json& json) {
	if (!json["pid"].is_number() ||
		!json["path"].is_string() ||
		!json["flags"].is_array() ||
		!json["mode"].is_number() ||
		!json["offset"].is_number() ||
		!json["fd"].is_number()) {
		return nullptr;
	}
	int flags = 0;
	for (auto& f : json["flags"].array_items()) {
		if (!f.is_string()) {
			return nullptr;
		}
		int flag = parse_open_flag(f.string_value().c_str());
		if (flag < 0) {
			return nullptr;
		}
		flags |= flag;
	}
	return new cmd_reg_open {
		json["pid"].int_value(),
		json["path"].string_value().c_str(),
		flags,
		(mode_t) json["mode"].int_value(),
		json["offset"].int_value(),
		json["fd"].int_value()
	};
}

static cmd_fork_child* parse_cmd_fork_child(const json11::Json& json) {
	if (!json["pid"].is_number() ||
		!json["child_pid"].is_number() ||
		!json["max_fd"].is_number()) {
		return nullptr;
	}
	return new cmd_fork_child { json["pid"].int_value(), 
	                            json["child_pid"].int_value(),
	                            json["max_fd"].int_value() };
}

static cmd_fini* parse_cmd_fini(const json11::Json& json) {
	if (!json["pid"].is_number()) {
		return nullptr;
	}
	return new cmd_fini { json["pid"].int_value() };
}

static cmd_create_thread* parse_create_thread(const json11::Json& json) {
	if (!json["pid"].is_number() || !json["tid"].is_number()) {
		return nullptr;
	}
	return new cmd_create_thread { json["pid"].int_value(), json["tid"].int_value() };
}

static cmd_duplicate_fd* parse_duplicate_fd(const json11::Json& json) {
	if (!json["pid"].is_number() || !json["old_fd"].is_number() ||
		!json["new_fd"].is_number()) {
		return nullptr;
	}
	return new cmd_duplicate_fd { 
		json["pid"].int_value(), json["old_fd"].int_value(), json["new_fd"].int_value()
	 };
}
