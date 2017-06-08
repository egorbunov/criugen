#pragma once

#include <iostream>
#include <string>

#include <cstdarg>

namespace log 
{
	void log_setup(std::string& log_file_name);

	void log_info(const char* fmt...);

	void log_error(const char* fmt...);

	void log_stderr(const char* fmt...);
}