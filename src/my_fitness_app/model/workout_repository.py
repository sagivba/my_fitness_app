import sqlite3
from pathlib import Path

from my_fitness_app.model.database import connect
from my_fitness_app.model.workout import NewWorkout, Workout


def create_workout(database_path: str | Path, workout: NewWorkout) -> Workout:
    connection = connect(database_path)
    try:
        cursor = connection.execute(
            """
            INSERT INTO workout (workout_date, workout_type, duration_minutes, source, notes)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                workout.workout_date,
                workout.workout_type,
                workout.duration_minutes,
                workout.source,
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
            """
            SELECT id, workout_date, workout_type, duration_minutes, source, notes,
                   created_at, updated_at
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
            """
            SELECT id, workout_date, workout_type, duration_minutes, source, notes,
                   created_at, updated_at
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
            """
            SELECT id, workout_date, workout_type, duration_minutes, source, notes,
                   created_at, updated_at
            FROM workout
            WHERE workout_date = ?
              AND workout_type = ?
              AND duration_minutes = ?
              AND source = 'garmin_csv'
              AND notes LIKE ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (
                workout_date,
                workout_type,
                duration_minutes,
                f"Garmin CSV start time: {start_time}%",
            ),
        ).fetchone()
    finally:
        connection.close()

    if row is None:
        return None
    return _workout_from_row(row)


def _workout_from_row(row: sqlite3.Row) -> Workout:
    return Workout(
        id=row["id"],
        workout_date=row["workout_date"],
        workout_type=row["workout_type"],
        duration_minutes=row["duration_minutes"],
        source=row["source"],
        notes=row["notes"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )
