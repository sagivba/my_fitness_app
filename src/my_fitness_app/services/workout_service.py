from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from my_fitness_app.model import workout_repository
from my_fitness_app.model.strength import StrengthExercise, StrengthSummary
from my_fitness_app.model.workout import NewWorkout, Workout
from my_fitness_app.services import strength_service


class WorkoutValidationError(ValueError):
    def __init__(self, errors: dict[str, str]):
        super().__init__("Invalid workout data")
        self.errors = errors


@dataclass(frozen=True)
class WorkoutDisplayMetrics:
    start_time: str
    source: str
    duration: str
    distance: str
    calories: str
    average_heart_rate: str
    max_heart_rate: str
    strength_summary: str
    has_strength: bool


@dataclass(frozen=True)
class WorkoutTableRow:
    workout: Workout
    metrics: WorkoutDisplayMetrics


@dataclass(frozen=True)
class WorkoutDetailView:
    workout: Workout
    metrics: WorkoutDisplayMetrics
    strength_exercises: list[StrengthExercise]
    strength_summary: StrengthSummary


def create_workout(database_path: str | Path, form_data: Mapping[str, str]) -> Workout:
    workout = _validate_workout(form_data)
    return workout_repository.create_workout(database_path, workout)


def list_workouts(database_path: str | Path) -> list[Workout]:
    return workout_repository.list_workouts(database_path)


def list_workout_table_rows(database_path: str | Path) -> list[WorkoutTableRow]:
    workouts = workout_repository.list_workouts(database_path)
    return [_build_workout_table_row(database_path, workout) for workout in workouts]


def get_workout(database_path: str | Path, workout_id: int) -> Workout | None:
    return workout_repository.get_workout(database_path, workout_id)


def get_workout_detail_view(
    database_path: str | Path,
    workout_id: int,
) -> WorkoutDetailView | None:
    workout = workout_repository.get_workout(database_path, workout_id)
    if workout is None:
        return None

    strength_exercises = strength_service.list_strength_exercises(database_path, workout.id)
    strength_summary = strength_service.summarize_strength_exercises(strength_exercises)
    return WorkoutDetailView(
        workout=workout,
        metrics=_display_metrics(workout, strength_summary),
        strength_exercises=strength_exercises,
        strength_summary=strength_summary,
    )


def _build_workout_table_row(
    database_path: str | Path,
    workout: Workout,
) -> WorkoutTableRow:
    strength_exercises = strength_service.list_strength_exercises(database_path, workout.id)
    strength_summary = strength_service.summarize_strength_exercises(strength_exercises)
    return WorkoutTableRow(
        workout=workout,
        metrics=_display_metrics(workout, strength_summary),
    )


def _display_metrics(workout: Workout, strength_summary: StrengthSummary) -> WorkoutDisplayMetrics:
    return WorkoutDisplayMetrics(
        start_time=_format_start_time(workout.start_time),
        source=_source_label(workout.source),
        duration=_format_duration(workout),
        distance=_format_distance(workout.distance_meters),
        calories=_format_optional_int(workout.calories),
        average_heart_rate=_format_optional_int(workout.average_heart_rate),
        max_heart_rate=_format_optional_int(workout.max_heart_rate),
        strength_summary=_format_strength_summary(strength_summary),
        has_strength=strength_summary.total_sets > 0,
    )


def _format_start_time(start_time: str | None) -> str:
    if not start_time:
        return "-"
    if "T" in start_time:
        return start_time.split("T", maxsplit=1)[1][:5]
    return start_time[:5]


def _source_label(source: str | None) -> str:
    source_labels = {
        "manual": "ידני",
        "garmin_csv": "Garmin CSV",
        "garmin_tcx": "Garmin TCX",
        "garmin_gpx": "Garmin GPX",
    }
    return source_labels.get(source or "", source or "-")


def _format_duration(workout: Workout) -> str:
    if workout.duration_seconds is not None:
        minutes = round(workout.duration_seconds / 60)
        return f"{minutes} דק׳ (מקובץ Garmin)"
    if workout.duration_minutes is not None:
        if workout.source == "manual":
            return f"{workout.duration_minutes} דק׳ (ידני)"
        return f"{workout.duration_minutes} דק׳ (מיובא)"
    return "-"


def _format_distance(distance_meters: float | None) -> str:
    if distance_meters is None:
        return "-"
    return f"{distance_meters / 1000:.2f} ק״מ"


def _format_optional_int(value: int | None) -> str:
    if value is None:
        return "-"
    return str(value)


def _format_strength_summary(strength_summary: StrengthSummary) -> str:
    if strength_summary.total_sets == 0:
        return "-"
    return (
        f"{strength_summary.total_exercises} תרגילים · "
        f"{strength_summary.total_sets} סטים · "
        f"{strength_summary.total_reps} חזרות · "
        f"{strength_summary.total_volume_kg:.2f} ק״ג"
    )


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
