#!/usr/bin/env bash

set -e
set -x

# Function to check memory usage
check_memory_usage() {
  echo "Memory usage at $1:"
  free -m
}

check_memory_usage "start"

# Run mypy on app/core and check memory usage
check_memory_usage "before mypy app/core"
mypy app/core
check_memory_usage "after mypy app/core"

# Run mypy on app/api and check memory usage
check_memory_usage "before mypy app/api"
mypy app/api
check_memory_usage "after mypy app/api"

# Run ruff linter and check memory usage
check_memory_usage "before ruff"
ruff app
check_memory_usage "after ruff"

# Run ruff formatter and check memory usage
check_memory_usage "before ruff format"
ruff format app --check
check_memory_usage "after ruff format"

check_memory_usage "end"