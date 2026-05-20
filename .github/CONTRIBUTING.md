# Contributing

## Purpose

This repository is an Personal fitness tracking application.

Keep it simple, readable, reviewable, and easy for both humans and AI agents to understand.

This template is designed for:

- Python 3.12+
- WSL-based local development
- VS Code
- unittest only
- small, focused changes
- minimal dependencies
- clear project structure
- optional Docker Compose support
- GitHub Actions CI
- Codex CLI and AI-assisted development workflows

## Working Principles

- Make minimal diffs.
- Prefer small, isolated changes that are easy to review.
- Do not perform broad refactors unless explicitly requested.
- Keep architecture simple.
- Do not introduce new abstractions unless they clearly reduce complexity.
- Keep consistency between code, tests, documentation, and automation scripts.
- Update documentation when behavior, setup, commands, or structure changes.
- Prefer explicit, boring, maintainable code over clever code.

## Architecture Expectations

Keep responsibilities separated:

- `src/<package_name>/app.py` is the application entry point and wiring layer.
- `src/<package_name>/config.py` contains configuration loading.
- `src/<package_name>/routes/` contains HTTP handlers only.
- `src/<package_name>/services/` contains application and business logic.
- `src/<package_name>/model/` contains domain models, data structures, and model-facing code.
- `src/<package_name>/utils/` contains small generic helpers only.
- `templates/` contains HTML templates.
- `static/` contains CSS, images, and static assets.
- `tests/` contains unittest-based test coverage.
- `docs/` contains project documentation.
- `scripts/` contains repeatable local commands.

Do not place business logic directly inside route handlers.

Do not add a database, background worker, frontend framework, queue, cache, or external service dependency unless explicitly requested.

Do not move files between layers unless the change is intentional and documented.

## Environment Rules

Primary local workflow:

- WSL
- VS Code connected to WSL
- dedicated Python environment using venv or Conda
- unittest discovery from CLI and VS Code

Docker Compose may be used as optional support.

Docker must not replace the main local development flow unless the project explicitly decides to make Docker the primary workflow.

## Testing Rules

- Use `unittest` only.
- Do not introduce `pytest`.
- Tests must run with:

```bash
PYTHONPATH=src python -m unittest discover -s tests -p "test_*.py" -v
```

The preferred project command is:

```bash
scripts/test.sh full
```

Add or update tests when changing behavior in:

- routes
- services
- validation
- configuration
- model/domain logic
- public APIs
- command scripts

Prefer deterministic tests.

Avoid:

- network calls
- real external services
- time-sensitive assertions
- tests that depend on execution order
- tests that require local secrets

## Dependency Rules

- Keep dependencies minimal.
- Add a dependency only when it is clearly justified.
- Prefer the Python standard library when practical.
- Do not add frameworks, libraries, or tools that are not required for the current task.
- Update `requirements.in`, `requirements.txt`, and relevant documentation when dependencies change.

## Secrets and Configuration

- Never commit secrets.
- Never commit credentials, tokens, passwords, certificates, or private keys.
- Keep environment-specific values out of source control.

Environment-file policy:

- Allowed to track: `.env.example` only.
- Must not be tracked: `.env`, `.env.*`, or any local secret-bearing file.
- Create local overrides by copying `.env.example` to `.env`.

Example:

```bash
cp .env.example .env
```

## CI Rules

Keep CI green.

Any code change should preserve the ability to run:

- application bootstrap
- unit tests
- lint checks
- GitHub Actions workflow

The expected checks are:

```bash
scripts/test.sh full
scripts/lint.sh
```

Do not merge changes that break the documented setup or test commands.

## Documentation Rules

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

## Pull Request Guidance

Each PR should aim to do one focused thing.

Good examples:

- bootstrap the repo structure
- add Flask app skeleton
- add a service function
- add an API endpoint
- add validation
- add tests
- improve documentation
- add CI
- add optional Docker support
- improve VS Code configuration

Avoid mixing unrelated changes in one PR.

Do not combine a feature change with broad formatting, renaming, or cleanup unless explicitly requested.

## Preferred Change Style

Prefer:

- explicit code
- clear names
- small functions
- narrow scope
- direct control flow
- simple tests
- stable commands

Avoid:

- speculative abstractions
- hidden magic
- over-engineering
- repo-wide cleanup unrelated to the task
- renaming or moving files without strong reason
- adding generic layers before they are needed

## For AI-assisted Contributions

If using Codex, ChatGPT, or another AI coding tool:

- keep each task narrow and self-contained
- make one logical change at a time
- preserve existing structure unless instructed otherwise
- update docs together with code
- do not invent missing requirements
- do not create extra layers beyond the intended architecture
- do not silently change testing framework, packaging approach, or runtime assumptions
- run the documented checks before claiming completion

Recommended branch prefix for Codex CLI work:

```text
codex-cli/<short-task-name>
```

Examples:

```text
codex-cli/add-health-endpoint
codex-cli/improve-config-loading
codex-cli/add-service-tests
```

## Review Checklist

Before submitting a change, verify:

- [ ] The diff is focused.
- [ ] The change matches the documented architecture.
- [ ] Tests were added or updated if behavior changed.
- [ ] `scripts/test.sh full` passes.
- [ ] `scripts/lint.sh` passes.
- [ ] Documentation was updated if setup, behavior, commands, or structure changed.
- [ ] No secrets or local environment files were committed.
- [ ] No unrelated formatting or cleanup was included.
