from collections.abc import Mapping
from pathlib import Path

from my_fitness_app.model import workout_repository
from my_fitness_app.model.workout import NewWorkout, Workout


class WorkoutValidationError(ValueError):
    def __init__(self, errors: dict[str, str]):
        super().__init__("Invalid workout data")
        self.errors = errors


def create_workout(database_path: str | Path, form_data: Mapping[str, str]) -> Workout:
    workout = _validate_workout(form_data)
    return workout_repository.create_workout(database_path, workout)


def list_workouts(database_path: str | Path) -> list[Workout]:
    return workout_repository.list_workouts(database_path)


def get_workout(database_path: str | Path, workout_id: int) -> Workout | None:
    return workout_repository.get_workout(database_path, workout_id)


def _validate_workout(form_data: Mapping[str, str]) -> NewWorkout:
    errors: dict[str, str] = {}

    workout_date = form_data.get("workout_date", "").strip()
    workout_type = form_data.get("workout_type", "").strip()
    duration_minutes = _parse_optional_positive_int(
        form_data.get("duration_minutes", "").strip(),
        "duration_minutes",
        "משך האימון חייב להיות מספר שלם חיובי.",
        errors,
    )
    notes = form_data.get("notes", "").strip() or None

    if not workout_date:
        errors["workout_date"] = "חובה להזין תאריך אימון."
    if not workout_type:
        errors["workout_type"] = "חובה להזין סוג אימון."

    if errors:
        raise WorkoutValidationError(errors)

    return NewWorkout(
        workout_date=workout_date,
        workout_type=workout_type,
        duration_minutes=duration_minutes,
        notes=notes,
    )


def _parse_optional_positive_int(
    value: str,
    field_name: str,
    error_message: str,
    errors: dict[str, str],
) -> int | None:
    if not value:
        return None

    try:
        parsed_value = int(value)
    except ValueError:
        errors[field_name] = error_message
        return None

    if parsed_value <= 0:
        errors[field_name] = error_message
        return None

    return parsed_value
