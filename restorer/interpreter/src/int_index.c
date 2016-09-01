#include "int_index.h"

void index_init(struct int_index* index)
{
	int i;
	for (i = 0; i < TABLE_SIZE; ++i) {
		index->is_init[i] = false;
	}
}

bool index_put(struct int_index* index, int key, int val)
{
	struct idx_pair p;
	p.k = key;
	p.v = val;
	if (index_get(index, key) > 0) 
		return false;
	if (!index->is_init[p.k % TABLE_SIZE])
		vec_init(&index->chains[p.k % TABLE_SIZE]);
	return vec_push(&index->chains[p.k % TABLE_SIZE], p) > 0;
}

int index_get(const struct int_index* index, int key)
{
	idx_vec chain;
	struct idx_pair p;
	int i;

	chain = index->chains[key % TABLE_SIZE];
	vec_foreach(&chain, p, i)
		if (p.k == key)
			return p.v;
	return -1;
}

void index_deinit(struct int_index* index)
{
	int i;
	for (i = 0; i < TABLE_SIZE; ++i) {
		if (index->is_init[i])
			vec_deinit(&index->chains[i]);
	}
}
