import tempfile
from pathlib import Path
from unittest import TestCase

from my_fitness_app.model.daily_log import NewDailyLog
from my_fitness_app.model.daily_log_repository import (
    create_daily_log,
    get_daily_log,
    list_daily_logs,
)
from my_fitness_app.model.database import initialize_database


class TestDailyLogRepository(TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.database_path = Path(self.temp_dir.name) / "fitness.db"
        initialize_database(self.database_path)

    def test_list_daily_logs_returns_empty_list(self):
        self.assertEqual(list_daily_logs(self.database_path), [])

    def test_create_daily_log_persists_data(self):
        created = create_daily_log(
            self.database_path,
            NewDailyLog(
                log_date="2026-05-20",
                body_weight_kg=82.5,
                mood="רגוע",
                energy_level=4,
                notes="Good day",
            ),
        )

        loaded = get_daily_log(self.database_path, created.id)

        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.id, created.id)
        self.assertEqual(loaded.log_date, "2026-05-20")
        self.assertEqual(loaded.body_weight_kg, 82.5)
        self.assertEqual(loaded.mood, "רגוע")
        self.assertEqual(loaded.energy_level, 4)
        self.assertEqual(loaded.notes, "Good day")

    def test_list_daily_logs_orders_newer_dates_first(self):
        older = create_daily_log(
            self.database_path,
            NewDailyLog(
                log_date="2026-05-19",
                body_weight_kg=None,
                mood=None,
                energy_level=None,
                notes=None,
            ),
        )
        newer = create_daily_log(
            self.database_path,
            NewDailyLog(
                log_date="2026-05-20",
                body_weight_kg=None,
                mood=None,
                energy_level=None,
                notes=None,
            ),
        )

        daily_logs = list_daily_logs(self.database_path)

        self.assertEqual([daily_log.id for daily_log in daily_logs], [newer.id, older.id])

    def test_get_daily_log_returns_existing_log(self):
        created = create_daily_log(
            self.database_path,
            NewDailyLog(
                log_date="2026-05-20",
                body_weight_kg=None,
                mood=None,
                energy_level=None,
                notes=None,
            ),
        )

        loaded = get_daily_log(self.database_path, created.id)

        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.id, created.id)

    def test_get_daily_log_returns_none_for_missing_id(self):
        self.assertIsNone(get_daily_log(self.database_path, 999))
