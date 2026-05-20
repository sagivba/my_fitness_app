import os
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from my_fitness_app.config import DEFAULT_DATABASE_PATH, AppConfig


class TestAppConfig(TestCase):
    def test_from_env_uses_defaults(self):
        with patch.dict(os.environ, {}, clear=True):
            config = AppConfig.from_env()

        self.assertEqual(config.project_name, "my-fitness-app")
        self.assertEqual(config.database_path, DEFAULT_DATABASE_PATH)

    def test_from_env_uses_database_path_override(self):
        with patch.dict(
            os.environ,
            {
                "PROJECT_NAME": "Test Fitness",
                "DATABASE_PATH": "/tmp/test_fitness.db",
            },
            clear=True,
        ):
            config = AppConfig.from_env()

        self.assertEqual(config.project_name, "Test Fitness")
        self.assertEqual(config.database_path, Path("/tmp/test_fitness.db"))
