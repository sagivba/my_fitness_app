#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  scripts/init_from_template.sh <new-project-name> [--package <package_name>] [--force]

Examples:
  scripts/init_from_template.sh chemistry-mock-site
  scripts/init_from_template.sh "Chemistry Mock Site" --package chemistry_web
  scripts/init_from_template.sh my-new-project --force

What it does:
  - Renames the Python package directory under src/
  - Rewrites package imports and references
  - Updates project metadata in README.md and pyproject.toml
  - Updates Docker/Compose project naming references where possible
  - Updates docs and workflow files
  - Keeps unittest as the test framework
  - Creates .template-initialized to prevent accidental repeated initialization

Run this once immediately after creating a new repository from the template.
EOF
}

PROJECT_NAME=""
PACKAGE_NAME=""
FORCE="false"
INIT_MARKER=".template-initialized"

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help|help)
      usage
      exit 0
      ;;
    --package)
      if [[ $# -lt 2 ]]; then
        echo "ERROR: --package requires a value." >&2
        exit 1
      fi
      PACKAGE_NAME="$2"
      shift 2
      ;;
    --force)
      FORCE="true"
      shift
      ;;
    -*)
      echo "ERROR: Unknown option: $1" >&2
      usage
      exit 1
      ;;
    *)
      if [[ -n "$PROJECT_NAME" ]]; then
        echo "ERROR: Project name already provided: $PROJECT_NAME" >&2
        usage
        exit 1
      fi
      PROJECT_NAME="$1"
      shift
      ;;
  esac
done

if [[ -z "$PROJECT_NAME" ]]; then
  echo "ERROR: Missing project name." >&2
  usage
  exit 1
fi

if [[ -f "$INIT_MARKER" && "$FORCE" != "true" ]]; then
  echo "ERROR: This repository was already initialized from the template." >&2
  echo "" >&2
  echo "Marker file found:" >&2
  echo "  $INIT_MARKER" >&2
  echo "" >&2
  echo "Initialization should normally be executed only once." >&2
  echo "If you are absolutely sure you want to re-run it, use:" >&2
  echo "  scripts/init_from_template.sh \"$PROJECT_NAME\" --force" >&2
  echo "" >&2
  echo "Current initialization marker:" >&2
  sed 's/^/  /' "$INIT_MARKER" >&2 || true
  exit 1
fi

if [[ ! -d ".git" ]]; then
  echo "WARNING: .git directory was not found."
  echo "This script is intended to run from the root of a Git repository."
  if [[ "$FORCE" != "true" ]]; then
    echo "Use --force to continue anyway."
    exit 1
  fi
fi

if [[ ! -d "src" ]]; then
  echo "ERROR: src/ directory was not found. Run this script from the repository root." >&2
  exit 1
fi

derive_package_name() {
  local raw="$1"
  echo "$raw" \
    | tr '[:upper:]' '[:lower:]' \
    | sed -E 's/[^a-z0-9]+/_/g; s/^_+//; s/_+$//'
}

if [[ -z "$PACKAGE_NAME" ]]; then
  PACKAGE_NAME="$(derive_package_name "$PROJECT_NAME")"
fi

if [[ ! "$PACKAGE_NAME" =~ ^[a-z_][a-z0-9_]*$ ]]; then
  echo "ERROR: Invalid Python package name: $PACKAGE_NAME" >&2
  echo "Use --package with a valid Python identifier, for example: --package chemistry_web" >&2
  exit 1
fi

mapfile -t SRC_PACKAGES < <(find src -mindepth 1 -maxdepth 1 -type d -printf '%f\n' | sort)

if [[ ${#SRC_PACKAGES[@]} -eq 0 ]]; then
  echo "ERROR: No package directory found under src/." >&2
  exit 1
fi

if [[ ${#SRC_PACKAGES[@]} -eq 1 ]]; then
  OLD_PACKAGE="${SRC_PACKAGES[0]}"
else
  if [[ -d "src/python_ai_friendly_template" ]]; then
    OLD_PACKAGE="python_ai_friendly_template"
  elif [[ -d "src/my_python_project" ]]; then
    OLD_PACKAGE="my_python_project"
  else
    echo "ERROR: Multiple package directories found under src/:" >&2
    printf '  - %s\n' "${SRC_PACKAGES[@]}" >&2
    echo "This script requires exactly one current package directory under src/." >&2
    exit 1
  fi
fi

if [[ "$OLD_PACKAGE" == "$PACKAGE_NAME" ]]; then
  echo "INFO: Package directory is already src/$PACKAGE_NAME"
else
  if [[ -e "src/$PACKAGE_NAME" ]]; then
    echo "ERROR: Target package directory already exists: src/$PACKAGE_NAME" >&2
    exit 1
  fi
fi

OLD_PROJECT_NAME="python-ai-friendly-template"
OLD_PROJECT_TITLE="Python AI-Friendly Template"
OLD_PROJECT_NAME_ALT="my-python-project"

echo "Initializing project from template"
echo "  Project name:     $PROJECT_NAME"
echo "  Package name:     $PACKAGE_NAME"
echo "  Current package:  $OLD_PACKAGE"
echo "  Marker file:      $INIT_MARKER"

if [[ "$FORCE" == "true" ]]; then
  echo ""
  echo "WARNING: --force was provided."
  echo "This can overwrite a previous template initialization marker."
fi

if [[ "$FORCE" != "true" ]]; then
  cat <<EOF

This will update files in the current repository and create:
  $INIT_MARKER

After that, the script will refuse to run again unless --force is used.

Continue? [y/N]
EOF
  read -r answer
  case "$answer" in
    y|Y|yes|YES)
      ;;
    *)
      echo "Aborted."
      exit 0
      ;;
  esac
fi

if [[ "$OLD_PACKAGE" != "$PACKAGE_NAME" ]]; then
  mv "src/$OLD_PACKAGE" "src/$PACKAGE_NAME"
fi

mapfile -t TEXT_FILES < <(
  find . -type f \
    ! -path './.git/*' \
    ! -path './.venv/*' \
    ! -path './venv/*' \
    ! -path './env/*' \
    ! -path './__pycache__/*' \
    ! -path './.ruff_cache/*' \
    ! -path './.mypy_cache/*' \
    ! -path './dist/*' \
    ! -path './build/*' \
    ! -path './*.png' \
    ! -path './*.jpg' \
    ! -path './*.jpeg' \
    ! -path './*.gif' \
    ! -path './*.ico' \
    ! -path './*.pdf' \
    ! -path './*.zip' \
    ! -path './*.tar' \
    ! -path './*.gz' \
    ! -path "./$INIT_MARKER" \
    -print
)

replace_in_file() {
  local file="$1"
  local old="$2"
  local new="$3"

  if grep -Iq . "$file" && grep -q "$old" "$file"; then
    sed -i "s|$old|$new|g" "$file"
  fi
}

for file in "${TEXT_FILES[@]}"; do
  replace_in_file "$file" "$OLD_PACKAGE" "$PACKAGE_NAME"
  replace_in_file "$file" "$OLD_PROJECT_NAME" "$PROJECT_NAME"
  replace_in_file "$file" "$OLD_PROJECT_TITLE" "$PROJECT_NAME"
  replace_in_file "$file" "$OLD_PROJECT_NAME_ALT" "$PROJECT_NAME"
  replace_in_file "$file" "python_template" "$PACKAGE_NAME"
done

if [[ -f ".env.example" ]]; then
  if grep -q '^PROJECT_NAME=' ".env.example"; then
    sed -i "s|^PROJECT_NAME=.*|PROJECT_NAME=$PROJECT_NAME|" ".env.example"
  else
    printf '\nPROJECT_NAME=%s\n' "$PROJECT_NAME" >> ".env.example"
  fi

  if ! grep -q '^PYTHONPATH=' ".env.example"; then
    printf 'PYTHONPATH=src\n' >> ".env.example"
  fi
fi

if [[ -f "pyproject.toml" ]]; then
  sed -i "s|^name = .*|name = \"$PROJECT_NAME\"|" "pyproject.toml"
fi

if [[ -f "README.md" ]]; then
  if head -n 1 "README.md" | grep -q '^# '; then
    sed -i "1s|^# .*|# $PROJECT_NAME|" "README.md"
  fi
fi

if [[ -d "scripts" ]]; then
  find scripts -type f -name "*.sh" -exec chmod +x {} \;
fi

cat > "$INIT_MARKER" <<EOF
Template initialized: yes
Project name: $PROJECT_NAME
Package name: $PACKAGE_NAME
Original package: $OLD_PACKAGE
Initialized at: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
Script: scripts/init_from_template.sh

This file prevents accidental repeated template initialization.
Do not delete it unless you intentionally want to re-run template initialization.
EOF

cat <<EOF

Done.

Updated project:
  $PROJECT_NAME

Python package:
  src/$PACKAGE_NAME

Initialization marker created:
  $INIT_MARKER

Recommended next steps:
  cp .env.example .env
  python -m venv .venv
  source .venv/bin/activate
  python -m pip install --upgrade pip
  python -m pip install -r requirements.txt
  scripts/test.sh full local
  scripts/lint.sh

Docker validation:
  PROJECT_NAME=$PACKAGE_NAME scripts/test.sh full docker-dev
  PROJECT_NAME=$PACKAGE_NAME scripts/test.sh full docker-qa

Review the diff:
  git status
  git diff

Then commit:
  git add .
  git commit -m "Initialize project from template"

EOF
