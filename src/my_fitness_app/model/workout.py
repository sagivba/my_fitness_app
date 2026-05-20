from dataclasses import dataclass


@dataclass(frozen=True)
class Workout:
    id: int
    workout_date: str
    workout_type: str
    duration_minutes: int | None
    source: str
    notes: str | None
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class NewWorkout:
    workout_date: str
    workout_type: str
    duration_minutes: int | None
    notes: str | None
    source: str = "manual"
