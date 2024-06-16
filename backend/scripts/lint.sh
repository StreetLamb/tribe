#!/usr/bin/env bash

set -e
set -x

mypy app --verbose --no-incremental
ruff app
ruff format app --check
