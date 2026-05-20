# Task 10 - Add OpenAI meal photo analysis

## Branch

```text
codex-cli/add-openai-meal-photo-analysis
```

## Suggested Codex effort

High. External API integration, secrets, file handling, and tests require care.

## Goal

Add optional AI-based meal photo analysis using OpenAI API while keeping all tests offline and deterministic.

## Scope

1. Add configuration for `OPENAI_API_KEY` through environment variables only.
2. Update `.env.example` with placeholder values only.
3. Add meal image upload if not already implemented.
4. Add a `food_ai_service` that accepts meal image information and optional user description.
5. Use an injectable client boundary so tests can use a fake client and never call the real API.
6. Store structured AI estimate fields on the meal record: calories, protein, carbs, fat, fiber, confidence, assumptions, warnings, and raw response JSON.
7. Allow the user to review and edit the AI estimate before or after saving.
8. Add tests for fake-client success, fake-client failure, malformed AI response, and user correction flow.
9. Document privacy, API key setup, and the fact that estimates are approximate and not medical advice.

## Out of scope

1. Do not make real OpenAI API calls in tests.
2. Do not commit API keys.
3. Do not add medical or dietary recommendations.
4. Do not add background jobs.
5. Do not integrate with recipe site scraping unless a separate task asks for it.

## Likely files to touch

- `src/my_fitness_app/services/food_ai_service.py`
- `src/my_fitness_app/services/meal_service.py`
- `src/my_fitness_app/routes/meal_routes.py`
- `src/my_fitness_app/model/meal.py`
- `templates/meals/*.html`
- `.env.example`
- `requirements.in`
- `requirements.txt`
- `tests/`
- `docs/meal-ai.md`

## Validation

```bash
scripts/test.sh full local
scripts/lint.sh
```

If dependencies or Docker runtime changed, also run:

```bash
scripts/test.sh full docker-dev
```

## Acceptance criteria

- Meal photo analysis can be triggered with a configured API key in development.
- Tests use fake clients only.
- AI estimates are editable.
- Raw AI response can be stored for audit.
- Docs explain setup and limitations.
- Tests and lint pass.


## Slash goal

```text
/goal
Add optional AI-based meal photo analysis using OpenAI API while keeping all tests offline and deterministic.

Use branch: codex-cli/add-openai-meal-photo-analysis

Scope:
1. Add configuration for `OPENAI_API_KEY` through environment variables only.
2. Update `.env.example` with placeholder values only.
3. Add meal image upload if not already implemented.
4. Add a `food_ai_service` that accepts meal image information and optional user description.
5. Use an injectable client boundary so tests can use a fake client and never call the real API.
6. Store structured AI estimate fields on the meal record: calories, protein, carbs, fat, fiber, confidence, assumptions, warnings, and raw response JSON.
7. Allow the user to review and edit the AI estimate before or after saving.
8. Add tests for fake-client success, fake-client failure, malformed AI response, and user correction flow.
9. Document privacy, API key setup, and the fact that estimates are approximate and not medical advice.

Out of scope:
1. Do not make real OpenAI API calls in tests.
2. Do not commit API keys.
3. Do not add medical or dietary recommendations.
4. Do not add background jobs.
5. Do not integrate with recipe site scraping unless a separate task asks for it.

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

If dependencies or Docker runtime changed, also run:

```bash
scripts/test.sh full docker-dev
```

Acceptance criteria:
- Meal photo analysis can be triggered with a configured API key in development.
- Tests use fake clients only.
- AI estimates are editable.
- Raw AI response can be stored for audit.
- Docs explain setup and limitations.
- Tests and lint pass.
```
