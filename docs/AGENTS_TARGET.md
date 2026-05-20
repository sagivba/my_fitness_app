# AGENTS.md - AI development instructions

This repository contains a personal Flask-based fitness tracking application.

The application is local-first and is designed to collect structured data about workouts, Garmin activity imports, sleep, meals, and future analytics.

These instructions apply to Codex CLI, ChatGPT, and any AI-assisted development workflow.

## Core rules

- Keep changes small and reviewable.
- Make one logical change at a time.
- Do not reorganize the repository unless the task explicitly asks for it.
- Do not edit unrelated files.
- Do not perform broad refactors unless explicitly requested.
- Preserve the existing architecture unless the task explicitly asks to change it.
- Prefer explicit, direct, maintainable code over clever code.
- Do not introduce speculative abstractions.
- Do not add dependencies unless they are necessary, documented, and covered by tests.
- Do not change public behavior without adding or updating tests.
- Update documentation when setup, commands, behavior, architecture, or workflow changes.
- Run the documented checks before claiming the task is complete.

## Technology assumptions

- Python 3.12+
- Flask
- WSL-based local development
- VS Code connected to WSL
- `unittest` only
- optional Docker Compose support
- GitHub Actions CI
- small, focused pull requests
- Codex CLI friendly branch and worktree workflows

Do not introduce `pytest`, a frontend framework, a background worker, a queue, a cache, or a public deployment model unless explicitly requested.

A database is allowed only in tasks that explicitly introduce persistence. The default MVP database is SQLite.

## Branch naming

For Codex CLI or AI-assisted implementation work, use this branch prefix:

```text
codex-cli/
```

Examples:

```text
codex-cli/initialize-fitness-app-foundation
codex-cli/add-sqlite-persistence
codex-cli/add-workout-crud
codex-cli/add-garmin-csv-import
```

Use concise, descriptive branch names. Avoid vague names such as:

```text
codex-cli/fixes
codex-cli/improvements
codex-cli/update
```

## Architecture boundaries

Keep responsibilities separated:

- `src/my_fitness_app/app.py`: application factory and wiring.
- `src/my_fitness_app/config.py`: configuration loading.
- `src/my_fitness_app/routes/`: request/response boundary only.
- `src/my_fitness_app/services/`: application and business logic.
- `src/my_fitness_app/model/`: domain models, persistence-facing code, and data structures.
- `src/my_fitness_app/utils/`: small generic helpers only.
- `templates/`: HTML templates.
- `static/`: CSS, images, and static assets.
- `tests/`: `unittest`-based test coverage.
- `docs/`: project documentation.
- `scripts/`: repeatable local automation commands.

Do not put business logic directly inside route handlers.

Route handlers should:

- parse request inputs
- call services
- return responses or render templates

Services should:

- contain business/application logic
- be easy to test with `unittest`
- avoid Flask-specific request objects unless strictly necessary

Models should:

- represent domain data or persistence-facing structures
- avoid HTTP concerns

Utilities should:

- remain generic
- not become a dumping ground for business rules

## Product-specific rules

### Garmin imports

- Do not integrate with Garmin Connect APIs unless a task explicitly asks for it.
- Start with manual file imports.
- Preserve raw imported files.
- Store file metadata and hashes.
- Keep imports as idempotent as practical.
- Detect likely duplicate activities before creating duplicate workouts.
- Prefer CSV, TCX, and GPX support before adding FIT parsing dependencies.

### Meals and AI nutrition estimates

- Manual meal logging comes before AI analysis.
- AI-generated nutrition values are estimates only.
- Users must be able to correct AI-generated values.
- Save raw AI responses for audit when AI analysis exists.
- Tests must not call the real OpenAI API.
- Use fake clients or mocks for OpenAI-related tests.
- Never commit API keys or real secrets.
- Do not present AI nutrition estimates as medical advice.

### Medical metrics

- Medical metrics are future module scope unless a task explicitly asks to implement them.
- Do not add diagnosis, treatment recommendations, or medical advice.
- Store user-provided measurements as data only.

### Analytics

- Correlation analytics are future scope.
- Do not infer causal claims.
- Use cautious wording such as correlation, association, trend, and possible relationship.
- Analytics should be based on structured data already stored by previous stages.

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
- persistence
- import/parsing logic
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

If code behavior changes but the README or docs still describe old behavior, the task is incomplete.

## Pull request expectations

Each PR should do one focused thing.

Good examples:

- initialize the project from the template
- add SQLite persistence
- add workout CRUD
- add a Garmin CSV importer
- add meal logging
- add tests
- improve documentation
- fix Docker test execution
- update CI

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
