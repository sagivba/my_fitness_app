import unittest

from my_python_project_template.model.example_model import HealthStatus


class TestHealthStatus(unittest.TestCase):
    def test_to_dict(self):
        status = HealthStatus(status="ok")

        self.assertEqual(status.to_dict(), {"status": "ok"})


if __name__ == "__main__":
    unittest.main()
