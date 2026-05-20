import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    project_name: str = "my-fitness-app"

    @classmethod
    def from_env(cls) -> "AppConfig":
        return cls(
            project_name=os.getenv("PROJECT_NAME", "my-fitness-app"),
        )
