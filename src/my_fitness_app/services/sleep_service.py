from collections.abc import Mapping
from pathlib import Path

from my_fitness_app.model import sleep_repository
from my_fitness_app.model.sleep import NewSleepLog, SleepLog


class SleepValidationError(ValueError):
    def __init__(self, errors: dict[str, str]):
        super().__init__("Invalid sleep log data")
        self.errors = errors


def create_sleep_log(database_path: str | Path, form_data: Mapping[str, str]) -> SleepLog:
    sleep_log = _validate_sleep_log(form_data)
    return sleep_repository.create_sleep_log(database_path, sleep_log)


def list_sleep_logs(database_path: str | Path) -> list[SleepLog]:
    return sleep_repository.list_sleep_logs(database_path)


def get_sleep_log(database_path: str | Path, sleep_log_id: int) -> SleepLog | None:
    return sleep_repository.get_sleep_log(database_path, sleep_log_id)


def _validate_sleep_log(form_data: Mapping[str, str]) -> NewSleepLog:
    errors: dict[str, str] = {}

    sleep_date = form_data.get("sleep_date", "").strip()
    start_time = form_data.get("start_time", "").strip() or None
    end_time = form_data.get("end_time", "").strip() or None
    duration_minutes = _parse_optional_positive_int(
        form_data.get("duration_minutes", "").strip(),
        "duration_minutes",
        "משך השינה חייב להיות מספר שלם חיובי.",
        errors,
    )
    sleep_quality = _parse_optional_positive_int(
        form_data.get("sleep_quality", "").strip(),
        "sleep_quality",
        "איכות השינה חייבת להיות מספר שלם חיובי.",
        errors,
    )
    notes = form_data.get("notes", "").strip() or None

    if not sleep_date:
        errors["sleep_date"] = "חובה להזין תאריך שינה."

    if errors:
        raise SleepValidationError(errors)

    return NewSleepLog(
        sleep_date=sleep_date,
        start_time=start_time,
        end_time=end_time,
        duration_minutes=duration_minutes,
        sleep_quality=sleep_quality,
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
