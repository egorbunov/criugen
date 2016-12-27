cmake_minimum_required(VERSION 3.0)
project(restorer)

set(ROOT "${CMAKE_CURRENT_SOURCE_DIR}")

# flags
set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -Wall -Werror -Wextra -std=c++14 -pedantic-errors")
set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -Wall -Werror -Wextra -std=c++14 -pedantic-errors")

# additional libraries
add_subdirectory(${ROOT}/lib/googletest)
add_subdirectory(${ROOT}/lib/json11)

include_directories(${ROOT}/include)
include_directories(${ROOT}/lib/googletest/include)
include_directories(${ROOT}/lib/json11)

# restorer sources
set(RESTORER_INCLUDE
	${ROOT}/include/command/cmd_close_fd.h
	${ROOT}/include/command/cmd_create_thread.h
	${ROOT}/include/command/cmd_duplicate_fd.h
	${ROOT}/include/command/cmd_fini.h
	${ROOT}/include/command/cmd_fork_child.h
	${ROOT}/include/command/cmd_reg_open.h
	${ROOT}/include/command/cmd_setsid.h
	${ROOT}/include/command/commands.h
	${ROOT}/include/command/commands.h
	${ROOT}/include/pid_utils.h
	${ROOT}/include/fd_utils.h
	${ROOT}/include/io_utils.h
	${ROOT}/include/ipc.h
	${ROOT}/include/log.h
	${ROOT}/include/parse.h
	${ROOT}/include/parse_util.h
	${ROOT}/include/restorer.h
	${ROOT}/include/restorer_node.h)

set(RESTORER_SOURCES
	${RESTORER_INCLUDE}
	${ROOT}/src/command/cmd_close_fd.cpp
	${ROOT}/src/command/cmd_create_thread.cpp
	${ROOT}/src/command/cmd_duplicate_fd.cpp
	${ROOT}/src/command/cmd_fini.cpp
	${ROOT}/src/command/cmd_fork_child.cpp
	${ROOT}/src/command/cmd_reg_open.cpp
	${ROOT}/src/command/cmd_setsid.cpp
	${ROOT}/src/command/commands.cpp
	${ROOT}/src/pid_utils.cpp
	${ROOT}/src/fd_utils.cpp
	${ROOT}/src/io_utils.cpp
	${ROOT}/src/ipc.cpp
	${ROOT}/src/log.cpp
	${ROOT}/src/parse.cpp
	${ROOT}/src/parse_util.cpp
	${ROOT}/src/restorer.cpp
	${ROOT}/src/restorer_node.cpp)

# restorer executable
add_executable(restorer ${ROOT}/src/main.cpp ${RESTORER_SOURCES})
target_link_libraries(restorer json11)

# unit tests
set(TEST_SOURCES
	${ROOT}/test/parse_test.cpp)
add_executable(unit_tester ${RESTORER_SOURCES} ${TEST_SOURCES})
target_link_libraries(unit_tester gtest_main json11)

include(CTest)
add_test (UnitTests unit_tester)
