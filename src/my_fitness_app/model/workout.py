from dataclasses import dataclass


@dataclass(frozen=True)
class Workout:
    id: int
    workout_date: str
    workout_type: str
    duration_minutes: int | None
    source: str
    start_time: str | None
    end_time: str | None
    duration_seconds: float | None
    distance_meters: float | None
    calories: int | None
    average_heart_rate: int | None
    max_heart_rate: int | None
    elevation_gain_meters: float | None
    elevation_loss_meters: float | None
    external_activity_id: str | None
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
    start_time: str | None = None
    end_time: str | None = None
    duration_seconds: float | None = None
    distance_meters: float | None = None
    calories: int | None = None
    average_heart_rate: int | None = None
    max_heart_rate: int | None = None
    elevation_gain_meters: float | None = None
    elevation_loss_meters: float | None = None
    external_activity_id: str | None = None
