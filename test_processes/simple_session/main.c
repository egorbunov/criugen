#include "cr_env.h"
#include "printers.h"
#include "socket.h"
#include "protocol.h"
#include "process_control.h"
#include "log.h"

void run(void) {
	int p_0;
	int p_1;
	int p_2;
	int p_3;
	int p_4;

	p_0 = getpid();

	// forking with sessions tree
	//                p_0 (sid = 0)
	//                 |
	//                p_1 (sid = 1)
	//             /       |
	//     p_2 (sid = 0)    p_3 (sid = 3)
	//                        |
	//                      p_4 (sid = 1)

	p_1 = pc_fork(p_0);
	p_2 = pc_fork(p_1);
	
	pc_setsid(p_1);
	
	p_3 = pc_fork(p_1);
	p_4 = pc_fork(p_3);

	pc_setsid(p_3);

	// setting init groups equal to pids
	
	pc_setpgid(p_2, 0, 0);
	pc_setpgid(p_4, 0, 0);

	// seting up final groups
}

int main(int argc, char* argv[])
{
	init_restorable_process_tree(argc, argv);
	init_process_contol();

	run();
	ready_to_dump();
	sleep(100);

	deinit_process_contol();
	deinit_cr();
	return 0;
}
