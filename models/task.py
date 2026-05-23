from dataclasses import dataclass, field
from datetime import datetime, timezone

VALID_STATUSES = {"todo", "in_progress", "review", "done"}
VALID_PRIORITIES = {"low", "medium", "high"}


@dataclass
class Note:
    author: str
    content: str
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        return {"author": self.author, "content": self.content, "timestamp": self.timestamp}

    @classmethod
    def from_dict(cls, data: dict) -> "Note":
        return cls(**data)


@dataclass
class Task:
    id: str
    title: str
    project: str
    description: str = ""
    status: str = "todo"
    priority: str = "medium"
    assigned_to: str = ""
    assigned_agent_type: str = ""
    created_at: str = ""
    updated_at: str = ""
    completed_at: str = ""
    related_files: list = field(default_factory=list)
    notes: list = field(default_factory=list)

    def __post_init__(self):
        if self.status not in VALID_STATUSES:
            raise ValueError(f"Invalid status: {self.status}")
        if self.priority not in VALID_PRIORITIES:
            raise ValueError(f"Invalid priority: {self.priority}")
        now = datetime.now(timezone.utc).isoformat()
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "assigned_to": self.assigned_to,
            "assigned_agent_type": self.assigned_agent_type,
            "project": self.project,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "completed_at": self.completed_at,
            "related_files": self.related_files,
            "notes": [n.to_dict() for n in self.notes],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        notes_data = data.pop("notes", [])
        task = cls(**data)
        task.notes = [Note.from_dict(n) for n in notes_data]
        return task
