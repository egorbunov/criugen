#include "restorer.h"

#include <iostream>

#include <cstring>

#include <unistd.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <sys/socket.h>
#include <sys/wait.h>

#include "log.h"
#include "io_utils.h"
#include "command/commands.h"
#include "ipc.h"
#include "pid_utils.h"
#include "restorer_node.h"

using namespace log;

namespace
{
	void sigchld_handler(int sig);
	int setup_child_handler();
}

void restorer::cleanup()
{
	for (const auto& p : sockets) {
		if (close(p.second) < 0) {
			log_error("Can't close socket %d", p.second);
		}
	}
	sockets.clear();
	for (const auto& p : connections) {
		if (close(p.second) < 0) {
			log_error("Can't close connection %d", p.second);
		}
	}
	connections.clear();
}

restorer::~restorer()
{
	log_info("Finalize restorer...");
	cleanup();
}

int restorer::create_sock_for_pid(pid_t pid)
{
	if (sockets.find(pid) != sockets.end()) {
		log_error("Socket is already opened for pid %d", pid);
		return -1;
	}
	int srv_fd = socket_open(pid);
	if (srv_fd < 0) {
		log_error("Can't open socket for pid %d", pid);
		return -1;
	}
	sockets[pid] = srv_fd;
	return 0;
}

int restorer::accept_node_connection(pid_t pid)
{
	if (sockets.find(pid) == sockets.end()) {
		log_error("Socket for pid [ %d ] not exists!", pid);
		return -1;
	}
	if (connections.find(pid) != connections.end()) {
		log_error("Connection is already establish pid %d", pid);
		return -1;
	}
	log_info("Accepting connection from [ %d ] ...", pid);
	int conn_fd = accept(sockets[pid], NULL, NULL);
	if (conn_fd < 0) {
		log_error("Can't open connection Master <-> %d", pid);
		return -1;
	}
	log_info("Connection accepted: %d", conn_fd);
	connections[pid] = conn_fd;
	return 0;
}

int restorer::run()
{
	// close first 3 fd to start with clean FDT!
	log_info("Cleaning fdt before starting restorer...");
	if (close(STDIN_FILENO) < 0 || close(STDOUT_FILENO) < 0 || close(STDERR_FILENO) < 0) {
		log_stderr("Can't clean fdt before start restorer!");
		return -1;
	}

	if (setup_child_handler()) {
		log_stderr("Can't setup child handler");
		return -1;
	}
	for (auto& scmd : program) {
		auto cmd = scmd.get();
		// commands may be adressed to master restorer
		if (scmd->get_tag() == cmd_fork_child::tag) {
			auto fork_cmd = dynamic_cast<cmd_fork_child*>(cmd);
			pid_t child = fork_cmd->get_child_pid();
			log_info("Got fork command: %s", cmd->to_string().c_str());
			if (create_sock_for_pid(child) < 0) {
				return -1;
			}
			if (cmd->get_owner() == 0) {
				pid_t pid = fork_pid(child);
				if (pid < 0) {
					log_error("Can't fork interpreter %d", child);
					return -1;
				} else if (pid == 0) { // child process
					cleanup();
					log_info("Starting new restorer node...");
					restorer_node new_node(fork_cmd->get_max_fd());
					int ret = new_node.run();
					if (ret < 0) {
						log_error("Restorer node failed...");
					}
					return ret;
				}
			} else {
				send_command(cmd);
			}
			if (accept_node_connection(child) < 0) {
				return -1;
			}
		} else if (cmd->get_owner() == 0) {
			log_info("Master restorer executing command %s", cmd->to_string().c_str());
			cmd->execute();
		} else {
			// just delegating command evaluation to its owning node
			send_command(cmd);
		}
	}
	return 0;
}

int restorer::send_command(command* cmd)
{
	log_info("Sending command [ %s ] to [ %d ]", cmd->get_tag().c_str(), cmd->get_owner());

	int conn = connections[cmd->get_owner()]; // TODO: consider error no key
	auto cmd_size = cmd->get_size();
	if (io_write(conn, cmd_size) < 0) {
		log_stderr("Can't send command size through socket");
		return -1;
	}
	char* cmdp = static_cast<char*>(command_ptr_get(cmd));
	if (io_write(conn, cmdp, cmd_size) < 0) {
		log_error("Can't send command via socket [%s]", strerror(errno));
		return -1;
	}
	return 0;
}

namespace 
{
	void sigchld_handler(int sig)
	{
	    pid_t p;
	    int status;
	    while ((p = waitpid(-1, &status, WNOHANG)) != -1) {
	    	log_info("Child dead [ %d ] catched", p);
	    }
	    (void) sig;
	}

	int setup_child_handler()
	{
		struct sigaction sa;
		memset(&sa, 0, sizeof(sa));
		sa.sa_handler = sigchld_handler;
		return sigaction(SIGCHLD, &sa, NULL);
	}
}
