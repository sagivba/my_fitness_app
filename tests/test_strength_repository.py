import tempfile
from pathlib import Path
from unittest import TestCase

from my_fitness_app.model.database import initialize_database
from my_fitness_app.model.strength import NewStrengthExercise, NewStrengthSet
from my_fitness_app.model.strength_repository import (
    create_exercise,
    create_set,
    list_exercises_for_workout,
    next_exercise_order,
    next_set_number,
)
from my_fitness_app.model.workout import NewWorkout
from my_fitness_app.model.workout_repository import create_workout


class TestStrengthRepository(TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.database_path = Path(self.temp_dir.name) / "fitness.db"
        initialize_database(self.database_path)
        self.workout = create_workout(
            self.database_path,
            NewWorkout(
                workout_date="2026-05-20",
                workout_type="Gym",
                duration_minutes=55,
                notes=None,
            ),
        )

    def test_create_and_list_exercise_with_sets(self):
        exercise = create_exercise(
            self.database_path,
            NewStrengthExercise(
                workout_id=self.workout.id,
                exercise_name="Bench Press",
                exercise_order=1,
                notes="Warmup first",
            ),
        )
        created_set = create_set(
            self.database_path,
            NewStrengthSet(
                strength_exercise_id=exercise.id,
                set_number=1,
                reps=8,
                weight_kg=60.0,
                perceived_effort=7,
                notes="Solid",
            ),
        )

        exercises = list_exercises_for_workout(self.database_path, self.workout.id)

        self.assertEqual(len(exercises), 1)
        self.assertEqual(exercises[0].exercise_name, "Bench Press")
        self.assertEqual(exercises[0].exercise_order, 1)
        self.assertEqual(exercises[0].notes, "Warmup first")
        self.assertEqual(exercises[0].sets, (created_set,))

    def test_next_order_and_set_number_are_auto_incremented(self):
        exercise = create_exercise(
            self.database_path,
            NewStrengthExercise(
                workout_id=self.workout.id,
                exercise_name="Squat",
                exercise_order=next_exercise_order(self.database_path, self.workout.id),
                notes=None,
            ),
        )
        create_set(
            self.database_path,
            NewStrengthSet(
                strength_exercise_id=exercise.id,
                set_number=next_set_number(self.database_path, exercise.id),
                reps=5,
                weight_kg=80.0,
                perceived_effort=None,
                notes=None,
            ),
        )

        self.assertEqual(next_exercise_order(self.database_path, self.workout.id), 2)
        self.assertEqual(next_set_number(self.database_path, exercise.id), 2)
