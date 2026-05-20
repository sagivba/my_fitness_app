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
- `dashboard.py` renders the mini workout metrics dashboard.
- `workouts.py` handles workout list, create form, create submit, and detail pages.
- `sleep.py` handles sleep log list, create form, create submit, and detail pages.
- `daily_logs.py` handles daily log list, create form, create submit, and detail pages.
- `meals.py` handles meal list, create form, create submit, detail, edit form, and
  update submit pages.
- `imports.py` handles raw import file list, upload form, upload submit, and detail
  pages, plus actions that trigger Garmin CSV, TCX, and GPX import for uploaded files.

## src/my_fitness_app/services

Business logic.

Services should be easy to test with unittest.

Workout validation and application logic live in `services/workout_service.py`.
Workout-linked strength training validation, exercise reuse, set numbering, and
summary calculations live in `services/strength_service.py`.
Sleep validation and application logic live in `services/sleep_service.py`.
Daily log validation and application logic live in `services/daily_log_service.py`.
Meal validation and application logic live in `services/meal_service.py`.
Raw import file validation, hashing, duplicate detection, and local storage logic live
in `services/import_file_service.py`.
Garmin CSV parsing, row validation, duplicate workout detection, workout creation, and
import status updates live in `services/garmin_csv_import_service.py`.
Garmin TCX XML parsing, duplicate workout detection, workout creation, and import
status updates live in `services/garmin_tcx_import_service.py`.
Garmin GPX XML parsing, distance calculation, duplicate workout detection, workout
creation, and import status updates live in `services/garmin_gpx_import_service.py`.
Mini dashboard aggregation from structured workout fields lives in
`services/dashboard_service.py`.

## src/my_fitness_app/model

Domain models, data structures, and model-facing code.

SQLite persistence foundation:

- `model/database.py` creates SQLite connections and initializes the schema.
- `model/schema.sql` defines the MVP tables: `daily_log`, `workout`, `sleep_log`,
  `strength_exercise`, `strength_set`, `meal`, and `imported_file`.
- `model/workout_repository.py` contains workout persistence operations.
- `model/strength_repository.py` contains strength exercise and set persistence
  operations.
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
`created_at`, and `updated_at`. CP07 adds minimal import tracking fields to
`imported_file`: `import_status` and `import_error_message`.

The workout table stores manual workout fields plus structured Garmin/workout metrics:
`start_time`, `end_time`, `duration_seconds`, `distance_meters`, `calories`,
`average_heart_rate`, `max_heart_rate`, `elevation_gain_meters`,
`elevation_loss_meters`, and `external_activity_id`. The existing `source` field
identifies manual entries and Garmin import sources.

Strength details are optional and linked to workouts through `strength_exercise`.
Each strength exercise belongs to one workout and can have many `strength_set` rows.
Deleting a workout cascades to its strength exercises and sets. The strength service
can reuse an existing exercise on the same workout when a new set uses the same
normalized exercise name.

Because the project does not use a migration framework, fresh databases receive these
columns through `model/schema.sql`, and existing SQLite databases are hardened by
idempotent compatibility checks in `model/database.py`. The compatibility logic only
adds missing nullable columns and creates missing strength detail tables. It does not
drop tables, recreate tables, or rewrite existing rows.

Garmin CSV, TCX, and GPX import creates normalized workout records from supported files
using the existing workout table. Importers set workout `source` to `garmin_csv`,
`garmin_tcx`, or `garmin_gpx` and persist parsed metrics structurally where possible.
Workout notes remain a deterministic, human-readable summary and legacy duplicate
fallback only; dashboard metrics must not parse notes.

FIT, Garmin Connect integration, advanced analytics, and charts remain future scope.

## src/my_fitness_app/utils

Small generic utilities.

Do not put project-specific business rules here.

Generic filename sanitization and path containment helpers live in `utils/files.py`.
