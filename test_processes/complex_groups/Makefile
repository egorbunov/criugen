BIN_DIR = bin
SRC_DIR = .
INCLUDE_DIR = .
INCLUDE_CRPROC_LIB = $(realpath ../libcrproc/include)
CRPROC_BUILD_DIR = $(realpath ../libcrproc/build)

CC = gcc
LD = gcc
CC_FLAGS = -Wall -Werror -I$(INCLUDE_DIR) -I$(INCLUDE_CRPROC_LIB)
LDFLAGS = -pthread -L$(CRPROC_BUILD_DIR) -lcrproc -Wl,-rpath,$(CRPROC_BUILD_DIR)

SOURCES = $(wildcard $(SRC_DIR)/*.c)
OBJECTS = $(patsubst $(SRC_DIR)/%.c, $(BIN_DIR)/%.o, $(SOURCES))
CRPROC_LIB_NAME = libcrpoc.so
CRPROC = $(CRPROC_BUILD_DIR)/$(CRPROC_LIB_NAME)
CRPROC_DIR = $(realpath ../libcrproc)

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

all: $(CRPROC) $(TARGET)

$(CRPROC):
	cd $(CRPROC_DIR) && $(MAKE) LOG_IMPORTANT=$(LOG_IMPORTANT)


$(BIN_DIR):
	mkdir $(BIN_DIR)

$(BIN_DIR)/%.o: $(SRC_DIR)/%.c $(BIN_DIR)
	$(CC) $(CC_FLAGS) -c $< -o $@

$(TARGET): $(OBJECTS)
	$(LD) $^ -o $(BIN_DIR)/$@ $(LDFLAGS)

.PHONY: clean all

all: $(TARGET)

clean: 
	rm -rf $(BIN_DIR)/*
