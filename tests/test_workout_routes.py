import tempfile
from pathlib import Path
from unittest import TestCase

from my_fitness_app.app import create_app
from my_fitness_app.config import AppConfig
from my_fitness_app.services.workout_service import create_workout


class TestWorkoutRoutes(TestCase):
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

    def test_workout_list_shows_empty_state(self):
        response = self.client.get("/workouts/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("עדיין אין אימונים שמורים.".encode(), response.data)

    def test_workout_list_shows_existing_workouts(self):
        create_workout(
            self.database_path,
            {
                "workout_date": "2026-05-20",
                "workout_type": "Walking",
                "duration_minutes": "45",
                "notes": "",
            },
        )

        response = self.client.get("/workouts/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"2026-05-20", response.data)
        self.assertIn(b"Walking", response.data)

    def test_new_workout_page_shows_form(self):
        response = self.client.get("/workouts/new")

        self.assertEqual(response.status_code, 200)
        self.assertIn("הוספת אימון".encode(), response.data)
        self.assertIn(b'name="workout_date"', response.data)
        self.assertIn(b'name="workout_type"', response.data)

    def test_post_valid_workout_redirects_to_detail(self):
        response = self.client.post(
            "/workouts/",
            data={
                "workout_date": "2026-05-20",
                "workout_type": "Walking",
                "duration_minutes": "45",
                "notes": "Easy pace",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertRegex(response.headers["Location"], r"/workouts/\d+$")

        detail_response = self.client.get(response.headers["Location"])
        self.assertEqual(detail_response.status_code, 200)
        self.assertIn(b"Walking", detail_response.data)
        self.assertIn(b"Easy pace", detail_response.data)

    def test_post_invalid_workout_returns_form_with_errors(self):
        response = self.client.post(
            "/workouts/",
            data={
                "workout_date": "",
                "workout_type": "",
                "duration_minutes": "0",
                "notes": "",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("חובה להזין תאריך אימון.".encode(), response.data)
        self.assertIn("חובה להזין סוג אימון.".encode(), response.data)
        self.assertIn("משך האימון חייב להיות מספר שלם חיובי.".encode(), response.data)

    def test_missing_workout_returns_404(self):
        response = self.client.get("/workouts/999")

        self.assertEqual(response.status_code, 404)
