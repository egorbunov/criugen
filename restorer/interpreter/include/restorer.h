#pragma once

#include <unordered_map>
#include <vector>
#include <memory>

#include <cerrno>

#include <unistd.h>

#include "command/command.h"

class restorer {
public:
	restorer(const restorer&) = delete;
	restorer(restorer&&) = delete;
	restorer& operator=(const restorer&) = delete;
	restorer& operator=(restorer&&) = delete;

	restorer(const std::vector<std::unique_ptr<command>>& program): program(program)
	{}

	~restorer();

	int run();
private:
	// server socket fd for every interpreter-worker
	std::unordered_map<pid_t, int> sockets;
	// connection fd for every interpreter-worker (restorer node)
	std::unordered_map<pid_t, int> connections;
	// program to interpret
	const std::vector<std::unique_ptr<command>>& program;

	/**
	 * send command to socket, which connected to process with pid = cmd->get_owner(),
	 * so that socket was created with `create_sock_for_pid(pid)` and accepted with
	 * `accept_node_connection(pid)
	 */
	int send_command(command* cmd);

	/**
	 * cleanup restorer process resources (do it before fork and exit)
	 */
	void cleanup();

	/**
	 * accept connection from restorer node with given pid
	 */
	int accept_node_connection(pid_t pid);

	/**
	 * create unix socket for restorer node with given pid
	 */
	int create_sock_for_pid(pid_t pid);
};
