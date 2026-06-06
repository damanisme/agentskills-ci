#!/usr/bin/env bash
# Safe, scoped cleanup of a demo directory. No rm -rf, no broad paths.
set -euo pipefail

target="${1:-./demo-output}"

if [[ "$target" == "/" || "$target" == "$HOME" ]]; then
  echo "Refusing to clean an unsafe path: $target" >&2
  exit 1
fi

if [[ -d "$target" ]]; then
  find "$target" -mindepth 1 -maxdepth 1 -delete
  echo "Cleaned contents of $target"
else
  echo "Nothing to clean: $target does not exist"
fi
