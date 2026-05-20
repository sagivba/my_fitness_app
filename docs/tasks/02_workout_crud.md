# Task 02 - Add workout CRUD screens and service layer

## Branch

```text
codex-cli/add-workout-crud
```

## Suggested Codex effort

High. This is the first real product feature and should be carefully scoped.

## Goal

Add create, list, view, edit, and delete support for workout records using Flask templates and the SQLite persistence layer.

## Scope

1. Add a `Workout` domain representation if not already present.
2. Add workout service functions for create/list/get/update/delete.
3. Add route handlers that delegate business logic to services.
4. Add templates for workout list, detail, create, and edit.
5. Support initial workout fields: date, start time, workout type, duration minutes, distance km, steps, calories, average heart rate, max heart rate, RPE, and notes.
6. Add validation for required fields and numeric ranges.
7. Add navigation links from the home/dashboard page.
8. Add unit tests for service validation and route behavior.

## Out of scope

1. Do not add strength exercise details in this task.
2. Do not add Garmin import.
3. Do not add analytics.
4. Do not add JavaScript-heavy UI or a frontend framework.

## Likely files to touch

- `src/my_fitness_app/routes/workout_routes.py`
- `src/my_fitness_app/services/workout_service.py`
- `src/my_fitness_app/model/workout.py`
- `templates/workouts/*.html`
- `templates/base.html` if needed
- `tests/`
- `docs/architecture.md` if structure changes

## Validation

```bash
scripts/test.sh full local
scripts/lint.sh
```

## Acceptance criteria

- A user can add, view, edit, list, and delete workouts locally.
- Invalid input is handled without crashing.
- Business logic is in services, not routes.
- Tests cover service behavior and main route flows.
- Tests and lint pass.


## Slash goal

```text
/goal
Add create, list, view, edit, and delete support for workout records using Flask templates and the SQLite persistence layer.

Use branch: codex-cli/add-workout-crud

Scope:
1. Add a `Workout` domain representation if not already present.
2. Add workout service functions for create/list/get/update/delete.
3. Add route handlers that delegate business logic to services.
4. Add templates for workout list, detail, create, and edit.
5. Support initial workout fields: date, start time, workout type, duration minutes, distance km, steps, calories, average heart rate, max heart rate, RPE, and notes.
6. Add validation for required fields and numeric ranges.
7. Add navigation links from the home/dashboard page.
8. Add unit tests for service validation and route behavior.

Out of scope:
1. Do not add strength exercise details in this task.
2. Do not add Garmin import.
3. Do not add analytics.
4. Do not add JavaScript-heavy UI or a frontend framework.

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
- A user can add, view, edit, list, and delete workouts locally.
- Invalid input is handled without crashing.
- Business logic is in services, not routes.
- Tests cover service behavior and main route flows.
- Tests and lint pass.
```
