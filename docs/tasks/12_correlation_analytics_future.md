# Task 12 - Add cautious correlation analytics

## Branch

```text
codex-cli/add-correlation-analytics
```

## Suggested Codex effort

High. Requires careful wording, deterministic calculations, and enough data.

## Goal

Add basic correlation-style analytics between workouts, sleep, meals, and daily subjective metrics after data collection features exist.

## Scope

1. Add analytics services that operate on already-stored structured data.
2. Start with simple aggregates and associations, not causal inference.
3. Candidate analyses: workout duration vs sleep duration, workout type vs sleep quality, late meals vs sleep quality, weekly training minutes vs fatigue, sleep duration vs next-day energy.
4. Add minimum data thresholds before showing an insight.
5. Use cautious wording in the UI.
6. Add tests for calculations and empty/insufficient-data cases.
7. Add documentation explaining limitations.

## Out of scope

1. Do not claim causality.
2. Do not provide medical advice.
3. Do not use external analytics services.
4. Do not add machine learning unless a separate task explicitly asks for it.
5. Do not show insights when data is insufficient.

## Likely files to touch

- `src/my_fitness_app/services/analytics_service.py`
- `src/my_fitness_app/routes/analytics_routes.py`
- `templates/analytics/*.html`
- `tests/`
- `docs/analytics.md`

## Validation

```bash
scripts/test.sh full local
scripts/lint.sh
```

## Acceptance criteria

- Analytics page handles no data, insufficient data, and enough data.
- Calculations are deterministic and tested.
- UI uses cautious non-causal wording.
- Tests and lint pass.


## Slash goal

```text
/goal
Add basic correlation-style analytics between workouts, sleep, meals, and daily subjective metrics after data collection features exist.

Use branch: codex-cli/add-correlation-analytics

Scope:
1. Add analytics services that operate on already-stored structured data.
2. Start with simple aggregates and associations, not causal inference.
3. Candidate analyses: workout duration vs sleep duration, workout type vs sleep quality, late meals vs sleep quality, weekly training minutes vs fatigue, sleep duration vs next-day energy.
4. Add minimum data thresholds before showing an insight.
5. Use cautious wording in the UI.
6. Add tests for calculations and empty/insufficient-data cases.
7. Add documentation explaining limitations.

Out of scope:
1. Do not claim causality.
2. Do not provide medical advice.
3. Do not use external analytics services.
4. Do not add machine learning unless a separate task explicitly asks for it.
5. Do not show insights when data is insufficient.

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
- Analytics page handles no data, insufficient data, and enough data.
- Calculations are deterministic and tested.
- UI uses cautious non-causal wording.
- Tests and lint pass.
```
