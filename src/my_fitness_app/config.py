import os
from dataclasses import dataclass
from pathlib import Path

DEFAULT_DATABASE_PATH = Path("instance/my_fitness_app.db")


@dataclass(frozen=True)
class AppConfig:
    project_name: str = "my-fitness-app"
    database_path: Path = DEFAULT_DATABASE_PATH

    @classmethod
    def from_env(cls) -> "AppConfig":
        return cls(
            project_name=os.getenv("PROJECT_NAME", "my-fitness-app"),
            database_path=Path(os.getenv("DATABASE_PATH", str(DEFAULT_DATABASE_PATH))),
        )
