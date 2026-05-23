from dataclasses import dataclass, field
from datetime import datetime, timezone

VALID_STATUSES = {"active", "paused", "completed", "archived"}


@dataclass
class Project:
    name: str
    title: str
    local_path: str
    description: str = ""
    status: str = "active"
    progress: float = 0.0
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self):
        if self.status not in VALID_STATUSES:
            raise ValueError(f"Invalid status: {self.status}. Must be one of {VALID_STATUSES}")
        now = datetime.now(timezone.utc).isoformat()
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "title": self.title,
            "description": self.description,
            "local_path": self.local_path,
            "status": self.status,
            "progress": self.progress,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Project":
        return cls(**data)
