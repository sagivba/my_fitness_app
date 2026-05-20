# Architecture

This project uses a simple layered structure.

## Layers

```text
routes -> services -> model
              |
            utils
```

## src/my_fitness_app/app.py

Creates and configures the Flask application.

## src/my_fitness_app/config.py

Loads configuration from environment variables.

## src/my_fitness_app/routes

HTTP boundary.

Route handlers should:

- parse inputs
- call services
- return responses

Route handlers should not contain business logic.

## src/my_fitness_app/services

Business logic.

Services should be easy to test with unittest.

## src/my_fitness_app/model

Domain models, data structures, and model-facing code.

## src/my_fitness_app/utils

Small generic utilities.

Do not put project-specific business rules here.
