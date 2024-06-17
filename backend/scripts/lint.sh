#!/usr/bin/env bash

set -e
set -x

# Function to check memory usage
check_memory_usage() {
  echo "Memory usage at $1:"
  free -m
}

# Run mypy on app/core and check memory usage
check_memory_usage "before"
mypy app/core/graph/skills
check_memory_usage "after"

ruff app
ruff format app --check