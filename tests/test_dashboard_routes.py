import tempfile
from pathlib import Path
from unittest import TestCase

from my_fitness_app.app import create_app
from my_fitness_app.config import AppConfig
from my_fitness_app.model.workout import NewWorkout
from my_fitness_app.model.workout_repository import create_workout


class TestDashboardRoutes(TestCase):
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

    def test_home_page_links_to_dashboard(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("לוח מדדים".encode(), response.data)
        self.assertIn(b'href="/dashboard/"', response.data)

    def test_dashboard_route_renders_summary(self):
        create_workout(
            self.database_path,
            NewWorkout(
                workout_date="2026-05-20",
                workout_type="Running",
                duration_minutes=40,
                notes=None,
                source="garmin_tcx",
                distance_meters=6200,
                calories=410,
                average_heart_rate=146,
                max_heart_rate=173,
            ),
        )

        response = self.client.get("/dashboard/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("לוח מדדים".encode(), response.data)
        self.assertIn("מספר אימונים".encode(), response.data)
        self.assertIn("מרחק כולל".encode(), response.data)
        self.assertIn("טבלת אימונים".encode(), response.data)
        self.assertIn(b"6.20", response.data)
        self.assertIn(b"Garmin TCX", response.data)
