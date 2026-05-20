# Task 05 - Add manual meal logging without AI

## Branch

```text
codex-cli/add-manual-meal-logging
```

## Suggested Codex effort

Medium.

## Goal

Add manual meal logging as the foundation for future AI meal photo analysis.

## Scope

1. Add meal CRUD using existing persistence.
2. Support meal date, meal time, meal type, description, recipe URL, estimated calories, protein, carbs, fat, fiber, and notes.
3. Add optional image path field only if upload storage already exists; otherwise leave image upload for a later task.
4. Add validation for numeric macro fields.
5. Add list/detail/create/edit templates.
6. Add tests for meal service validation and route flows.
7. Document that AI nutrition analysis is future scope.

## Out of scope

1. Do not call OpenAI API.
2. Do not implement image upload unless raw upload infrastructure already exists.
3. Do not add food database integrations.
4. Do not add medical or dietary advice.

## Likely files to touch

- `src/my_fitness_app/routes/meal_routes.py`
- `src/my_fitness_app/services/meal_service.py`
- `src/my_fitness_app/model/meal.py`
- `templates/meals/*.html`
- `tests/`
- `README.md` or docs as needed

## Validation

```bash
scripts/test.sh full local
scripts/lint.sh
```

## Acceptance criteria

- A user can manually log meals and estimated nutrition values.
- Recipe URL is optional.
- AI fields are not required yet.
- Tests and lint pass.


## Slash goal

```text
/goal
Add manual meal logging as the foundation for future AI meal photo analysis.

Use branch: codex-cli/add-manual-meal-logging

Scope:
1. Add meal CRUD using existing persistence.
2. Support meal date, meal time, meal type, description, recipe URL, estimated calories, protein, carbs, fat, fiber, and notes.
3. Add optional image path field only if upload storage already exists; otherwise leave image upload for a later task.
4. Add validation for numeric macro fields.
5. Add list/detail/create/edit templates.
6. Add tests for meal service validation and route flows.
7. Document that AI nutrition analysis is future scope.

Out of scope:
1. Do not call OpenAI API.
2. Do not implement image upload unless raw upload infrastructure already exists.
3. Do not add food database integrations.
4. Do not add medical or dietary advice.

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
- A user can manually log meals and estimated nutrition values.
- Recipe URL is optional.
- AI fields are not required yet.
- Tests and lint pass.
```
