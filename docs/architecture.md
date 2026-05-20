# Architecture

This project uses a simple layered structure.

## Layers

```text
routes -> services -> model
              |
            utils
```

## src/my_fitness_app/app.py

Creates and configures the Flask application.

## src/my_fitness_app/config.py

Loads configuration from environment variables.

Current environment-backed settings:

- `PROJECT_NAME`
- `DATABASE_PATH`, defaulting to `instance/my_fitness_app.db`

## src/my_fitness_app/routes

HTTP boundary.

Route handlers should:

- parse inputs
- call services
- return responses

Route handlers should not contain business logic.

Current web route groups:

- `web.py` renders the home page.
- `workouts.py` handles workout list, create form, create submit, and detail pages.
- `sleep.py` handles sleep log list, create form, create submit, and detail pages.
- `daily_logs.py` handles daily log list, create form, create submit, and detail pages.

## src/my_fitness_app/services

Business logic.

Services should be easy to test with unittest.

Workout validation and application logic live in `services/workout_service.py`.
Sleep validation and application logic live in `services/sleep_service.py`.
Daily log validation and application logic live in `services/daily_log_service.py`.

## src/my_fitness_app/model

Domain models, data structures, and model-facing code.

SQLite persistence foundation:

- `model/database.py` creates SQLite connections and initializes the schema.
- `model/schema.sql` defines the MVP tables: `daily_log`, `workout`, `sleep_log`,
  `meal`, and `imported_file`.
- `model/workout_repository.py` contains workout persistence operations.
- `model/sleep_repository.py` contains sleep log persistence operations.
- `model/daily_log_repository.py` contains daily log persistence operations.
- Route handlers must not call SQLite directly.

## src/my_fitness_app/utils

Small generic utilities.

Do not put project-specific business rules here.
