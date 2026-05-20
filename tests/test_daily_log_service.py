import tempfile
from pathlib import Path
from unittest import TestCase

from my_fitness_app.model.database import initialize_database
from my_fitness_app.services.daily_log_service import (
    DailyLogValidationError,
    create_daily_log,
    get_daily_log,
    list_daily_logs,
)


class TestDailyLogService(TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.database_path = Path(self.temp_dir.name) / "fitness.db"
        initialize_database(self.database_path)

    def test_create_daily_log_trims_text_and_persists(self):
        created = create_daily_log(
            self.database_path,
            {
                "log_date": " 2026-05-20 ",
                "body_weight_kg": "82.5",
                "mood": " רגוע ",
                "energy_level": "4",
                "notes": " Good day ",
            },
        )

        loaded = get_daily_log(self.database_path, created.id)

        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.log_date, "2026-05-20")
        self.assertEqual(loaded.body_weight_kg, 82.5)
        self.assertEqual(loaded.mood, "רגוע")
        self.assertEqual(loaded.energy_level, 4)
        self.assertEqual(loaded.notes, "Good day")

    def test_create_daily_log_rejects_missing_date(self):
        with self.assertRaises(DailyLogValidationError) as context:
            create_daily_log(
                self.database_path,
                {
                    "log_date": "",
                    "body_weight_kg": "",
                    "mood": "",
                    "energy_level": "",
                    "notes": "",
                },
            )

        self.assertEqual(context.exception.errors, {"log_date": "חובה להזין תאריך."})

    def test_create_daily_log_accepts_optional_numeric_fields(self):
        created = create_daily_log(
            self.database_path,
            {
                "log_date": "2026-05-20",
                "body_weight_kg": "82.5",
                "mood": "",
                "energy_level": "4",
                "notes": "",
            },
        )

        self.assertEqual(created.body_weight_kg, 82.5)
        self.assertEqual(created.energy_level, 4)

    def test_create_daily_log_rejects_invalid_weight(self):
        with self.assertRaises(DailyLogValidationError) as context:
            create_daily_log(
                self.database_path,
                {
                    "log_date": "2026-05-20",
                    "body_weight_kg": "invalid",
                    "mood": "",
                    "energy_level": "",
                    "notes": "",
                },
            )

        self.assertEqual(
            context.exception.errors,
            {"body_weight_kg": "משקל חייב להיות מספר חיובי."},
        )

    def test_create_daily_log_rejects_invalid_energy_level(self):
        with self.assertRaises(DailyLogValidationError) as context:
            create_daily_log(
                self.database_path,
                {
                    "log_date": "2026-05-20",
                    "body_weight_kg": "",
                    "mood": "",
                    "energy_level": "0",
                    "notes": "",
                },
            )

        self.assertEqual(
            context.exception.errors,
            {"energy_level": "רמת אנרגיה חייבת להיות מספר שלם חיובי."},
        )

    def test_create_daily_log_allows_blank_optional_fields(self):
        created = create_daily_log(
            self.database_path,
            {
                "log_date": "2026-05-20",
                "body_weight_kg": "",
                "mood": "",
                "energy_level": "",
                "notes": "",
            },
        )

        self.assertIsNone(created.body_weight_kg)
        self.assertIsNone(created.mood)
        self.assertIsNone(created.energy_level)
        self.assertIsNone(created.notes)

    def test_list_daily_logs_returns_created_logs(self):
        create_daily_log(
            self.database_path,
            {
                "log_date": "2026-05-20",
                "body_weight_kg": "",
                "mood": "",
                "energy_level": "",
                "notes": "",
            },
        )

        self.assertEqual(len(list_daily_logs(self.database_path)), 1)
