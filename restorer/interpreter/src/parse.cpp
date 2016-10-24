#include "parse.h"

#include <map>
#include <fstream>
#include <vector>

#include <cstdio>
#include <cctype>
#include <cstdbool>
#include <cstring>

#include <fcntl.h>

#include "jsmn.h"

/*
 * For every possible command parser function must be specified
 * and added to `cmd_parser_map` map.
 *
 * Command name are equivalent to tags, which are parsed by `get_cmd_by_str`
 * function from command module (file).
 *
 * So command tag + command id and present parser functions must be agreed
 */

static command parse_cmd_setsid(const char* s, jsmntok_t* ts, int n);
static command parse_cmd_fork_child(const char* s, jsmntok_t* ts, int n);
static command parse_cmd_create_thread(const char* s, jsmntok_t* ts, int n);
static command parse_cmd_reg_open(const char* s, jsmntok_t* ts, int n);
static command parse_cmd_close_fd(const char* s, jsmntok_t* ts, int n);
static command parse_cmd_duplicate_fd(const char* s, jsmntok_t* ts, int n);
static command parse_cmd_fini(const char* s, jsmntok_t* ts, int n);

typedef command (*cmd_parser_fun)(const char*, jsmntok_t*, int tok_num);

static std::map<enum cmd_type, cmd_parser_fun> cmd_parser_map = {
	{ CMD_FORK_CHILD,    parse_cmd_fork_child },
	{ CMD_SETSID,        parse_cmd_setsid },
	{ CMD_REG_OPEN,      parse_cmd_reg_open },
	{ CMD_CLOSE_FD,      parse_cmd_close_fd },
	{ CMD_DUPLICATE_FD,  parse_cmd_duplicate_fd },
	{ CMD_CREATE_THREAD, parse_cmd_create_thread },
	{ CMD_FINI,          parse_cmd_fini }
};


static bool read_check_char(std::ifstream& in, char ch, char* c);
static bool read_one_cmd_str(std::ifstream& in, char* str);
static bool jsoneq(const char *json, jsmntok_t *tok, const char *s);
static cmd_type parse_cmd_type(const char* str);
static int parse_open_flag(const char* str);


int parse_program(const char* ppath, std::vector<command>& program)
{
	auto err_cleanup = [&program](int ret) {
		for (const auto& cmd : program) {
			free(cmd.c);
		}
		program.clear();
		return ret;
	};

	const size_t max_cmd_json_len = 1000;
	char cmd_str[max_cmd_json_len];
	char c;

	std::ifstream in(ppath, std::fstream::in);
	if (!in) {
		return -1;
	}
	if (!read_check_char(in, '[', &c)) {
		return -1;
	}
	do {
		if (!read_one_cmd_str(in, cmd_str)) {
			break;
		}
		command cmd;
		if (parse_one_command(cmd_str, &cmd) < 0) {
			return err_cleanup(-1);
		}
		program.push_back(cmd);
	} while (read_check_char(in, ',', &c));

	if (c != ']') {
		return err_cleanup(-1);
	}
	return 0;
}

int parse_one_command(const char* cmd_str, struct command* cmd)
{
	const size_t max_tokens_per_cmd = 150;
	jsmntok_t ts[max_tokens_per_cmd];

	jsmn_parser parser;
	jsmn_init(&parser);
	int tok_num = jsmn_parse(&parser, cmd_str, strlen(cmd_str), ts, max_tokens_per_cmd);
	// command json must be object
	if (tok_num < 1 || ts[0].type != JSMN_OBJECT) {
		return -1;
	}
	// finding command type first
	cmd_type ct = CMD_UNKNOWN;
	for (int i = 1; i < tok_num; i++) {
		if (jsoneq(cmd_str, &ts[i], "#command"))
			ct = parse_cmd_type(cmd_str + ts[i + 1].start);
	}
	if (ct == CMD_UNKNOWN) {
		return -1;
	}
	// parsing command
	*cmd = cmd_parser_map[ct](cmd_str, ts + 1, tok_num);
	if (cmd.c == NULL) {
		return -1;
	}
	return 0;
}

static enum cmd_type parse_cmd_type(const char* str)
{
	return get_cmd_by_str(str);
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
	if (tok->type == JSMN_STRING && (int) strlen(s) == tok->end - tok->start 
		&& strncmp(json + tok->start, s, tok->end - tok->start) == 0) {
		return true;
	}
	return false;
}

static bool read_one_cmd_str(std::ifstream& in, char* str)
{
	char ch;
	if (!read_check_char(in, '{', &ch)) 
		return false;
	int balance = 1;
	int i = 0;
	str[i++] = '{';
	while (balance != 0) {
		ch = in.get();
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
 static bool read_check_char(std::ifstream& in, char ch, char* c)
 {
 	*c = ' ';
 	while (isspace(*c)) {
 		*c = in.get();
 	}
 	return *c == ch;
 }

static command parse_cmd_setsid(const char* s, jsmntok_t* ts, int n)
{
	command cmd = { CMD_UNKNOWN, -1, NULL };
	cmd_setsid* c = new cmd_setsid();
	if (!c) {
		return cmd;
	}
	for (int i = 0; i < n; ++i) {
		if (jsoneq(s, &ts[i], "pid")){
			c->pid = atoi(s + ts[i + 1].start);
			break;
		}
	}
	cmd.type = CMD_SETSID;
	cmd.owner = c->pid;
	cmd.c = c;
	return cmd;
}

static command parse_cmd_fork_child(const char* s, jsmntok_t* ts, int n)
{
	int i;
	struct command cmd = { CMD_UNKNOWN, -1, NULL };
	struct cmd_fork_child* c = new cmd_fork_child();
	if (!c) {
		return cmd;
	}

	for (i = 0; i < n; ++i) {
		if (jsoneq(s, &ts[i], "pid"))
			c->pid = atoi(s + ts[i + 1].start);
		if (jsoneq(s, &ts[i], "child_pid"))
			c->child_pid = atoi(s + ts[i + 1].start);
		if (jsoneq(s, &ts[i], "max_fd"))
			c->max_fd = atoi(s + ts[i + 1].start);
		i++;
	}
	cmd.type = CMD_FORK_CHILD;
	cmd.owner = c->pid;
	cmd.c = c;
	return cmd;
}

static command parse_cmd_create_thread(const char* s, jsmntok_t* ts, int n)
{
	struct command cmd = { CMD_UNKNOWN, -1, NULL };
	struct cmd_create_thread* c = new cmd_create_thread();
	c = (struct cmd_create_thread*) malloc(sizeof(struct cmd_create_thread));
	if (!c) {
		return cmd;
	}

	for (int i = 0; i < n; ++i) {
		if (jsoneq(s, &ts[i], "pid"))
			c->pid = atoi(s + ts[i + 1].start);
		if (jsoneq(s, &ts[i], "tid"))
			c->tid = atoi(s + ts[i + 1].start);
		i++;
	}
	cmd.type = CMD_CREATE_THREAD;
	cmd.owner = c->pid;
	cmd.c = c;
	return cmd;
}

static command parse_cmd_reg_open(const char* s, jsmntok_t* ts, int n)
{
	command cmd = { CMD_UNKNOWN, -1, NULL };
	cmd_reg_open* c = new cmd_reg_open();
	if (!c) {
		return cmd;
	}

	for (int i = 0; i < n; ++i) {
		if (jsoneq(s, &ts[i], "pid")){
			c->pid = atoi(s + ts[++i].start);
		} else if (jsoneq(s, &ts[i], "fd")) {
			c->fd = atoi(s + ts[++i].start);
		} else if (jsoneq(s, &ts[i], "offset")) {
			c->offset = atoi(s + ts[++i].start);
		} else if (jsoneq(s, &ts[i], "mode")) {
			c->mode = atoi(s + ts[++i].start);
		} else if (jsoneq(s, &ts[i], "flags")) {
			if (ts[i + 1].type != JSMN_ARRAY) {
				return cmd;
			}
			c->flags = 0;
			for (int j = 0; j < ts[i + 1].size; j++) {
				c->flags |= parse_open_flag(s + ts[i + j + 2].start);
			}
			i += ts[i + 1].size + 1;
		} else if (jsoneq(s, &ts[i], "path")) {
			strncpy(c->path, s + ts[i + 1].start, 
				ts[i + 1].end - ts[i + 1].start);
		}

	}
	cmd.type = CMD_REG_OPEN;
	cmd.owner = c->pid;
	cmd.c = c;
	return cmd;
}

static command parse_cmd_close_fd(const char* s, jsmntok_t* ts, int n)
{
	command cmd = { CMD_UNKNOWN, -1, NULL };
	cmd_close_fd* c = new cmd_close_fd();
	if (!c)
		return cmd;

	for (int i = 0; i < n; ++i) {
		if (jsoneq(s, &ts[i], "pid"))
			c->pid = atoi(s + ts[i + 1].start);
		if (jsoneq(s, &ts[i], "fd"))
			c->fd = atoi(s + ts[i + 1].start);
		i++;
	}
	cmd.type = CMD_CLOSE_FD;
	cmd.owner = c->pid;
	cmd.c = c;
	return cmd;
}

static command parse_cmd_duplicate_fd(const char* s, jsmntok_t* ts, int n)
{
	command cmd = { CMD_UNKNOWN, -1, NULL };
	cmd_duplicate_fd* c = new cmd_duplicate_fd();

	if (!c) {
		return cmd;
	}
	for (int i = 0; i < n; ++i) {
		if (jsoneq(s, &ts[i], "pid"))
			c->pid = atoi(s + ts[i + 1].start);
		if (jsoneq(s, &ts[i], "new_fd"))
			c->new_fd = atoi(s + ts[i + 1].start);
		if (jsoneq(s, &ts[i], "old_fd"))
			c->old_fd = atoi(s + ts[i + 1].start);
		i++;
	}
	cmd.type = CMD_DUPLICATE_FD;
	cmd.owner = c->pid;
	cmd.c = c;
	return cmd;
}

static command parse_cmd_fini(const char* s, jsmntok_t* ts, int n)
{
	command cmd = { CMD_UNKNOWN, -1, NULL };
	cmd_fini* c = new cmd_fini();

	if (!c) {
		return cmd;
	}
	for (int i = 0; i < n; ++i) {
		if (jsoneq(s, &ts[i], "pid"))
			c->pid = atoi(s + ts[i + 1].start);
		i++;
	}

	cmd.type = CMD_FINI;
	cmd.owner = c->pid;
	cmd.c = c;
	return cmd;
}
