import sqlite3
from pathlib import Path

from my_fitness_app.model.database import connect
from my_fitness_app.model.sleep import NewSleepLog, SleepLog


def create_sleep_log(database_path: str | Path, sleep_log: NewSleepLog) -> SleepLog:
    connection = connect(database_path)
    try:
        cursor = connection.execute(
            """
            INSERT INTO sleep_log (
                sleep_date, start_time, end_time, duration_minutes, sleep_quality, notes
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                sleep_log.sleep_date,
                sleep_log.start_time,
                sleep_log.end_time,
                sleep_log.duration_minutes,
                sleep_log.sleep_quality,
                sleep_log.notes,
            ),
        )
        connection.commit()
        created_id = cursor.lastrowid
        if created_id is None:
            raise RuntimeError("Failed to create sleep log")
        created_sleep_log = get_sleep_log(database_path, created_id)
        if created_sleep_log is None:
            raise RuntimeError("Created sleep log could not be loaded")
        return created_sleep_log
    finally:
        connection.close()


def list_sleep_logs(database_path: str | Path) -> list[SleepLog]:
    connection = connect(database_path)
    try:
        rows = connection.execute(
            """
            SELECT id, sleep_date, start_time, end_time, duration_minutes, sleep_quality,
                   notes, created_at, updated_at
            FROM sleep_log
            ORDER BY sleep_date DESC, id DESC
            """
        ).fetchall()
    finally:
        connection.close()

    return [_sleep_log_from_row(row) for row in rows]


def get_sleep_log(database_path: str | Path, sleep_log_id: int) -> SleepLog | None:
    connection = connect(database_path)
    try:
        row = connection.execute(
            """
            SELECT id, sleep_date, start_time, end_time, duration_minutes, sleep_quality,
                   notes, created_at, updated_at
            FROM sleep_log
            WHERE id = ?
            """,
            (sleep_log_id,),
        ).fetchone()
    finally:
        connection.close()

    if row is None:
        return None
    return _sleep_log_from_row(row)


def _sleep_log_from_row(row: sqlite3.Row) -> SleepLog:
    return SleepLog(
        id=row["id"],
        sleep_date=row["sleep_date"],
        start_time=row["start_time"],
        end_time=row["end_time"],
        duration_minutes=row["duration_minutes"],
        sleep_quality=row["sleep_quality"],
        notes=row["notes"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )
