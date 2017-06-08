#include "log.h"

#include <string>
#include <mutex>

#include <cerrno>
#include <cstring>

#include <sys/types.h>
#include <unistd.h>

namespace {
	std::string g_log_file;
	std::mutex g_log_lock;

	FILE* open_log_file()
	{
		FILE* p_file = fopen(g_log_file.c_str(), "a");
		if (p_file == nullptr) {
			perror("Can't open log file");
		}
		return p_file;
	}

	void log_lock()
	{
		while (!g_log_lock.try_lock()) {}
	}

	void log_unlock()
	{
		g_log_lock.unlock();
	}

	void log_tagged(FILE* out, const char* tag, const char* fmt, va_list args)
	{
		fprintf(out, "[%d] %s: ", getpid(), tag);
		vfprintf(out, fmt, args);
	}
}


void log::log_setup(std::string& log_file_name)
{
	g_log_file = log_file_name;
}

void log::log_info(const char* fmt...) 
{
	log_lock();
	auto out = open_log_file();
	if (out == nullptr) return;

    va_list args;
	va_start(args, fmt);
	log_tagged(out, "INFO", fmt, args);
	va_end(args);

	fprintf(out, "\n");
	fclose(out);
	log_unlock();
}

void log::log_error(const char* fmt...) 
{
	log_lock();
	auto out = open_log_file();
	if (out == nullptr) return;

    va_list args;
	va_start(args, fmt);
	log_tagged(out, "ERROR", fmt, args);
	va_end(args);

	fprintf(out, "\n");
	fclose(out);
	log_unlock();
}

void log::log_stderr(const char* fmt...) 
{
	log_lock();
	auto out = open_log_file();
	if (out == nullptr) return;

    va_list args;
	va_start(args, fmt);
	log_tagged(out, "ERROR", fmt, args);
	va_end(args);

	fprintf(out, " [%s]\n", strerror(errno));
	fclose(out);
	log_unlock();
}
