from collections.abc import Mapping
from pathlib import Path

from my_fitness_app.model import daily_log_repository
from my_fitness_app.model.daily_log import DailyLog, NewDailyLog


class DailyLogValidationError(ValueError):
    def __init__(self, errors: dict[str, str]):
        super().__init__("Invalid daily log data")
        self.errors = errors


def create_daily_log(database_path: str | Path, form_data: Mapping[str, str]) -> DailyLog:
    daily_log = _validate_daily_log(form_data)
    return daily_log_repository.create_daily_log(database_path, daily_log)


def list_daily_logs(database_path: str | Path) -> list[DailyLog]:
    return daily_log_repository.list_daily_logs(database_path)


def get_daily_log(database_path: str | Path, daily_log_id: int) -> DailyLog | None:
    return daily_log_repository.get_daily_log(database_path, daily_log_id)


def _validate_daily_log(form_data: Mapping[str, str]) -> NewDailyLog:
    errors: dict[str, str] = {}

    log_date = form_data.get("log_date", "").strip()
    body_weight_kg = _parse_optional_positive_float(
        form_data.get("body_weight_kg", "").strip(),
        "body_weight_kg",
        "משקל חייב להיות מספר חיובי.",
        errors,
    )
    mood = form_data.get("mood", "").strip() or None
    energy_level = _parse_optional_positive_int(
        form_data.get("energy_level", "").strip(),
        "energy_level",
        "רמת אנרגיה חייבת להיות מספר שלם חיובי.",
        errors,
    )
    notes = form_data.get("notes", "").strip() or None

    if not log_date:
        errors["log_date"] = "חובה להזין תאריך."

    if errors:
        raise DailyLogValidationError(errors)

    return NewDailyLog(
        log_date=log_date,
        body_weight_kg=body_weight_kg,
        mood=mood,
        energy_level=energy_level,
        notes=notes,
    )


def _parse_optional_positive_float(
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

    if parsed_value <= 0:
        errors[field_name] = error_message
        return None

    return parsed_value


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
