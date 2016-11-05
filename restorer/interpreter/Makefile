BIN_NAME := restorer
BIN_DIR := ./bin
CXX := g++
CXXFLAGS += -Wall -Werror -Wextra -std=c++11 -pedantic-errors -pthread
LDFLAGS += -L/usr/local/lib -lpthread -Wl,-rpath,/usr/local/lib
SRC_DIR := src
TEST_DIR := test
TEST_BIN_DIR = $(BIN_DIR)/test
TESTER = $(TEST_BIN_DIR)/tester

RESTORER_SOURCES = $(shell find $(SRC_DIR) -name '*.cpp' -a -not -name 'main.cpp' -printf '%T@\t%p\n'\ | sort -k 1nr | cut -f2-)
RESTORER_OBJECTS = $(RESTORER_SOURCES:$(SRC_DIR)/%.cpp=$(BIN_DIR)/%.o)

.PHONY: all
all: $(BIN_DIR)/$(BIN_NAME) $(TESTER)

# ======= Json Parser ========
JSON_LIB_DIR = lib/json11

RESTORER_OBJECTS += $(BIN_DIR)/json11.o

$(BIN_DIR)/json11.o: $(JSON_LIB_DIR)/json11.cpp \
	               $(JSON_LIB_DIR)/json11.hpp
	$(CXX) $(CPPFLAGS) -I$(JSON_LIB_DIR)/src $(CXXFLAGS) -c \
			$(JSON_LIB_DIR)/json11.cpp -o $@
# ======= End Json Parser ====

# ======= Google Test ========
GTEST_DIR = lib/googletest
CPPFLAGS += -isystem $(GTEST_DIR)/include
CXXFLAGS += -g -Wall -Wextra -pthread
GTEST_LIB_DIR = $(BIN_DIR)
GTEST_HEADERS = $(GTEST_DIR)/include/gtest/*.h \
                $(GTEST_DIR)/include/gtest/internal/*.h

GTEST_SRCS_ = $(GTEST_DIR)/src/*.cc $(GTEST_DIR)/src/*.h $(GTEST_HEADERS)

$(BIN_DIR)/gtest-all.o: $(GTEST_SRCS_)
	$(CXX) $(CPPFLAGS) -I$(GTEST_DIR) $(CXXFLAGS) -c \
            $(GTEST_DIR)/src/gtest-all.cc -o $@

$(BIN_DIR)/gtest_main.o: $(GTEST_SRCS_)
	$(CXX) $(CPPFLAGS) -I$(GTEST_DIR) $(CXXFLAGS) -c \
            $(GTEST_DIR)/src/gtest_main.cc -o $@

$(BIN_DIR)/gtest.a: $(BIN_DIR)/gtest-all.o
	$(AR) $(ARFLAGS) $@ $^

$(BIN_DIR)/gtest_main.a: $(BIN_DIR)/gtest-all.o $(BIN_DIR)/gtest_main.o
	$(AR) $(ARFLAGS) $@ $^

.PHONY: gtest
gtest: $(BIN_DIR) $(BIN_DIR)/gtest.a $(BIN_DIR)/gtest_main.a
# ========= End Google Test =========

# ========= Tester ==========
TEST_SOURCES = $(wildcard $(TEST_DIR)/*.cpp)
TEST_OBJECTS = $(patsubst $(TEST_DIR)/%.cpp, $(TEST_BIN_DIR)/%.o, $(TEST_SOURCES))
GTEST_LIBS = $(BIN_DIR)/gtest_main.a $(BIN_DIR)/gtest.a
GTEST_INCLUDE = $(GTEST_DIR)/include

$(TEST_BIN_DIR): 
	@mkdir -p $(TEST_BIN_DIR)

$(TEST_BIN_DIR)/%.o: $(TEST_DIR)/%.cpp
	$(CXX) -I./include -I$(GTEST_INCLUDE) $(CXXFLAGS) -c $< -o $@

$(TESTER): $(TEST_BIN_DIR) $(TEST_OBJECTS) $(RESTORER_OBJECTS) $(GTEST_LIBS)
	$(CXX) -L$(GTEST_LIB_DIR) $(GTEST_LIBS) $(LDFLAGS) \
		$(TEST_OBJECTS) $(RESTORER_OBJECTS) -o $@

.PHONY: tester
tester: $(TESTER)
# ========= End Tester =========

# ========= Restorer ==========
$(BIN_DIR):
	@mkdir -p $(BIN_DIR)

$(BIN_DIR)/$(BIN_NAME): $(BIN_DIR) $(RESTORER_OBJECTS) $(BIN_DIR)/main.o
	$(CXX) $(RESTORER_OBJECTS) $(BIN_DIR)/main.o $(LDFLAGS) -o $@

$(BIN_DIR)/%.o: $(SRC_DIR)/%.cpp
	@mkdir -p $(shell dirname $@)
	$(CXX) -I./include -I$(JSON_LIB_DIR) $(CXXFLAGS) -c $< -o $@

$(BIN_DIR)/main.o: $(SRC_DIR)/main.cpp
	$(CXX) -I./include $(CXXFLAGS) -c $< -o $@
# ========= End Restorer =========

.PHONY: clean
clean:
	rm -rf $(BIN_DIR)/*

.PHONY: test
test: $(TESTER)
	$(TESTER)

