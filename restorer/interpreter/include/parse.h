#pragma once

#include <vector>
#include <istream>
#include <memory>

#include "command/command.h"

/**
 * @param input stream with program
 * @param program vector there commands will be added
 * @return non-negative value if all is ok;
 *
 * WARNING: all commands are allocated on the heap
 */
int parse_program(std::istream &in, std::vector<std::shared_ptr<command>>& program);
