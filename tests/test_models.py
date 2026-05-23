import json
from datetime import datetime
from models.project import Project
from models.task import Task, Note


class TestProject:
    def test_create_project_with_minimal_fields(self):
        p = Project(name="test-proj", title="Test", local_path="/tmp/test")
        assert p.name == "test-proj"
        assert p.status == "active"
        assert p.progress == 0.0
        assert p.created_at is not None

    def test_project_to_dict_roundtrip(self):
        p = Project(name="test", title="T", description="D", local_path="/tmp/t")
        d = p.to_dict()
        assert d["name"] == "test"
        assert d["progress"] == 0.0
        restored = Project.from_dict(d)
        assert restored.name == p.name
        assert restored.title == p.title
        assert restored.status == p.status

    def test_project_status_validation(self):
        import pytest
        with pytest.raises(ValueError):
            Project(name="x", title="x", local_path="/x", status="invalid")


class TestTask:
    def test_create_task_with_minimal_fields(self):
        t = Task(id="t1", title="My Task", project="test-proj")
        assert t.status == "todo"
        assert t.priority == "medium"
        assert t.notes == []

    def test_task_to_dict_roundtrip(self):
        t = Task(
            id="t1", title="Task", project="p1",
            status="in_progress", priority="high"
        )
        t.notes.append(Note(author="user", content="a note"))
        d = t.to_dict()
        restored = Task.from_dict(d)
        assert restored.id == "t1"
        assert restored.status == "in_progress"
        assert len(restored.notes) == 1
        assert restored.notes[0].content == "a note"

    def test_task_status_validation(self):
        import pytest
        with pytest.raises(ValueError):
            Task(id="t1", title="x", project="p", status="invalid_status")

    def test_task_priority_validation(self):
        import pytest
        with pytest.raises(ValueError):
            Task(id="t1", title="x", project="p", priority="invalid")
