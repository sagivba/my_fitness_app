from dataclasses import dataclass


@dataclass(frozen=True)
class StrengthSet:
    id: int
    strength_exercise_id: int
    set_number: int
    reps: int
    weight_kg: float | None
    perceived_effort: int | None
    notes: str | None
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class NewStrengthSet:
    strength_exercise_id: int
    set_number: int
    reps: int
    weight_kg: float | None
    perceived_effort: int | None
    notes: str | None


@dataclass(frozen=True)
class StrengthExercise:
    id: int
    workout_id: int
    exercise_name: str
    exercise_order: int
    notes: str | None
    created_at: str
    updated_at: str
    sets: tuple[StrengthSet, ...] = ()


@dataclass(frozen=True)
class NewStrengthExercise:
    workout_id: int
    exercise_name: str
    exercise_order: int
    notes: str | None


@dataclass(frozen=True)
class StrengthSummary:
    total_exercises: int
    total_sets: int
    total_reps: int
    total_volume_kg: float
