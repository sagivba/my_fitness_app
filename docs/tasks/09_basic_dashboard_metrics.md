# Task 09 - Add basic dashboard metrics

## Branch

```text
codex-cli/add-basic-dashboard-metrics
```

## Suggested Codex effort

Medium.

## Goal

Add a simple dashboard that summarizes collected data without advanced analytics.

## Scope

1. Add dashboard service functions for today and weekly summaries.
2. Display recent workouts, total workouts this week, total training minutes this week, workout type distribution, recent sleep duration, and recent meals.
3. Add simple empty states when data is missing.
4. Add links to add workout, add sleep log, add meal, and import file.
5. Keep calculations deterministic and service-tested.
6. Add route tests and service tests.

## Out of scope

1. Do not add correlation analytics.
2. Do not add charts that require heavy JavaScript dependencies.
3. Do not add medical advice or recommendations.
4. Do not add user accounts.

## Likely files to touch

- `src/my_fitness_app/routes/dashboard_routes.py`
- `src/my_fitness_app/services/dashboard_service.py`
- `templates/dashboard.html`
- `templates/base.html`
- `tests/`
- `README.md` if usage changes

## Validation

```bash
scripts/test.sh full local
scripts/lint.sh
```

## Acceptance criteria

- Dashboard renders with and without data.
- Weekly metrics are calculated correctly in tests.
- No advanced analytics or causal claims are shown.
- Tests and lint pass.


## Slash goal

```text
/goal
Add a simple dashboard that summarizes collected data without advanced analytics.

Use branch: codex-cli/add-basic-dashboard-metrics

Scope:
1. Add dashboard service functions for today and weekly summaries.
2. Display recent workouts, total workouts this week, total training minutes this week, workout type distribution, recent sleep duration, and recent meals.
3. Add simple empty states when data is missing.
4. Add links to add workout, add sleep log, add meal, and import file.
5. Keep calculations deterministic and service-tested.
6. Add route tests and service tests.

Out of scope:
1. Do not add correlation analytics.
2. Do not add charts that require heavy JavaScript dependencies.
3. Do not add medical advice or recommendations.
4. Do not add user accounts.

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
- Dashboard renders with and without data.
- Weekly metrics are calculated correctly in tests.
- No advanced analytics or causal claims are shown.
- Tests and lint pass.
```
