# Task 03 - Add strength training details

## Branch

```text
codex-cli/add-strength-training-details
```

## Suggested Codex effort

Medium to high. Keep UI simple and avoid over-modeling.

## Goal

Add optional strength exercise details for workouts that include strength training.

## Scope

1. Add a `strength_exercise` table or equivalent persistence structure linked to workouts.
2. Support exercise name, muscle group, set count, reps, weight kg, rest seconds, RPE, pain/discomfort flag, and notes.
3. Allow adding strength exercises to a workout detail page.
4. Allow editing and deleting strength exercise rows.
5. Keep route handlers thin and service-driven.
6. Add tests for service validation and route behavior.
7. Update docs to explain the workout-to-strength-exercise relationship.

## Out of scope

1. Do not add exercise library/catalog management.
2. Do not add charts.
3. Do not add advanced progressive overload analysis.
4. Do not add AI recommendations.

## Likely files to touch

- `src/my_fitness_app/model/strength_exercise.py`
- `src/my_fitness_app/services/strength_service.py`
- `src/my_fitness_app/routes/workout_routes.py` or dedicated strength routes
- `templates/workouts/*.html`
- `tests/`
- `docs/architecture.md`

## Validation

```bash
scripts/test.sh full local
scripts/lint.sh
```

## Acceptance criteria

- Strength details are optional per workout.
- Strength entries are linked to a workout.
- Invalid strength data is rejected or shown with validation errors.
- Tests and lint pass.


## Slash goal

```text
/goal
Add optional strength exercise details for workouts that include strength training.

Use branch: codex-cli/add-strength-training-details

Scope:
1. Add a `strength_exercise` table or equivalent persistence structure linked to workouts.
2. Support exercise name, muscle group, set count, reps, weight kg, rest seconds, RPE, pain/discomfort flag, and notes.
3. Allow adding strength exercises to a workout detail page.
4. Allow editing and deleting strength exercise rows.
5. Keep route handlers thin and service-driven.
6. Add tests for service validation and route behavior.
7. Update docs to explain the workout-to-strength-exercise relationship.

Out of scope:
1. Do not add exercise library/catalog management.
2. Do not add charts.
3. Do not add advanced progressive overload analysis.
4. Do not add AI recommendations.

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
- Strength details are optional per workout.
- Strength entries are linked to a workout.
- Invalid strength data is rejected or shown with validation errors.
- Tests and lint pass.
```
