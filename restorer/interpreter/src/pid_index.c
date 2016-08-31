#include "pid_index.h"

void index_init(struct pid_index* index)
{
	int i;
	for (i = 0; i < TABLE_SIZE; ++i) {
		index->is_init[i] = false;
	}
}

bool index_put(struct pid_index* index, pid_t pid, int id)
{
	struct idx_pair p;
	p.k = pid;
	p.i = id;
	if (index_get(index, pid) > 0) 
		return false;
	if (!index->is_init[pid % TABLE_SIZE])
		vec_init(&index->is_init[pid % TABLE_SIZE]);
	return vec_push(&(index->chains[pid % TABLE_SIZE]), p) > 0;
}

int index_get(const struct pid_index* index, pid_t pid)
{
	idx_vec chain;
	struct idx_pair p;
	int i;

	chain = index->chains[pid % TABLE_SIZE];
	vec_foreach(&chain, p, i)
		if (p.k == pid)
			return p.i;
	return -1;
}

void index_deinit(struct pid_index* index)
{
	int i;
	for (i = 0; i < TABLE_SIZE; ++i) {
		if (index->is_init[i])
			vec_deinit(&index->chains[i]);
	}
}
