import sqlite3
import tempfile
from pathlib import Path
from unittest import TestCase

from my_fitness_app.model.database import connect, initialize_database

REQUIRED_TABLES = {
    "daily_log",
    "workout",
    "sleep_log",
    "meal",
    "imported_file",
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
