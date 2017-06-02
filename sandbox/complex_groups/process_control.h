#ifndef PROCESS_CONTROL_H_INCLUDED__
#define PROCESS_CONTROL_H_INCLUDED__

#include <stdint.h>

/**
 * Initializes current process as process control master.
 * 
 * Creates two threads in the current process: master process control thread,
 * which listens for connections and stores connected sockets; Another thread is
 * a slave thread for current process, which listens for commands and executes them.
 *
 * Assumes that log module is initialized
**/
int init_process_contol();

void deinit_process_contol();

/**
 * @return pid of forked child be executor_pid process, negative in case of error
 */
int pc_fork(int executor_pid);

/**
 * @param executor_pid -- pid of the process, which will execute setpgid(pid, pgid)
 * @return 0 on success (command was executed suuccesfully), 
 *         negative on failure (failure may occur on this side ot on the
 * 		   side of the executor)
 */
int pc_setpgid(int executor_pid, uint32_t pid, uint32_t pgid);

/**
 * Send finish message to process with executor_pid
 */
int pc_finish(int executor_pid);


#endif
