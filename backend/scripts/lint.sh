#!/usr/bin/env bash

set -e
set -x

mypy app --verbose
ruff app
ruff format app --check
