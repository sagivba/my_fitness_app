# Codex workflow

This repository is designed to work well with Codex CLI and other AI coding agents.

## Recommended workflow

Use two worktrees:

- Dev worktree: AI/Codex performs implementation.
- QA worktree: human verifies and tests before merge.

## Branch naming

Use:

```text
codex-cli/<short-task-name>
```

## Task shape

Good task:

```text
Add a /health endpoint that returns {"status": "ok"}.
Update unittest coverage.
Do not modify unrelated files.
Run scripts/test.sh quick.
```

Bad task:

```text
Improve the project.
```

## Checks

Quick:

```bash
scripts/test.sh quick
```

Full:

```bash
scripts/test.sh full
```

Lint:

```bash
scripts/lint.sh
```

## Review checklist

- [ ] Diff is focused.
- [ ] Tests were added or updated.
- [ ] unittest passes.
- [ ] No unrelated formatting churn.
- [ ] Documentation updated if behavior changed.
