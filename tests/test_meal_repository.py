import tempfile
from pathlib import Path
from unittest import TestCase

from my_fitness_app.model.database import initialize_database
from my_fitness_app.model.meal import NewMeal
from my_fitness_app.model.meal_repository import create_meal, get_meal, list_meals, update_meal


class TestMealRepository(TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.database_path = Path(self.temp_dir.name) / "fitness.db"
        initialize_database(self.database_path)

    def test_create_and_get_meal(self):
        created = create_meal(
            self.database_path,
            NewMeal(
                meal_date="2026-05-20",
                meal_type="Breakfast",
                description="Eggs and toast",
                calories=450,
                protein_grams=25.5,
                carbs_grams=40.0,
                fat_grams=18.0,
                fiber_grams=5.0,
                notes="Manual estimate",
            ),
        )

        loaded = get_meal(self.database_path, created.id)

        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.id, created.id)
        self.assertEqual(loaded.meal_date, "2026-05-20")
        self.assertEqual(loaded.meal_type, "Breakfast")
        self.assertEqual(loaded.description, "Eggs and toast")
        self.assertEqual(loaded.calories, 450)
        self.assertEqual(loaded.protein_grams, 25.5)
        self.assertEqual(loaded.carbs_grams, 40.0)
        self.assertEqual(loaded.fat_grams, 18.0)
        self.assertEqual(loaded.fiber_grams, 5.0)
        self.assertEqual(loaded.source, "manual")
        self.assertEqual(loaded.notes, "Manual estimate")

    def test_list_meals_orders_newer_dates_first(self):
        older = create_meal(
            self.database_path,
            NewMeal(
                meal_date="2026-05-19",
                meal_type="Dinner",
                description="Soup",
                calories=None,
                protein_grams=None,
                carbs_grams=None,
                fat_grams=None,
                fiber_grams=None,
                notes=None,
            ),
        )
        newer = create_meal(
            self.database_path,
            NewMeal(
                meal_date="2026-05-20",
                meal_type="Lunch",
                description="Salad",
                calories=None,
                protein_grams=None,
                carbs_grams=None,
                fat_grams=None,
                fiber_grams=None,
                notes=None,
            ),
        )

        meals = list_meals(self.database_path)

        self.assertEqual([meal.id for meal in meals], [newer.id, older.id])

    def test_get_meal_returns_none_for_missing_id(self):
        self.assertIsNone(get_meal(self.database_path, 999))

    def test_update_meal_updates_existing_meal(self):
        created = create_meal(
            self.database_path,
            NewMeal(
                meal_date="2026-05-20",
                meal_type="Breakfast",
                description="Eggs",
                calories=300,
                protein_grams=None,
                carbs_grams=None,
                fat_grams=None,
                fiber_grams=None,
                notes=None,
            ),
        )

        updated = update_meal(
            self.database_path,
            created.id,
            NewMeal(
                meal_date="2026-05-21",
                meal_type="Lunch",
                description="Rice bowl",
                calories=650,
                protein_grams=30.0,
                carbs_grams=80.0,
                fat_grams=20.0,
                fiber_grams=8.0,
                notes="Updated",
            ),
        )

        self.assertIsNotNone(updated)
        self.assertEqual(updated.id, created.id)
        self.assertEqual(updated.meal_date, "2026-05-21")
        self.assertEqual(updated.meal_type, "Lunch")
        self.assertEqual(updated.description, "Rice bowl")
        self.assertEqual(updated.calories, 650)
        self.assertEqual(updated.protein_grams, 30.0)
        self.assertEqual(updated.carbs_grams, 80.0)
        self.assertEqual(updated.fat_grams, 20.0)
        self.assertEqual(updated.fiber_grams, 8.0)
        self.assertEqual(updated.source, "manual")
        self.assertEqual(updated.notes, "Updated")

    def test_update_meal_returns_none_for_missing_id(self):
        updated = update_meal(
            self.database_path,
            999,
            NewMeal(
                meal_date="2026-05-20",
                meal_type="Breakfast",
                description="Eggs",
                calories=None,
                protein_grams=None,
                carbs_grams=None,
                fat_grams=None,
                fiber_grams=None,
                notes=None,
            ),
        )

        self.assertIsNone(updated)
