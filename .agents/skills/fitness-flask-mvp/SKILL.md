---
name: fitness-flask-mvp
description: use this skill when implementing my fitness app mvp features in this repository, especially flask routes, services, sqlite3 persistence, html templates, docker validation, and unittest coverage. do not use it for garmin import, openai meal photo analysis, medical metrics, public deployment, or correlation analytics unless explicitly requested.
---

# Fitness Flask MVP Skill

Use this skill for implementation work in the My Fitness App repository.

## Required reading before implementation

Read these files before making changes:

- AGENTS.md
- README.md
- docs/project_context.md
- docs/task_order.md
- docs/architecture.md
- The relevant task file under docs/tasks/

## Architecture rules

Preserve the project architecture:

```text
routes -> services -> model
              |
            utils
```

Rules:

- Keep HTTP request/response handling in `routes`.
- Keep business logic in `services`.
- Keep persistence-facing and domain data code in `model`.
- Keep `utils` limited to small generic helpers.
- Do not put business logic directly in route handlers.

## Technology rules

- Use Flask.
- Use `unittest` only.
- Do not introduce `pytest`.
- Prefer `sqlite3` from the Python standard library for early persistence work unless the user explicitly approves another dependency.
- Keep the app Docker-first.
- Do not add secrets.
- Do not add authentication, Garmin import, OpenAI API, medical metrics, or analytics unless the current task explicitly asks for them.

## Implementation workflow

1. Inspect the current repository state.
2. Summarize the intended plan before broad changes.
3. Implement in small, reviewable steps.
4. Add or update tests with each meaningful behavior change.
5. Keep templates simple and server-rendered.
6. Use Hebrew RTL labels in user-facing templates when practical.
7. Avoid unrelated refactors.

## Validation

Run these commands before reporting completion:

```bash
scripts/test.sh full docker-dev
docker compose -p my_fitness_app_dev -f docker-compose.yml -f docker-compose.dev.yml run --rm app python3 -m ruff check src tests
docker compose -p my_fitness_app_dev -f docker-compose.yml -f docker-compose.dev.yml run --rm app python3 -m ruff format --check src tests
```

If validation fails, report the exact failure and fix it if it is in scope.
