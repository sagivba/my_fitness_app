# Task 13 - Add project hardening, export, and backup helpers

## Branch

```text
codex-cli/add-project-hardening-and-export
```

## Suggested Codex effort

Medium.

## Goal

Add practical hardening utilities for a local-first personal app, including export and backup support.

## Scope

1. Add a simple data export feature for user-owned data, preferably JSON and/or CSV.
2. Add a local backup helper or documented backup command for the SQLite database and uploads directory.
3. Add tests for export services.
4. Review `.gitignore` so local database files, uploads, and secrets are not committed.
5. Update README and docs with backup/export guidance.
6. Add a final project checklist for running tests, lint, and optional Docker QA.

## Out of scope

1. Do not add cloud backup.
2. Do not add authentication.
3. Do not add encryption unless explicitly requested.
4. Do not implement public deployment.

## Likely files to touch

- `src/my_fitness_app/services/export_service.py`
- `src/my_fitness_app/routes/export_routes.py` if UI export is included
- `templates/export/*.html` if UI export is included
- `scripts/` if helper scripts are added
- `.gitignore`
- `tests/`
- `README.md`
- `docs/dev-python.md`

## Validation

```bash
scripts/test.sh full local
scripts/lint.sh
```

For final validation, prefer:

```bash
scripts/test.sh full docker-qa
```

## Acceptance criteria

- User can export app data or has a documented local export path.
- Local DB, uploads, and secrets remain untracked.
- Backup guidance is documented.
- Tests and lint pass.


## Slash goal

```text
/goal
Add practical hardening utilities for a local-first personal app, including export and backup support.

Use branch: codex-cli/add-project-hardening-and-export

Scope:
1. Add a simple data export feature for user-owned data, preferably JSON and/or CSV.
2. Add a local backup helper or documented backup command for the SQLite database and uploads directory.
3. Add tests for export services.
4. Review `.gitignore` so local database files, uploads, and secrets are not committed.
5. Update README and docs with backup/export guidance.
6. Add a final project checklist for running tests, lint, and optional Docker QA.

Out of scope:
1. Do not add cloud backup.
2. Do not add authentication.
3. Do not add encryption unless explicitly requested.
4. Do not implement public deployment.

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

For final validation, prefer:

```bash
scripts/test.sh full docker-qa
```

Acceptance criteria:
- User can export app data or has a documented local export path.
- Local DB, uploads, and secrets remain untracked.
- Backup guidance is documented.
- Tests and lint pass.
```
