#pragma once

#include "cmd_close_fd.h"
#include "cmd_create_thread.h"
#include "cmd_fini.h"
#include "cmd_duplicate_fd.h"
#include "cmd_fork_child.h"
#include "cmd_reg_open.h"
#include "cmd_setsid.h"

/**
 * returns pointer to derived command, which is really
 * pointed by given base pointer
 */
void* command_ptr_get(command* cmd);

/**
 * Returns size of the largest command
 */
size_t command_max_size();

/**
 * dirty cast wrapper
 */
command* ptr_to_command(void* cmd_ptr);

