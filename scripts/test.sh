#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-quick}"
TARGET="${2:-local}"

PROJECT_NAME="${PROJECT_NAME:-python_template}"
DEV_COMPOSE_PROJECT="${DEV_COMPOSE_PROJECT:-${PROJECT_NAME}_dev}"
QA_COMPOSE_PROJECT="${QA_COMPOSE_PROJECT:-${PROJECT_NAME}_qa}"

export PYTHONPATH="${PYTHONPATH:-src}"

usage() {
  cat <<'EOF'
Usage:
  scripts/test.sh [quick|full] [local|docker-dev|docker-qa]

Examples:
  scripts/test.sh
  scripts/test.sh quick
  scripts/test.sh full
  scripts/test.sh quick local
  scripts/test.sh full docker-dev
  scripts/test.sh full docker-qa

Defaults:
  MODE=quick
  TARGET=local

Environment overrides:
  PROJECT_NAME=my_project
  DEV_COMPOSE_PROJECT=my_project_dev
  QA_COMPOSE_PROJECT=my_project_qa
EOF
}

verbose_flag() {
  case "$MODE" in
    quick)
      echo ""
      ;;
    full)
      echo "-v"
      ;;
    -h|--help|help)
      usage
      exit 0
      ;;
    *)
      echo "ERROR: Unknown test mode: $MODE" >&2
      usage
      exit 1
      ;;
  esac
}

run_local_tests() {
  local verbosity
  verbosity="$(verbose_flag)"

  if [[ -n "$verbosity" ]]; then
    python -m unittest discover -s tests -p "test_*.py" "$verbosity"
  else
    python -m unittest discover -s tests -p "test_*.py"
  fi
}

run_docker_tests() {
  local compose_project="$1"
  local compose_override="$2"
  local verbosity
  verbosity="$(verbose_flag)"

  if ! command -v docker >/dev/null 2>&1; then
    echo "ERROR: docker command was not found." >&2
    exit 1
  fi

  if [[ -n "$verbosity" ]]; then
    docker compose \
      -p "$compose_project" \
      -f docker-compose.yml \
      -f "$compose_override" \
      run --rm app \
      python -m unittest discover -s tests -p "test_*.py" "$verbosity"
  else
    docker compose \
      -p "$compose_project" \
      -f docker-compose.yml \
      -f "$compose_override" \
      run --rm app \
      python -m unittest discover -s tests -p "test_*.py"
  fi
}

case "$TARGET" in
  local)
    run_local_tests
    ;;
  docker-dev)
    run_docker_tests "$DEV_COMPOSE_PROJECT" "docker-compose.dev.yml"
    ;;
  docker-qa)
    run_docker_tests "$QA_COMPOSE_PROJECT" "docker-compose.qa.yml"
    ;;
  -h|--help|help)
    usage
    ;;
  *)
    echo "ERROR: Unknown test target: $TARGET" >&2
    usage
    exit 1
    ;;
esac
