#include "parse.h"

#include <stdio.h>
#include <ctype.h>
#include <stdbool.h>
#include <string.h>

#include <fcntl.h>

#include "jsmn.h"

typedef void* (*cmd_parser_fun)(const char*, jsmntok_t*, int);

static bool read_check_char(FILE* f, char ch, char* c);
static bool read_one_cmd_str(FILE* f, char* str);
static bool jsoneq(const char *json, jsmntok_t *tok, const char *s);
static enum cmd_type parse_cmd_type(const char* str);
static int parse_open_flag(const char* str);

static void* parse_cmd_fork_root(const char* s, jsmntok_t* ts, int n)
{
	int i;
	struct cmd_fork_root* cmd;
	cmd = (struct cmd_fork_root*) malloc(sizeof(struct cmd_fork_root));
	if (!cmd)
		return NULL;
	for (i = 0; i < n; ++i) {
		if (jsoneq(s, &ts[i], "pid")) {
			cmd->pid = atoi(s + ts[i + 1].start);
			break;
		}
	}
	return (void*) cmd;
}

static void* parse_cmd_setsid(const char* s, jsmntok_t* ts, int n)
{
	int i;
	struct cmd_setsid* cmd;
	cmd = (struct cmd_setsid*) malloc(sizeof(struct cmd_setsid));
	if (!cmd)
		return NULL;
	for (i = 0; i < n; ++i) {
		if (jsoneq(s, &ts[i], "pid")){
			cmd->pid = atoi(s + ts[i + 1].start);
			break;
		}
	}
	return (void*) cmd;
}

static void* parse_cmd_fork_child(const char* s, jsmntok_t* ts, int n)
{
	int i;
	struct cmd_fork_child* cmd;
	cmd = (struct cmd_fork_child*) malloc(sizeof(struct cmd_fork_child));
	if (!cmd)
		return NULL;
	for (i = 0; i < n; ++i) {
		if (jsoneq(s, &ts[i], "pid"))
			cmd->pid = atoi(s + ts[i + 1].start);
		if (jsoneq(s, &ts[i], "child_pid"))
			cmd->child_pid = atoi(s + ts[i + 1].start);
		i++;
	}
	return (void*) cmd;
}

static void* parse_cmd_create_thread(const char* s, jsmntok_t* ts, int n)
{
	int i;
	struct cmd_create_thread* cmd;
	cmd = (struct cmd_create_thread*) malloc(sizeof(struct cmd_create_thread));
	if (!cmd)
		return NULL;
	for (i = 0; i < n; ++i) {
		if (jsoneq(s, &ts[i], "pid"))
			cmd->pid = atoi(s + ts[i + 1].start);
		if (jsoneq(s, &ts[i], "tid"))
			cmd->tid = atoi(s + ts[i + 1].start);
		i++;
	}
	return (void*) cmd;
}

static void* parse_cmd_reg_open(const char* s, jsmntok_t* ts, int n)
{
	int i, j;
	struct cmd_reg_open* cmd;
	cmd = (struct cmd_reg_open*) malloc(sizeof(struct cmd_reg_open));
	if (!cmd)
		return NULL;
	for (i = 0; i < n; ++i) {
		if (jsoneq(s, &ts[i], "pid")){
			cmd->pid = atoi(s + ts[i + 1].start);
			i++;
		} else if (jsoneq(s, &ts[i], "fd")) {
			cmd->fd = atoi(s + ts[i + 1].start);
			i++;
		} else if (jsoneq(s, &ts[i], "offset")) {
			cmd->offset = atoi(s + ts[i + 1].start);
			i++;
		} else if (jsoneq(s, &ts[i], "mode")) {
			cmd->mode = atoi(s + ts[i + 1].start);
			i++;
		} else if (jsoneq(s, &ts[i], "flags")) {
			if (ts[i + 1].type != JSMN_ARRAY) {
				return NULL;
			}
			cmd->flags = 0;
			for (j = 0; j < ts[i+1].size; j++) {
				cmd->flags |= parse_open_flag(s + ts[i+j+2].start);
			}
			i += ts[i+1].size + 1;
		} else if (jsoneq(s, &ts[i], "path")) {
			strncpy(cmd->path, s + ts[i + 1].start, 
				ts[i + 1].end - ts[i + 1].start);
		}

	}
	return (void*) cmd;
}

static void* parse_cmd_close_fd(const char* s, jsmntok_t* ts, int n)
{
	int i;
	struct cmd_close_fd* cmd;
	cmd = (struct cmd_close_fd*) malloc(sizeof(struct cmd_close_fd));
	if (!cmd)
		return NULL;
	for (i = 0; i < n; ++i) {
		if (jsoneq(s, &ts[i], "pid"))
			cmd->pid = atoi(s + ts[i + 1].start);
		if (jsoneq(s, &ts[i], "fd"))
			cmd->fd = atoi(s + ts[i + 1].start);
		i++;
	}
	return (void*) cmd;
}

static void* parse_cmd_duplicate_fd(const char* s, jsmntok_t* ts, int n)
{
	int i;
	struct cmd_duplicate_fd* cmd;
	cmd = (struct cmd_duplicate_fd*) malloc(sizeof(struct cmd_duplicate_fd));
	if (!cmd)
		return NULL;
	for (i = 0; i < n; ++i) {
		if (jsoneq(s, &ts[i], "pid"))
			cmd->pid = atoi(s + ts[i + 1].start);
		if (jsoneq(s, &ts[i], "new_fd"))
			cmd->new_fd = atoi(s + ts[i + 1].start);
		if (jsoneq(s, &ts[i], "old_fd"))
			cmd->old_fd = atoi(s + ts[i + 1].start);
		i++;
	}
	return (void*) cmd;
}

static cmd_parser_fun cmd_parser_map[COMMAND_NUM] = {
	[CMD_FORK_ROOT] = parse_cmd_fork_root,
	[CMD_SETSID] = parse_cmd_setsid,
	[CMD_FORK_CHILD] = parse_cmd_fork_child,
	[CMD_REG_OPEN] = parse_cmd_reg_open,
	[CMD_CLOSE_FD] = parse_cmd_close_fd,
	[CMD_DUPLICATE_FD] = parse_cmd_duplicate_fd,
	[CMD_CREATE_THREAD] = parse_cmd_create_thread
};

int parse_program(const char* ppath, struct program* out_p)
{
	const size_t max_cmd_json_len = 1000;
	const size_t max_tokens_per_cmd = 150;
	jsmntok_t ts[max_tokens_per_cmd];
	char cmd_str[max_cmd_json_len];
	jsmn_parser parser;
	char c;
	int i;
	int tok_num;
	enum cmd_type ct;
	struct command cmd;
	FILE* f;

	f = fopen(ppath, "r");
	if (!f)
		goto err;

	if (!read_check_char(f, '[', &c))
		goto err;
	do {
		if (!read_one_cmd_str(f, cmd_str))
			break;
		jsmn_init(&parser);
		tok_num = jsmn_parse(&parser, cmd_str, strlen(cmd_str), ts, max_tokens_per_cmd);
		// json must be object
		if (tok_num < 1 || ts[0].type != JSMN_OBJECT) {
			return -1;
		}
		// finding command type first
		ct = CMD_UNKNOWN;
		for (i = 1; i < tok_num; i++)
			if (jsoneq(cmd_str, &ts[i], "#command")) {
				ct = parse_cmd_type(cmd_str + ts[i + 1].start);
			}
		if (ct == CMD_UNKNOWN) {
			return -1;
		}
		// parsing command
		cmd.type = ct;
		cmd.c = cmd_parser_map[ct](cmd_str, ts + 1, tok_num);
		if (cmd.c == NULL || prog_add_cmd(out_p, cmd) < 0) {
			return -1;
		}
	} while (read_check_char(f, ',', &c));
	if (c != ']')
		goto err;

	goto suc;
err:
	fclose(f);
	return -1;
suc:
	fclose(f);
	return 0;
} 

static enum cmd_type parse_cmd_type(const char* str)
{
	if (strncmp(str, CMD_TAG_SETSID, strlen(CMD_TAG_SETSID)) == 0)
		return CMD_SETSID;
	if (strncmp(str, CMD_TAG_REG_OPEN, strlen(CMD_TAG_REG_OPEN)) == 0)
		return CMD_REG_OPEN;
	if (strncmp(str, CMD_TAG_FORK_ROOT, strlen(CMD_TAG_FORK_ROOT)) == 0)
		return CMD_FORK_ROOT;
	if (strncmp(str, CMD_TAG_FORK_CHILD, strlen(CMD_TAG_FORK_CHILD)) == 0)
		return CMD_FORK_CHILD;
	if (strncmp(str, CMD_TAG_DUP_FD, strlen(CMD_TAG_DUP_FD)) == 0)
		return CMD_DUPLICATE_FD;
	if (strncmp(str, CMD_TAG_CLOSE_FD, strlen(CMD_TAG_CLOSE_FD)) == 0)
		return CMD_CLOSE_FD;
	return CMD_UNKNOWN;
}

static int parse_open_flag(const char* str)
{
	if (strncmp(str, "O_RDWR", strlen("O_RDWR")))
		return O_RDWR;
	if (strncmp(str, "O_LARGEFILE", strlen("O_LARGEFILE")))
		return 0; // TODO ?
	if (strncmp(str, "O_CREAT", strlen("O_CREAT")))
		return O_CREAT;
	if (strncmp(str, "O_EXCL", strlen("O_EXCL")))
		return O_EXCL;
	if (strncmp(str, "O_APPEND", strlen("O_APPEND")))
		return O_APPEND;
	if (strncmp(str, "O_WRONLY", strlen("O_WRONLY")))
		return O_WRONLY;
	if (strncmp(str, "O_RDONLY", strlen("O_RDONLY")))
		return O_RDONLY;
	if (strncmp(str, "O_TRUNC", strlen("O_TRUNC")))
		return O_TRUNC;
	printf("flag not parsed: %.*s", 10, str);
	return 0;
}

static bool jsoneq(const char *json, jsmntok_t *tok, const char *s) {
	if (tok->type == JSMN_STRING && (int) strlen(s) == tok->end - tok->start &&
			strncmp(json + tok->start, s, tok->end - tok->start) == 0) {
		return true;
	}
	return false;
}

static bool read_one_cmd_str(FILE* f, char* str)
{
	int balance;
	char ch;
	int i;

	if (!read_check_char(f, '{', &ch)) 
		return false;
	balance = 1;
	i = 0;
	str[i++] = '{';
	while (balance != 0) {
		ch = fgetc(f);
		if (ch == '{')
			balance += 1;
		else if (ch == '}')
			balance -= 1;
		else if (ch == EOF)
			return false;
		if (!isspace(ch))
			str[i++] = ch;
	}
	str[i] = '\0';
	return true;
}

/**
 * Reads characters to `c` from file and stops on first non-space one.
 * If that character is equal to given `ch` true is returned, else false
 */
static bool read_check_char(FILE* f, char ch, char* c)
{
	*c = ' ';
	while (isspace(*c)) {
		*c = fgetc(f);
	}
	return *c == ch;
}

