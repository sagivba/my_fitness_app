import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from my_fitness_app.model import imported_file_repository, workout_repository
from my_fitness_app.model.imported_file import ImportedFile
from my_fitness_app.model.workout import NewWorkout

IMPORT_STATUS_NOT_IMPORTED = "not_imported"
IMPORT_STATUS_IMPORTED = "imported"
IMPORT_STATUS_PARTIAL_FAILURE = "partial_failure"
IMPORT_STATUS_FAILED = "failed"

CANONICAL_HEADER_ALIASES = {
    "activity date": "workout_date",
    "activity_date": "workout_date",
    "date": "workout_date",
    "start time": "start_time",
    "start_time": "start_time",
    "time": "start_time",
    "activity type": "workout_type",
    "activity_type": "workout_type",
    "type": "workout_type",
    "duration minutes": "duration_minutes",
    "duration_minutes": "duration_minutes",
    "duration": "duration_minutes",
    "notes": "notes",
}
REQUIRED_CANONICAL_HEADERS = {
    "workout_date",
    "start_time",
    "workout_type",
    "duration_minutes",
}


class GarminCsvImportError(ValueError):
    pass


@dataclass(frozen=True)
class GarminCsvWorkoutRow:
    row_number: int
    workout_date: str
    start_time: str
    workout_type: str
    duration_minutes: int
    notes: str | None


@dataclass(frozen=True)
class GarminCsvParseResult:
    rows_read: int
    workout_rows: list[GarminCsvWorkoutRow]
    errors: list[str]


@dataclass(frozen=True)
class GarminCsvImportResult:
    imported_file: ImportedFile
    rows_read: int
    workouts_created: int
    duplicate_rows_skipped: int
    malformed_rows: int
    errors: list[str]
    import_status: str


def map_garmin_csv_headers(headers: list[str] | None) -> dict[str, str]:
    if not headers:
        raise GarminCsvImportError("CSV file must include a header row.")

    mapped_headers: dict[str, str] = {}
    for header in headers:
        normalized_header = _normalize_header(header)
        canonical_header = CANONICAL_HEADER_ALIASES.get(normalized_header)
        if canonical_header and canonical_header not in mapped_headers:
            mapped_headers[canonical_header] = header

    missing_headers = sorted(REQUIRED_CANONICAL_HEADERS - set(mapped_headers))
    if missing_headers:
        raise GarminCsvImportError(
            "CSV file is missing required columns: " + ", ".join(missing_headers)
        )

    return mapped_headers


def parse_garmin_csv_file(file_path: str | Path) -> GarminCsvParseResult:
    with Path(file_path).open(newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)
        header_mapping = map_garmin_csv_headers(reader.fieldnames)
        workout_rows: list[GarminCsvWorkoutRow] = []
        errors: list[str] = []
        rows_read = 0

        for row_number, row in enumerate(reader, start=2):
            rows_read += 1
            try:
                workout_rows.append(_parse_workout_row(row_number, row, header_mapping))
            except GarminCsvImportError as error:
                errors.append(f"Row {row_number}: {error}")

    if rows_read == 0:
        errors.append("CSV file must include at least one activity row.")

    return GarminCsvParseResult(
        rows_read=rows_read,
        workout_rows=workout_rows,
        errors=errors,
    )


def import_garmin_csv(
    database_path: str | Path,
    imported_file_id: int,
) -> GarminCsvImportResult | None:
    imported_file = imported_file_repository.get_imported_file(database_path, imported_file_id)
    if imported_file is None:
        return None

    if imported_file.file_type != "csv":
        return _finish_import(
            database_path,
            imported_file,
            rows_read=0,
            workouts_created=0,
            duplicate_rows_skipped=0,
            errors=["Only CSV imported files can be processed by the Garmin CSV importer."],
        )

    try:
        parse_result = parse_garmin_csv_file(imported_file.stored_path)
    except (OSError, UnicodeError, csv.Error, GarminCsvImportError) as error:
        return _finish_import(
            database_path,
            imported_file,
            rows_read=0,
            workouts_created=0,
            duplicate_rows_skipped=0,
            errors=[str(error)],
        )

    workouts_created = 0
    duplicate_rows_skipped = 0
    for workout_row in parse_result.workout_rows:
        duplicate = workout_repository.find_garmin_csv_workout_duplicate(
            database_path,
            workout_row.workout_date,
            workout_row.start_time,
            workout_row.workout_type,
            workout_row.duration_minutes,
        )
        if duplicate is not None:
            duplicate_rows_skipped += 1
            continue

        workout_repository.create_workout(
            database_path,
            NewWorkout(
                workout_date=workout_row.workout_date,
                workout_type=workout_row.workout_type,
                duration_minutes=workout_row.duration_minutes,
                notes=_build_workout_notes(workout_row),
                source="garmin_csv",
            ),
        )
        workouts_created += 1

    return _finish_import(
        database_path,
        imported_file,
        rows_read=parse_result.rows_read,
        workouts_created=workouts_created,
        duplicate_rows_skipped=duplicate_rows_skipped,
        errors=parse_result.errors,
    )


def _parse_workout_row(
    row_number: int,
    row: dict[str, str],
    header_mapping: dict[str, str],
) -> GarminCsvWorkoutRow:
    workout_date = _parse_date(_required_value(row, header_mapping, "workout_date"))
    start_time = _parse_start_time(_required_value(row, header_mapping, "start_time"))
    workout_type = _required_value(row, header_mapping, "workout_type")
    duration_minutes = _parse_duration_minutes(
        _required_value(row, header_mapping, "duration_minutes")
    )
    notes = _optional_value(row, header_mapping, "notes")

    return GarminCsvWorkoutRow(
        row_number=row_number,
        workout_date=workout_date,
        start_time=start_time,
        workout_type=workout_type,
        duration_minutes=duration_minutes,
        notes=notes,
    )


def _finish_import(
    database_path: str | Path,
    imported_file: ImportedFile,
    rows_read: int,
    workouts_created: int,
    duplicate_rows_skipped: int,
    errors: list[str],
) -> GarminCsvImportResult:
    malformed_rows = len(errors)
    processed_rows = workouts_created + duplicate_rows_skipped
    if errors and processed_rows == 0:
        import_status = IMPORT_STATUS_FAILED
    elif errors:
        import_status = IMPORT_STATUS_PARTIAL_FAILURE
    else:
        import_status = IMPORT_STATUS_IMPORTED

    updated_file = imported_file_repository.update_import_status(
        database_path,
        imported_file.id,
        import_status,
        "\n".join(errors) if errors else None,
    )
    if updated_file is None:
        raise RuntimeError("Imported file disappeared while updating import status")

    return GarminCsvImportResult(
        imported_file=updated_file,
        rows_read=rows_read,
        workouts_created=workouts_created,
        duplicate_rows_skipped=duplicate_rows_skipped,
        malformed_rows=malformed_rows,
        errors=errors,
        import_status=import_status,
    )


def _required_value(
    row: dict[str, str],
    header_mapping: dict[str, str],
    canonical_header: str,
) -> str:
    value = row.get(header_mapping[canonical_header], "").strip()
    if not value:
        raise GarminCsvImportError(f"{canonical_header} is required.")
    return value


def _optional_value(
    row: dict[str, str],
    header_mapping: dict[str, str],
    canonical_header: str,
) -> str | None:
    source_header = header_mapping.get(canonical_header)
    if source_header is None:
        return None

    return row.get(source_header, "").strip() or None


def _parse_date(value: str) -> str:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date().isoformat()
    except ValueError as error:
        raise GarminCsvImportError("workout_date must use YYYY-MM-DD.") from error


def _parse_start_time(value: str) -> str:
    for time_format in ("%H:%M", "%H:%M:%S"):
        try:
            return datetime.strptime(value, time_format).strftime("%H:%M")
        except ValueError:
            continue

    raise GarminCsvImportError("start_time must use HH:MM or HH:MM:SS.")


def _parse_duration_minutes(value: str) -> int:
    try:
        duration_minutes = int(value)
    except ValueError as error:
        raise GarminCsvImportError("duration_minutes must be a positive integer.") from error

    if duration_minutes <= 0:
        raise GarminCsvImportError("duration_minutes must be a positive integer.")

    return duration_minutes


def _build_workout_notes(workout_row: GarminCsvWorkoutRow) -> str:
    notes = [
        f"Garmin CSV start time: {workout_row.start_time}",
        f"Garmin CSV row: {workout_row.row_number}",
    ]
    if workout_row.notes:
        notes.append(workout_row.notes)

    return "\n".join(notes)


def _normalize_header(header: str) -> str:
    return " ".join(header.strip().lower().replace("_", " ").split())
