import tempfile
from pathlib import Path
from unittest import TestCase

from my_fitness_app.model.database import initialize_database
from my_fitness_app.services.sleep_service import (
    SleepValidationError,
    create_sleep_log,
    get_sleep_log,
    list_sleep_logs,
)


class TestSleepService(TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.database_path = Path(self.temp_dir.name) / "fitness.db"
        initialize_database(self.database_path)

    def test_create_sleep_log_trims_text_and_persists(self):
        created = create_sleep_log(
            self.database_path,
            {
                "sleep_date": " 2026-05-20 ",
                "start_time": "22:30",
                "end_time": "06:30",
                "duration_minutes": "480",
                "sleep_quality": "4",
                "notes": " Slept well ",
            },
        )

        loaded = get_sleep_log(self.database_path, created.id)

        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.sleep_date, "2026-05-20")
        self.assertEqual(loaded.start_time, "22:30")
        self.assertEqual(loaded.end_time, "06:30")
        self.assertEqual(loaded.duration_minutes, 480)
        self.assertEqual(loaded.sleep_quality, 4)
        self.assertEqual(loaded.notes, "Slept well")

    def test_create_sleep_log_rejects_missing_date(self):
        with self.assertRaises(SleepValidationError) as context:
            create_sleep_log(
                self.database_path,
                {
                    "sleep_date": "",
                    "start_time": "",
                    "end_time": "",
                    "duration_minutes": "",
                    "sleep_quality": "",
                    "notes": "",
                },
            )

        self.assertEqual(context.exception.errors, {"sleep_date": "חובה להזין תאריך שינה."})

    def test_create_sleep_log_accepts_positive_duration(self):
        created = create_sleep_log(
            self.database_path,
            {
                "sleep_date": "2026-05-20",
                "start_time": "",
                "end_time": "",
                "duration_minutes": "480",
                "sleep_quality": "",
                "notes": "",
            },
        )

        self.assertEqual(created.duration_minutes, 480)

    def test_create_sleep_log_rejects_zero_duration(self):
        with self.assertRaises(SleepValidationError) as context:
            create_sleep_log(
                self.database_path,
                {
                    "sleep_date": "2026-05-20",
                    "start_time": "",
                    "end_time": "",
                    "duration_minutes": "0",
                    "sleep_quality": "",
                    "notes": "",
                },
            )

        self.assertEqual(
            context.exception.errors,
            {"duration_minutes": "משך השינה חייב להיות מספר שלם חיובי."},
        )

    def test_create_sleep_log_rejects_negative_duration(self):
        with self.assertRaises(SleepValidationError) as context:
            create_sleep_log(
                self.database_path,
                {
                    "sleep_date": "2026-05-20",
                    "start_time": "",
                    "end_time": "",
                    "duration_minutes": "-1",
                    "sleep_quality": "",
                    "notes": "",
                },
            )

        self.assertEqual(
            context.exception.errors,
            {"duration_minutes": "משך השינה חייב להיות מספר שלם חיובי."},
        )

    def test_create_sleep_log_allows_blank_optional_fields(self):
        created = create_sleep_log(
            self.database_path,
            {
                "sleep_date": "2026-05-20",
                "start_time": "",
                "end_time": "",
                "duration_minutes": "",
                "sleep_quality": "",
                "notes": "",
            },
        )

        self.assertIsNone(created.start_time)
        self.assertIsNone(created.end_time)
        self.assertIsNone(created.duration_minutes)
        self.assertIsNone(created.sleep_quality)
        self.assertIsNone(created.notes)

    def test_list_sleep_logs_returns_created_logs(self):
        create_sleep_log(
            self.database_path,
            {
                "sleep_date": "2026-05-20",
                "start_time": "",
                "end_time": "",
                "duration_minutes": "",
                "sleep_quality": "",
                "notes": "",
            },
        )

        self.assertEqual(len(list_sleep_logs(self.database_path)), 1)
