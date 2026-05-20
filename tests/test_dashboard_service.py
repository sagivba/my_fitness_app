import tempfile
from pathlib import Path
from unittest import TestCase

from my_fitness_app.model.database import initialize_database
from my_fitness_app.model.workout import NewWorkout
from my_fitness_app.model.workout_repository import create_workout
from my_fitness_app.services.dashboard_service import get_workout_dashboard_summary


class TestDashboardService(TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.database_path = Path(self.temp_dir.name) / "fitness.db"
        initialize_database(self.database_path)

    def test_dashboard_summary_aggregates_structured_fields(self):
        create_workout(
            self.database_path,
            NewWorkout(
                workout_date="2026-05-20",
                workout_type="Running",
                duration_minutes=40,
                notes=None,
                source="garmin_tcx",
                duration_seconds=2400,
                distance_meters=6200,
                calories=410,
                average_heart_rate=146,
                max_heart_rate=173,
            ),
        )
        create_workout(
            self.database_path,
            NewWorkout(
                workout_date="2026-05-19",
                workout_type="Walking",
                duration_minutes=30,
                notes=None,
                source="manual",
            ),
        )

        summary = get_workout_dashboard_summary(self.database_path)

        self.assertEqual(summary.total_workouts, 2)
        self.assertEqual(summary.total_duration_minutes, 70)
        self.assertEqual(summary.total_distance_km, 6.2)
        self.assertEqual(summary.total_calories, 410)
        self.assertEqual(summary.average_heart_rate, 146)
        self.assertEqual(summary.max_heart_rate, 173)
        self.assertEqual(
            [item.label for item in summary.source_breakdown],
            ["garmin_tcx", "manual"],
        )
        self.assertEqual(summary.recent_workouts[0].workout_date, "2026-05-20")

    def test_dashboard_summary_does_not_parse_workout_notes(self):
        create_workout(
            self.database_path,
            NewWorkout(
                workout_date="2026-05-20",
                workout_type="Walking",
                duration_minutes=20,
                notes="Distance meters: 999999.00\nCalories: 9999",
                source="garmin_gpx",
            ),
        )

        summary = get_workout_dashboard_summary(self.database_path)

        self.assertEqual(summary.total_distance_km, 0)
        self.assertEqual(summary.total_calories, 0)
