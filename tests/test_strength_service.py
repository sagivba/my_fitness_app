import tempfile
from pathlib import Path
from unittest import TestCase

from my_fitness_app.model.database import initialize_database
from my_fitness_app.services.strength_service import (
    StrengthValidationError,
    StrengthWorkoutNotFoundError,
    add_strength_set,
    list_strength_exercises,
    summarize_strength_exercises,
)
from my_fitness_app.services.workout_service import create_workout


class TestStrengthService(TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.database_path = Path(self.temp_dir.name) / "fitness.db"
        initialize_database(self.database_path)
        self.workout = create_workout(
            self.database_path,
            {
                "workout_date": "2026-05-20",
                "workout_type": "Gym",
                "duration_minutes": "50",
                "notes": "",
            },
        )

    def test_add_strength_set_creates_exercise_and_set(self):
        created_set = add_strength_set(
            self.database_path,
            self.workout.id,
            {
                "exercise_name": " Bench Press ",
                "reps": "8",
                "weight_kg": "60.5",
                "perceived_effort": "7",
                "notes": " Good set ",
            },
        )

        exercises = list_strength_exercises(self.database_path, self.workout.id)

        self.assertEqual(created_set.reps, 8)
        self.assertEqual(len(exercises), 1)
        self.assertEqual(exercises[0].exercise_name, "Bench Press")
        self.assertEqual(exercises[0].sets[0].weight_kg, 60.5)
        self.assertEqual(exercises[0].sets[0].perceived_effort, 7)
        self.assertEqual(exercises[0].sets[0].notes, "Good set")

    def test_add_strength_set_reuses_existing_exercise_by_normalized_name(self):
        add_strength_set(
            self.database_path,
            self.workout.id,
            {
                "exercise_name": "Bench   Press",
                "reps": "8",
                "weight_kg": "60",
                "perceived_effort": "",
                "notes": "",
            },
        )
        add_strength_set(
            self.database_path,
            self.workout.id,
            {
                "exercise_name": " bench press ",
                "reps": "6",
                "weight_kg": "",
                "perceived_effort": "8",
                "notes": "",
            },
        )

        exercises = list_strength_exercises(self.database_path, self.workout.id)

        self.assertEqual(len(exercises), 1)
        self.assertEqual([strength_set.set_number for strength_set in exercises[0].sets], [1, 2])
        self.assertEqual([strength_set.reps for strength_set in exercises[0].sets], [8, 6])

    def test_add_strength_set_rejects_missing_workout(self):
        with self.assertRaises(StrengthWorkoutNotFoundError):
            add_strength_set(
                self.database_path,
                999,
                {
                    "exercise_name": "Squat",
                    "reps": "5",
                    "weight_kg": "80",
                    "perceived_effort": "",
                    "notes": "",
                },
            )

    def test_add_strength_set_rejects_invalid_values(self):
        with self.assertRaises(StrengthValidationError) as context:
            add_strength_set(
                self.database_path,
                self.workout.id,
                {
                    "exercise_name": "",
                    "reps": "0",
                    "weight_kg": "-1",
                    "perceived_effort": "11",
                    "notes": "",
                },
            )

        self.assertEqual(
            context.exception.errors,
            {
                "reps": "חובה להזין מספר חזרות חיובי.",
                "weight_kg": "משקל חייב להיות מספר לא שלילי.",
                "perceived_effort": "מאמץ נתפס חייב להיות מספר שלם בין 1 ל-10.",
                "exercise_name": "חובה להזין שם תרגיל.",
            },
        )

    def test_summarize_strength_exercises_totals_weighted_sets_only_for_volume(self):
        add_strength_set(
            self.database_path,
            self.workout.id,
            {
                "exercise_name": "Squat",
                "reps": "5",
                "weight_kg": "80",
                "perceived_effort": "",
                "notes": "",
            },
        )
        add_strength_set(
            self.database_path,
            self.workout.id,
            {
                "exercise_name": "Push Up",
                "reps": "12",
                "weight_kg": "",
                "perceived_effort": "",
                "notes": "",
            },
        )

        summary = summarize_strength_exercises(
            list_strength_exercises(self.database_path, self.workout.id)
        )

        self.assertEqual(summary.total_exercises, 2)
        self.assertEqual(summary.total_sets, 2)
        self.assertEqual(summary.total_reps, 17)
        self.assertEqual(summary.total_volume_kg, 400.0)
