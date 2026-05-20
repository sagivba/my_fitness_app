from dataclasses import dataclass
import os


@dataclass(frozen=True)
class AppConfig:
    project_name: str = "my-python-project-template"

    @classmethod
    def from_env(cls) -> "AppConfig":
        return cls(
            project_name=os.getenv("PROJECT_NAME", "my-python-project-template"),
        )
