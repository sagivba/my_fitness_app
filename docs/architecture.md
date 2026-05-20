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
- `UPLOAD_DIRECTORY`, defaulting to `instance/uploads`

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
- `meals.py` handles meal list, create form, create submit, detail, edit form, and
  update submit pages.
- `imports.py` handles raw import file list, upload form, upload submit, and detail
  pages.

## src/my_fitness_app/services

Business logic.

Services should be easy to test with unittest.

Workout validation and application logic live in `services/workout_service.py`.
Sleep validation and application logic live in `services/sleep_service.py`.
Daily log validation and application logic live in `services/daily_log_service.py`.
Meal validation and application logic live in `services/meal_service.py`.
Raw import file validation, hashing, duplicate detection, and local storage logic live
in `services/import_file_service.py`.

## src/my_fitness_app/model

Domain models, data structures, and model-facing code.

SQLite persistence foundation:

- `model/database.py` creates SQLite connections and initializes the schema.
- `model/schema.sql` defines the MVP tables: `daily_log`, `workout`, `sleep_log`,
  `meal`, and `imported_file`.
- `model/workout_repository.py` contains workout persistence operations.
- `model/sleep_repository.py` contains sleep log persistence operations.
- `model/daily_log_repository.py` contains daily log persistence operations.
- `model/meal_repository.py` contains meal persistence operations.
- `model/imported_file_repository.py` contains raw import file metadata persistence
  operations.
- Route handlers must not call SQLite directly.

Meal logging currently uses only existing `meal` table fields. AI nutrition analysis,
image upload, `meal_time`, and `recipe_url` are future scope.

Raw import file storage currently uses only existing `imported_file` table fields:
`original_filename`, `stored_path`, `file_hash`, `file_type`, `imported_at`,
`created_at`, and `updated_at`. CP06 stores raw files only under the configured upload
directory. Garmin parsing, workout creation, metric creation, Garmin Connect
integration, and analytics remain future scope.

## src/my_fitness_app/utils

Small generic utilities.

Do not put project-specific business rules here.

Generic filename sanitization and path containment helpers live in `utils/files.py`.
