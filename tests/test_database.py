import sqlite3
import tempfile
from pathlib import Path
from unittest import TestCase

from my_fitness_app.model.database import connect, initialize_database

REQUIRED_TABLES = {
    "daily_log",
    "workout",
    "strength_exercise",
    "strength_set",
    "sleep_log",
    "meal",
    "imported_file",
}

REQUIRED_COLUMNS = {
    "workout": {
        "average_heart_rate",
        "calories",
        "distance_meters",
        "duration_seconds",
        "elevation_gain_meters",
        "elevation_loss_meters",
        "end_time",
        "external_activity_id",
        "max_heart_rate",
        "start_time",
    },
    "meal": {
        "fiber_grams",
    },
    "imported_file": {
        "import_error_message",
        "import_status",
        "updated_at",
    },
    "strength_exercise": {
        "workout_id",
        "exercise_name",
        "exercise_order",
        "notes",
    },
    "strength_set": {
        "strength_exercise_id",
        "set_number",
        "reps",
        "weight_kg",
        "perceived_effort",
        "notes",
    },
}


class TestDatabase(TestCase):
    def test_connect_creates_parent_directory_and_configures_connection(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "nested" / "fitness.db"

            connection = connect(database_path)
            try:
                foreign_keys_enabled = connection.execute("PRAGMA foreign_keys").fetchone()[0]
                connection.execute("CREATE TABLE demo (name TEXT NOT NULL)")
                connection.execute("INSERT INTO demo (name) VALUES (?)", ("row access",))
                row = connection.execute("SELECT name FROM demo").fetchone()
            finally:
                connection.close()

            self.assertTrue(database_path.exists())
            self.assertEqual(foreign_keys_enabled, 1)
            self.assertIsInstance(row, sqlite3.Row)
            self.assertEqual(row["name"], "row access")

    def test_initialize_database_creates_required_tables(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "fitness.db"

            initialize_database(database_path)

            connection = connect(database_path)
            try:
                rows = connection.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                ).fetchall()
            finally:
                connection.close()

        table_names = {row["name"] for row in rows}
        self.assertTrue(REQUIRED_TABLES.issubset(table_names))

    def test_initialize_database_creates_required_schema_columns(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "fitness.db"

            initialize_database(database_path)

            connection = connect(database_path)
            try:
                table_columns = {
                    table_name: {
                        row["name"]
                        for row in connection.execute(f"PRAGMA table_info({table_name})")
                    }
                    for table_name in REQUIRED_COLUMNS
                }
            finally:
                connection.close()

        for table_name, required_columns in REQUIRED_COLUMNS.items():
            self.assertTrue(required_columns.issubset(table_columns[table_name]))

    def test_initialize_database_is_repeatable(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "fitness.db"

            initialize_database(database_path)
            initialize_database(database_path)

            connection = connect(database_path)
            try:
                workout_count = connection.execute("SELECT COUNT(*) FROM workout").fetchone()[0]
            finally:
                connection.close()

        self.assertEqual(workout_count, 0)

    def test_initialize_database_adds_import_status_columns_to_existing_imported_file_table(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "fitness.db"
            connection = connect(database_path)
            try:
                connection.execute(
                    """
                    CREATE TABLE imported_file (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        original_filename TEXT NOT NULL,
                        stored_path TEXT NOT NULL,
                        file_hash TEXT NOT NULL UNIQUE,
                        file_type TEXT NOT NULL,
                        imported_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
                connection.commit()
            finally:
                connection.close()

            initialize_database(database_path)

            connection = connect(database_path)
            try:
                columns = {
                    row["name"] for row in connection.execute("PRAGMA table_info(imported_file)")
                }
            finally:
                connection.close()

        self.assertIn("import_status", columns)
        self.assertIn("import_error_message", columns)

    def test_initialize_database_adds_metric_columns_to_existing_workout_table(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "fitness.db"
            connection = connect(database_path)
            try:
                connection.execute(
                    """
                    CREATE TABLE workout (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        workout_date TEXT NOT NULL,
                        workout_type TEXT NOT NULL,
                        duration_minutes INTEGER,
                        source TEXT NOT NULL DEFAULT 'manual',
                        notes TEXT,
                        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
                connection.execute(
                    """
                    INSERT INTO workout (workout_date, workout_type, duration_minutes, notes)
                    VALUES ('2026-05-20', 'Walking', 45, 'existing row')
                    """
                )
                connection.commit()
            finally:
                connection.close()

            initialize_database(database_path)

            connection = connect(database_path)
            try:
                columns = {row["name"] for row in connection.execute("PRAGMA table_info(workout)")}
                row = connection.execute(
                    "SELECT workout_type, notes, start_time, distance_meters FROM workout"
                ).fetchone()
            finally:
                connection.close()

        self.assertTrue(REQUIRED_COLUMNS["workout"].issubset(columns))
        self.assertEqual(row["workout_type"], "Walking")
        self.assertEqual(row["notes"], "existing row")
        self.assertIsNone(row["start_time"])
        self.assertIsNone(row["distance_meters"])

    def test_initialize_database_adds_strength_tables_to_existing_database(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "fitness.db"
            connection = connect(database_path)
            try:
                connection.execute(
                    """
                    CREATE TABLE workout (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        workout_date TEXT NOT NULL,
                        workout_type TEXT NOT NULL,
                        duration_minutes INTEGER,
                        source TEXT NOT NULL DEFAULT 'manual',
                        notes TEXT,
                        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
                connection.commit()
            finally:
                connection.close()

            initialize_database(database_path)

            connection = connect(database_path)
            try:
                table_names = {
                    row["name"]
                    for row in connection.execute(
                        "SELECT name FROM sqlite_master WHERE type = 'table'"
                    )
                }
            finally:
                connection.close()

        self.assertIn("strength_exercise", table_names)
        self.assertIn("strength_set", table_names)
