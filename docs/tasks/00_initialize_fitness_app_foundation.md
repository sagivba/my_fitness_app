# Task 00 - Initialize fitness app foundation and align AGENTS.md

## Branch

```text
codex-cli/initialize-fitness-app-foundation
```

## Suggested Codex effort

Medium. This is mostly controlled rename and documentation alignment, but it touches many files.

## Goal

Prepare the existing repository as the foundation for a personal Flask-based fitness tracking application named my_fitness_app.

## Scope

1. Inspect the current repository structure before editing.
2. Rename the internal Python package from the template package name to `my_fitness_app`.
3. Update imports, test imports, Flask app references, pyproject metadata, README, .env.example, VS Code settings, Docker Compose project names, and documentation references.
4. Update `AGENTS.md` so it is project-specific, well formatted, and aligned with `AGENTS_TARGET.md` from this task pack.
5. Keep the existing health endpoint behavior working.
6. Add a short product description to README: personal local-first fitness data collection app for workouts, Garmin imports, sleep, meals, and future analytics.
7. Keep the repository name `sagivba/my_fitness_app` unchanged.

## Out of scope

1. Do not implement database persistence.
2. Do not implement Garmin imports.
3. Do not implement meal photo analysis or OpenAI API calls.
4. Do not implement analytics.
5. Do not add new dependencies unless the existing template initialization flow requires it.

## Likely files to touch

- `src/`
- `tests/`
- `README.md`
- `AGENTS.md`
- `.github/CONTRIBUTING.md`
- `docs/*.md`
- `.env.example`
- `.vscode/*`
- `docker-compose*.yml`
- `pyproject.toml`

## Validation

```bash
scripts/test.sh full local
scripts/lint.sh
```

If Docker-related names or runtime wiring changed, also run:

```bash
scripts/test.sh full docker-dev
```

## Acceptance criteria

- The app runs with the new package name.
- Health endpoint still returns `{"status": "ok"}` or the existing documented equivalent.
- No references to `my_python_project_template` remain except in archived/template documentation if deliberately retained and documented.
- `AGENTS.md` is readable, project-specific, and uses `src/my_fitness_app/...` paths.
- Tests and lint pass.


## Slash goal

```text
/goal
Prepare the existing repository as the foundation for a personal Flask-based fitness tracking application named my_fitness_app.

Use branch: codex-cli/initialize-fitness-app-foundation

Scope:
1. Inspect the current repository structure before editing.
2. Rename the internal Python package from the template package name to `my_fitness_app`.
3. Update imports, test imports, Flask app references, pyproject metadata, README, .env.example, VS Code settings, Docker Compose project names, and documentation references.
4. Update `AGENTS.md` so it is project-specific, well formatted, and aligned with `AGENTS_TARGET.md` from this task pack.
5. Keep the existing health endpoint behavior working.
6. Add a short product description to README: personal local-first fitness data collection app for workouts, Garmin imports, sleep, meals, and future analytics.
7. Keep the repository name `sagivba/my_fitness_app` unchanged.

Out of scope:
1. Do not implement database persistence.
2. Do not implement Garmin imports.
3. Do not implement meal photo analysis or OpenAI API calls.
4. Do not implement analytics.
5. Do not add new dependencies unless the existing template initialization flow requires it.

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

If Docker-related names or runtime wiring changed, also run:

```bash
scripts/test.sh full docker-dev
```

Acceptance criteria:
- The app runs with the new package name.
- Health endpoint still returns `{"status": "ok"}` or the existing documented equivalent.
- No references to `my_python_project_template` remain except in archived/template documentation if deliberately retained and documented.
- `AGENTS.md` is readable, project-specific, and uses `src/my_fitness_app/...` paths.
- Tests and lint pass.
```
