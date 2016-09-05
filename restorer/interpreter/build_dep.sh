#! /bin/bash

# build dependencies (run before make)

DEST_DIR=bin/zlog
rm -rf $DEST_DIR > /dev/null && \
mkdir -p $DEST_DIR && \
git clone https://github.com/HardySimpson/zlog.git $DEST_DIR && \
# ( cd $DEST_DIR && git checkout tags/latest-stable ) && \
( cd $DEST_DIR && sudo make clean install ) && \
rm -rf $DEST_DIR
