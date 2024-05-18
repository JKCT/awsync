#!/usr/bin/env bash
set -e # Exit on error
# Builds and publishes documentation to GitHub pages

# Get example code from main file, turn newlines into \n for perl parsing.
EXAMPLE_CODE=$( awk '{printf "%s\\n", $0}' awsync/__main__.py )
# Copy example code into README python markdown block.
perl -i -p0e 's/```python\n.*?\n```/```python\n'"${EXAMPLE_CODE}"'```/s' README.md

# Copy README into documentation index.
cp README.md docs/index.md
# Deploy documentation to GitHub Pages.
mkdocs gh-deploy --force

