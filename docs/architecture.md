# Architecture

This project uses a simple layered structure.

## Layers

```text
routes -> services -> model
              |
            utils
```

## src/my_python_project_template/app.py

Creates and configures the Flask application.

## src/my_python_project_template/config.py

Loads configuration from environment variables.

## src/my_python_project_template/routes

HTTP boundary.

Route handlers should:

- parse inputs
- call services
- return responses

Route handlers should not contain business logic.

## src/my_python_project_template/services

Business logic.

Services should be easy to test with unittest.

## src/my_python_project_template/model

Domain models, data structures, and model-facing code.

## src/my_python_project_template/utils

Small generic utilities.

Do not put project-specific business rules here.
