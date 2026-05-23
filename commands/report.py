import click
import webbrowser
from utils.console import echo
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
@click.option("--open/--no-open", "open_browser", default=False, help="生成后自动打开浏览器")
def generate(project_name, open_browser):
    """生成 HTML 看板报告"""
    store = get_store()
    env = get_template_env()
    template = env.get_template("kanban.html")
    rep_dir = path_utils.reports_dir()

    if project_name:
        project = store.load_project(project_name)
        if not project:
            raise click.ClickException(f"项目 '{project_name}' 不存在")
        tasks = store.load_tasks(project_name)
        html = template.render(
            project=project.to_dict(),
            tasks=[t.to_dict() for t in tasks],
            is_global=False
        )
        out_dir = rep_dir / project_name
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "kanban.html"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
        echo(f"看板已生成: {out_path}")
        if open_browser:
            webbrowser.open(str(out_path.resolve()))
    else:
        projects = store.list_projects()
        html = template.render(
            projects=[p.to_dict() for p in projects],
            tasks=None,
            is_global=True
        )
        out_path = rep_dir / "index.html"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
        echo(f"全局看板已生成: {out_path}")
        for p in projects:
            tasks = store.load_tasks(p.name)
            ph = template.render(
                project=p.to_dict(),
                tasks=[t.to_dict() for t in tasks],
                is_global=False
            )
            p_dir = rep_dir / p.name
            p_dir.mkdir(parents=True, exist_ok=True)
            with open(p_dir / "kanban.html", "w", encoding="utf-8") as f:
                f.write(ph)
        echo(f"共 {len(projects)} 个项目看板已同步更新")
        if open_browser:
            webbrowser.open(str(out_path.resolve()))


@report_group.command(name="open")
@click.argument("project_name", required=False, default=None)
def cmd_open(project_name):
    """生成并打开看板"""
    ctx = click.get_current_context()
    ctx.invoke(generate, project_name=project_name, open_browser=True)
