import unittest
from pathlib import Path

from my_fitness_app.app import create_app
from my_fitness_app.config import AppConfig


class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = create_app(
            AppConfig(
                project_name="Test Project",
                database_path=Path("test.db"),
            )
        )
        self.client = self.app.test_client()

    def test_index(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Welcome to Test Project", response.data)

    def test_health(self):
        response = self.client.get("/api/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"status": "ok"})

    def test_database_path_config(self):
        self.assertEqual(self.app.config["DATABASE_PATH"], "test.db")


if __name__ == "__main__":
    unittest.main()
