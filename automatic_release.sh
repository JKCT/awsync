#!/bin/bash
# Creates a GitHub Release if version file has an unreleased version.
set -e

VERSION=$(poetry version --short)
RELEASES=$(gh release list --exclude-drafts --exclude-pre-releases)
# Check if version is in release list
echo ${RELEASES} | grep -w -q ${VERSION}
if [[ $? ]];
then
  gh release create --generate-notes --latest --title "${VERSION}"
else
  echo "Release already exists for version '${VERSION}'."
fi
