import os
from dataclasses import dataclass
from pathlib import Path

DEFAULT_DATABASE_PATH = Path("instance/my_fitness_app.db")
DEFAULT_UPLOAD_DIRECTORY = Path("instance/uploads")


@dataclass(frozen=True)
class AppConfig:
    project_name: str = "my-fitness-app"
    database_path: Path = DEFAULT_DATABASE_PATH
    upload_directory: Path = DEFAULT_UPLOAD_DIRECTORY

    @classmethod
    def from_env(cls) -> "AppConfig":
        return cls(
            project_name=os.getenv("PROJECT_NAME", "my-fitness-app"),
            database_path=Path(os.getenv("DATABASE_PATH", str(DEFAULT_DATABASE_PATH))),
            upload_directory=Path(os.getenv("UPLOAD_DIRECTORY", str(DEFAULT_UPLOAD_DIRECTORY))),
        )
