#!/bin/bash
GLFW_VERSION=3.0.3
GLFW_PATH=glfw-$GLFW_VERSION

set -e

echo "To configure GLFW build parameters, enter $GLFW_PATH and run 'ccmake .'"
pushd $GLFW_PATH
rm -rf build
mkdir build
pushd build
cmake ..
ccmake .
make
cp src/*.{dylib,so,dll} ../../glfw
popd
popd
