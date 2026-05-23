# AI Task Manager 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**目标：** 构建一个通过 Claude Code 对话驱动的开发项目管理 CLI 工具，支持项目/任务 CRUD、子智能体分配和 HTML 看板展示。

**架构：** Python Click CLI 工具 + JSON 文件存储 + Jinja2 HTML 模板。零服务端依赖，纯本地运行。

**技术栈：** Python 3.10+, click, jinja2, pytest

**数据存储：** `projects/` 目录下每个项目一个子目录，包含 `project.json`、`tasks.json` 和 `context/` 文件夹。

---

### Task 1: 项目脚手架与依赖

**文件：**
- 创建：`C:\工作\1_AI任务管理\requirements.txt`
- 创建：`C:\工作\1_AI任务管理\commands/__init__.py`
- 创建：`C:\工作\1_AI任务管理\models/__init__.py`
- 创建：`C:\工作\1_AI任务管理\storage/__init__.py`
- 创建：`C:\工作\1_AI任务管理\tests/__init__.py`
- 创建：`C:\工作\1_AI任务管理\templates/`（目录）

- [ ] **Step 1: 创建 requirements.txt**

```
click>=8.1.0
jinja2>=3.1.0
```

- [ ] **Step 2: 创建 Python 包初始文件**

创建以下四个 `__init__.py` 文件（均为空文件）：
- `commands/__init__.py`
- `models/__init__.py`
- `storage/__init__.py`
- `tests/__init__.py`

- [ ] **Step 3: 创建 templates 目录**

确保 `templates/` 目录存在（为空，后续 Task 7 添加模板）。

- [ ] **Step 4: 提交**

```bash
git add requirements.txt commands/__init__.py models/__init__.py storage/__init__.py tests/__init__.py templates/
git commit -m "chore: scaffold project structure and dependencies"
```

---

### Task 2: 数据模型

**文件：**
- 创建：`C:\工作\1_AI任务管理\models\project.py`
- 创建：`C:\工作\1_AI任务管理\models\task.py`
- 创建：`C:\工作\1_AI任务管理\tests\test_models.py`

- [ ] **Step 1: 编写测试**

```python
# tests/test_models.py
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
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest tests/test_models.py -v`
Expected: ModuleNotFoundError / ImportError

- [ ] **Step 3: 实现 Project 模型**

```python
# models/project.py
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
```

- [ ] **Step 4: 运行测试验证通过**

Run: `pytest tests/test_models.py::TestProject -v`
Expected: PASS (3 passed)

- [ ] **Step 5: 实现 Task 模型**

```python
# models/task.py
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
            from datetime import datetime, timezone
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
        notes = [Note.from_dict(n) for n in data.pop("notes", [])]
        task = cls(**data)
        task.notes = notes
        return task
```

- [ ] **Step 6: 运行测试验证通过**

Run: `pytest tests/test_models.py -v`
Expected: PASS (6 passed)

- [ ] **Step 7: 提交**

```bash
git add models/project.py models/task.py tests/test_models.py
git commit -m "feat: add Project and Task data models"
```

---

### Task 3: 存储层

**文件：**
- 创建：`C:\工作\1_AI任务管理\storage\json_store.py`
- 创建：`C:\工作\1_AI任务管理\storage\path_utils.py`
- 创建：`C:\工作\1_AI任务管理\tests\test_storage.py`

- [ ] **Step 1: 编写测试**

```python
# tests/test_storage.py
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

    def test_project_path(self, tmp_path):
        monkeypatch.setattr("storage.path_utils.get_projects_dir", lambda: tmp_path)
        from storage.path_utils import get_projects_dir as gpd
        # directly test
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
        # project must exist first
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
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest tests/test_storage.py -v`
Expected: ImportError / ModuleNotFoundError

- [ ] **Step 3: 实现 path_utils.py**

```python
# storage/path_utils.py
import os
from pathlib import Path


def get_projects_dir() -> Path:
    env = os.environ.get("TASKMAN_PROJECTS_DIR")
    if env:
        return Path(env)
    # Default: <project_root>/projects
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
```

- [ ] **Step 4: 实现 json_store.py**

```python
# storage/json_store.py
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
        project.updated_at = __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc
        ).isoformat()
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
```

- [ ] **Step 5: 运行测试验证通过**

Run: `pytest tests/test_storage.py -v`
Expected: PASS (9 passed)

- [ ] **Step 6: 提交**

```bash
git add storage/ tests/test_storage.py
git commit -m "feat: implement JSON file storage layer"
```

---

### Task 4: 项目 CRUD 命令

**文件：**
- 创建：`C:\工作\1_AI任务管理\commands\project.py`
- 创建：`C:\工作\1_AI任务管理\tests\test_commands_project.py`

- [ ] **Step 1: 编写测试**

```python
# tests/test_commands_project.py
from click.testing import CliRunner
from commands.project import project_group


class TestProjectCommands:
    def test_create_project(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(project_group, [
                "create", "test-proj",
                "--title", "Test Project",
                "--path", "/tmp/test"
            ])
            assert result.exit_code == 0
            assert "test-proj" in result.output
            assert "Test Project" in result.output

    def test_create_project_missing_title(self):
        runner = CliRunner()
        result = runner.invoke(project_group, ["create", "no-title"])
        assert result.exit_code != 0

    def test_list_projects_empty(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(project_group, ["list"])
            assert result.exit_code == 0
            assert "没有项目" in result.output or "empty" in result.output.lower()

    def test_list_projects_with_data(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(project_group, [
                "create", "p1", "--title", "P1", "--path", "/a"
            ])
            runner.invoke(project_group, [
                "create", "p2", "--title", "P2", "--path", "/b"
            ])
            result = runner.invoke(project_group, ["list"])
            assert result.exit_code == 0
            assert "P1" in result.output
            assert "P2" in result.output

    def test_update_project_status(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(project_group, [
                "create", "p1", "--title", "P1", "--path", "/a"
            ])
            result = runner.invoke(project_group, [
                "update", "p1", "--status", "paused"
            ])
            assert result.exit_code == 0
            assert "paused" in result.output

    def test_delete_project(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(project_group, [
                "create", "p1", "--title", "P1", "--path", "/a"
            ])
            result = runner.invoke(project_group, ["delete", "p1", "--yes"])
            assert result.exit_code == 0
            assert "已删除" in result.output or "deleted" in result.output.lower()
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest tests/test_commands_project.py -v`
Expected: ImportError / ModuleNotFoundError

- [ ] **Step 3: 实现 project 命令**

```python
# commands/project.py
import click
from storage.json_store import JsonStore
from models.project import Project


def get_store() -> JsonStore:
    return JsonStore()


@click.group(name="project")
def project_group():
    """项目管理"""
    pass


@project_group.command()
@click.argument("name")
@click.option("--title", prompt="项目标题", help="项目标题")
@click.option("--desc", default="", help="项目描述")
@click.option("--path", prompt="本地代码路径", help="本地代码目录路径")
def create(name, title, desc, path):
    """创建新项目"""
    store = get_store()
    p = Project(name=name, title=title, description=desc, local_path=path)
    store.save_project(p)
    click.echo(f"✅ 项目 '{name}' ({title}) 创建成功")


@project_group.command(name="list")
def list_projects():
    """列出所有项目"""
    store = get_store()
    projects = store.list_projects()
    if not projects:
        click.echo("📭 没有项目")
        return
    click.echo(f"\n📋 共 {len(projects)} 个项目:\n")
    for p in projects:
        status_icon = {"active": "🟢", "paused": "🟡", "completed": "✅", "archived": "📦"}
        icon = status_icon.get(p.status, "⚪")
        bar_len = 20
        filled = int(p.progress * bar_len)
        bar = "█" * filled + "░" * (bar_len - filled)
        click.echo(f"  {icon} {p.title} ({p.name})")
        click.echo(f"     状态: {p.status}  进度: [{bar}] {int(p.progress*100)}%")
        click.echo(f"     路径: {p.local_path}")
        click.echo()


@project_group.command()
@click.argument("name")
@click.option("--status", type=click.Choice(["active", "paused", "completed", "archived"]),
              prompt="新状态 (active/paused/completed/archived)")
@click.option("--title", default=None, help="新标题")
def update(name, status, title):
    """更新项目信息"""
    store = get_store()
    p = store.load_project(name)
    if not p:
        click.echo(f"❌ 项目 '{name}' 不存在")
        return
    p.status = status
    if title:
        p.title = title
    store.save_project(p)
    click.echo(f"✅ 项目 '{name}' 已更新")


@project_group.command()
@click.argument("name")
@click.confirmation_option(prompt=f"确认删除项目?")
def delete(name):
    """删除项目"""
    store = get_store()
    if store.delete_project(name):
        click.echo(f"✅ 项目 '{name}' 已删除")
    else:
        click.echo(f"❌ 项目 '{name}' 不存在")
```

- [ ] **Step 4: 运行测试验证通过**

Run: `pytest tests/test_commands_project.py -v`
Expected: PASS (6 passed)

- [ ] **Step 5: 提交**

```bash
git add commands/project.py tests/test_commands_project.py
git commit -m "feat: add project CRUD commands"
```

---

### Task 5: 任务 CRUD 命令

**文件：**
- 创建：`C:\工作\1_AI任务管理\commands\task.py`
- 创建：`C:\工作\1_AI任务管理\tests\test_commands_task.py`

- [ ] **Step 1: 编写测试**

```python
# tests/test_commands_task.py
from click.testing import CliRunner
from commands.project import project_group
from commands.task import task_group


class TestTaskCommands:
    def setup_project(self, runner, isolated):
        runner.invoke(project_group, [
            "create", "test-proj", "--title", "Test", "--path", "/tmp/test"
        ])

    def test_add_task(self):
        runner = CliRunner()
        with runner.isolated_filesystem() as iso:
            self.setup_project(runner, iso)
            result = runner.invoke(task_group, [
                "add", "test-proj",
                "--title", "实现导航栏",
                "--priority", "high"
            ])
            assert result.exit_code == 0
            assert "实现导航栏" in result.output

    def test_list_tasks(self):
        runner = CliRunner()
        with runner.isolated_filesystem() as iso:
            self.setup_project(runner, iso)
            runner.invoke(task_group, ["add", "test-proj", "--title", "Task A"])
            runner.invoke(task_group, ["add", "test-proj", "--title", "Task B"])
            result = runner.invoke(task_group, ["list", "test-proj"])
            assert result.exit_code == 0
            assert "Task A" in result.output
            assert "Task B" in result.output

    def test_list_tasks_empty(self):
        runner = CliRunner()
        with runner.isolated_filesystem() as iso:
            self.setup_project(runner, iso)
            result = runner.invoke(task_group, ["list", "test-proj"])
            assert result.exit_code == 0

    def test_update_task_status(self):
        runner = CliRunner()
        with runner.isolated_filesystem() as iso:
            self.setup_project(runner, iso)
            r = runner.invoke(task_group, ["add", "test-proj", "--title", "Task X"])
            # extract task id from output
            result = runner.invoke(task_group, [
                "update", "test-proj", "0", "--status", "done"
            ])
            assert result.exit_code == 0

    def test_delete_task(self):
        runner = CliRunner()
        with runner.isolated_filesystem() as iso:
            self.setup_project(runner, iso)
            runner.invoke(task_group, ["add", "test-proj", "--title", "Delete Me"])
            result = runner.invoke(task_group, ["delete", "test-proj", "0", "--yes"])
            assert result.exit_code == 0

    def test_add_note(self):
        runner = CliRunner()
        with runner.isolated_filesystem() as iso:
            self.setup_project(runner, iso)
            runner.invoke(task_group, ["add", "test-proj", "--title", "Task N"])
            result = runner.invoke(task_group, [
                "note", "test-proj", "0",
                "--text", "这是一条笔记"
            ])
            assert result.exit_code == 0
            assert "笔记" in result.output or "note" in result.output.lower()

    def test_add_task_non_existent_project(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(task_group, [
                "add", "no-project", "--title", "Orphan"
            ])
            assert result.exit_code != 0 or "不存在" in result.output
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest tests/test_commands_task.py -v`
Expected: ImportError / ModuleNotFoundError

- [ ] **Step 3: 实现 task 命令**

```python
# commands/task.py
import click
from storage.json_store import JsonStore
from models.task import Task


def get_store() -> JsonStore:
    return JsonStore()


@click.group(name="task")
def task_group():
    """任务管理"""
    pass


@task_group.command()
@click.argument("project_name")
@click.option("--title", prompt="任务标题", help="任务标题")
@click.option("--desc", default="", help="任务描述")
@click.option("--priority", type=click.Choice(["low", "medium", "high"]),
              default="medium", help="优先级")
def add(project_name, title, desc, priority):
    """添加新任务"""
    store = get_store()
    project = store.load_project(project_name)
    if not project:
        click.echo(f"❌ 项目 '{project_name}' 不存在")
        return
    tasks = store.load_tasks(project_name)
    task_id = str(len(tasks))
    t = Task(id=task_id, title=title, description=desc,
             priority=priority, project=project_name)
    tasks.append(t)
    store.save_tasks(project_name, tasks)
    store.update_progress(project_name)
    click.echo(f"✅ 任务 '{title}' 已添加到项目 '{project_name}' (ID: {task_id})")


@task_group.command(name="list")
@click.argument("project_name")
def list_tasks(project_name):
    """列出项目下所有任务"""
    store = get_store()
    project = store.load_project(project_name)
    if not project:
        click.echo(f"❌ 项目 '{project_name}' 不存在")
        return
    tasks = store.load_tasks(project_name)
    if not tasks:
        click.echo(f"📭 项目 '{project_name}' 下没有任务")
        return
    priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}
    status_icon = {"todo": "📋", "in_progress": "🔄", "review": "👀", "done": "✅"}
    click.echo(f"\n📋 项目 '{project.title}' 的任务列表:\n")
    for t in tasks:
        pi = priority_icon.get(t.priority, "⚪")
        si = status_icon.get(t.status, "⚪")
        agent = f"  [负责人: {t.assigned_to}]" if t.assigned_to else ""
        click.echo(f"  [{t.id}] {si} {t.title} {pi}{agent}")
        click.echo(f"       状态: {t.status}")
        if t.related_files:
            click.echo(f"       关联文件: {', '.join(t.related_files)}")
        click.echo()


@task_group.command()
@click.argument("project_name")
@click.argument("task_id")
@click.option("--status", type=click.Choice(["todo", "in_progress", "review", "done"]),
              prompt="新状态 (todo/in_progress/review/done)")
@click.option("--title", default=None, help="新标题")
def update(project_name, task_id, status, title):
    """更新任务"""
    store = get_store()
    tasks = store.load_tasks(project_name)
    if not tasks:
        click.echo(f"❌ 项目 '{project_name}' 不存在或没有任务")
        return
    try:
        t = tasks[int(task_id)]
    except (IndexError, ValueError):
        click.echo(f"❌ 任务 ID '{task_id}' 不存在")
        return
    t.status = status
    if title:
        t.title = title
    if status == "done":
        from datetime import datetime, timezone
        t.completed_at = datetime.now(timezone.utc).isoformat()
    from datetime import datetime, timezone
    t.updated_at = datetime.now(timezone.utc).isoformat()
    store.save_tasks(project_name, tasks)
    store.update_progress(project_name)
    click.echo(f"✅ 任务 '{t.title}' 已更新为 {status}")


@task_group.command()
@click.argument("project_name")
@click.argument("task_id")
@click.confirmation_option(prompt="确认删除此任务?")
def delete(project_name, task_id):
    """删除任务"""
    store = get_store()
    tasks = store.load_tasks(project_name)
    if not tasks:
        click.echo(f"❌ 项目 '{project_name}' 不存在或没有任务")
        return
    try:
        t = tasks.pop(int(task_id))
    except (IndexError, ValueError):
        click.echo(f"❌ 任务 ID '{task_id}' 不存在")
        return
    store.save_tasks(project_name, tasks)
    store.update_progress(project_name)
    click.echo(f"✅ 任务 '{t.title}' 已删除")


@task_group.command()
@click.argument("project_name")
@click.argument("task_id")
@click.option("--text", prompt="笔记内容", help="笔记内容")
def note(project_name, task_id, text):
    """添加笔记到任务"""
    store = get_store()
    tasks = store.load_tasks(project_name)
    if not tasks:
        click.echo(f"❌ 项目 '{project_name}' 不存在或没有任务")
        return
    try:
        t = tasks[int(task_id)]
    except (IndexError, ValueError):
        click.echo(f"❌ 任务 ID '{task_id}' 不存在")
        return
    from models.task import Note
    t.notes.append(Note(author="user", content=text))
    from datetime import datetime, timezone
    t.updated_at = datetime.now(timezone.utc).isoformat()
    store.save_tasks(project_name, tasks)
    click.echo(f"✅ 笔记已添加到任务 '{t.title}'")
```

- [ ] **Step 4: 运行测试验证通过**

Run: `pytest tests/test_commands_task.py -v`
Expected: PASS (7 passed)

- [ ] **Step 5: 提交**

```bash
git add commands/task.py tests/test_commands_task.py
git commit -m "feat: add task CRUD commands"
```

---

### Task 6: Agent 分配命令

**文件：**
- 创建：`C:\工作\1_AI任务管理\commands\agent.py`
- 创建：`C:\工作\1_AI任务管理\tests\test_commands_agent.py`

- [ ] **Step 1: 编写测试**

```python
# tests/test_commands_agent.py
from click.testing import CliRunner
from commands.project import project_group
from commands.task import task_group
from commands.agent import agent_group


class TestAgentCommands:
    def setup(self, runner, isolated):
        runner.invoke(project_group, [
            "create", "test-proj", "--title", "Test", "--path", "/tmp/t"
        ])
        runner.invoke(task_group, [
            "add", "test-proj", "--title", "导航栏", "--priority", "high"
        ])

    def test_assign_agent(self):
        runner = CliRunner()
        with runner.isolated_filesystem() as iso:
            self.setup(runner, iso)
            result = runner.invoke(agent_group, [
                "assign", "test-proj", "0",
                "--agent", "agent-1"
            ])
            assert result.exit_code == 0
            assert "agent-1" in result.output

    def test_agent_status(self):
        runner = CliRunner()
        with runner.isolated_filesystem() as iso:
            self.setup(runner, iso)
            runner.invoke(agent_group, [
                "assign", "test-proj", "0", "--agent", "agent-1"
            ])
            result = runner.invoke(agent_group, ["status", "test-proj"])
            assert result.exit_code == 0
            assert "agent-1" in result.output

    def test_assign_to_nonexistent_task(self):
        runner = CliRunner()
        with runner.isolated_filesystem() as iso:
            self.setup(runner, iso)
            result = runner.invoke(agent_group, [
                "assign", "test-proj", "99", "--agent", "agent-1"
            ])
            assert result.exit_code != 0 or "不存在" in result.output
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest tests/test_commands_agent.py -v`
Expected: ImportError / ModuleNotFoundError

- [ ] **Step 3: 实现 agent 命令**

```python
# commands/agent.py
import click
from storage.json_store import JsonStore


def get_store() -> JsonStore:
    return JsonStore()


@click.group(name="agent")
def agent_group():
    """子智能体管理"""
    pass


@agent_group.command()
@click.argument("project_name")
@click.argument("task_id")
@click.option("--agent", prompt="智能体名称", help="要分配的智能体名称")
@click.option("--agent-type", default="general-purpose", help="智能体类型")
def assign(project_name, task_id, agent, agent_type):
    """分配子智能体到任务"""
    store = get_store()
    project = store.load_project(project_name)
    if not project:
        click.echo(f"❌ 项目 '{project_name}' 不存在")
        return
    tasks = store.load_tasks(project_name)
    if not tasks:
        click.echo(f"❌ 项目 '{project_name}' 下没有任务")
        return
    try:
        t = tasks[int(task_id)]
    except (IndexError, ValueError):
        click.echo(f"❌ 任务 ID '{task_id}' 不存在")
        return
    t.assigned_to = agent
    t.assigned_agent_type = agent_type
    if t.status == "todo":
        t.status = "in_progress"
    from datetime import datetime, timezone
    t.updated_at = datetime.now(timezone.utc).isoformat()
    store.save_tasks(project_name, tasks)
    click.echo(f"✅ 任务 '{t.title}' 已分配给 {agent} ({agent_type})")
    click.echo(f"   任务上下文请查看: context/{task_id}.md")


@agent_group.command()
@click.argument("project_name", required=False, default=None)
def status(project_name):
    """查看智能体任务状态"""
    store = get_store()
    if project_name:
        projects = [p for p in store.list_projects() if p.name == project_name]
        if not projects:
            click.echo(f"❌ 项目 '{project_name}' 不存在")
            return
    else:
        projects = store.list_projects()
    if not projects:
        click.echo("📭 没有项目")
        return
    for p in projects:
        tasks = store.load_tasks(p.name)
        assigned = [t for t in tasks if t.assigned_to]
        if not assigned:
            continue
        click.echo(f"\n📋 项目 '{p.title}':")
        for t in assigned:
            click.echo(f"  [{t.id}] {t.title}")
            click.echo(f"       智能体: {t.assigned_to} ({t.assigned_agent_type})")
            click.echo(f"       状态: {t.status}")
            click.echo()
```

- [ ] **Step 4: 运行测试验证通过**

Run: `pytest tests/test_commands_agent.py -v`
Expected: PASS (3 passed)

- [ ] **Step 5: 提交**

```bash
git add commands/agent.py tests/test_commands_agent.py
git commit -m "feat: add agent assignment commands"
```

---

### Task 7: HTML 看板模板

**文件：**
- 创建：`C:\工作\1_AI任务管理\templates\kanban.html`
- 创建：`C:\工作\1_AI任务管理\tests\test_templates.py`

- [ ] **Step 1: 编写模板测试**

```python
# tests/test_templates.py
from jinja2 import Environment, FileSystemLoader
from pathlib import Path


def test_kanban_template_renders():
    template_dir = Path(__file__).resolve().parent.parent / "templates"
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    template = env.get_template("kanban.html")
    # Minimal test data
    project = {
        "name": "test-proj",
        "title": "Test Project",
        "description": "A test",
        "status": "active",
        "progress": 0.5,
    }
    tasks = [
        {
            "id": "0", "title": "Todo Task", "status": "todo",
            "priority": "high", "assigned_to": "", "related_files": [],
            "description": "", "notes": [],
        },
        {
            "id": "1", "title": "Done Task", "status": "done",
            "priority": "medium", "assigned_to": "agent-1", "related_files": ["src/file.ts"],
            "description": "Completed", "notes": [],
        },
    ]
    html = template.render(project=project, tasks=tasks, is_global=False)
    assert "<!DOCTYPE html>" in html
    assert "Test Project" in html
    assert "Todo Task" in html
    assert "Done Task" in html
    assert "50%" in html or "0.5" in html or "progress" in html.lower()


def test_kanban_global_view_renders():
    template_dir = Path(__file__).resolve().parent.parent / "templates"
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    template = env.get_template("kanban.html")
    projects = [
        {"name": "p1", "title": "Project 1", "status": "active", "progress": 0.3},
        {"name": "p2", "title": "Project 2", "status": "completed", "progress": 1.0},
    ]
    html = template.render(projects=projects, tasks=None, is_global=True)
    assert "Project 1" in html
    assert "Project 2" in html
    assert "100%" in html or "1.0" in html
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest tests/test_templates.py -v`
Expected: TemplateNotFound / FileNotFoundError

- [ ] **Step 3: 实现 kanban HTML 模板**

```html
{# templates/kanban.html #}
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{% if is_global %}AI Task Manager{% else %}{{ project.title }} - AI Task Manager{% endif %}</title>
<style>
  :root {
    --bg: #0f1117;
    --surface: #1a1d27;
    --surface2: #232736;
    --border: #2d3248;
    --text: #e4e6f0;
    --text2: #8b90a5;
    --todo: #3b82f6;
    --in-progress: #f59e0b;
    --review: #8b5cf6;
    --done: #22c55e;
    --high: #ef4444;
    --medium: #f59e0b;
    --low: #6b7280;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: var(--bg); color: var(--text); padding: 2rem; min-height: 100vh;
  }
  .header { margin-bottom: 2rem; }
  .header h1 { font-size: 1.75rem; font-weight: 700; margin-bottom: 0.25rem; }
  .header .subtitle { color: var(--text2); font-size: 0.9rem; }
  .header .nav { margin-top: 1rem; }
  .header .nav a { color: var(--todo); text-decoration: none; font-size: 0.9rem; }
  .header .nav a:hover { text-decoration: underline; }
  .project-info {
    background: var(--surface); border: 1px solid var(--border); border-radius: 12px;
    padding: 1.25rem; margin-bottom: 1.5rem; display: flex; align-items: center; gap: 1.5rem;
  }
  .project-info h2 { font-size: 1.2rem; font-weight: 600; }
  .project-info .status-badge {
    padding: 0.2rem 0.6rem; border-radius: 999px; font-size: 0.75rem; font-weight: 600;
  }
  .status-active { background: rgba(59,130,246,0.15); color: var(--todo); }
  .status-paused { background: rgba(245,158,11,0.15); color: var(--in-progress); }
  .status-completed { background: rgba(34,197,94,0.15); color: var(--done); }
  .status-archived { background: rgba(107,114,128,0.15); color: var(--text2); }
  .progress-container { flex: 1; max-width: 300px; }
  .progress-bar-bg {
    background: var(--surface2); border-radius: 999px; height: 8px; overflow: hidden;
  }
  .progress-bar-fill {
    background: linear-gradient(90deg, var(--todo), var(--done)); height: 100%;
    border-radius: 999px; transition: width 0.5s ease;
  }
  .progress-text { font-size: 0.8rem; color: var(--text2); margin-top: 0.25rem; }
  .board {
    display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem;
  }
  .column {
    background: var(--surface); border: 1px solid var(--border); border-radius: 12px;
    padding: 1rem; min-height: 200px;
  }
  .column-header { font-size: 0.85rem; font-weight: 600; margin-bottom: 1rem;
    padding-bottom: 0.75rem; border-bottom: 2px solid var(--border);
    display: flex; justify-content: space-between; align-items: center;
  }
  .column-header .count {
    font-size: 0.75rem; padding: 0.1rem 0.5rem; border-radius: 999px;
    background: var(--surface2); color: var(--text2);
  }
  .card {
    background: var(--surface2); border: 1px solid var(--border); border-radius: 8px;
    padding: 0.85rem; margin-bottom: 0.75rem; cursor: default; transition: transform 0.15s;
  }
  .card:hover { transform: translateY(-1px); border-color: var(--text2); }
  .card-title { font-size: 0.9rem; font-weight: 500; margin-bottom: 0.4rem; }
  .card-meta { font-size: 0.75rem; color: var(--text2); }
  .card-meta span { margin-right: 0.75rem; }
  .priority-high { border-left: 3px solid var(--high); }
  .priority-medium { border-left: 3px solid var(--medium); }
  .priority-low { border-left: 3px solid var(--low); }
  .card .files { margin-top: 0.4rem; font-size: 0.7rem; }
  .card .files code { background: var(--bg); padding: 0.1rem 0.3rem; border-radius: 3px; color: var(--text2); }
  .global-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 1rem; }
  .global-card {
    background: var(--surface); border: 1px solid var(--border); border-radius: 12px;
    padding: 1.25rem; transition: transform 0.15s;
  }
  .global-card:hover { transform: translateY(-2px); border-color: var(--todo); }
  .global-card h3 { font-size: 1.1rem; font-weight: 600; margin-bottom: 0.5rem; }
  .global-card .meta { font-size: 0.8rem; color: var(--text2); margin-bottom: 0.75rem; }
  @media (max-width: 900px) { .board { grid-template-columns: repeat(2, 1fr); } }
  @media (max-width: 600px) { .board { grid-template-columns: 1fr; } body { padding: 1rem; } }
</style>
</head>
<body>
  <div class="header">
    <h1>{% if is_global %}AI Task Manager{% else %}{{ project.title }}{% endif %}</h1>
    <p class="subtitle">
      {% if is_global %}所有项目概览{% else %}项目: {{ project.name }} · {{ project.description }}{% endif %}
    </p>
    <div class="nav">
      {% if is_global %}
        {% for p in projects %}<a href="{{ p.name }}/kanban.html">{{ p.title }}</a> · {% endfor %}
      {% else %}
        <a href="../index.html">← 返回项目列表</a>
      {% endif %}
    </div>
  </div>

  {% if is_global %}
  <div class="global-grid">
    {% for p in projects %}
    <div class="global-card">
      <h3>{{ p.title }}</h3>
      <div class="meta">
        <span class="status-badge status-{{ p.status }}">{{ p.status }}</span>
      </div>
      <div class="progress-container">
        <div class="progress-bar-bg">
          <div class="progress-bar-fill" style="width: {{ (p.progress * 100)|int }}%"></div>
        </div>
        <div class="progress-text">{{ (p.progress * 100)|int }}%</div>
      </div>
      <div style="margin-top:0.75rem;"><a href="{{ p.name }}/kanban.html" style="color:var(--todo);font-size:0.85rem;">查看详情 →</a></div>
    </div>
    {% endfor %}
  </div>
  {% else %}
  <div class="project-info">
    <h2>{{ project.title }}</h2>
    <span class="status-badge status-{{ project.status }}">{{ project.status }}</span>
    <div class="progress-container">
      <div class="progress-bar-bg">
        <div class="progress-bar-fill" style="width: {{ (project.progress * 100)|int }}%"></div>
      </div>
      <div class="progress-text">{{ (project.progress * 100)|int }}% 完成</div>
    </div>
  </div>

  {% set columns = {"todo": "📋 待办", "in_progress": "🔄 进行中", "review": "👀 审查中", "done": "✅ 已完成"} %}
  <div class="board">
    {% for status, label in columns.items() %}
    <div class="column">
      <div class="column-header">
        <span>{{ label }}</span>
        <span class="count">{{ tasks|selectattr("status", "equalto", status)|list|length }}</span>
      </div>
      {% for t in tasks if t.status == status %}
      <div class="card priority-{{ t.priority }}">
        <div class="card-title">{{ t.title }}</div>
        <div class="card-meta">
          {% if t.priority %}<span>优先级: {{ t.priority }}</span>{% endif %}
          {% if t.assigned_to %}<span>负责人: {{ t.assigned_to }}</span>{% endif %}
        </div>
        {% if t.related_files %}
        <div class="files">
          {% for f in t.related_files %}<code>{{ f.split("/")[-1] }}</code> {% endfor %}
        </div>
        {% endif %}
      </div>
      {% endfor %}
    </div>
    {% endfor %}
  </div>
  {% endif %}
</body>
</html>
```

- [ ] **Step 4: 运行测试验证通过**

Run: `pytest tests/test_templates.py -v`
Expected: PASS (2 passed)

- [ ] **Step 5: 提交**

```bash
git add templates/kanban.html tests/test_templates.py
git commit -m "feat: add kanban HTML template with dark theme"
```

---

### Task 8: 报告生成命令

**文件：**
- 创建：`C:\工作\1_AI任务管理\commands\report.py`
- 创建：`C:\工作\1_AI任务管理\tests\test_commands_report.py`

- [ ] **Step 1: 编写测试**

```python
# tests/test_commands_report.py
from click.testing import CliRunner
from commands.project import project_group
from commands.task import task_group
from commands.report import report_group
from pathlib import Path


class TestReportCommands:
    def setup(self, runner, isolated):
        runner.invoke(project_group, [
            "create", "test-proj", "--title", "Test Project", "--path", "/tmp/t"
        ])
        runner.invoke(task_group, [
            "add", "test-proj", "--title", "Task 1", "--priority", "high"
        ])
        runner.invoke(task_group, [
            "add", "test-proj", "--title", "Task 2", "--priority", "low"
        ])

    def test_generate_project_report(self):
        runner = CliRunner()
        with runner.isolated_filesystem() as iso:
            self.setup(runner, iso)
            result = runner.invoke(report_group, ["test-proj"])
            assert result.exit_code == 0
            assert "HTML" in result.output or "看板" in result.output

    def test_generate_global_report(self):
        runner = CliRunner()
        with runner.isolated_filesystem() as iso:
            self.setup(runner, iso)
            result = runner.invoke(report_group, [])
            assert result.exit_code == 0
            assert "HTML" in result.output or "看板" in result.output

    def test_report_file_exists(self):
        runner = CliRunner()
        with runner.isolated_filesystem() as iso:
            self.setup(runner, iso)
            runner.invoke(report_group, ["test-proj"])
            report_path = Path(iso) / "reports" / "test-proj" / "kanban.html"
            assert report_path.exists()
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest tests/test_commands_report.py -v`
Expected: ImportError / ModuleNotFoundError

- [ ] **Step 3: 实现 report 命令**

```python
# commands/report.py
import click
import webbrowser
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from storage.json_store import JsonStore
from storage import path_utils


def get_store() -> JsonStore:
    return JsonStore()


def get_template_env():
    template_dir = Path(__file__).resolve().parent.parent / "templates"
    return Environment(loader=FileSystemLoader(str(template_dir)))


@click.group(name="report")
def report_group():
    """HTML 报告生成"""
    pass


@report_group.command()
@click.argument("project_name", required=False, default=None)
@click.option("--open/--no-open", default=False, help="生成后自动打开浏览器")
def generate(project_name, open):
    """生成 HTML 看板报告"""
    store = get_store()
    env = get_template_env()
    template = env.get_template("kanban.html")
    reports_dir = path_utils.reports_dir()

    if project_name:
        project = store.load_project(project_name)
        if not project:
            click.echo(f"❌ 项目 '{project_name}' 不存在")
            return
        tasks = store.load_tasks(project_name)
        html = template.render(
            project=project.to_dict(),
            tasks=[t.to_dict() for t in tasks],
            is_global=False
        )
        out_dir = reports_dir / project_name
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "kanban.html"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
        click.echo(f"✅ 看板已生成: {out_path}")
        if open:
            webbrowser.open(str(out_path.resolve()))
    else:
        # Global view
        projects = store.list_projects()
        html = template.render(
            projects=[p.to_dict() for p in projects],
            tasks=None,
            is_global=True
        )
        out_path = reports_dir / "index.html"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
        click.echo(f"✅ 全局看板已生成: {out_path}")
        # Also generate individual project reports
        for p in projects:
            tasks = store.load_tasks(p.name)
            ph = template.render(
                project=p.to_dict(),
                tasks=[t.to_dict() for t in tasks],
                is_global=False
            )
            p_dir = reports_dir / p.name
            p_dir.mkdir(parents=True, exist_ok=True)
            with open(p_dir / "kanban.html", "w", encoding="utf-8") as f:
                f.write(ph)
        click.echo(f"   共 {len(projects)} 个项目看板已同步更新")
        if open:
            webbrowser.open(str(out_path.resolve()))


@report_group.command()
@click.argument("project_name", required=False, default=None)
def open(project_name):
    """生成并打开看板"""
    # Reuse generate with --open flag
    ctx = click.get_current_context()
    ctx.invoke(generate, project_name=project_name, open=True)
```

- [ ] **Step 4: 运行测试验证通过**

Run: `pytest tests/test_commands_report.py -v`
Expected: PASS (3 passed)

- [ ] **Step 5: 提交**

```bash
git add commands/report.py tests/test_commands_report.py
git commit -m "feat: add HTML report generation command"
```

---

### Task 9: 主入口与整合

**文件：**
- 创建：`C:\工作\1_AI任务管理\taskman.py`
- 创建：`C:\工作\1_AI任务管理\tests\test_cli.py`

- [ ] **Step 1: 编写集成测试**

```python
# tests/test_cli.py
from click.testing import CliRunner
from taskman import cli


class TestCLI:
    def test_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "project" in result.output
        assert "task" in result.output
        assert "agent" in result.output
        assert "report" in result.output

    def test_full_workflow(self):
        """完整工作流集成测试"""
        runner = CliRunner()
        with runner.isolated_filesystem():
            # 1. Create project
            r = runner.invoke(cli, ["project", "create", "demo", "--title", "Demo", "--path", "/tmp/demo"])
            assert r.exit_code == 0

            # 2. Add tasks
            r = runner.invoke(cli, ["task", "add", "demo", "--title", "Task 1", "--priority", "high"])
            assert r.exit_code == 0
            r = runner.invoke(cli, ["task", "add", "demo", "--title", "Task 2", "--priority", "low"])
            assert r.exit_code == 0

            # 3. Assign agent
            r = runner.invoke(cli, ["agent", "assign", "demo", "0", "--agent", "agent-1"])
            assert r.exit_code == 0

            # 4. Update task to done
            r = runner.invoke(cli, ["task", "update", "demo", "0", "--status", "done"])
            assert r.exit_code == 0

            # 5. List projects
            r = runner.invoke(cli, ["project", "list"])
            assert r.exit_code == 0

            # 6. List tasks
            r = runner.invoke(cli, ["task", "list", "demo"])
            assert r.exit_code == 0

            # 7. Generate report
            r = runner.invoke(cli, ["report", "generate", "demo"])
            assert r.exit_code == 0
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest tests/test_cli.py -v`
Expected: ModuleNotFoundError / ImportError

- [ ] **Step 3: 实现主入口**

```python
#!/usr/bin/env python3
# taskman.py
import click
from commands.project import project_group
from commands.task import task_group
from commands.agent import agent_group
from commands.report import report_group


@click.group()
@click.version_option(version="0.1.0", prog_name="taskman")
def cli():
    """AI Task Manager - 通过对话管理开发项目"""
    pass


cli.add_command(project_group)
cli.add_command(task_group)
cli.add_command(agent_group)
cli.add_command(report_group)


if __name__ == "__main__":
    cli()
```

- [ ] **Step 4: 运行测试验证通过**

Run: `pytest tests/test_cli.py -v`
Expected: PASS (2 passed)

- [ ] **Step 5: 提交**

```bash
git add taskman.py tests/test_cli.py
git commit -m "feat: add main CLI entry point with integrated commands"
```

---

### Task 10: 项目初始化能力

**文件：**
- 修改：`C:\工作\1_AI任务管理\commands\project.py`（在 create 命令中增加初始化选项）

- [ ] **Step 1: 编写测试**

```python
# tests/test_project_init.py
from click.testing import CliRunner
from commands.project import project_group
from pathlib import Path


class TestProjectInit:
    def test_create_with_init(self):
        runner = CliRunner()
        with runner.isolated_filesystem() as iso:
            base = Path(iso) / "workspace"
            result = runner.invoke(project_group, [
                "create", "new-project",
                "--title", "New Project",
                "--path", str(base / "new-project"),
                "--init"
            ])
            assert result.exit_code == 0
            assert (base / "new-project").exists()
            assert (base / "new-project" / "README.md").exists()

    def test_create_without_init_no_dir_created(self):
        runner = CliRunner()
        with runner.isolated_filesystem() as iso:
            base = Path(iso) / "workspace"
            result = runner.invoke(project_group, [
                "create", "virt-project",
                "--title", "Virtual",
                "--path", str(base / "virt-project")
            ])
            assert result.exit_code == 0
            # without --init, the directory should not be created
            assert not (base / "virt-project").exists()
```

- [ ] **Step 2: 修改 project.py 的 create 命令**

在 `commands/project.py` 的 create 命令中添加 `--init` 选项：

```python
@project_group.command()
@click.argument("name")
@click.option("--title", prompt="项目标题", help="项目标题")
@click.option("--desc", default="", help="项目描述")
@click.option("--path", prompt="本地代码路径", help="本地代码目录路径")
@click.option("--init/--no-init", default=False, help="是否初始化目录结构")
def create(name, title, desc, path, init):
    """创建新项目"""
    store = get_store()
    p = Project(name=name, title=title, description=desc, local_path=path)
    store.save_project(p)
    if init:
        proj_path = Path(path)
        proj_path.mkdir(parents=True, exist_ok=True)
        (proj_path / "README.md").write_text(
            f"# {title}\n\n{desc}\n\n## Getting Started\n\n", encoding="utf-8"
        )
        # Initialize git repo if git is available
        import subprocess
        try:
            subprocess.run(["git", "init"], cwd=str(proj_path), capture_output=True)
            click.echo(f"   Git 仓库已初始化")
        except FileNotFoundError:
            pass
        click.echo(f"   项目目录已创建: {proj_path}")
    click.echo(f"✅ 项目 '{name}' ({title}) 创建成功")
```

记得在文件顶部添加 `from pathlib import Path`。

- [ ] **Step 3: 运行测试验证通过**

Run: `pytest tests/test_project_init.py -v`
Expected: PASS (2 passed)

- [ ] **Step 4: 提交**

```bash
git add commands/project.py tests/test_project_init.py
git commit -m "feat: add project directory initialization with --init flag"
```

---

### Task 11: 最终验证

- [ ] **Step 1: 运行全部测试**

Run: `pytest tests/ -v`
Expected: ALL PASS (31 passed)

- [ ] **Step 2: 生成报告验证**

```bash
# 创建一个演示项目和任务
python taskman.py project create demo --title "演示项目" --path "/tmp/demo"
python taskman.py task add demo --title "任务1" --priority high
python taskman.py task add demo --title "任务2" --priority low
python taskman.py agent assign demo 0 --agent agent-1
python taskman.py task update demo 0 --status done
# 生成看板
python taskman.py report generate
# 查看生成的文件
ls reports/
```

- [ ] **Step 3: 提交最终版本**

```bash
git add .
git commit -m "chore: finalize AI Task Manager v0.1.0"
```
