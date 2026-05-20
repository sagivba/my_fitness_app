from dataclasses import dataclass


@dataclass(frozen=True)
class DailyLog:
    id: int
    log_date: str
    body_weight_kg: float | None
    mood: str | None
    energy_level: int | None
    notes: str | None
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class NewDailyLog:
    log_date: str
    body_weight_kg: float | None
    mood: str | None
    energy_level: int | None
    notes: str | None
