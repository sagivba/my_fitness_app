# Task 07 - Add Garmin CSV import

## Branch

```text
codex-cli/add-garmin-csv-import
```

## Suggested Codex effort

High. Data mapping needs careful validation.

## Goal

Parse Garmin-related CSV activity exports and create normalized workout records from them.

## Scope

1. Add CSV parsing using the Python standard library.
2. Add a mapping layer from CSV headers to workout fields.
3. Support a small documented fixture CSV format first.
4. Add preview/validation behavior before creating workouts if the current UI supports it; otherwise implement service-level parse-and-import with clear results.
5. Store import status and errors on `imported_file`.
6. Detect likely duplicate workouts by date, start time, workout type, and duration.
7. Add tests with small fixture CSV files.
8. Document expected CSV columns and limitations.

## Out of scope

1. Do not parse FIT, TCX, or GPX in this task.
2. Do not integrate Garmin Connect API.
3. Do not add advanced charts.
4. Do not silently ignore malformed rows.

## Likely files to touch

- `src/my_fitness_app/services/garmin_csv_import_service.py`
- `src/my_fitness_app/services/import_file_service.py`
- `src/my_fitness_app/services/workout_service.py`
- `src/my_fitness_app/model/workout.py`
- `tests/fixtures/*.csv`
- `tests/`
- `docs/garmin-imports.md`

## Validation

```bash
scripts/test.sh full local
scripts/lint.sh
```

## Acceptance criteria

- A supported CSV fixture imports one or more workout records.
- Malformed CSV data produces clear errors.
- Duplicate workout detection is tested.
- Import status is recorded.
- Tests and lint pass.


## Slash goal

```text
/goal
Parse Garmin-related CSV activity exports and create normalized workout records from them.

Use branch: codex-cli/add-garmin-csv-import

Scope:
1. Add CSV parsing using the Python standard library.
2. Add a mapping layer from CSV headers to workout fields.
3. Support a small documented fixture CSV format first.
4. Add preview/validation behavior before creating workouts if the current UI supports it; otherwise implement service-level parse-and-import with clear results.
5. Store import status and errors on `imported_file`.
6. Detect likely duplicate workouts by date, start time, workout type, and duration.
7. Add tests with small fixture CSV files.
8. Document expected CSV columns and limitations.

Out of scope:
1. Do not parse FIT, TCX, or GPX in this task.
2. Do not integrate Garmin Connect API.
3. Do not add advanced charts.
4. Do not silently ignore malformed rows.

Constraints:
- Read AGENTS.md before making changes.
- Keep changes small and reviewable.
- Preserve routes -> services -> model boundaries.
- Use unittest only. Do not introduce pytest.
- Do not edit unrelated files.
- Do not commit secrets or local .env files.
- Update docs when commands, structure, behavior, or workflow changes.

Validation:
```bash
scripts/test.sh full local
scripts/lint.sh
```

Acceptance criteria:
- A supported CSV fixture imports one or more workout records.
- Malformed CSV data produces clear errors.
- Duplicate workout detection is tested.
- Import status is recorded.
- Tests and lint pass.
```
