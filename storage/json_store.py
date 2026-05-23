import datetime
import json
import shutil
from pathlib import Path
from typing import Optional

from models.project import Project
from models.task import Task
from storage import path_utils


class JsonStore:
    def __init__(self, base_dir: Optional[str] = None):
        if base_dir:
            self._base_dir = Path(base_dir)
        else:
            self._base_dir = path_utils.get_projects_dir()
        self._base_dir.mkdir(parents=True, exist_ok=True)

    def _proj_path(self, name: str) -> Path:
        return self._base_dir / name

    def _proj_json(self, name: str) -> Path:
        return self._proj_path(name) / "project.json"

    def _tasks_json(self, name: str) -> Path:
        return self._proj_path(name) / "tasks.json"

    def save_project(self, project: Project) -> None:
        proj_dir = self._proj_path(project.name)
        proj_dir.mkdir(parents=True, exist_ok=True)
        project.updated_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        with open(self._proj_json(project.name), "w", encoding="utf-8") as f:
            json.dump(project.to_dict(), f, indent=2, ensure_ascii=False)

    def load_project(self, name: str) -> Optional[Project]:
        path = self._proj_json(name)
        if not path.exists():
            return None
        with open(path, "r", encoding="utf-8") as f:
            return Project.from_dict(json.load(f))

    def save_tasks(self, project_name: str, tasks: list[Task]) -> None:
        proj_dir = self._proj_path(project_name)
        proj_dir.mkdir(parents=True, exist_ok=True)
        data = [t.to_dict() for t in tasks]
        with open(self._tasks_json(project_name), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load_tasks(self, project_name: str) -> list[Task]:
        path = self._tasks_json(project_name)
        if not path.exists():
            return []
        with open(path, "r", encoding="utf-8") as f:
            return [Task.from_dict(d) for d in json.load(f)]

    def list_projects(self) -> list[Project]:
        if not self._base_dir.exists():
            return []
        projects = []
        for entry in sorted(self._base_dir.iterdir()):
            if entry.is_dir() and (entry / "project.json").exists():
                p = self.load_project(entry.name)
                if p:
                    projects.append(p)
        return projects

    def delete_project(self, name: str) -> bool:
        proj_dir = self._proj_path(name)
        if proj_dir.exists():
            shutil.rmtree(proj_dir)
            return True
        return False

    def update_progress(self, project_name: str) -> None:
        tasks = self.load_tasks(project_name)
        if not tasks:
            return
        done = sum(1 for t in tasks if t.status == "done")
        progress = round(done / len(tasks), 2)
        p = self.load_project(project_name)
        if p:
            p.progress = progress
            self.save_project(p)
