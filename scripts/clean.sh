#!/usr/bin/env bash
set -euo pipefail

echo -e "removing '__pycache__' files ..."
find . -type d -name "__pycache__" -prune -exec rm -rf {} +

echo -e "removing '.pytest_cache' files ..."
find . -type d -name ".pytest_cache" -prune -exec rm -rf {} +

echo -e "removing '.ruff_cache' files ..."
find . -type d -name ".ruff_cache" -prune -exec rm -rf {} +

echo -e "removing '*.pyc' files ..."
find . -type f -name "*.pyc" -delete

echo -e "removing '.coverage' files ..."
find . -type f -name ".coverage" -delete

echo -e "removing '*:Zone.Identifier' files ..."
find . -type f -name '*:Zone.Identifier' -delete

echo done
