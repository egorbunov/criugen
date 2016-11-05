#pragma once

#include <memory>

#include "command/commands.h"

/**
 * Restorer worker - process from target process tree, which
 * at restoring stage acts like interpreter.
 */
class restorer_node {
	const int max_fd;

	/**
	 * next free file descriptor where to open service file
	 * if needed
	 */
	int free_fd;

	/**
	 * socket connection with root restorer process,
	 * which will send us commands to execute
	 */
	int master_connection = -1;

	/**
	 * Read command bytes from socket. Blocking call.
	 * It returnes char array wrapped with shared pointer.
	 */
	std::shared_ptr<char> fetch_command_bytes();

	/**
	 * establish connection with root restorer
	 */
	int connect_to_master();

	/**
	 * remaps file descriptor to free_fd
	 * method must be used for every service file descriptor
	 * because we do not want to pollute fdt of target process 
	 * with restoring stage descriptors
	 * 
	 * @return new fd, to which given was remapped or negative value on error
	 */
	int remap_fd(int fd);

	void cleanup();
public:
	restorer_node(const restorer_node&) = delete;
	restorer_node(restorer_node&&) = delete;
	restorer_node& operator=(const restorer_node&) = delete;
	restorer_node& operator=(restorer_node&&) = delete;

	~restorer_node();

	/**
	 * @param max_fd max used file descriptor for target process, so for 
	 *               opening auxiliary files `max_fd + 1` and greater may
	 *               be used
	 */
	restorer_node(int max_fd): max_fd(max_fd), free_fd(max_fd + 1)
	{}

	int run();
};