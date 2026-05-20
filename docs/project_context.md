# Project context for Codex

## Product

Build a personal fitness data collection web application for a single user.

The application should collect, normalize, and display data about:

- workouts
- Garmin imports from a Garmin Vivoactive watch
- strength training details
- sleep
- meals
- meal photos and AI-based nutrition estimates in a later stage
- daily subjective metrics
- future medical metrics
- future correlation analytics

## MVP principle

The first objective is reliable data collection, not advanced analytics.

Do not implement correlation analysis until enough structured data exists.

## Initial deployment model

The application is local-first:

- Flask web application
- runs locally in the browser
- no public deployment in MVP
- no login system in MVP
- SQLite local database in MVP
- raw imported files stored locally under an instance/upload directory

## Workouts to support

Priority workout types:

- outdoor strength workout
- gym workout with aerobic and strength parts
- elliptical
- walking
- cycling

Typical workout duration: 30 to 60 minutes.

## Nutrition direction

Start with manual meal logging.

Later, add meal photo upload and OpenAI API analysis:

- image of plate
- user description
- optional recipe URL
- estimated calories and macros
- user can edit the estimate
- raw AI response is saved for audit
- no medical advice

## Garmin direction

Start with manual file imports.

Support raw file storage first, then parsing:

- CSV first
- TCX and GPX next with standard library XML parsing
- FIT later only if a dependency is explicitly justified

Do not attempt Garmin Connect API integration in MVP.

## Medical metrics

Medical metrics are future module scope only unless the specific task asks to implement them.

Possible future metrics:

- blood pressure
- glucose
- weight
- body measurements
- medication notes

## Technology constraints

- Python 3.12+
- Flask
- `unittest` only
- no pytest
- minimal dependencies
- simple server-rendered HTML
- RTL/Hebrew UI can be introduced incrementally
- no frontend framework in MVP
- no background worker in MVP
- no external service calls in tests

## Architecture constraints

Keep this structure:

```text
src/my_fitness_app/
  app.py
  config.py
  routes/
  services/
  model/
  utils/
templates/
static/
tests/
docs/
scripts/
```

Do not put business logic in route handlers.
