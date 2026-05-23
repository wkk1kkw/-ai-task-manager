from datetime import datetime, timezone
import click
from storage.json_store import JsonStore
from storage.path_utils import project_path, context_dir
from utils.console import echo


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
        raise click.ClickException(f"项目 '{project_name}' 不存在")
    tasks = store.load_tasks(project_name)
    if not tasks:
        raise click.ClickException(f"项目 '{project_name}' 下没有任务")
    t = next((t for t in tasks if t.id == task_id), None)
    if not t:
        raise click.ClickException(f"任务 ID '{task_id}' 不存在")
    t.assigned_to = agent
    t.assigned_agent_type = agent_type
    if t.status == "todo":
        t.status = "in_progress"
    t.updated_at = datetime.now(timezone.utc).isoformat()
    store.save_tasks(project_name, tasks)

    # Write context file
    ctx_dir = context_dir(project_path(project_name))
    ctx_file = ctx_dir / f"{task_id}.md"
    ctx_file.write_text(
        f"# Task: {t.title}\n\n"
        f"Description: {t.description}\n"
        f"Assigned to: {agent} ({agent_type})\n"
        f"Status: {t.status}\n"
        f"Related files: {', '.join(t.related_files)}\n",
        encoding="utf-8"
    )

    echo(f"任务 '{t.title}' 已分配给 {agent} ({agent_type})")
    echo(f"   任务上下文请查看: context/{task_id}.md")


@agent_group.command()
@click.argument("project_name", required=False, default=None)
def status(project_name):
    """查看智能体任务状态"""
    store = get_store()
    if project_name:
        projects = [p for p in store.list_projects() if p.name == project_name]
        if not projects:
            raise click.ClickException(f"项目 '{project_name}' 不存在")
    else:
        projects = store.list_projects()
    if not projects:
        echo("没有项目")
        return
    for p in projects:
        tasks = store.load_tasks(p.name)
        assigned = [t for t in tasks if t.assigned_to]
        if not assigned:
            continue
        echo(f"\n项目 '{p.title}':")
        for t in assigned:
            echo(f"  [{t.id}] {t.title}")
            echo(f"       智能体: {t.assigned_to} ({t.assigned_agent_type})")
            echo(f"       状态: {t.status}")
            echo()
