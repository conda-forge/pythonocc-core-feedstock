#!/bin/bash

mkdir build
cd build

cmake ${CMAKE_ARGS} -G Ninja \
    -D CMAKE_INSTALL_PREFIX:FILEPATH=$PREFIX \
    -D PYTHONOCC_BUILD_TYPE:STRING=Release \
    -D Python3_FIND_STRATEGY:STRING=LOCATION \
    -D Python3_FIND_FRAMEWORK:STRING=NEVER \
    -D SWIG_HIDE_WARNINGS:BOOL=ON \
    -D PYTHONOCC_INSTALL_DIRECTORY=$SP_DIR/OCC \
    -D PYTHONOCC_MESHDS_NUMPY=ON \
    ..

ninja install
