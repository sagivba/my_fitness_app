import sqlite3
from pathlib import Path

SCHEMA_PATH = Path(__file__).with_name("schema.sql")


def connect(database_path: str | Path) -> sqlite3.Connection:
    path = Path(database_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database(database_path: str | Path) -> None:
    schema = SCHEMA_PATH.read_text(encoding="utf-8")

    connection = connect(database_path)
    try:
        connection.executescript(schema)
        _ensure_strength_tables(connection)
        _ensure_imported_file_status_columns(connection)
        _ensure_workout_metric_columns(connection)
        connection.commit()
    finally:
        connection.close()


def _ensure_imported_file_status_columns(connection: sqlite3.Connection) -> None:
    columns = {row["name"] for row in connection.execute("PRAGMA table_info(imported_file)")}

    if "import_status" not in columns:
        connection.execute(
            "ALTER TABLE imported_file "
            "ADD COLUMN import_status TEXT NOT NULL DEFAULT 'not_imported'"
        )
    if "import_error_message" not in columns:
        connection.execute("ALTER TABLE imported_file ADD COLUMN import_error_message TEXT")


def _ensure_workout_metric_columns(connection: sqlite3.Connection) -> None:
    columns = {row["name"] for row in connection.execute("PRAGMA table_info(workout)")}
    metric_columns = {
        "start_time": "TEXT",
        "end_time": "TEXT",
        "duration_seconds": "REAL",
        "distance_meters": "REAL",
        "calories": "INTEGER",
        "average_heart_rate": "INTEGER",
        "max_heart_rate": "INTEGER",
        "elevation_gain_meters": "REAL",
        "elevation_loss_meters": "REAL",
        "external_activity_id": "TEXT",
    }

    for column_name, column_type in metric_columns.items():
        if column_name not in columns:
            connection.execute(f"ALTER TABLE workout ADD COLUMN {column_name} {column_type}")


def _ensure_strength_tables(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS strength_exercise (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workout_id INTEGER NOT NULL,
            exercise_name TEXT NOT NULL,
            exercise_order INTEGER NOT NULL,
            notes TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (workout_id) REFERENCES workout(id) ON DELETE CASCADE
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS strength_set (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            strength_exercise_id INTEGER NOT NULL,
            set_number INTEGER NOT NULL,
            reps INTEGER NOT NULL,
            weight_kg REAL,
            perceived_effort INTEGER,
            notes TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (strength_exercise_id)
                REFERENCES strength_exercise(id) ON DELETE CASCADE
        )
        """
    )
