# Task 08 - Add Garmin TCX and GPX import

## Branch

```text
codex-cli/add-garmin-tcx-gpx-import
```

## Suggested Codex effort

High. XML parsing can grow quickly; keep scope narrow.

## Goal

Add basic TCX and GPX parsing for Garmin activity files using the Python standard library where practical.

## Scope

1. Add TCX parser for basic activity fields: start time, duration, distance, calories, average heart rate if available, max heart rate if available, and notes/source metadata.
2. Add GPX parser for basic route fields: start time if available, distance estimate if safely implemented, and source metadata.
3. Use standard library XML parsing first.
4. Keep parsing tolerant but explicit about unsupported data.
5. Add fixture files for TCX and GPX.
6. Add tests for successful parse, missing fields, malformed XML, and unsupported structures.
7. Update `docs/garmin-imports.md` with supported and unsupported fields.

## Out of scope

1. Do not add FIT parsing in this task.
2. Do not add a new dependency unless absolutely necessary and documented.
3. Do not integrate Garmin Connect API.
4. Do not implement route maps or charts.

## Likely files to touch

- `src/my_fitness_app/services/garmin_tcx_import_service.py`
- `src/my_fitness_app/services/garmin_gpx_import_service.py`
- `src/my_fitness_app/services/import_file_service.py`
- `tests/fixtures/*.tcx`
- `tests/fixtures/*.gpx`
- `tests/`
- `docs/garmin-imports.md`

## Validation

```bash
scripts/test.sh full local
scripts/lint.sh
```

## Acceptance criteria

- TCX fixture imports a workout with expected fields.
- GPX fixture parses without crashing and records supported data.
- Unsupported/missing fields are handled predictably.
- Tests and lint pass.


## Slash goal

```text
/goal
Add basic TCX and GPX parsing for Garmin activity files using the Python standard library where practical.

Use branch: codex-cli/add-garmin-tcx-gpx-import

Scope:
1. Add TCX parser for basic activity fields: start time, duration, distance, calories, average heart rate if available, max heart rate if available, and notes/source metadata.
2. Add GPX parser for basic route fields: start time if available, distance estimate if safely implemented, and source metadata.
3. Use standard library XML parsing first.
4. Keep parsing tolerant but explicit about unsupported data.
5. Add fixture files for TCX and GPX.
6. Add tests for successful parse, missing fields, malformed XML, and unsupported structures.
7. Update `docs/garmin-imports.md` with supported and unsupported fields.

Out of scope:
1. Do not add FIT parsing in this task.
2. Do not add a new dependency unless absolutely necessary and documented.
3. Do not integrate Garmin Connect API.
4. Do not implement route maps or charts.

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
- TCX fixture imports a workout with expected fields.
- GPX fixture parses without crashing and records supported data.
- Unsupported/missing fields are handled predictably.
- Tests and lint pass.
```
