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

## src/my_fitness_app/services

Business logic.

Services should be easy to test with unittest.

## src/my_fitness_app/model

Domain models, data structures, and model-facing code.

SQLite persistence foundation:

- `model/database.py` creates SQLite connections and initializes the schema.
- `model/schema.sql` defines the MVP tables: `daily_log`, `workout`, `sleep_log`,
  `meal`, and `imported_file`.
- Route handlers must not call SQLite directly.

## src/my_fitness_app/utils

Small generic utilities.

Do not put project-specific business rules here.
