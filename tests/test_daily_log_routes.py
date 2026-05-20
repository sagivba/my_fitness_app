import tempfile
from pathlib import Path
from unittest import TestCase

from my_fitness_app.app import create_app
from my_fitness_app.config import AppConfig
from my_fitness_app.services.daily_log_service import create_daily_log


class TestDailyLogRoutes(TestCase):
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

    def test_daily_log_list_shows_empty_state(self):
        response = self.client.get("/daily-logs/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("עדיין אין רשומות יומיות שמורות.".encode(), response.data)

    def test_daily_log_list_shows_existing_logs(self):
        create_daily_log(
            self.database_path,
            {
                "log_date": "2026-05-20",
                "body_weight_kg": "82.5",
                "mood": "רגוע",
                "energy_level": "",
                "notes": "",
            },
        )

        response = self.client.get("/daily-logs/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"2026-05-20", response.data)
        self.assertIn("רגוע".encode(), response.data)

    def test_new_daily_log_page_shows_form(self):
        response = self.client.get("/daily-logs/new")

        self.assertEqual(response.status_code, 200)
        self.assertIn("הוספת רשומה יומית".encode(), response.data)
        self.assertIn(b'name="log_date"', response.data)
        self.assertIn(b'name="body_weight_kg"', response.data)

    def test_post_valid_daily_log_redirects_to_detail(self):
        response = self.client.post(
            "/daily-logs/",
            data={
                "log_date": "2026-05-20",
                "body_weight_kg": "82.5",
                "mood": "רגוע",
                "energy_level": "4",
                "notes": "Good day",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertRegex(response.headers["Location"], r"/daily-logs/\d+$")

        detail_response = self.client.get(response.headers["Location"])
        self.assertEqual(detail_response.status_code, 200)
        self.assertIn(b"2026-05-20", detail_response.data)
        self.assertIn(b"Good day", detail_response.data)

    def test_post_invalid_daily_log_returns_form_with_errors(self):
        response = self.client.post(
            "/daily-logs/",
            data={
                "log_date": "",
                "body_weight_kg": "0",
                "mood": "",
                "energy_level": "0",
                "notes": "",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("חובה להזין תאריך.".encode(), response.data)
        self.assertIn("משקל חייב להיות מספר חיובי.".encode(), response.data)
        self.assertIn("רמת אנרגיה חייבת להיות מספר שלם חיובי.".encode(), response.data)

    def test_missing_daily_log_returns_404(self):
        response = self.client.get("/daily-logs/999")

        self.assertEqual(response.status_code, 404)
