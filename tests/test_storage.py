import tempfile
from pathlib import Path
from storage.path_utils import get_projects_dir, project_path, project_json_path, tasks_json_path
from storage.json_store import JsonStore
from models.project import Project
from models.task import Task


class TestPathUtils:
    def test_get_projects_dir_uses_env_var(self, monkeypatch):
        monkeypatch.setenv("TASKMAN_PROJECTS_DIR", "/custom/path")
        assert get_projects_dir() == Path("/custom/path")

    def test_project_path_uses_projects_dir(self, tmp_path, monkeypatch):
        monkeypatch.setattr("storage.path_utils.get_projects_dir", lambda: tmp_path)
        path = project_path("my-project")
        assert path.name == "my-project"
        assert path.parent == tmp_path

    def test_project_json_path(self, tmp_path):
        path = project_json_path(tmp_path / "my-proj")
        assert path.name == "project.json"
        assert path.parent == tmp_path / "my-proj"

    def test_tasks_json_path(self, tmp_path):
        path = tasks_json_path(tmp_path / "my-proj")
        assert path.name == "tasks.json"
        assert path.parent == tmp_path / "my-proj"


class TestJsonStore:
    def test_save_and_load_project(self, tmp_path):
        store = JsonStore(base_dir=str(tmp_path))
        p = Project(name="test-p", title="Test", local_path="/tmp/x")
        store.save_project(p)

        loaded = store.load_project("test-p")
        assert loaded.name == "test-p"
        assert loaded.title == "Test"

    def test_save_and_load_tasks(self, tmp_path):
        store = JsonStore(base_dir=str(tmp_path))
        p = Project(name="test-p", title="Test", local_path="/tmp/x")
        store.save_project(p)

        tasks = [
            Task(id="t1", title="Task 1", project="test-p"),
            Task(id="t2", title="Task 2", project="test-p"),
        ]
        store.save_tasks("test-p", tasks)

        loaded = store.load_tasks("test-p")
        assert len(loaded) == 2
        assert loaded[0].id == "t1"
        assert loaded[1].title == "Task 2"

    def test_list_projects(self, tmp_path):
        store = JsonStore(base_dir=str(tmp_path))
        p1 = Project(name="p1", title="Project 1", local_path="/a")
        p2 = Project(name="p2", title="Project 2", local_path="/b")
        store.save_project(p1)
        store.save_project(p2)

        projects = store.list_projects()
        assert len(projects) == 2
        names = {p.name for p in projects}
        assert names == {"p1", "p2"}

    def test_delete_project(self, tmp_path):
        store = JsonStore(base_dir=str(tmp_path))
        p = Project(name="del-proj", title="Delete Me", local_path="/x")
        store.save_project(p)
        assert len(store.list_projects()) == 1

        store.delete_project("del-proj")
        assert len(store.list_projects()) == 0

    def test_load_nonexistent_project_returns_none(self, tmp_path):
        store = JsonStore(base_dir=str(tmp_path))
        assert store.load_project("nonexistent") is None

    def test_load_nonexistent_tasks_returns_empty_list(self, tmp_path):
        store = JsonStore(base_dir=str(tmp_path))
        assert store.load_tasks("nonexistent") == []

    def test_calculate_progress(self, tmp_path):
        store = JsonStore(base_dir=str(tmp_path))
        p = Project(name="prog-test", title="Progress", local_path="/p")
        store.save_project(p)

        tasks = [
            Task(id="t1", title="Done", project="prog-test", status="done"),
            Task(id="t2", title="Doing", project="prog-test", status="in_progress"),
            Task(id="t3", title="Todo", project="prog-test", status="todo"),
            Task(id="t4", title="Review", project="prog-test", status="review"),
            Task(id="t5", title="Done 2", project="prog-test", status="done"),
        ]
        store.save_tasks("prog-test", tasks)
        store.update_progress("prog-test")

        loaded = store.load_project("prog-test")
        assert loaded.progress == 0.4  # 2/5 = 0.4
