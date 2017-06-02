CC = gcc
LD = gcc
CC_FLAGS = -Wall -Werror
LDFLAGS = -pthread

BIN_DIR = bin
SRC_DIR = .

SOURCES = $(wildcard $(SRC_DIR)/*.c)
OBJECTS = $(patsubst $(SRC_DIR)/%.c, $(BIN_DIR)/%.o, $(SOURCES))

TARGET = complex_groups


DEBUG     ?= 0
ifeq ($(DEBUG), 1)
	CC_FLAGS += -O0 -g -pg -DDEBUG
else
	CC_FLAGS += -O3
endif

LOG_IMPORTANT ?= 0
ifeq ($(LOG_IMPORTANT), 1)
	CC_FLAGS += -DLOG_IMPORTANT
endif

all: $(TARGET)

$(BIN_DIR):
	mkdir $(BIN_DIR)

$(BIN_DIR)/%.o: $(SRC_DIR)/%.c $(BIN_DIR)
	$(CC) $(CC_FLAGS) -c $< -o $@

$(TARGET): $(OBJECTS)
	$(LD) $(LDFLAGS) $^ -o $(BIN_DIR)/$@

.PHONY: clean all

all: $(TARGET)

clean: 
	rm -rf $(BIN_DIR)/*
