#include <gtest/gtest.h>

#include <vector>
#include <sstream>
#include <iostream>
#include <string>

#include <cstring>
#include <cassert>

#include <fcntl.h>

#include "parse.h"
#include "command/commands.h"

static std::shared_ptr<command> parse_one_cmd_prog(std::string& str) 
{
	std::stringstream ss(str);
	std::vector<std::shared_ptr<command>> program;
	int err = parse_program(ss, program);
	assert(err >= 0);
	assert(program.size() == (size_t) 1);
	return program[0];
}

TEST(parse_test, setsid_parse) 
{
	std::string program_str = "["
	                          "    {"
        					  "       \"#command\": \"SETSID\","
        					  "       \"pid\": 11284"
        					  "    }"
							  "]";
	auto scmd = parse_one_cmd_prog(program_str);

	ASSERT_EQ(scmd.get()->get_owner(), 11284);
	auto cmd = *dynamic_cast<cmd_setsid*>(scmd.get());
	ASSERT_EQ(cmd.get_pid(), 11284);
}

TEST(parse_test, reg_open_parse) 
{
	std::string program_str = "["
							  "     {"		
										"\"#command\": \"REG_OPEN\","
								        "\"fd\": 4,"
								        "\"flags\": ["
								            "\"O_RDWR\","
								            "\"O_LARGEFILE\""
								        "],"
								        "\"mode\": 33204,"
								        "\"offset\": 0,"
								        "\"path\": \"/path/to/file\","
								        "\"pid\": 11285"
  							  "     }"	
							  "]";
	auto scmd = parse_one_cmd_prog(program_str);
	ASSERT_EQ(scmd.get()->get_owner(), 11285);
	auto cmd = *dynamic_cast<cmd_reg_open*>(scmd.get());
	ASSERT_EQ(cmd.get_pid(), 11285);
	ASSERT_EQ(cmd.get_mode(), (mode_t) 33204);
	ASSERT_EQ(cmd.get_offset(), 0);
	ASSERT_EQ(std::string(cmd.get_path()), "/path/to/file");
	ASSERT_EQ(cmd.get_flags(), O_RDWR | O_LARGEFILE);
	ASSERT_EQ(cmd.get_fd(), 4);
}

TEST(parse_test, close_fd_parse) 
{
	std::string program_str = "["
								    "{"
								        "\"#command\": \"CLOSE_FD\","
								        "\"fd\": 4,"
								        "\"pid\": 11285"
								    "}"
							  "]";
	auto scmd = parse_one_cmd_prog(program_str);

	ASSERT_EQ(scmd.get()->get_owner(), 11285);
	auto cmd = *dynamic_cast<cmd_close_fd*>(scmd.get());
	ASSERT_EQ(cmd.get_pid(), 11285);
	ASSERT_EQ(cmd.get_fd(), 4);
}

TEST(parse_test, create_thread_parse) 
{
	std::string program_str = "["
									"{"
							            "\"#command\" : \"CREATE_THREAD\","
							            "\"pid\"     : 11285,"
							            "\"tid\"     : 123"
							        "}"
							  "]";
	auto scmd = parse_one_cmd_prog(program_str);

	ASSERT_EQ(scmd.get()->get_owner(), 11285);
	auto cmd = *dynamic_cast<cmd_create_thread*>(scmd.get());
	ASSERT_EQ(cmd.get_pid(), 11285);
	ASSERT_EQ(cmd.get_tid(), 123);
}

TEST(parse_test, dup_fd_parse) 
{
	std::string program_str = "["
									"{"
								        "\"#command\": \"DUP_FD\","
								        "\"new_fd\": 2,"
								        "\"old_fd\": 0,"
								        "\"pid\": 11284"
								    "}"
							  "]";
	auto scmd = parse_one_cmd_prog(program_str);

	ASSERT_EQ(scmd.get()->get_owner(), 11284);
	auto cmd = *dynamic_cast<cmd_duplicate_fd*>(scmd.get());
	ASSERT_EQ(cmd.get_pid(), 11284);
	ASSERT_EQ(cmd.get_new_fd(), 2);
	ASSERT_EQ(cmd.get_old_fd(), 0);
}

TEST(parse_test, fini_parse) 
{
	std::string program_str = "["
									"{"
									    "\"#command\": \"FINI_CMD\","
									    "\"pid\": 11285"
									"}"
							  "]";
	auto scmd = parse_one_cmd_prog(program_str);

	ASSERT_EQ(scmd.get()->get_owner(), 11285);
	auto cmd = *dynamic_cast<cmd_fini*>(scmd.get());
	ASSERT_EQ(cmd.get_pid(), 11285);
}

TEST(parse_test, fork_child_parse) 
{
	std::string program_str = "["
									"{"
							            "\"#command\" : \"FORK_CHILD\","
							            "\"child_pid\"     : 11285,"
							            "\"pid\"     : 11233,"
							            "\"max_fd\"  : 10"
							        "}"
							  "]";
	auto scmd = parse_one_cmd_prog(program_str);

	ASSERT_EQ(scmd.get()->get_owner(), 11233);
	auto cmd = *dynamic_cast<cmd_fork_child*>(scmd.get());
	ASSERT_EQ(cmd.get_pid(), 11233);
	ASSERT_EQ(cmd.get_child_pid(), 11285);
	ASSERT_EQ(cmd.get_max_fd(), 10);
}