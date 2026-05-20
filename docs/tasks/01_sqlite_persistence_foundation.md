# Task 01 - Add SQLite persistence foundation

## Branch

```text
codex-cli/add-sqlite-persistence-foundation
```

## Suggested Codex effort

High. Persistence affects architecture, tests, configuration, and future tasks.

## Goal

Add a minimal SQLite persistence layer for the local-first fitness app without adding user-facing CRUD features yet.

## Scope

1. Add configuration for a local SQLite database path, defaulting to an `instance/` location.
2. Add database connection helpers in the model layer.
3. Add schema initialization for the first domain tables: `daily_log`, `workout`, `sleep_log`, `meal`, and `imported_file`.
4. Keep schema simple and explicit.
5. Add a repeatable initialization path for tests using a temporary database.
6. Add unit tests for database initialization and connection behavior.
7. Document the local database location and reset/init workflow.

## Out of scope

1. Do not add workout screens.
2. Do not add Garmin parsing.
3. Do not add OpenAI integration.
4. Do not add SQLAlchemy unless explicitly justified and approved by the task result.
5. Do not add migrations framework yet.

## Likely files to touch

- `src/my_fitness_app/config.py`
- `src/my_fitness_app/model/database.py`
- `src/my_fitness_app/model/schema.sql` or equivalent
- `tests/`
- `README.md`
- `docs/architecture.md`
- `.env.example`

## Validation

```bash
scripts/test.sh full local
scripts/lint.sh
```

## Acceptance criteria

- Tests can create and initialize an isolated temporary SQLite database.
- Schema includes the MVP tables needed by later tasks.
- No application route contains persistence logic directly.
- Documentation explains how persistence works locally.
- Tests and lint pass.


## Slash goal

```text
/goal
Add a minimal SQLite persistence layer for the local-first fitness app without adding user-facing CRUD features yet.

Use branch: codex-cli/add-sqlite-persistence-foundation

Scope:
1. Add configuration for a local SQLite database path, defaulting to an `instance/` location.
2. Add database connection helpers in the model layer.
3. Add schema initialization for the first domain tables: `daily_log`, `workout`, `sleep_log`, `meal`, and `imported_file`.
4. Keep schema simple and explicit.
5. Add a repeatable initialization path for tests using a temporary database.
6. Add unit tests for database initialization and connection behavior.
7. Document the local database location and reset/init workflow.

Out of scope:
1. Do not add workout screens.
2. Do not add Garmin parsing.
3. Do not add OpenAI integration.
4. Do not add SQLAlchemy unless explicitly justified and approved by the task result.
5. Do not add migrations framework yet.

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
- Tests can create and initialize an isolated temporary SQLite database.
- Schema includes the MVP tables needed by later tasks.
- No application route contains persistence logic directly.
- Documentation explains how persistence works locally.
- Tests and lint pass.
```
