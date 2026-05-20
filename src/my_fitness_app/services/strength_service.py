from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from my_fitness_app.model import strength_repository, workout_repository
from my_fitness_app.model.strength import (
    NewStrengthExercise,
    NewStrengthSet,
    StrengthExercise,
    StrengthSet,
    StrengthSummary,
)


class StrengthValidationError(ValueError):
    def __init__(self, errors: dict[str, str]):
        super().__init__("Invalid strength training data")
        self.errors = errors


class StrengthWorkoutNotFoundError(LookupError):
    pass


@dataclass(frozen=True)
class _ValidatedStrengthSet:
    exercise_name: str
    reps: int
    weight_kg: float | None
    perceived_effort: int | None
    notes: str | None


def list_strength_exercises(
    database_path: str | Path,
    workout_id: int,
) -> list[StrengthExercise]:
    return strength_repository.list_exercises_for_workout(database_path, workout_id)


def summarize_strength_exercises(exercises: list[StrengthExercise]) -> StrengthSummary:
    total_sets = 0
    total_reps = 0
    total_volume_kg = 0.0

    for exercise in exercises:
        for strength_set in exercise.sets:
            total_sets += 1
            total_reps += strength_set.reps
            if strength_set.weight_kg is not None:
                total_volume_kg += strength_set.reps * strength_set.weight_kg

    return StrengthSummary(
        total_exercises=len(exercises),
        total_sets=total_sets,
        total_reps=total_reps,
        total_volume_kg=total_volume_kg,
    )


def add_strength_set(
    database_path: str | Path,
    workout_id: int,
    form_data: Mapping[str, str],
) -> StrengthSet:
    if workout_repository.get_workout(database_path, workout_id) is None:
        raise StrengthWorkoutNotFoundError

    validated_set = _validate_strength_set_form(form_data)
    exercise = _find_or_create_exercise(
        database_path,
        workout_id,
        validated_set.exercise_name,
    )
    set_number = strength_repository.next_set_number(database_path, exercise.id)
    return strength_repository.create_set(
        database_path,
        NewStrengthSet(
            strength_exercise_id=exercise.id,
            set_number=set_number,
            reps=validated_set.reps,
            weight_kg=validated_set.weight_kg,
            perceived_effort=validated_set.perceived_effort,
            notes=validated_set.notes,
        ),
    )


def _find_or_create_exercise(
    database_path: str | Path,
    workout_id: int,
    exercise_name: str,
) -> StrengthExercise:
    normalized_name = _normalize_exercise_name(exercise_name)
    for exercise in strength_repository.list_exercises_for_workout(database_path, workout_id):
        if _normalize_exercise_name(exercise.exercise_name) == normalized_name:
            return exercise

    exercise_order = strength_repository.next_exercise_order(database_path, workout_id)
    return strength_repository.create_exercise(
        database_path,
        NewStrengthExercise(
            workout_id=workout_id,
            exercise_name=exercise_name,
            exercise_order=exercise_order,
            notes=None,
        ),
    )


def _normalize_exercise_name(value: str) -> str:
    return " ".join(value.casefold().split())


def _validate_strength_set_form(form_data: Mapping[str, str]) -> _ValidatedStrengthSet:
    errors: dict[str, str] = {}
    exercise_name = form_data.get("exercise_name", "").strip()
    reps = _parse_positive_int(
        form_data.get("reps", "").strip(),
        "reps",
        "חובה להזין מספר חזרות חיובי.",
        errors,
    )
    weight_kg = _parse_optional_non_negative_float(
        form_data.get("weight_kg", "").strip(),
        "weight_kg",
        "משקל חייב להיות מספר לא שלילי.",
        errors,
    )
    perceived_effort = _parse_optional_effort(
        form_data.get("perceived_effort", "").strip(),
        errors,
    )
    notes = form_data.get("notes", "").strip() or None

    if not exercise_name:
        errors["exercise_name"] = "חובה להזין שם תרגיל."

    if errors:
        raise StrengthValidationError(errors)

    return _ValidatedStrengthSet(
        exercise_name=exercise_name,
        reps=reps,
        weight_kg=weight_kg,
        perceived_effort=perceived_effort,
        notes=notes,
    )


def _parse_positive_int(
    value: str,
    field_name: str,
    error_message: str,
    errors: dict[str, str],
) -> int:
    try:
        parsed_value = int(value)
    except ValueError:
        errors[field_name] = error_message
        return 0

    if parsed_value <= 0:
        errors[field_name] = error_message
        return 0

    return parsed_value


def _parse_optional_non_negative_float(
    value: str,
    field_name: str,
    error_message: str,
    errors: dict[str, str],
) -> float | None:
    if not value:
        return None

    try:
        parsed_value = float(value)
    except ValueError:
        errors[field_name] = error_message
        return None

    if parsed_value < 0:
        errors[field_name] = error_message
        return None

    return parsed_value


def _parse_optional_effort(value: str, errors: dict[str, str]) -> int | None:
    if not value:
        return None

    try:
        parsed_value = int(value)
    except ValueError:
        errors["perceived_effort"] = "מאמץ נתפס חייב להיות מספר שלם בין 1 ל-10."
        return None

    if parsed_value < 1 or parsed_value > 10:
        errors["perceived_effort"] = "מאמץ נתפס חייב להיות מספר שלם בין 1 ל-10."
        return None

    return parsed_value
