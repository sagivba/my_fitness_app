import sqlite3
from pathlib import Path

from my_fitness_app.model.database import connect
from my_fitness_app.model.workout import NewWorkout, Workout

WORKOUT_SELECT_COLUMNS = """
    id, workout_date, workout_type, duration_minutes, source, start_time, end_time,
    duration_seconds, distance_meters, calories, average_heart_rate, max_heart_rate,
    elevation_gain_meters, elevation_loss_meters, external_activity_id, notes,
    created_at, updated_at
"""


def create_workout(database_path: str | Path, workout: NewWorkout) -> Workout:
    connection = connect(database_path)
    try:
        cursor = connection.execute(
            """
            INSERT INTO workout (
                workout_date, workout_type, duration_minutes, source, start_time, end_time,
                duration_seconds, distance_meters, calories, average_heart_rate,
                max_heart_rate, elevation_gain_meters, elevation_loss_meters,
                external_activity_id, notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                workout.workout_date,
                workout.workout_type,
                workout.duration_minutes,
                workout.source,
                workout.start_time,
                workout.end_time,
                workout.duration_seconds,
                workout.distance_meters,
                workout.calories,
                workout.average_heart_rate,
                workout.max_heart_rate,
                workout.elevation_gain_meters,
                workout.elevation_loss_meters,
                workout.external_activity_id,
                workout.notes,
            ),
        )
        connection.commit()
        created_id = cursor.lastrowid
        if created_id is None:
            raise RuntimeError("Failed to create workout")
        created_workout = get_workout(database_path, created_id)
        if created_workout is None:
            raise RuntimeError("Created workout could not be loaded")
        return created_workout
    finally:
        connection.close()


def list_workouts(database_path: str | Path) -> list[Workout]:
    connection = connect(database_path)
    try:
        rows = connection.execute(
            f"""
            SELECT {WORKOUT_SELECT_COLUMNS}
            FROM workout
            ORDER BY workout_date DESC, id DESC
            """
        ).fetchall()
    finally:
        connection.close()

    return [_workout_from_row(row) for row in rows]


def get_workout(database_path: str | Path, workout_id: int) -> Workout | None:
    connection = connect(database_path)
    try:
        row = connection.execute(
            f"""
            SELECT {WORKOUT_SELECT_COLUMNS}
            FROM workout
            WHERE id = ?
            """,
            (workout_id,),
        ).fetchone()
    finally:
        connection.close()

    if row is None:
        return None
    return _workout_from_row(row)


def find_garmin_csv_workout_duplicate(
    database_path: str | Path,
    workout_date: str,
    start_time: str,
    workout_type: str,
    duration_minutes: int,
) -> Workout | None:
    connection = connect(database_path)
    try:
        row = connection.execute(
            f"""
            SELECT {WORKOUT_SELECT_COLUMNS}
            FROM workout
            WHERE workout_date = ?
          AND workout_type = ?
          AND duration_minutes = ?
          AND source = 'garmin_csv'
          AND (
              start_time = ?
              OR (start_time IS NULL AND notes LIKE ?)
          )
            ORDER BY id DESC
            LIMIT 1
            """,
            (
                workout_date,
                workout_type,
                duration_minutes,
                start_time,
                f"Garmin CSV start time: {_legacy_note_time(start_time)}%",
            ),
        ).fetchone()
    finally:
        connection.close()

    if row is None:
        return None
    return _workout_from_row(row)


def find_garmin_file_workout_duplicate(
    database_path: str | Path,
    source: str,
    workout_date: str,
    start_time: str,
    workout_type: str,
    duration_minutes: int | None,
    distance_meters: float | None,
) -> Workout | None:
    query = f"""
        SELECT {WORKOUT_SELECT_COLUMNS}
        FROM workout
        WHERE workout_date = ?
          AND workout_type = ?
          AND source = ?
          AND (
              start_time = ?
              OR (start_time IS NULL AND notes LIKE ?)
          )
    """
    parameters: list[str | int | float | None] = [
        workout_date,
        workout_type,
        source,
        start_time,
        f"{_source_note_prefix(source)} start time: {_legacy_note_time(start_time)}%",
    ]

    if duration_minutes is None:
        query += " AND duration_minutes IS NULL"
    else:
        query += " AND duration_minutes = ?"
        parameters.append(duration_minutes)

    if distance_meters is not None:
        query += """
            AND (
                (distance_meters IS NOT NULL AND ABS(distance_meters - ?) < 0.01)
                OR (distance_meters IS NULL AND notes LIKE ?)
            )
        """
        parameters.extend((distance_meters, f"%Distance meters: {distance_meters:.2f}%"))

    query += " ORDER BY id DESC LIMIT 1"

    connection = connect(database_path)
    try:
        row = connection.execute(query, parameters).fetchone()
    finally:
        connection.close()

    if row is None:
        return None
    return _workout_from_row(row)


def _source_note_prefix(source: str) -> str:
    if source == "garmin_tcx":
        return "Garmin TCX"
    if source == "garmin_gpx":
        return "Garmin GPX"
    return "Garmin"


def _legacy_note_time(start_time: str) -> str:
    if "T" not in start_time:
        return start_time
    return start_time.split("T", maxsplit=1)[1][:5]


def _workout_from_row(row: sqlite3.Row) -> Workout:
    return Workout(
        id=row["id"],
        workout_date=row["workout_date"],
        workout_type=row["workout_type"],
        duration_minutes=row["duration_minutes"],
        source=row["source"],
        start_time=row["start_time"],
        end_time=row["end_time"],
        duration_seconds=row["duration_seconds"],
        distance_meters=row["distance_meters"],
        calories=row["calories"],
        average_heart_rate=row["average_heart_rate"],
        max_heart_rate=row["max_heart_rate"],
        elevation_gain_meters=row["elevation_gain_meters"],
        elevation_loss_meters=row["elevation_loss_meters"],
        external_activity_id=row["external_activity_id"],
        notes=row["notes"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )
