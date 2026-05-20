import sqlite3
from pathlib import Path

from my_fitness_app.model.daily_log import DailyLog, NewDailyLog
from my_fitness_app.model.database import connect


def create_daily_log(database_path: str | Path, daily_log: NewDailyLog) -> DailyLog:
    connection = connect(database_path)
    try:
        cursor = connection.execute(
            """
            INSERT INTO daily_log (log_date, body_weight_kg, mood, energy_level, notes)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                daily_log.log_date,
                daily_log.body_weight_kg,
                daily_log.mood,
                daily_log.energy_level,
                daily_log.notes,
            ),
        )
        connection.commit()
        created_id = cursor.lastrowid
        if created_id is None:
            raise RuntimeError("Failed to create daily log")
        created_daily_log = get_daily_log(database_path, created_id)
        if created_daily_log is None:
            raise RuntimeError("Created daily log could not be loaded")
        return created_daily_log
    finally:
        connection.close()


def list_daily_logs(database_path: str | Path) -> list[DailyLog]:
    connection = connect(database_path)
    try:
        rows = connection.execute(
            """
            SELECT id, log_date, body_weight_kg, mood, energy_level, notes,
                   created_at, updated_at
            FROM daily_log
            ORDER BY log_date DESC, id DESC
            """
        ).fetchall()
    finally:
        connection.close()

    return [_daily_log_from_row(row) for row in rows]


def get_daily_log(database_path: str | Path, daily_log_id: int) -> DailyLog | None:
    connection = connect(database_path)
    try:
        row = connection.execute(
            """
            SELECT id, log_date, body_weight_kg, mood, energy_level, notes,
                   created_at, updated_at
            FROM daily_log
            WHERE id = ?
            """,
            (daily_log_id,),
        ).fetchone()
    finally:
        connection.close()

    if row is None:
        return None
    return _daily_log_from_row(row)


def _daily_log_from_row(row: sqlite3.Row) -> DailyLog:
    return DailyLog(
        id=row["id"],
        log_date=row["log_date"],
        body_weight_kg=row["body_weight_kg"],
        mood=row["mood"],
        energy_level=row["energy_level"],
        notes=row["notes"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )
