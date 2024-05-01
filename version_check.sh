#!/bin/bash
# Exits with error if the provided argument version does not match the project file version.
set -e

VERSION=$(poetry version --short)
if [[ ${1} != ${VERSION} ]];
then
  echo "ERROR: Argument '${1}' does not match '${VERSION}' in pyproject.toml."
  exit 1
fi
