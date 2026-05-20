# My Fitness App

Personal Flask-based fitness tracking application.

The application is intended to collect and organize personal fitness, sleep, nutrition, and future medical metrics data.

## Current status

This repository currently contains the initialized Flask foundation for the app.

The first development phase focuses on repository cleanup, package naming, Docker validation, tests, and AI/Codex-friendly project structure.

## Initial scope

- Manual workout logging
- Strength training details
- Sleep logs
- Daily logs
- Manual meal logging
- Garmin file import foundation
- Future OpenAI-based meal photo analysis
- Future correlation analytics between workouts, food, sleep, and recovery

## Technology

- Python
- Flask
- HTML templates
- SQLite in later stages
- unittest only
- Docker Compose first workflow
- WSL + VS Code friendly workflow

## Architecture

The project follows this structure:

```text
routes -> services -> model
              |
            utils
```

Rules:

- Keep request and response handling in `routes`.
- Keep business logic in `services`.
- Keep domain/data structures and persistence-facing code in `model`.
- Keep only small generic helpers in `utils`.
- Do not put business logic directly in route handlers.

## Start here

Before changing code, read:

```text
AGENTS.md
.github/CONTRIBUTING.md
docs/project_context.md
docs/task_order.md
```

## Docker-first workflow

This project is intended to be developed and validated primarily with Docker.

Run the full test suite in the Dev Docker environment:

```bash
scripts/test.sh full docker-dev
```

Run QA validation:

```bash
scripts/test.sh full docker-qa
```

Run lint in Docker:

```bash
docker compose \
  -p my_fitness_app_dev \
  -f docker-compose.yml \
  -f docker-compose.dev.yml \
  run --rm app python3 -m ruff check src tests

docker compose \
  -p my_fitness_app_dev \
  -f docker-compose.yml \
  -f docker-compose.dev.yml \
  run --rm app python3 -m ruff format --check src tests
```

## Optional local workflow

Local Python execution is optional.

If you choose to run locally, create an environment and install dependencies first:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```

Then run:

```bash
scripts/test.sh full local
scripts/lint.sh
```

## Run the app locally

With local dependencies installed:

```bash
PYTHONPATH=src flask --app my_fitness_app.app:create_app run --debug
```

Open:

```text
http://127.0.0.1:5000
```

Health endpoint:

```text
http://127.0.0.1:5000/api/health
```

## Codex task plan

The staged Codex tasks are under:

```text
docs/tasks/
```

Run them in order. Do not give Codex all tasks at once.

Start with:

```text
docs/tasks/00_initialize_fitness_app_foundation.md
```

After this foundation alignment is complete, Task 00 should only verify and finish remaining details.
