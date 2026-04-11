#!/bin/bash
# POSIX-ish: avoid `pipefail` so `sh`/`dash` invocations do not fail before any command runs
set -eu
mkdir -p "${PREFIX}/share/pythonocc-core-source"
# Ensure we have a source tree (rattler sets SRC_DIR to the extracted work root)
if [ ! -f "${SRC_DIR}/CMakeLists.txt" ]; then
  echo "install_source.sh: expected ${SRC_DIR}/CMakeLists.txt" >&2
  exit 1
fi
cp -a "${SRC_DIR}"/. "${PREFIX}/share/pythonocc-core-source/"
