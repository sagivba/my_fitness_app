import tempfile
from pathlib import Path
from unittest import TestCase

from my_fitness_app.model.database import initialize_database
from my_fitness_app.model.sleep import NewSleepLog
from my_fitness_app.model.sleep_repository import (
    create_sleep_log,
    get_sleep_log,
    list_sleep_logs,
)


class TestSleepRepository(TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.database_path = Path(self.temp_dir.name) / "fitness.db"
        initialize_database(self.database_path)

    def test_list_sleep_logs_returns_empty_list(self):
        self.assertEqual(list_sleep_logs(self.database_path), [])

    def test_create_sleep_log_persists_data(self):
        created = create_sleep_log(
            self.database_path,
            NewSleepLog(
                sleep_date="2026-05-20",
                start_time="22:30",
                end_time="06:30",
                duration_minutes=480,
                sleep_quality=4,
                notes="Slept well",
            ),
        )

        loaded = get_sleep_log(self.database_path, created.id)

        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.id, created.id)
        self.assertEqual(loaded.sleep_date, "2026-05-20")
        self.assertEqual(loaded.start_time, "22:30")
        self.assertEqual(loaded.end_time, "06:30")
        self.assertEqual(loaded.duration_minutes, 480)
        self.assertEqual(loaded.sleep_quality, 4)
        self.assertEqual(loaded.notes, "Slept well")

    def test_list_sleep_logs_orders_newer_dates_first(self):
        older = create_sleep_log(
            self.database_path,
            NewSleepLog(
                sleep_date="2026-05-19",
                start_time=None,
                end_time=None,
                duration_minutes=None,
                sleep_quality=None,
                notes=None,
            ),
        )
        newer = create_sleep_log(
            self.database_path,
            NewSleepLog(
                sleep_date="2026-05-20",
                start_time=None,
                end_time=None,
                duration_minutes=None,
                sleep_quality=None,
                notes=None,
            ),
        )

        sleep_logs = list_sleep_logs(self.database_path)

        self.assertEqual([sleep_log.id for sleep_log in sleep_logs], [newer.id, older.id])

    def test_get_sleep_log_returns_existing_log(self):
        created = create_sleep_log(
            self.database_path,
            NewSleepLog(
                sleep_date="2026-05-20",
                start_time=None,
                end_time=None,
                duration_minutes=None,
                sleep_quality=None,
                notes=None,
            ),
        )

        loaded = get_sleep_log(self.database_path, created.id)

        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.id, created.id)

    def test_get_sleep_log_returns_none_for_missing_id(self):
        self.assertIsNone(get_sleep_log(self.database_path, 999))
