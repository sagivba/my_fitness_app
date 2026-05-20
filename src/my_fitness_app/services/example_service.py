from my_fitness_app.model.example_model import HealthStatus


def get_welcome_message(project_name: str) -> str:
    return f"Welcome to {project_name}"


def get_health_status() -> dict[str, str]:
    status = HealthStatus(status="ok")
    return status.to_dict()
