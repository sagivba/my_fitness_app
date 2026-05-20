# Task 04 - Add sleep logs and daily subjective logs

## Branch

```text
codex-cli/add-sleep-and-daily-logs
```

## Suggested Codex effort

Medium.

## Goal

Add simple local logging for sleep and daily subjective metrics.

## Scope

1. Add sleep log CRUD: sleep date, bedtime, wake time, duration minutes, sleep quality, morning fatigue, source, and notes.
2. Calculate duration when bedtime and wake time are provided.
3. Add daily log CRUD: log date, energy level, mood level, stress level, and notes.
4. Add list and edit screens for sleep logs and daily logs.
5. Add service tests for duration calculation and validation.
6. Add route tests for main flows.
7. Link the screens from the main navigation.

## Out of scope

1. Do not import sleep from Garmin yet.
2. Do not add analytics/correlation.
3. Do not add medical interpretation.
4. Do not add reminders or background jobs.

## Likely files to touch

- `src/my_fitness_app/routes/sleep_routes.py`
- `src/my_fitness_app/routes/daily_log_routes.py`
- `src/my_fitness_app/services/sleep_service.py`
- `src/my_fitness_app/services/daily_log_service.py`
- `src/my_fitness_app/model/sleep_log.py`
- `src/my_fitness_app/model/daily_log.py`
- `templates/sleep/*.html`
- `templates/daily_logs/*.html`
- `tests/`

## Validation

```bash
scripts/test.sh full local
scripts/lint.sh
```

## Acceptance criteria

- A user can record sleep and subjective daily metrics.
- Duration calculations are tested.
- Data can be listed and edited.
- Tests and lint pass.


## Slash goal

```text
/goal
Add simple local logging for sleep and daily subjective metrics.

Use branch: codex-cli/add-sleep-and-daily-logs

Scope:
1. Add sleep log CRUD: sleep date, bedtime, wake time, duration minutes, sleep quality, morning fatigue, source, and notes.
2. Calculate duration when bedtime and wake time are provided.
3. Add daily log CRUD: log date, energy level, mood level, stress level, and notes.
4. Add list and edit screens for sleep logs and daily logs.
5. Add service tests for duration calculation and validation.
6. Add route tests for main flows.
7. Link the screens from the main navigation.

Out of scope:
1. Do not import sleep from Garmin yet.
2. Do not add analytics/correlation.
3. Do not add medical interpretation.
4. Do not add reminders or background jobs.

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
- A user can record sleep and subjective daily metrics.
- Duration calculations are tested.
- Data can be listed and edited.
- Tests and lint pass.
```
