# my-python-project-template

AI-friendly Python project template.

This repository is a reusable template for small-to-medium Python applications developed with:

- Python 3.12+
- VS Code / WSL
- `unittest`
- optional Docker Compose
- GitHub Actions CI
- Codex CLI friendly workflows
- clear documentation for humans and AI agents

## Purpose

The goal of this template is to provide a clean, predictable starting point for Python projects.

It favors:

- small, reviewable changes
- simple architecture
- deterministic tests
- minimal dependencies
- explicit scripts
- documentation that stays close to the code
- AI-friendly repository conventions

## Use this template

This repository is intended to be used as a GitHub Template repository.

For the full workflow, including:

- preparing this repository as a template
- using `Use this template`
- creating a new repository from the template
- cloning the new repository
- running `scripts/init_from_template.sh`
- importing the template into an existing local directory
- understanding when Git creates a new directory

Full instructions: [docs/template-usage.md](docs/template-usage.md)

Minimal flow:

```bash
gh repo create sagivba/my-new-project --template sagivba/python-ai-friendly-template --private --clone
cd my-new-project
scripts/init_from_template.sh my-new-project
```

Do not run the initialization script from `src/`. Run it from the project root.

## Start here

Before making changes, read these files:

```text
AGENTS.md
.github/CONTRIBUTING.md
```

Use:

- `AGENTS.md` for AI agents, Codex CLI, ChatGPT, and other AI-assisted coding workflows.
- `.github/CONTRIBUTING.md` for human contribution rules, review expectations, testing policy, dependency policy, and documentation expectations.

These two files are part of the template contract. Keep them aligned with the repository structure, commands, and workflow.

## Use this template

This repository is intended to be marked as a GitHub Template repository.

After creating a new repository from this template, run:

```bash
scripts/init_from_template.sh my-new-project
```

Or, if you want to choose the Python package name explicitly:

```bash
scripts/init_from_template.sh "My New Project" --package my_new_project
```

The initialization script updates:

- project name
- Python package directory under `src/`
- imports and package references
- `README.md`
- `pyproject.toml`
- `.env.example`
- Docker-related project naming references where possible

The script creates this marker file:

```text
.template-initialized
```

This prevents accidental repeated initialization. A second run will fail unless `--force` is used.

Use `--force` only when you intentionally want to re-run initialization:

```bash
scripts/init_from_template.sh my-new-project --force
```

## Project structure

```text
my-python-project-template/
├── .github/
│   ├── workflows/
│   │   └── ci.yml
│   └── CONTRIBUTING.md
├── .vscode/
│   ├── settings.json
│   ├── launch.json
│   └── tasks.json
├── docs/
│   ├── architecture.md
│   ├── codex-workflow.md
│   └── dev-python.md
├── scripts/
│   ├── init_from_template.sh
│   ├── test.sh
│   ├── lint.sh
│   └── clean.sh
├── src/
│   └── my_python_project_template/
│       ├── __init__.py
│       ├── app.py
│       ├── config.py
│       ├── routes/
│       ├── services/
│       ├── model/
│       └── utils/
├── tests/
├── templates/
├── static/
├── .env.example
├── .gitignore
├── AGENTS.md
├── Dockerfile
├── docker-compose.yml
├── docker-compose.dev.yml
├── docker-compose.qa.yml
├── Makefile
├── README.md
├── TODO.md
├── requirements.in
├── requirements.txt
└── pyproject.toml
```

## Architecture

The template uses a simple layered structure:

```text
routes -> services -> model
              |
            utils
```

Responsibilities:

- `app.py`: application factory and wiring
- `config.py`: configuration loading
- `routes/`: HTTP request/response boundary
- `services/`: application and business logic
- `model/`: domain models, data structures, model-facing code
- `utils/`: small generic helpers only
- `tests/`: `unittest` test coverage

Do not put business logic directly inside route handlers.

For more detail, read:

```text
docs/architecture.md
```

## Quick start

### 1. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

For Conda:

```bash
conda create -n my-python-project-template python=3.12 -y
conda activate my-python-project-template
```

### 2. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 3. Create local environment file

```bash
cp .env.example .env
```

The important value is:

```text
PYTHONPATH=src
```

### 4. Run tests

```bash
scripts/test.sh quick
```

or:

```bash
scripts/test.sh full
```

### 5. Run the app

```bash
PYTHONPATH=src flask --app my_python_project_template.app:create_app run --debug
```

Open:

```text
http://127.0.0.1:5000
```

Health endpoint:

```text
http://127.0.0.1:5000/api/health
```

Expected response:

```json
{
  "status": "ok"
}
```

## Running tests

This project supports running tests either locally or inside Docker.

### Local tests

Use local tests when working in WSL with a dedicated Python environment such as `venv` or Conda.

```bash
scripts/test.sh quick
scripts/test.sh full
```

Equivalent direct command:

```bash
PYTHONPATH=src python -m unittest discover -s tests -p "test_*.py" -v
```

### Docker Dev tests

Use Docker Dev tests when you want to run the test suite inside the Dev Docker Compose environment.

```bash
scripts/test.sh quick docker-dev
scripts/test.sh full docker-dev
```

### Docker QA tests

Use Docker QA tests when validating the project in a QA-like Docker Compose environment before merging.

```bash
scripts/test.sh quick docker-qa
scripts/test.sh full docker-qa
```

### Test command format

```bash
scripts/test.sh [quick|full] [local|docker-dev|docker-qa]
```

Defaults:

```bash
scripts/test.sh
```

is equivalent to:

```bash
scripts/test.sh quick local
```

### Docker Compose project names

The Docker test targets use project-name based Compose names.

You can override them with environment variables:

```bash
PROJECT_NAME=my_python_project_template scripts/test.sh full docker-dev
DEV_COMPOSE_PROJECT=my_python_project_template_dev scripts/test.sh full docker-dev
QA_COMPOSE_PROJECT=my_python_project_template_qa scripts/test.sh full docker-qa
```

## Docker

Docker support is optional. The primary local development flow is WSL + VS Code + a dedicated Python environment.

### Start Dev environment

```bash
docker compose -p my_python_project_template_dev -f docker-compose.yml -f docker-compose.dev.yml up -d --build
```

### Start QA environment

```bash
docker compose -p my_python_project_template_qa -f docker-compose.yml -f docker-compose.qa.yml up -d --build
```

### Stop Dev environment

```bash
docker compose -p my_python_project_template_dev -f docker-compose.yml -f docker-compose.dev.yml down
```

### Stop QA environment

```bash
docker compose -p my_python_project_template_qa -f docker-compose.yml -f docker-compose.qa.yml down
```

### View logs

```bash
docker compose -p my_python_project_template_dev -f docker-compose.yml -f docker-compose.dev.yml logs -f app
```

## Lint and formatting

Run lint checks:

```bash
scripts/lint.sh
```

Format code:

```bash
python -m ruff format src tests
python -m ruff check --fix src tests
```

## Testing policy

This repository uses **unittest**.

Do not introduce `pytest` unless the project explicitly decides to migrate.

Expected test command:

```bash
PYTHONPATH=src python -m unittest discover -s tests -p "test_*.py" -v
```

Preferred project command:

```bash
scripts/test.sh full local
```

Testing rules are also documented in:

```text
AGENTS.md
.github/CONTRIBUTING.md
```

## VS Code / WSL

Open the repository from WSL:

```bash
code .
```

The template includes:

- `.vscode/settings.json`
- `.vscode/launch.json`
- `.vscode/tasks.json`

These files configure:

- unittest discovery
- Flask launch profile
- test tasks
- lint task
- Docker Dev/QA tasks

For more detail, read:

```text
docs/dev-python.md
```

## GitHub Actions CI

The workflow is located at:

```text
.github/workflows/ci.yml
```

The CI workflow runs:

- dependency installation
- Ruff lint check
- Ruff format check
- unittest discovery

## AI / Codex notes

Read this file before making automated changes:

```text
AGENTS.md
```

`AGENTS.md` defines:

- architecture boundaries
- AI/Codex working rules
- branch naming conventions
- local and Docker test targets
- lint expectations
- dependency rules
- documentation rules
- review checklist

Recommended Codex CLI branch prefix:

```text
codex-cli/<short-task-name>
```

Examples:

```text
codex-cli/add-health-endpoint
codex-cli/fix-docker-test-target
codex-cli/improve-config-loading
```

For more detail, read:

```text
docs/codex-workflow.md
```

## Contributing

Read this file before opening or reviewing pull requests:

```text
.github/CONTRIBUTING.md
```

`CONTRIBUTING.md` defines:

- working principles
- architecture expectations
- environment rules
- testing rules
- dependency rules
- secrets and configuration policy
- CI rules
- documentation rules
- pull request guidance
- preferred change style
- AI-assisted contribution rules

## Recommended workflow after creating a new repo from this template

```bash
git clone <new-repo-url>
cd <new-repo>

scripts/init_from_template.sh my-new-project

cp .env.example .env

python -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

scripts/test.sh full local
scripts/lint.sh

git status
git add .
git commit -m "Initialize project from template"
```

Optional Docker validation:

```bash
PROJECT_NAME=my_new_project scripts/test.sh full docker-dev
PROJECT_NAME=my_new_project scripts/test.sh full docker-qa
```

## Important files

- `AGENTS.md`: instructions for AI agents and Codex-style workflows
- `.github/CONTRIBUTING.md`: human contribution rules and review expectations
- `docs/dev-python.md`: local Python development guide
- `docs/architecture.md`: architecture boundaries
- `docs/codex-workflow.md`: Codex workflow guidance
- `scripts/init_from_template.sh`: one-time initialization script after creating a new repository from the template
- `scripts/test.sh`: canonical local and Docker test runner
- `scripts/lint.sh`: canonical lint runner
- `.github/workflows/ci.yml`: CI definition
