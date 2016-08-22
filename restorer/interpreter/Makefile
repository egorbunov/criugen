BIN_NAME := restorer
BIN_DIR := ./bin
CXX := g++
CXX_FLAGS := -std=c++11 -Wall -Werror -Wextra -pedantic-errors -I "./include" -I "./include/proto"
LD_FLAGS := -lprotobuf
SRC_EXT := cpp
SRC_PATH := src

SOURCES = $(shell find $(SRC_PATH) -name '*.$(SRC_EXT)' -printf '%T@\t%p\n' | sort -k 1nr | cut -f2-)
OBJECTS = $(SOURCES:$(SRC_PATH)/%.$(SRC_EXT)=$(BIN_DIR)/%.o)

.PHONY: all
all: $(BIN_DIR)/$(BIN_NAME)

.PHONY: clean
clean:
	rm -rf $(BIN_DIR)/$(BIN_NAME) $(OBJECTS)

$(BIN_DIR)/$(BIN_NAME): $(OBJECTS) 
	@mkdir -p $(BIN_DIR)
	$(CXX) $(OBJECTS) $(LD_FLAGS) -o $@

$(BIN_DIR)/%.o: $(SRC_PATH)/%.$(SRC_EXT)
	@mkdir -p $(shell dirname $@)
	$(CXX) $(CXX_FLAGS) -c $< -o $@
