import unittest

from my_python_project_template.services.example_service import get_health_status, get_welcome_message


class TestExampleService(unittest.TestCase):
    def test_get_welcome_message(self):
        self.assertEqual(
            get_welcome_message("Demo"),
            "Welcome to Demo",
        )

    def test_get_health_status(self):
        self.assertEqual(
            get_health_status(),
            {"status": "ok"},
        )


if __name__ == "__main__":
    unittest.main()
