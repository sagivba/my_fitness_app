#!/usr/bin/env bash
set -euo pipefail

python -m ruff check src tests
python -m ruff format --check src tests
