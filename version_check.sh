#!/usr/bin/env bash
set -e # Exit on error
# Checks branch version is updated from main

VERSION_FILE="pyproject.toml"
CURRENT_BRANCH=$( git branch --show-current )

if [[ ${CURRENT_BRANCH} == "main" ]]
then
  echo "On main branch, skipping version check."
else
  echo "Checking version in '${VERSION_FILE}' is updated from main branch..."
  # True if version has been changed from main branch
  VERSION_UPDATED=$( git diff origin/main -- ${VERSION_FILE} | egrep '^\+version' )
  if [[ -z ${VERSION_UPDATED} ]]
  then
    echo "ERROR: Version has not been updated from main branch in '${VERSION_FILE}'."
    echo "Version update is required, see https://semver.org/"
    echo ""
    exit 1
  else
    echo "Version has been updated from main branch in '${VERSION_FILE}'."
    echo ""
  fi
fi
