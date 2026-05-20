# My Fitness App

Personal Flask-based fitness tracking application.

The application is intended to collect and organize personal fitness, sleep, nutrition, and future medical metrics data.

## Current status

This repository currently contains the initialized Flask foundation for the app and a
minimal SQLite persistence foundation with basic workout, sleep, daily log, manual
meal data entry, and raw activity file storage.

The Garmin import foundation stores raw files only. It does not parse Garmin files,
create workouts, or create derived metrics.

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
- SQLite local persistence
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

Workout pages:

```text
http://127.0.0.1:5000/workouts/
http://127.0.0.1:5000/workouts/new
```

Sleep pages:

```text
http://127.0.0.1:5000/sleep/
http://127.0.0.1:5000/sleep/new
```

Daily log pages:

```text
http://127.0.0.1:5000/daily-logs/
http://127.0.0.1:5000/daily-logs/new
```

Meal pages:

```text
http://127.0.0.1:5000/meals/
http://127.0.0.1:5000/meals/new
```

Manual meal logging uses only the current SQLite `meal` table fields. AI nutrition
analysis, meal photo upload, `meal_time`, and `recipe_url` are future scope.

Raw import file pages:

```text
http://127.0.0.1:5000/imports/
http://127.0.0.1:5000/imports/new
```

Raw import storage accepts `.csv`, `.tcx`, `.gpx`, and `.fit` files. Uploaded files are
stored locally under `UPLOAD_DIRECTORY`, defaulting to `instance/uploads`.

Each raw file is stored as `<sha256>.<ext>`. The app records only the existing
`imported_file` metadata fields: original filename, stored path, SHA-256 hash, file
type, import time, created time, and updated time. Duplicate uploads are detected by
SHA-256 hash and do not create another physical file or database row.

This CP06 import foundation stores raw files only. Garmin parsing, workout creation,
metric creation, duplicate activity matching, and Garmin Connect integration are future
scope.

## SQLite persistence

The app reads its database location from `DATABASE_PATH`.

Default:

```text
instance/my_fitness_app.db
```

The `instance/` directory is local application data and is not tracked by Git.

The app reads its raw import upload directory from `UPLOAD_DIRECTORY`.

Default:

```text
instance/uploads
```

The app initializes the configured SQLite schema during startup. The model layer owns
database access in:

```text
src/my_fitness_app/model/database.py
src/my_fitness_app/model/schema.sql
```

The initial schema creates these MVP tables:

- `daily_log`
- `workout`
- `sleep_log`
- `meal`
- `imported_file`

You can also initialize the configured database directly in Docker:

```bash
docker compose \
  -p my_fitness_app_dev \
  -f docker-compose.yml \
  -f docker-compose.dev.yml \
  run --rm app python3 -c "from my_fitness_app.config import AppConfig; from my_fitness_app.model.database import initialize_database; initialize_database(AppConfig.from_env().database_path)"
```

To reset the local database, remove the database file and run initialization again:

```bash
rm -f instance/my_fitness_app.db
```

## Codex task plan

The staged Codex tasks are under:

```text
docs/tasks/
```

Run them in order. Do not give Codex all tasks at once.

Follow `docs/task_order.md` and run one task at a time.
