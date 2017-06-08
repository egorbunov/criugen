#include "restorer_node.h"

#include <memory>

#include <unistd.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <sys/socket.h>
#include <sys/wait.h>

#include "log.h"
#include "io_utils.h"
#include "ipc.h"
#include "pid_utils.h"
#include "fd_utils.h"

using namespace log;

namespace
{
	void sigchld_handler(int sig);
	int setup_child_handler();
}
int restorer_node::fetch_command_bytes(char* buffer, size_t buffer_size)
{
	size_t cmd_size;
	log_info("Fetching command from socket %d...", master_connection);
	if (io_read<size_t>(master_connection, &cmd_size) < 0) {
		log_stderr("Can't fetch commnd, failed to read cmd size");
		return -1;
	}
	if (cmd_size > buffer_size) {
		log_error("Buffer is to small to write command: %d < %d", buffer_size, cmd_size);
		return -1;
	}
	if (io_read(master_connection, buffer, cmd_size) < 0) {
		log_stderr("Can't fetch command, faild to read cmd bytes");
		return -1;
	}
	return 0;
}

int restorer_node::connect_to_master()
{
	log_info("Connecting to master socket...");
	master_connection = socket_connect(getpid());
	if (master_connection < 0) {
		log_stderr("Can't connect to master restorer from node [ %d ]", getpid());
		return -1;
	}
	log_info("Connected!");
	// remapping socket fd
	master_connection = remap_fd(master_connection);
	log_info("Remapped connection to %d", master_connection);
	if (master_connection < 0) {
		return -1;
	}
	return 0;
}

int restorer_node::remap_fd(int fd)
{
	int target = free_fd;
	int r = move_fd(fd, free_fd);
	if (r < 0) {
		log_error("Can't remap fd [ %d ] to [ %d ], err: %d", fd, free_fd, r);
		return r;
	}
	free_fd += 1;
	return target;
}

restorer_node::~restorer_node()
{
	log_info("Finalizing restorer node...");
	cleanup();
}

int restorer_node::run()
{
	if (setup_child_handler()) {
		log_stderr("Can't setup child handler");
		return -1;
	}

	if (connect_to_master() < 0) {
		return -1;
	}

	bool command_pending = true;
	auto cmd_buf_ptr = std::make_unique<char[]>(command_max_size());
	while (command_pending) {
		log_info("Waiting for command...");
		if (fetch_command_bytes(cmd_buf_ptr.get(), command_max_size()) < 0) {
			log_error("Failed to fetch command!");
			return -1;
		}
		auto cmd = ptr_to_command(static_cast<void*>(cmd_buf_ptr.get()));
		if (cmd->get_owner() != getpid()) {
			log_error("Got foreign node [ %d ] command", cmd->get_owner());
			return -1;
		}

		log_info("Executing command %s", cmd->to_string().c_str());

		// fork is a special case due to cleanup
		if (cmd->get_tag() == cmd_fork_child::tag) {
			auto fork_cmd = dynamic_cast<cmd_fork_child*>(cmd);
			pid_t child = fork_cmd->get_child_pid();
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
			if (cmd->get_tag() == cmd_fini::tag) {
				// last commnd ==> we can cleanup all service stuff!
				cleanup();
				command_pending = false;
			}
			int ret = cmd->execute();
			if (ret < 0) {
				log_error("Command [ %s ] execution failed", cmd->to_string().c_str());
				return ret;
			}
		}
	}
	return 0;
}

void restorer_node::cleanup()
{
	if (master_connection >= 0) {
		log_info("Closing connection %d", master_connection);
		close(master_connection); // it is okay to fail here, I think
	}
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


