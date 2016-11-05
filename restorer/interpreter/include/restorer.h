#pragma once

#include <unordered_map>
#include <vector>
#include <memory>

#include <cerrno>

#include <unistd.h>

#include "command/command.h"

class restorer {
	// server socket fd for every interpreter-worker
	std::unordered_map<pid_t, int> sockets;
	// connection fd for every interpreter-worker (restorer node)
	std::unordered_map<pid_t, int> connections;
	// program to interpret
	const std::vector<std::shared_ptr<command>>& program;

	int send_command(command* cmd);
	void cleanup();

	/**
	 * accept connection from restorer node with given pid
	 */
	int accept_node_connection(pid_t pid);

	/**
	 * create unix socket for restorer node with given pid
	 */
	int create_sock_for_pid(pid_t pid);
public:
	restorer(const restorer&) = delete;
	restorer(restorer&&) = delete;
	restorer& operator=(const restorer&) = delete;
	restorer& operator=(restorer&&) = delete;

	restorer(const std::vector<std::shared_ptr<command>>& program): program(program)
	{}

	~restorer();

	int run();
};
