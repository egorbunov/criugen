BIN_NAME := restorer
BIN_DIR := ./bin
CXX := gcc
CXX_FLAGS := -Wall -Werror -Wextra -pedantic-errors -I "./include" -I "./include/lib"
LD_FLAGS := -L/usr/local/lib -lzlog -lpthread -Wl,-rpath,/usr/local/lib
SRC_EXT := c
SRC_PATH := src

SOURCES = $(shell find $(SRC_PATH) -name '*.$(SRC_EXT)' -printf '%T@\t%p\n' | sort -k 1nr | cut -f2-)
OBJECTS = $(SOURCES:$(SRC_PATH)/%.$(SRC_EXT)=$(BIN_DIR)/%.o)
ZLOG_CONF = zlog.conf

.PHONY: all
all: $(BIN_DIR)/$(BIN_NAME) $(BIN_DIR)/$(ZLOG_CONF)

.PHONY: clean
clean:
	rm -rf $(BIN_DIR)/$(BIN_NAME) $(OBJECTS)
	rm -f $(BIN_DIR)/$(ZLOG_CONF)

$(BIN_DIR)/$(BIN_NAME): $(OBJECTS) 
	@mkdir -p $(BIN_DIR)
	$(CXX) $(OBJECTS) $(LD_FLAGS) -o $@

$(BIN_DIR)/%.o: $(SRC_PATH)/%.$(SRC_EXT)
	@mkdir -p $(shell dirname $@)
	$(CXX) $(CXX_FLAGS) -c $< -o $@

$(BIN_DIR)/$(ZLOG_CONF): ./conf/$(ZLOG_CONF)
	cp $< $@
