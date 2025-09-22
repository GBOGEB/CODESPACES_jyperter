#!/usr/bin/env bash
# Generate a diff patch and zip bundle of the repository.
set -euo pipefail

git diff --binary > patch.diff
zip -q patch.zip patch.diff

