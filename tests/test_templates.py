from jinja2 import Environment, FileSystemLoader
from pathlib import Path


def test_kanban_template_renders():
    template_dir = Path(__file__).resolve().parent.parent / "templates"
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    template = env.get_template("kanban.html")
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
            "priority": "medium", "assigned_to": "agent-1",
            "related_files": ["src/file.ts"],
            "description": "Completed", "notes": [],
        },
    ]
    html = template.render(project=project, tasks=tasks, is_global=False)
    assert "<!DOCTYPE html>" in html
    assert "Test Project" in html
    assert "Todo Task" in html
    assert "Done Task" in html


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
