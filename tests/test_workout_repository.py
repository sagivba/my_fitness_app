import tempfile
from pathlib import Path
from unittest import TestCase

from my_fitness_app.model.database import initialize_database
from my_fitness_app.model.workout import NewWorkout
from my_fitness_app.model.workout_repository import create_workout, get_workout, list_workouts


class TestWorkoutRepository(TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.database_path = Path(self.temp_dir.name) / "fitness.db"
        initialize_database(self.database_path)

    def test_create_and_get_workout(self):
        created = create_workout(
            self.database_path,
            NewWorkout(
                workout_date="2026-05-20",
                workout_type="Walking",
                duration_minutes=45,
                notes="Easy pace",
            ),
        )

        loaded = get_workout(self.database_path, created.id)

        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.id, created.id)
        self.assertEqual(loaded.workout_date, "2026-05-20")
        self.assertEqual(loaded.workout_type, "Walking")
        self.assertEqual(loaded.duration_minutes, 45)
        self.assertEqual(loaded.notes, "Easy pace")
        self.assertEqual(loaded.source, "manual")

    def test_list_workouts_orders_newer_dates_first(self):
        older = create_workout(
            self.database_path,
            NewWorkout(
                workout_date="2026-05-19",
                workout_type="Elliptical",
                duration_minutes=None,
                notes=None,
            ),
        )
        newer = create_workout(
            self.database_path,
            NewWorkout(
                workout_date="2026-05-20",
                workout_type="Gym",
                duration_minutes=60,
                notes=None,
            ),
        )

        workouts = list_workouts(self.database_path)

        self.assertEqual([workout.id for workout in workouts], [newer.id, older.id])

    def test_get_workout_returns_none_for_missing_id(self):
        self.assertIsNone(get_workout(self.database_path, 999))
