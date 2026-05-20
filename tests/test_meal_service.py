import tempfile
from pathlib import Path
from unittest import TestCase

from my_fitness_app.model.database import initialize_database
from my_fitness_app.services.meal_service import (
    MealValidationError,
    create_meal,
    get_meal,
    list_meals,
    update_meal,
)


class TestMealService(TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.database_path = Path(self.temp_dir.name) / "fitness.db"
        initialize_database(self.database_path)

    def test_create_meal_trims_text_and_persists(self):
        created = create_meal(
            self.database_path,
            {
                "meal_date": " 2026-05-20 ",
                "meal_type": " Breakfast ",
                "description": " Eggs and toast ",
                "calories": "450",
                "protein_grams": "25.5",
                "carbs_grams": "40",
                "fat_grams": "18",
                "fiber_grams": "5",
                "notes": " Manual estimate ",
            },
        )

        loaded = get_meal(self.database_path, created.id)

        self.assertIsNotNone(loaded)
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

    def test_create_meal_rejects_missing_required_fields(self):
        with self.assertRaises(MealValidationError) as context:
            create_meal(
                self.database_path,
                {
                    "meal_date": "",
                    "meal_type": "",
                    "description": "",
                    "calories": "",
                    "protein_grams": "",
                    "carbs_grams": "",
                    "fat_grams": "",
                    "fiber_grams": "",
                    "notes": "",
                },
            )

        self.assertEqual(
            context.exception.errors,
            {
                "meal_date": "חובה להזין תאריך ארוחה.",
                "meal_type": "חובה להזין סוג ארוחה.",
                "description": "חובה להזין תיאור ארוחה.",
            },
        )

    def test_create_meal_rejects_invalid_numeric_fields(self):
        with self.assertRaises(MealValidationError) as context:
            create_meal(
                self.database_path,
                {
                    "meal_date": "2026-05-20",
                    "meal_type": "Breakfast",
                    "description": "Eggs",
                    "calories": "0",
                    "protein_grams": "0",
                    "carbs_grams": "invalid",
                    "fat_grams": "-1",
                    "fiber_grams": "0",
                    "notes": "",
                },
            )

        self.assertEqual(
            context.exception.errors,
            {
                "calories": "קלוריות חייבות להיות מספר שלם חיובי.",
                "protein_grams": "חלבון חייב להיות מספר חיובי.",
                "carbs_grams": "פחמימות חייבות להיות מספר חיובי.",
                "fat_grams": "שומן חייב להיות מספר חיובי.",
                "fiber_grams": "סיבים חייבים להיות מספר חיובי.",
            },
        )

    def test_create_meal_allows_blank_optional_fields(self):
        created = create_meal(
            self.database_path,
            {
                "meal_date": "2026-05-20",
                "meal_type": "Breakfast",
                "description": "Eggs",
                "calories": "",
                "protein_grams": "",
                "carbs_grams": "",
                "fat_grams": "",
                "fiber_grams": "",
                "notes": "",
            },
        )

        self.assertIsNone(created.calories)
        self.assertIsNone(created.protein_grams)
        self.assertIsNone(created.carbs_grams)
        self.assertIsNone(created.fat_grams)
        self.assertIsNone(created.fiber_grams)
        self.assertIsNone(created.notes)
        self.assertEqual(created.source, "manual")

    def test_update_meal_validates_and_updates(self):
        created = create_meal(
            self.database_path,
            {
                "meal_date": "2026-05-20",
                "meal_type": "Breakfast",
                "description": "Eggs",
                "calories": "",
                "protein_grams": "",
                "carbs_grams": "",
                "fat_grams": "",
                "fiber_grams": "",
                "notes": "",
            },
        )

        updated = update_meal(
            self.database_path,
            created.id,
            {
                "meal_date": "2026-05-21",
                "meal_type": "Lunch",
                "description": "Rice bowl",
                "calories": "650",
                "protein_grams": "30",
                "carbs_grams": "80",
                "fat_grams": "20",
                "fiber_grams": "8",
                "notes": "Updated",
            },
        )

        self.assertIsNotNone(updated)
        self.assertEqual(updated.meal_date, "2026-05-21")
        self.assertEqual(updated.meal_type, "Lunch")
        self.assertEqual(updated.description, "Rice bowl")
        self.assertEqual(updated.calories, 650)
        self.assertEqual(updated.source, "manual")

    def test_update_meal_rejects_invalid_data(self):
        created = create_meal(
            self.database_path,
            {
                "meal_date": "2026-05-20",
                "meal_type": "Breakfast",
                "description": "Eggs",
                "calories": "",
                "protein_grams": "",
                "carbs_grams": "",
                "fat_grams": "",
                "fiber_grams": "",
                "notes": "",
            },
        )

        with self.assertRaises(MealValidationError) as context:
            update_meal(
                self.database_path,
                created.id,
                {
                    "meal_date": "",
                    "meal_type": "",
                    "description": "",
                    "calories": "0",
                    "protein_grams": "",
                    "carbs_grams": "",
                    "fat_grams": "",
                    "fiber_grams": "",
                    "notes": "",
                },
            )

        self.assertEqual(
            context.exception.errors,
            {
                "calories": "קלוריות חייבות להיות מספר שלם חיובי.",
                "meal_date": "חובה להזין תאריך ארוחה.",
                "meal_type": "חובה להזין סוג ארוחה.",
                "description": "חובה להזין תיאור ארוחה.",
            },
        )

    def test_update_meal_returns_none_for_missing_id(self):
        updated = update_meal(
            self.database_path,
            999,
            {
                "meal_date": "2026-05-20",
                "meal_type": "Breakfast",
                "description": "Eggs",
                "calories": "",
                "protein_grams": "",
                "carbs_grams": "",
                "fat_grams": "",
                "fiber_grams": "",
                "notes": "",
            },
        )

        self.assertIsNone(updated)

    def test_list_meals_returns_created_meals(self):
        create_meal(
            self.database_path,
            {
                "meal_date": "2026-05-20",
                "meal_type": "Breakfast",
                "description": "Eggs",
                "calories": "",
                "protein_grams": "",
                "carbs_grams": "",
                "fat_grams": "",
                "fiber_grams": "",
                "notes": "",
            },
        )

        self.assertEqual(len(list_meals(self.database_path)), 1)
