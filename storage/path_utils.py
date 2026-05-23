import os
from pathlib import Path


def get_projects_dir() -> Path:
    env = os.environ.get("TASKMAN_PROJECTS_DIR")
    if env:
        return Path(env)
    return Path(__file__).resolve().parent.parent / "projects"


def ensure_projects_dir() -> Path:
    d = get_projects_dir()
    d.mkdir(parents=True, exist_ok=True)
    return d


def project_path(name: str) -> Path:
    return ensure_projects_dir() / name


def project_json_path(proj_path: Path) -> Path:
    return proj_path / "project.json"


def tasks_json_path(proj_path: Path) -> Path:
    return proj_path / "tasks.json"


def context_dir(proj_path: Path) -> Path:
    d = proj_path / "context"
    d.mkdir(parents=True, exist_ok=True)
    return d


def reports_dir() -> Path:
    d = Path(__file__).resolve().parent.parent / "reports"
    d.mkdir(parents=True, exist_ok=True)
    return d
