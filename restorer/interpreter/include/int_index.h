#ifndef INT_INDEX_H_INCLUDED__
#define INT_INDEX_H_INCLUDED__

#include <stdbool.h>

#include <unistd.h>
#include <sys/types.h>

#include "vec.h"

struct idx_pair 
{
	int k;
	int v;
};

typedef vec_t(struct idx_pair) idx_vec;

#define TABLE_SIZE 827

struct int_index
{
	idx_vec chains[TABLE_SIZE];
	bool is_init[TABLE_SIZE];
};

void index_init(struct int_index* index);
bool index_put(struct int_index* index, int key, int val);
int index_get(const struct int_index* index, int key, int* val);
void index_deinit(struct int_index* index);

#endif
