# Codex Git Workflow Rules

Use this reference for Codex tasks in this repository when planning or executing code changes.

## Default Git permissions

Codex may run the following commands without additional approval:

```bash
git fetch
git status --short | cat
git branch --show-current | cat
git log --oneline --decorate -5 | cat
git diff --stat | cat
git diff | cat
```

Use `git fetch` before starting repository work when the task depends on the latest remote state.

## Branch rules

- Do not work directly on `main` for implementation tasks unless the user explicitly instructs otherwise.
- Use task branches for Codex work.
- Task branch names must start with:

```text
codex-cli/...
```

- Prefer descriptive branch names, for example:

```text
codex-cli/cp07-garmin-csv-import
codex-cli/update-local-skill-git-workflow
```

## Commands requiring explicit user approval

Codex must not run any of the following unless the user explicitly instructs it:

```bash
git merge
git rebase
git reset --hard
git push
git push --force
git branch --delete
git branch -D
git push origin --delete
```

Also do not modify remote branches, delete branches, rewrite history, merge pull requests, or open pull requests unless explicitly instructed by the user.

## Commit rules

- Do not commit changes unless the user explicitly asks for a commit.
- If the user asks for a commit, inspect the diff first and summarize what will be committed.
- Do not include secrets, `.env` files, local database files, uploaded files, `instance/` data, cache files, or generated local artifacts in commits.

## Start-of-task repository inspection

Before changing files, inspect repository state with:

```bash
git fetch
git status --short | cat
git branch --show-current | cat
git log --oneline --decorate -5 | cat
```

If the working tree is dirty before the task starts, stop and report the existing changes before modifying files, unless the user already gave instructions for how to handle them.

## End-of-task report

At the end of each Codex task, report:

- current branch name
- changed files
- whether a commit was created
- validation commands run
- validation results
- any skipped validation and the reason
- any follow-up risks or decisions needed

## Safety boundaries

- Keep repository work scoped to the requested task.
- Do not edit unrelated files.
- Do not perform cleanup, formatting, refactoring, or dependency changes unless they are required for the task.
- Do not add dependencies without a clear task-level reason.
- Do not change CI, deployment, or release workflows unless explicitly requested.
