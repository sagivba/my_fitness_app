import math
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

SOURCE = "garmin_gpx"
EARTH_RADIUS_METERS = 6_371_000


class GarminGpxImportError(ValueError):
    pass


@dataclass(frozen=True)
class GpxTrackPoint:
    latitude: float
    longitude: float
    elevation_meters: float | None
    timestamp: datetime | None
    timestamp_text: str | None


@dataclass(frozen=True)
class GarminGpxWorkoutData:
    workout_date: str
    start_time: str
    start_timestamp: str
    end_timestamp: str
    workout_type: str
    duration_minutes: int
    distance_meters: float
    point_count: int
    segment_count: int
    elevation_min_meters: float | None
    elevation_max_meters: float | None
    elevation_gain_meters: float | None
    missing_optional_fields: list[str]


@dataclass(frozen=True)
class GarminGpxImportResult:
    imported_file: ImportedFile
    rows_read: int
    workouts_created: int
    duplicate_rows_skipped: int
    malformed_rows: int
    errors: list[str]
    import_status: str


def parse_gpx_file(file_path: str | Path) -> GarminGpxWorkoutData:
    try:
        root = ElementTree.parse(file_path).getroot()
    except ElementTree.ParseError as error:
        raise GarminGpxImportError(f"Malformed GPX XML: {error}") from error

    tracks = _descendants(root, "trk")
    if not tracks:
        raise GarminGpxImportError("GPX file must include at least one track.")

    workout_type = _track_type(tracks[0])
    segment_count = 0
    point_count = 0
    all_points: list[GpxTrackPoint] = []
    distance_meters = 0.0
    elevation_gain_meters = 0.0
    has_elevation_gain = False

    for track in tracks:
        for segment in _children(track, "trkseg"):
            segment_count += 1
            segment_points = [_parse_track_point(point) for point in _children(segment, "trkpt")]
            point_count += len(segment_points)
            all_points.extend(segment_points)
            distance_meters += _segment_distance(segment_points)
            segment_gain, has_segment_gain = _segment_elevation_gain(segment_points)
            elevation_gain_meters += segment_gain
            has_elevation_gain = has_elevation_gain or has_segment_gain

    if segment_count == 0:
        raise GarminGpxImportError("GPX track must include at least one segment.")
    if point_count < 2:
        raise GarminGpxImportError("GPX import requires at least two track points.")

    timed_points = [point for point in all_points if point.timestamp is not None]
    if len(timed_points) < 2:
        raise GarminGpxImportError(
            "GPX track points must include at least first and last timestamps."
        )

    start_point = timed_points[0]
    end_point = timed_points[-1]
    duration_seconds = (end_point.timestamp - start_point.timestamp).total_seconds()
    if duration_seconds <= 0:
        raise GarminGpxImportError("GPX track duration must be positive.")

    elevations = [
        point.elevation_meters for point in all_points if point.elevation_meters is not None
    ]
    missing_optional_fields = []
    if not elevations:
        missing_optional_fields.append("elevation")

    return GarminGpxWorkoutData(
        workout_date=start_point.timestamp.date().isoformat(),
        start_time=start_point.timestamp.strftime("%H:%M"),
        start_timestamp=start_point.timestamp_text or start_point.timestamp.isoformat(),
        end_timestamp=end_point.timestamp_text or end_point.timestamp.isoformat(),
        workout_type=workout_type,
        duration_minutes=max(1, round(duration_seconds / 60)),
        distance_meters=distance_meters,
        point_count=point_count,
        segment_count=segment_count,
        elevation_min_meters=min(elevations) if elevations else None,
        elevation_max_meters=max(elevations) if elevations else None,
        elevation_gain_meters=elevation_gain_meters if has_elevation_gain else None,
        missing_optional_fields=missing_optional_fields,
    )


def import_garmin_gpx(
    database_path: str | Path,
    imported_file_id: int,
) -> GarminGpxImportResult | None:
    imported_file = imported_file_repository.get_imported_file(database_path, imported_file_id)
    if imported_file is None:
        return None

    if imported_file.file_type != "gpx":
        return _finish_import(
            database_path,
            imported_file,
            rows_read=0,
            workouts_created=0,
            duplicate_rows_skipped=0,
            errors=["Only GPX imported files can be processed by the Garmin GPX importer."],
        )

    try:
        workout_data = parse_gpx_file(imported_file.stored_path)
    except (OSError, UnicodeError, GarminGpxImportError) as error:
        return _finish_import(
            database_path,
            imported_file,
            rows_read=0,
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
            rows_read=workout_data.point_count,
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
        rows_read=workout_data.point_count,
        workouts_created=1,
        duplicate_rows_skipped=0,
        errors=[],
    )


def _finish_import(
    database_path: str | Path,
    imported_file: ImportedFile,
    rows_read: int,
    workouts_created: int,
    duplicate_rows_skipped: int,
    errors: list[str],
) -> GarminGpxImportResult:
    import_status = IMPORT_STATUS_FAILED if errors else IMPORT_STATUS_IMPORTED
    updated_file = imported_file_repository.update_import_status(
        database_path,
        imported_file.id,
        import_status,
        "\n".join(errors) if errors else None,
    )
    if updated_file is None:
        raise RuntimeError("Imported file disappeared while updating import status")

    return GarminGpxImportResult(
        imported_file=updated_file,
        rows_read=rows_read,
        workouts_created=workouts_created,
        duplicate_rows_skipped=duplicate_rows_skipped,
        malformed_rows=len(errors),
        errors=errors,
        import_status=import_status,
    )


def _build_workout_notes(workout_data: GarminGpxWorkoutData) -> str:
    notes = [
        f"Garmin GPX start time: {workout_data.start_time}",
        f"Start timestamp: {workout_data.start_timestamp}",
        f"End timestamp: {workout_data.end_timestamp}",
        f"Distance meters: {workout_data.distance_meters:.2f}",
        f"Point count: {workout_data.point_count}",
        f"Segment count: {workout_data.segment_count}",
    ]
    if workout_data.elevation_min_meters is not None:
        notes.append(f"Elevation min meters: {workout_data.elevation_min_meters:.2f}")
    if workout_data.elevation_max_meters is not None:
        notes.append(f"Elevation max meters: {workout_data.elevation_max_meters:.2f}")
    if workout_data.elevation_gain_meters is not None:
        notes.append(f"Elevation gain meters: {workout_data.elevation_gain_meters:.2f}")
    if workout_data.missing_optional_fields:
        notes.append("Missing optional fields: " + ", ".join(workout_data.missing_optional_fields))
    notes.append("Source metadata: GPX track")
    return "\n".join(notes)


def _parse_track_point(point: ElementTree.Element) -> GpxTrackPoint:
    try:
        latitude = float(point.attrib["lat"])
        longitude = float(point.attrib["lon"])
    except (KeyError, ValueError) as error:
        raise GarminGpxImportError("GPX track points must include numeric lat/lon.") from error

    elevation_text = _child_text(point, "ele")
    time_text = _child_text(point, "time")
    return GpxTrackPoint(
        latitude=latitude,
        longitude=longitude,
        elevation_meters=_parse_optional_float(elevation_text),
        timestamp=_parse_optional_datetime(time_text),
        timestamp_text=time_text,
    )


def _segment_distance(points: list[GpxTrackPoint]) -> float:
    distance_meters = 0.0
    for previous_point, current_point in zip(points, points[1:], strict=False):
        distance_meters += _haversine_distance(previous_point, current_point)
    return distance_meters


def _segment_elevation_gain(points: list[GpxTrackPoint]) -> tuple[float, bool]:
    elevation_gain = 0.0
    has_elevation_gain = False
    previous_elevation: float | None = None

    for point in points:
        if point.elevation_meters is None:
            continue
        if previous_elevation is not None:
            delta = point.elevation_meters - previous_elevation
            if delta > 0:
                elevation_gain += delta
                has_elevation_gain = True
        previous_elevation = point.elevation_meters

    return elevation_gain, has_elevation_gain


def _haversine_distance(
    previous_point: GpxTrackPoint,
    current_point: GpxTrackPoint,
) -> float:
    previous_latitude = math.radians(previous_point.latitude)
    current_latitude = math.radians(current_point.latitude)
    latitude_delta = math.radians(current_point.latitude - previous_point.latitude)
    longitude_delta = math.radians(current_point.longitude - previous_point.longitude)
    haversine = (
        math.sin(latitude_delta / 2) ** 2
        + math.cos(previous_latitude)
        * math.cos(current_latitude)
        * math.sin(longitude_delta / 2) ** 2
    )
    return EARTH_RADIUS_METERS * 2 * math.atan2(math.sqrt(haversine), math.sqrt(1 - haversine))


def _track_type(track: ElementTree.Element) -> str:
    return _child_text(track, "type") or _child_text(track, "name") or "GPX activity"


def _parse_optional_float(value: str | None) -> float | None:
    if not value:
        return None
    try:
        return float(value)
    except ValueError as error:
        raise GarminGpxImportError("GPX elevation values must be numeric.") from error


def _parse_optional_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    normalized_value = value.strip().replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized_value)
    except ValueError as error:
        raise GarminGpxImportError("GPX time values must be ISO-8601 timestamps.") from error


def _descendants(element: ElementTree.Element, descendant_name: str) -> list[ElementTree.Element]:
    return [
        descendant
        for descendant in element.iter()
        if _local_name(descendant.tag) == descendant_name
    ]


def _children(element: ElementTree.Element, child_name: str) -> list[ElementTree.Element]:
    return [child for child in element if _local_name(child.tag) == child_name]


def _child_text(element: ElementTree.Element, child_name: str) -> str | None:
    for child in element:
        if _local_name(child.tag) == child_name and child.text:
            return child.text.strip() or None
    return None


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]
