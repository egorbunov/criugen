#! /bin/bash

# build dependencies (run before make)

git clone https://github.com/HardySimpson/zlog.git
git checkout tags/latest-stable
sudo make clean install
