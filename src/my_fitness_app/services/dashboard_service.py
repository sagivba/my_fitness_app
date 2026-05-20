from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from my_fitness_app.model import workout_repository
from my_fitness_app.model.workout import Workout


@dataclass(frozen=True)
class DashboardBreakdownItem:
    label: str
    count: int


@dataclass(frozen=True)
class WorkoutDashboardSummary:
    total_workouts: int
    total_duration_minutes: int
    total_distance_km: float
    total_calories: int
    average_heart_rate: int | None
    max_heart_rate: int | None
    recent_workouts: list[Workout]
    source_breakdown: list[DashboardBreakdownItem]
    workout_type_breakdown: list[DashboardBreakdownItem]


def get_workout_dashboard_summary(database_path: str | Path) -> WorkoutDashboardSummary:
    workouts = workout_repository.list_workouts(database_path)
    duration_seconds = sum(_duration_seconds(workout) for workout in workouts)
    distance_meters = sum(workout.distance_meters or 0 for workout in workouts)
    calories = sum(workout.calories or 0 for workout in workouts)
    average_heart_rates = [
        workout.average_heart_rate for workout in workouts if workout.average_heart_rate is not None
    ]
    max_heart_rates = [
        workout.max_heart_rate for workout in workouts if workout.max_heart_rate is not None
    ]

    return WorkoutDashboardSummary(
        total_workouts=len(workouts),
        total_duration_minutes=round(duration_seconds / 60),
        total_distance_km=round(distance_meters / 1000, 2),
        total_calories=calories,
        average_heart_rate=(
            round(sum(average_heart_rates) / len(average_heart_rates))
            if average_heart_rates
            else None
        ),
        max_heart_rate=max(max_heart_rates) if max_heart_rates else None,
        recent_workouts=workouts[:5],
        source_breakdown=_breakdown(workout.source for workout in workouts),
        workout_type_breakdown=_breakdown(workout.workout_type for workout in workouts),
    )


def _duration_seconds(workout: Workout) -> float:
    if workout.duration_seconds is not None:
        return workout.duration_seconds
    if workout.duration_minutes is not None:
        return workout.duration_minutes * 60
    return 0


def _breakdown(values: Iterable[str | None]) -> list[DashboardBreakdownItem]:
    counts: dict[str, int] = {}
    for value in values:
        label = str(value) if value else "לא ידוע"
        counts[label] = counts.get(label, 0) + 1

    return [
        DashboardBreakdownItem(label=label, count=count)
        for label, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    ]
