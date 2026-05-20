import tempfile
from pathlib import Path
from unittest import TestCase

from my_fitness_app.app import create_app
from my_fitness_app.config import AppConfig
from my_fitness_app.services.sleep_service import create_sleep_log


class TestSleepRoutes(TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.database_path = Path(self.temp_dir.name) / "fitness.db"
        self.app = create_app(
            AppConfig(
                project_name="Test Project",
                database_path=self.database_path,
            )
        )
        self.client = self.app.test_client()

    def test_sleep_list_shows_empty_state(self):
        response = self.client.get("/sleep/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("עדיין אין רשומות שינה שמורות.".encode(), response.data)

    def test_sleep_list_shows_existing_logs(self):
        create_sleep_log(
            self.database_path,
            {
                "sleep_date": "2026-05-20",
                "start_time": "22:30",
                "end_time": "06:30",
                "duration_minutes": "480",
                "sleep_quality": "",
                "notes": "",
            },
        )

        response = self.client.get("/sleep/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"2026-05-20", response.data)
        self.assertIn("480 דקות".encode(), response.data)

    def test_new_sleep_log_page_shows_form(self):
        response = self.client.get("/sleep/new")

        self.assertEqual(response.status_code, 200)
        self.assertIn("הוספת שינה".encode(), response.data)
        self.assertIn(b'name="sleep_date"', response.data)
        self.assertIn(b'name="duration_minutes"', response.data)

    def test_post_valid_sleep_log_redirects_to_detail(self):
        response = self.client.post(
            "/sleep/",
            data={
                "sleep_date": "2026-05-20",
                "start_time": "22:30",
                "end_time": "06:30",
                "duration_minutes": "480",
                "sleep_quality": "4",
                "notes": "Slept well",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertRegex(response.headers["Location"], r"/sleep/\d+$")

        detail_response = self.client.get(response.headers["Location"])
        self.assertEqual(detail_response.status_code, 200)
        self.assertIn(b"2026-05-20", detail_response.data)
        self.assertIn(b"Slept well", detail_response.data)

    def test_post_invalid_sleep_log_returns_form_with_errors(self):
        response = self.client.post(
            "/sleep/",
            data={
                "sleep_date": "",
                "start_time": "",
                "end_time": "",
                "duration_minutes": "0",
                "sleep_quality": "",
                "notes": "",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("חובה להזין תאריך שינה.".encode(), response.data)
        self.assertIn("משך השינה חייב להיות מספר שלם חיובי.".encode(), response.data)

    def test_missing_sleep_log_returns_404(self):
        response = self.client.get("/sleep/999")

        self.assertEqual(response.status_code, 404)
