import tempfile
from pathlib import Path
from unittest import TestCase

from my_fitness_app.app import create_app
from my_fitness_app.config import AppConfig
from my_fitness_app.services.meal_service import create_meal


class TestMealRoutes(TestCase):
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

    def test_meal_list_shows_empty_state(self):
        response = self.client.get("/meals/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("עדיין אין ארוחות שמורות.".encode(), response.data)

    def test_meal_list_shows_existing_meals(self):
        create_meal(
            self.database_path,
            {
                "meal_date": "2026-05-20",
                "meal_type": "Breakfast",
                "description": "Eggs",
                "calories": "450",
                "protein_grams": "",
                "carbs_grams": "",
                "fat_grams": "",
                "fiber_grams": "",
                "notes": "",
            },
        )

        response = self.client.get("/meals/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"2026-05-20", response.data)
        self.assertIn(b"Breakfast", response.data)
        self.assertIn("450 קלוריות".encode(), response.data)

    def test_new_meal_page_shows_form(self):
        response = self.client.get("/meals/new")

        self.assertEqual(response.status_code, 200)
        self.assertIn("הוספת ארוחה".encode(), response.data)
        self.assertIn(b'name="meal_date"', response.data)
        self.assertIn(b'name="meal_type"', response.data)
        self.assertIn(b'name="description"', response.data)

    def test_post_valid_meal_redirects_to_detail(self):
        response = self.client.post(
            "/meals/",
            data={
                "meal_date": "2026-05-20",
                "meal_type": "Breakfast",
                "description": "Eggs and toast",
                "calories": "450",
                "protein_grams": "25.5",
                "carbs_grams": "40",
                "fat_grams": "18",
                "fiber_grams": "5",
                "notes": "Manual estimate",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertRegex(response.headers["Location"], r"/meals/\d+$")

        detail_response = self.client.get(response.headers["Location"])
        self.assertEqual(detail_response.status_code, 200)
        self.assertIn(b"Eggs and toast", detail_response.data)
        self.assertIn(b"Manual estimate", detail_response.data)

    def test_post_invalid_meal_returns_form_with_errors(self):
        response = self.client.post(
            "/meals/",
            data={
                "meal_date": "",
                "meal_type": "",
                "description": "",
                "calories": "0",
                "protein_grams": "0",
                "carbs_grams": "0",
                "fat_grams": "0",
                "fiber_grams": "0",
                "notes": "",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("חובה להזין תאריך ארוחה.".encode(), response.data)
        self.assertIn("חובה להזין סוג ארוחה.".encode(), response.data)
        self.assertIn("חובה להזין תיאור ארוחה.".encode(), response.data)
        self.assertIn("קלוריות חייבות להיות מספר שלם חיובי.".encode(), response.data)
        self.assertIn("חלבון חייב להיות מספר חיובי.".encode(), response.data)

    def test_detail_missing_meal_returns_404(self):
        response = self.client.get("/meals/999")

        self.assertEqual(response.status_code, 404)

    def test_edit_meal_page_shows_form(self):
        meal = create_meal(
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

        response = self.client.get(f"/meals/{meal.id}/edit")

        self.assertEqual(response.status_code, 200)
        self.assertIn("עריכת ארוחה".encode(), response.data)
        self.assertIn(b"Eggs", response.data)

    def test_update_valid_meal_redirects_to_detail(self):
        meal = create_meal(
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

        response = self.client.post(
            f"/meals/{meal.id}",
            data={
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

        self.assertEqual(response.status_code, 302)
        self.assertRegex(response.headers["Location"], rf"/meals/{meal.id}$")

        detail_response = self.client.get(response.headers["Location"])
        self.assertEqual(detail_response.status_code, 200)
        self.assertIn(b"Rice bowl", detail_response.data)
        self.assertIn(b"Updated", detail_response.data)

    def test_update_invalid_meal_returns_form_with_errors(self):
        meal = create_meal(
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

        response = self.client.post(
            f"/meals/{meal.id}",
            data={
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

        self.assertEqual(response.status_code, 400)
        self.assertIn("חובה להזין תאריך ארוחה.".encode(), response.data)
        self.assertIn("חובה להזין סוג ארוחה.".encode(), response.data)
        self.assertIn("חובה להזין תיאור ארוחה.".encode(), response.data)
        self.assertIn("קלוריות חייבות להיות מספר שלם חיובי.".encode(), response.data)

    def test_edit_missing_meal_returns_404(self):
        response = self.client.get("/meals/999/edit")

        self.assertEqual(response.status_code, 404)

    def test_update_missing_meal_returns_404(self):
        response = self.client.post(
            "/meals/999",
            data={
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

        self.assertEqual(response.status_code, 404)
