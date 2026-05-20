#!/usr/bin/env bash
set -euo pipefail

python3 -m ruff check src tests
python3 -m ruff format --check src tests
