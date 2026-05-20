# Task 11 - Add future medical metrics module

## Branch

```text
codex-cli/add-medical-metrics-module
```

## Suggested Codex effort

Medium to high. Keep the module data-oriented and avoid medical advice.

## Goal

Add a simple data-only module for manually recording medical metrics such as blood pressure, glucose, weight, and body measurements.

## Scope

1. Add `medical_metric` persistence if not already present.
2. Support metric date/time, metric type, value fields, unit, source, and notes.
3. Add CRUD screens for medical metrics.
4. Add validation by metric type where simple and safe.
5. Add clear UI copy that these are user-recorded data points, not medical interpretation.
6. Add tests for service validation and route behavior.
7. Document the module and its limitations.

## Out of scope

1. Do not provide medical advice.
2. Do not infer diagnoses.
3. Do not recommend treatments or medication changes.
4. Do not add integrations with medical devices in this task.
5. Do not add analytics unless explicitly requested.

## Likely files to touch

- `src/my_fitness_app/routes/medical_routes.py`
- `src/my_fitness_app/services/medical_metric_service.py`
- `src/my_fitness_app/model/medical_metric.py`
- `templates/medical/*.html`
- `tests/`
- `docs/medical-metrics.md`

## Validation

```bash
scripts/test.sh full local
scripts/lint.sh
```

## Acceptance criteria

- User can record and view medical metrics manually.
- The module avoids medical interpretation.
- Tests and lint pass.


## Slash goal

```text
/goal
Add a simple data-only module for manually recording medical metrics such as blood pressure, glucose, weight, and body measurements.

Use branch: codex-cli/add-medical-metrics-module

Scope:
1. Add `medical_metric` persistence if not already present.
2. Support metric date/time, metric type, value fields, unit, source, and notes.
3. Add CRUD screens for medical metrics.
4. Add validation by metric type where simple and safe.
5. Add clear UI copy that these are user-recorded data points, not medical interpretation.
6. Add tests for service validation and route behavior.
7. Document the module and its limitations.

Out of scope:
1. Do not provide medical advice.
2. Do not infer diagnoses.
3. Do not recommend treatments or medication changes.
4. Do not add integrations with medical devices in this task.
5. Do not add analytics unless explicitly requested.

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
- User can record and view medical metrics manually.
- The module avoids medical interpretation.
- Tests and lint pass.
```
