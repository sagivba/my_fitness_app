from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree

from my_fitness_app.model import imported_file_repository, workout_repository
from my_fitness_app.model.imported_file import ImportedFile
from my_fitness_app.model.workout import NewWorkout
from my_fitness_app.services.garmin_csv_import_service import (
    IMPORT_STATUS_FAILED,
    IMPORT_STATUS_IMPORTED,
)

SOURCE = "garmin_tcx"


class GarminTcxImportError(ValueError):
    pass


@dataclass(frozen=True)
class GarminTcxWorkoutData:
    workout_date: str
    start_time: str
    start_timestamp: str
    workout_type: str
    duration_seconds: float | None
    duration_minutes: int | None
    distance_meters: float | None
    calories: int | None
    average_heart_rate_bpm: int | None
    max_heart_rate_bpm: int | None
    missing_optional_fields: list[str]


@dataclass(frozen=True)
class GarminTcxImportResult:
    imported_file: ImportedFile
    rows_read: int
    workouts_created: int
    duplicate_rows_skipped: int
    malformed_rows: int
    errors: list[str]
    import_status: str


def parse_tcx_file(file_path: str | Path) -> GarminTcxWorkoutData:
    try:
        root = ElementTree.parse(file_path).getroot()
    except ElementTree.ParseError as error:
        raise GarminTcxImportError(f"Malformed TCX XML: {error}") from error

    activity = _first_descendant(root, "Activity")
    if activity is None:
        raise GarminTcxImportError("TCX file must include an Activity element.")

    workout_type = activity.attrib.get("Sport", "").strip() or "TCX activity"
    laps = _children(activity, "Lap")
    if not laps:
        raise GarminTcxImportError("TCX Activity must include at least one Lap.")

    start_timestamp = _first_lap_start_time(laps) or _child_text(activity, "Id")
    if not start_timestamp:
        raise GarminTcxImportError("TCX Activity must include a start time.")

    parsed_start = _parse_xml_datetime(start_timestamp, "TCX start time")
    duration_seconds = _sum_float_child(laps, "TotalTimeSeconds")
    distance_meters = _sum_float_child(laps, "DistanceMeters")
    calories = _sum_int_child(laps, "Calories")
    average_hr_values = _heart_rate_values(laps, "AverageHeartRateBpm")
    max_hr_values = _heart_rate_values(laps, "MaximumHeartRateBpm")
    average_heart_rate_bpm = (
        round(sum(average_hr_values) / len(average_hr_values)) if average_hr_values else None
    )
    max_heart_rate_bpm = max(max_hr_values) if max_hr_values else None

    missing_optional_fields = []
    if duration_seconds is None:
        missing_optional_fields.append("duration")
    if distance_meters is None:
        missing_optional_fields.append("distance")
    if calories is None:
        missing_optional_fields.append("calories")
    if average_heart_rate_bpm is None:
        missing_optional_fields.append("average heart rate")
    if max_heart_rate_bpm is None:
        missing_optional_fields.append("max heart rate")

    return GarminTcxWorkoutData(
        workout_date=parsed_start.date().isoformat(),
        start_time=parsed_start.strftime("%H:%M"),
        start_timestamp=start_timestamp,
        workout_type=workout_type,
        duration_seconds=duration_seconds,
        duration_minutes=_duration_minutes(duration_seconds),
        distance_meters=distance_meters,
        calories=calories,
        average_heart_rate_bpm=average_heart_rate_bpm,
        max_heart_rate_bpm=max_heart_rate_bpm,
        missing_optional_fields=missing_optional_fields,
    )


def import_garmin_tcx(
    database_path: str | Path,
    imported_file_id: int,
) -> GarminTcxImportResult | None:
    imported_file = imported_file_repository.get_imported_file(database_path, imported_file_id)
    if imported_file is None:
        return None

    if imported_file.file_type != "tcx":
        return _finish_import(
            database_path,
            imported_file,
            workouts_created=0,
            duplicate_rows_skipped=0,
            errors=["Only TCX imported files can be processed by the Garmin TCX importer."],
        )

    try:
        workout_data = parse_tcx_file(imported_file.stored_path)
    except (OSError, UnicodeError, GarminTcxImportError) as error:
        return _finish_import(
            database_path,
            imported_file,
            workouts_created=0,
            duplicate_rows_skipped=0,
            errors=[str(error)],
        )

    duplicate = workout_repository.find_garmin_file_workout_duplicate(
        database_path,
        SOURCE,
        workout_data.workout_date,
        workout_data.start_time,
        workout_data.workout_type,
        workout_data.duration_minutes,
        workout_data.distance_meters,
    )
    if duplicate is not None:
        return _finish_import(
            database_path,
            imported_file,
            workouts_created=0,
            duplicate_rows_skipped=1,
            errors=[],
        )

    workout_repository.create_workout(
        database_path,
        NewWorkout(
            workout_date=workout_data.workout_date,
            workout_type=workout_data.workout_type,
            duration_minutes=workout_data.duration_minutes,
            notes=_build_workout_notes(workout_data),
            source=SOURCE,
        ),
    )

    return _finish_import(
        database_path,
        imported_file,
        workouts_created=1,
        duplicate_rows_skipped=0,
        errors=[],
    )


def _finish_import(
    database_path: str | Path,
    imported_file: ImportedFile,
    workouts_created: int,
    duplicate_rows_skipped: int,
    errors: list[str],
) -> GarminTcxImportResult:
    import_status = IMPORT_STATUS_FAILED if errors else IMPORT_STATUS_IMPORTED
    updated_file = imported_file_repository.update_import_status(
        database_path,
        imported_file.id,
        import_status,
        "\n".join(errors) if errors else None,
    )
    if updated_file is None:
        raise RuntimeError("Imported file disappeared while updating import status")

    return GarminTcxImportResult(
        imported_file=updated_file,
        rows_read=1,
        workouts_created=workouts_created,
        duplicate_rows_skipped=duplicate_rows_skipped,
        malformed_rows=len(errors),
        errors=errors,
        import_status=import_status,
    )


def _build_workout_notes(workout_data: GarminTcxWorkoutData) -> str:
    notes = [
        f"Garmin TCX start time: {workout_data.start_time}",
        f"Start timestamp: {workout_data.start_timestamp}",
        f"Activity sport: {workout_data.workout_type}",
    ]
    if workout_data.duration_seconds is not None:
        notes.append(f"Duration seconds: {workout_data.duration_seconds:.2f}")
    if workout_data.distance_meters is not None:
        notes.append(f"Distance meters: {workout_data.distance_meters:.2f}")
    if workout_data.calories is not None:
        notes.append(f"Calories: {workout_data.calories}")
    if workout_data.average_heart_rate_bpm is not None:
        notes.append(f"Average heart rate bpm: {workout_data.average_heart_rate_bpm}")
    if workout_data.max_heart_rate_bpm is not None:
        notes.append(f"Max heart rate bpm: {workout_data.max_heart_rate_bpm}")
    if workout_data.missing_optional_fields:
        notes.append("Missing optional fields: " + ", ".join(workout_data.missing_optional_fields))
    notes.append("Source metadata: TCX Activity")
    return "\n".join(notes)


def _first_lap_start_time(laps: list[ElementTree.Element]) -> str | None:
    for lap in laps:
        start_time = lap.attrib.get("StartTime", "").strip()
        if start_time:
            return start_time
    return None


def _sum_float_child(elements: list[ElementTree.Element], child_name: str) -> float | None:
    values = []
    for element in elements:
        value = _child_text(element, child_name)
        if value:
            try:
                values.append(float(value))
            except ValueError:
                continue

    return sum(values) if values else None


def _sum_int_child(elements: list[ElementTree.Element], child_name: str) -> int | None:
    values = []
    for element in elements:
        value = _child_text(element, child_name)
        if value:
            try:
                values.append(int(value))
            except ValueError:
                continue

    return sum(values) if values else None


def _heart_rate_values(elements: list[ElementTree.Element], parent_name: str) -> list[int]:
    values = []
    for element in elements:
        heart_rate = _first_child(element, parent_name)
        if heart_rate is None:
            continue
        value = _child_text(heart_rate, "Value")
        if value:
            try:
                values.append(int(value))
            except ValueError:
                continue
    return values


def _parse_xml_datetime(value: str, label: str) -> datetime:
    normalized_value = value.strip().replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized_value)
    except ValueError as error:
        raise GarminTcxImportError(f"{label} must be an ISO-8601 timestamp.") from error


def _duration_minutes(duration_seconds: float | None) -> int | None:
    if duration_seconds is None:
        return None
    return max(1, round(duration_seconds / 60))


def _first_descendant(
    element: ElementTree.Element,
    descendant_name: str,
) -> ElementTree.Element | None:
    for descendant in element.iter():
        if _local_name(descendant.tag) == descendant_name:
            return descendant
    return None


def _children(element: ElementTree.Element, child_name: str) -> list[ElementTree.Element]:
    return [child for child in element if _local_name(child.tag) == child_name]


def _first_child(
    element: ElementTree.Element,
    child_name: str,
) -> ElementTree.Element | None:
    for child in element:
        if _local_name(child.tag) == child_name:
            return child
    return None


def _child_text(element: ElementTree.Element, child_name: str) -> str | None:
    child = _first_child(element, child_name)
    if child is None or child.text is None:
        return None
    return child.text.strip() or None


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]
