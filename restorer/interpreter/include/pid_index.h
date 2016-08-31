#ifndef PID_INDEX_H_INCLUDED__
#define PID_INDEX_H_INCLUDED__

#include <stdbool.h>

#include <unistd.h>
#include <sys/types.h>

#include "vec.h"

struct idx_pair 
{
	pid_t k;
	int i;
};

typedef vec_t(struct idx_pair) idx_vec;

#define TABLE_SIZE 827

struct pid_index
{
	idx_vec chains[TABLE_SIZE];
	bool is_init[TABLE_SIZE];
};

void index_init(struct pid_index* index);
bool index_put(struct pid_index* index, pid_t pid, int id);
int index_get(const struct pid_index* index, pid_t pid);
void index_deinit(struct pid_index* index);

#endif
