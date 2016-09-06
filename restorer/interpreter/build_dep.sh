#! /bin/bash

# build dependencies (run before make)

DEST_DIR=bin/zlog
rm -rf $DEST_DIR > /dev/null && \
mkdir -p $DEST_DIR && \
git clone https://github.com/egorbunov/zlog.git $DEST_DIR && \
( cd $DEST_DIR && git checkout zlog-simple ) && \
( cd $DEST_DIR && make clean all) && \
( cd $DEST_DIR && sudo make install ) && \
rm -rf $DEST_DIR
