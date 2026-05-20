from dataclasses import dataclass


@dataclass(frozen=True)
class SleepLog:
    id: int
    sleep_date: str
    start_time: str | None
    end_time: str | None
    duration_minutes: int | None
    sleep_quality: int | None
    notes: str | None
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class NewSleepLog:
    sleep_date: str
    start_time: str | None
    end_time: str | None
    duration_minutes: int | None
    sleep_quality: int | None
    notes: str | None
