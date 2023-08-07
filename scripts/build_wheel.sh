#!/bin/bash

set -eo pipefail

GLT_ROOT_DIR=$(dirname $(dirname "$(realpath "$0")"))
CORES=$(cat < /proc/cpuinfo | grep -c "processor")

cd $GLT_ROOT_DIR

set -x

bash install_dependencies.sh
pip install ninja
pip install parameterized
cmake .
make -j$CORES
python setup.py bdist_wheel
pip install dist/* --force-reinstall
