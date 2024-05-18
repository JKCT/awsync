#!/usr/bin/env bash
set -e # Exit on error
# Creates a new GitHub release on merge to main

TOKEN=$1 # Expect first argument is TOKEN with 'contents:write' permissions
VERSION=$(poetry version --short)

echo "Creating new GitHub release: '${VERSION}'..."
# Requires token with permissions: contents:write
# https://docs.github.com/en/rest/releases/releases?apiVersion=2022-11-28#create-a-release
curl -L \
  -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/JKCT/awsync/releases \
# Automatically generate release notes and set as latest version.
  -d '{"tag_name":"'${VERSION}'","name":"'${VERSION}'","generate_release_notes":true,"make_latest":true}'
