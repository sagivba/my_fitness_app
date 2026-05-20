import tempfile
from pathlib import Path
from unittest import TestCase

from my_fitness_app.model.database import initialize_database
from my_fitness_app.services.workout_service import (
    WorkoutValidationError,
    create_workout,
    get_workout,
    list_workouts,
)


class TestWorkoutService(TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.database_path = Path(self.temp_dir.name) / "fitness.db"
        initialize_database(self.database_path)

    def test_create_workout_trims_text_and_persists(self):
        created = create_workout(
            self.database_path,
            {
                "workout_date": " 2026-05-20 ",
                "workout_type": " Walking ",
                "duration_minutes": "45",
                "notes": " Easy pace ",
            },
        )

        loaded = get_workout(self.database_path, created.id)

        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.workout_date, "2026-05-20")
        self.assertEqual(loaded.workout_type, "Walking")
        self.assertEqual(loaded.duration_minutes, 45)
        self.assertEqual(loaded.notes, "Easy pace")

    def test_create_workout_allows_blank_optional_fields(self):
        created = create_workout(
            self.database_path,
            {
                "workout_date": "2026-05-20",
                "workout_type": "Walking",
                "duration_minutes": "",
                "notes": "",
            },
        )

        self.assertIsNone(created.duration_minutes)
        self.assertIsNone(created.notes)

    def test_create_workout_rejects_missing_required_fields(self):
        with self.assertRaises(WorkoutValidationError) as context:
            create_workout(
                self.database_path,
                {
                    "workout_date": "",
                    "workout_type": "",
                    "duration_minutes": "",
                    "notes": "",
                },
            )

        self.assertEqual(
            context.exception.errors,
            {
                "workout_date": "חובה להזין תאריך אימון.",
                "workout_type": "חובה להזין סוג אימון.",
            },
        )

    def test_create_workout_rejects_invalid_duration(self):
        with self.assertRaises(WorkoutValidationError) as context:
            create_workout(
                self.database_path,
                {
                    "workout_date": "2026-05-20",
                    "workout_type": "Walking",
                    "duration_minutes": "0",
                    "notes": "",
                },
            )

        self.assertEqual(
            context.exception.errors,
            {"duration_minutes": "משך האימון חייב להיות מספר שלם חיובי."},
        )

    def test_list_workouts_returns_created_workouts(self):
        create_workout(
            self.database_path,
            {
                "workout_date": "2026-05-20",
                "workout_type": "Walking",
                "duration_minutes": "",
                "notes": "",
            },
        )

        self.assertEqual(len(list_workouts(self.database_path)), 1)
