#include <string.h>
#include <stdlib.h>
#include <errno.h>
#include <stdio.h>
#include <stdarg.h>
#include <stdint.h>

#include <inttypes.h>

#include <unistd.h>
#include <linux/sched.h>
#include <sys/wait.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <time.h>

#include <sys/mman.h>

#include <pthread.h>

#include "utils.h"

static const int MAP_SIZE = 4096 * 10;

int file_creator(const char* filename);
int file_opener(const char* filename);
void* shared_anon_mapper(int length);
void* private_anon_mapper(int length);
void* file_shared_mapper(int fd, int length);
void* file_private_mapper(int fd, int length);

// thread funcs
void* idle_thread_fun(void* arg) {
	static int counter = 0;
	for (int i = 0; i < 100; ++i) {
		counter += 1;
		sleep(1);
	}
	return NULL;
}

int main(int argc, char* argv[])
{
	int fdp, fdc;
	pid_t chld;

	srand(time(NULL));

	if (argc > 1) {
		init_log(argv[1]);
	} else {
		printf("%s\n", "No log file specified, continue without logging.");
	}

	daemonize();	
	add_log("%d", getpid());

	// opening a pipe
    int pipefd[2];
	if (pipe(pipefd) < 0) {
	    exit_err("pipe open");
    }

	// spwning additional thread
	pthread_t th;
	if (pthread_create(&th, NULL, idle_thread_fun, NULL) < 0) {
		exit_err("thread spawn");
	}

	// start forking process tree
	char filename_buf[50];

	char* tmp_file = rand_tmpfile(filename_buf, 20);
	add_log("creating tmp file: [%s]", tmp_file);

	void* pa_addr_0 = private_anon_mapper(MAP_SIZE);
	void* sa_addr_0 = shared_anon_mapper(MAP_SIZE);
	int fd_0 = file_creator(tmp_file);

	int child01 = fork();
	if (child01 < 0) exit_err("fork child 01");
	if (child01 == 0) {
		// child 1 of parent 0
		int child11 = fork();
		if (child11 < 0) exit_err("fork child 11");
		if (child11 == 0) {
			// child 1 of parent 1
		} else {
			// child 1 of parent 0
			if (munmap(sa_addr_0, MAP_SIZE) < 0) exit_err("unmap sa_addr_0");
			int child12 = fork();
			if (child12 < 0) exit_err("fork child 12");
			if (child12 == 0) {
				// child 2 of parent 1
				if (munmap(pa_addr_0, MAP_SIZE) < 0) exit_err("unmap pa_addr_0");
			} else {
				// child 1 of parent 0
				if (close(fd_0) < 0) exit_err("close fd_0");
				int fd_01 = file_opener(tmp_file);
				file_private_mapper(fd_01, MAP_SIZE);
				file_shared_mapper(fd_01, MAP_SIZE);
			}
		}
	} else {
		// root process
		int child02 = fork();
		if (child02 < 0) exit_err("fork child 02");
		if (child02 == 0) {

		} else {
			close(fd_0);
		}
	}

	sleep(100);
	return 0;
}

int file_creator(const char* filename) {
	int fd = open(filename, O_CREAT, 0666);
	if (fd < 0) {
		exit_err("file creator failed");
	}
	return fd;
}

int file_opener(const char* filename) {
	int fd = open(filename, O_RDWR | O_APPEND);
	if (fd < 0) {
		exit_err("file opener failed");
	}
	const char* str = "file data\n";
	if (write(fd, str, sizeof(str)) < 0) {
		exit_err("file write in opener"); 
	}

	return fd;
}

void* shared_anon_mapper(int length) {
	void* addr = mmap(NULL, length, PROT_READ | PROT_WRITE, MAP_SHARED | MAP_ANON, -1, 0);
	if (addr == (void*) -1) {
		exit_err("shared anon mmap");
	}
	return addr;
}

void* private_anon_mapper(int length) {
	void* addr = mmap(NULL, length, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANON, -1, 0);
	if (addr == (void*) -1) {
		exit_err("private anon mmap");
	}
	return addr;
}

void* file_shared_mapper(int fd, int length) {
	void* addr = mmap(NULL, length, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
	if (addr == (void*) -1) {
		exit_err("file shared mmap");
	}
	return addr;
}

void* file_private_mapper(int fd, int length) {
	void* addr = mmap(NULL, length, PROT_READ | PROT_WRITE, MAP_PRIVATE, fd, 0);
	if (addr == (void*) -1) {
		exit_err("file private mmap");
	}
	return addr;
}
