#include "interpreter.h"

#include <stdio.h>

#include "int_index.h"
#include "ipc.h"
#include "fd_utils.h"

typedef int pipe_t[2];
typedef vec_t(pipe_t) vec_pipes;

/**
 * Master interpreter procedure, which responsible for
 * sending commands to interpreter-workers -- processes
 * from restoring process tree, who will evaluate commands
 * and resotre themselves
 * @param  p command list
 */
int interpreter_run(const command_vec* p)
{
	int i;
	struct command cmd;
	vec_int_t id_pid_map;
	// we need index to sotre data attached to particular processes in arrays
	struct int_index pid_idx; 


	vec_init(&id_pid_map);

	vec_foreach(p, cmd, i) {
		printf("!");
	}

	(void) pid_idx;
	(void) cmd;
	return 0;
}

/**
 * Main procedure for interpreter-worker (particular process from
 * process tree to restore)
 * @param p_from_master fd for pipe to listen to master-interpreter msgs
 * @param p_to_master   fd for pipe to send msgs to master
 */
// static void interpreter_worker(int p_from_master, int p_to_master)
// {
// 	(void) p_from_master;
// 	(void) p_to_master;
// }
