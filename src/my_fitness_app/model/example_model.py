from dataclasses import dataclass


@dataclass(frozen=True)
class HealthStatus:
    status: str

    def to_dict(self) -> dict[str, str]:
        return {"status": self.status}
