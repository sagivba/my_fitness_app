# AGENTS.md

Instructions for AI agents, Codex CLI, ChatGPT, and other AI-assisted development workflows.

This repository is an AI-friendly Python project template. The main goal is to keep the project simple, readable, reviewable, and predictable for both humans and automated agents.

## Core rules

- Keep changes small and reviewable.
- Make one logical change at a time.
- Do not reorganize the repository unless explicitly requested.
- Do not edit unrelated files.
- Do not perform broad refactors unless explicitly requested.
- Preserve the existing architecture unless the task explicitly asks to change it.
- Prefer explicit, direct, maintainable code over clever code.
- Do not introduce speculative abstractions.
- Do not add dependencies unless they are necessary and documented.
- Do not change public behavior without adding or updating tests.
- Update documentation when setup, commands, behavior, architecture, or workflow changes.
- Run the documented checks before claiming the task is complete.

## Technology assumptions

This template assumes:

- Python 3.12+
- WSL-based local development
- VS Code connected to WSL
- `unittest` only
- optional Docker Compose support
- GitHub Actions CI
- small, focused pull requests
- Codex CLI friendly branch and worktree workflows

Do not introduce `pytest`, a database, a background worker, a frontend framework, a queue, a cache, or an external service dependency unless explicitly requested.

## Branch naming

For Codex CLI or AI-assisted implementation work, use this branch prefix:

```text
codex-cli/<short-task-name>
```

Examples:

```text
codex-cli/add-health-endpoint
codex-cli/improve-config-loading
codex-cli/add-service-tests
codex-cli/fix-docker-test-target
```

Use concise, descriptive branch names. Avoid vague names such as:

```text
codex-cli/fixes
codex-cli/improvements
codex-cli/update
```

## Architecture boundaries

Keep responsibilities separated:

- `src/<package_name>/app.py`: application factory and wiring.
- `src/<package_name>/config.py`: configuration loading.
- `src/<package_name>/routes/`: request/response boundary only.
- `src/<package_name>/services/`: application and business logic.
- `src/<package_name>/model/`: domain models, data structures, model-facing code.
- `src/<package_name>/utils/`: small generic helpers only.
- `templates/`: HTML templates.
- `static/`: CSS, images, and static assets.
- `tests/`: `unittest`-based test coverage.
- `docs/`: project documentation.
- `scripts/`: repeatable local automation commands.

Do not put business logic directly inside route handlers.

Route handlers should:

- parse request inputs
- call services
- return responses

Services should:

- contain business/application logic
- be easy to test with `unittest`
- avoid Flask-specific request objects unless strictly necessary

Models should:

- represent domain data or model-facing structures
- avoid HTTP concerns

Utilities should:

- remain generic
- not become a dumping ground for business rules

## Testing policy

This project uses `unittest` only.

Do not introduce `pytest` unless explicitly requested.

The direct test command is:

```bash
PYTHONPATH=src python -m unittest discover -s tests -p "test_*.py" -v
```

The preferred project command is:

```bash
scripts/test.sh full local
```

Add or update tests when changing behavior in:

- routes
- services
- validation
- configuration
- model/domain logic
- public APIs
- command scripts
- Docker/runtime wiring

Prefer deterministic tests.

Avoid tests that require:

- network access
- real external services
- local secrets
- wall-clock-sensitive assertions
- specific execution order

## Test targets

The canonical test command is:

```bash
scripts/test.sh [quick|full] [local|docker-dev|docker-qa]
```

Defaults:

```bash
scripts/test.sh
```

is equivalent to:

```bash
scripts/test.sh quick local
```

Use local tests by default:

```bash
scripts/test.sh full local
```

When a task changes Docker behavior, app startup, environment variables, dependencies, or runtime wiring, also run:

```bash
scripts/test.sh full docker-dev
```

Before merge or release validation, prefer:

```bash
scripts/test.sh full docker-qa
```

Do not claim Docker compatibility unless the relevant Docker test target was executed successfully.

## Lint and formatting

Use the project lint command:

```bash
scripts/lint.sh
```

If formatting is required, use the documented formatter command from the repository, usually:

```bash
python -m ruff format src tests
python -m ruff check --fix src tests
```

Do not include broad formatting churn in unrelated tasks.

## Expected checks

For a normal code change, run:

```bash
scripts/test.sh full local
scripts/lint.sh
```

For a Docker-related change, run:

```bash
scripts/test.sh full local
scripts/test.sh full docker-dev
scripts/lint.sh
```

For release-like validation, run:

```bash
scripts/test.sh full local
scripts/test.sh full docker-qa
scripts/lint.sh
```

If a check cannot be run, state clearly which check was not run and why.

## Dependency rules

- Keep dependencies minimal.
- Prefer the Python standard library when practical.
- Add a dependency only when it is clearly justified.
- Update `requirements.in`, `requirements.txt`, and relevant documentation when dependencies change.
- Do not add development tools, frameworks, or libraries that are unrelated to the current task.
- Do not silently change the packaging approach.

## Secrets and configuration

Never commit:

- credentials
- passwords
- tokens
- private keys
- certificates
- real connection strings
- local `.env` files

Environment-file policy:

- Allowed to track: `.env.example`
- Must not be tracked: `.env`, `.env.*`, or any local secret-bearing file

Create local overrides by copying:

```bash
cp .env.example .env
```

Do not add real secrets to examples. Use placeholder values only.

## Documentation rules

When relevant, update:

- `README.md`
- `docs/dev-python.md`
- `docs/architecture.md`
- `docs/codex-workflow.md`
- `.github/CONTRIBUTING.md`
- `AGENTS.md`

Documentation must stay aligned with:

- repository structure
- local setup steps
- run commands
- test commands
- Docker commands
- CI behavior
- AI/Codex workflow expectations

If code behavior changes but the README or docs still describe the old behavior, the task is incomplete.

## Pull request expectations

Each PR should do one focused thing.

Good examples:

- add a Flask route
- add a service function
- add validation
- add tests
- improve documentation
- fix Docker test execution
- update CI
- improve VS Code settings

Avoid mixing unrelated changes in one PR.

Do not combine a feature change with broad formatting, renaming, dependency updates, and documentation rewrites unless explicitly requested.

## Preferred change style

Prefer:

- explicit code
- clear names
- small functions
- narrow scope
- direct control flow
- simple tests
- stable commands
- readable documentation

Avoid:

- speculative abstractions
- hidden magic
- over-engineering
- global rewrites
- unnecessary layers
- unrelated cleanup
- renaming or moving files without strong reason

## AI-assisted workflow

When using Codex, ChatGPT, or another AI coding tool:

- keep each task narrow and self-contained
- make one logical change at a time
- preserve existing structure unless instructed otherwise
- update docs together with code
- do not invent missing requirements
- do not create extra layers beyond the intended architecture
- do not silently change the testing framework
- do not silently change runtime assumptions
- run the documented checks before claiming completion

Good AI task:

```text
Add a /api/health endpoint that returns {"status": "ok"}.
Use unittest only.
Update tests.
Do not modify unrelated files.
Run scripts/test.sh full local.
```

Better AI task when Docker is relevant:

```text
Fix scripts/test.sh so tests can run locally and inside Docker.
Support local, docker-dev, and docker-qa targets.
Update README.md and AGENTS.md.
Run scripts/test.sh full local and scripts/test.sh full docker-dev.
Do not introduce pytest.
```

Bad AI task:

```text
Improve the project.
```

## Review checklist

Before submitting a change, verify:

- [ ] The diff is focused.
- [ ] The change matches the documented architecture.
- [ ] No unrelated files were edited.
- [ ] Tests were added or updated if behavior changed.
- [ ] `scripts/test.sh full local` passes.
- [ ] Docker tests were run if Docker/runtime behavior changed.
- [ ] `scripts/lint.sh` passes.
- [ ] Documentation was updated if setup, behavior, commands, or structure changed.
- [ ] No secrets or local environment files were committed.
- [ ] No unrelated formatting or cleanup was included.

## If unsure

If a requirement is unclear:

- do not invent behavior
- make the smallest safe change
- document assumptions explicitly
- prefer adding tests around confirmed behavior
- ask for clarification before broad changes
