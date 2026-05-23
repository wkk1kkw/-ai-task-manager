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
        click.echo(f"项目 '{project_name}' 不存在")
        return
    tasks = store.load_tasks(project_name)
    if not tasks:
        click.echo(f"项目 '{project_name}' 下没有任务")
        return
    try:
        t = tasks[int(task_id)]
    except (IndexError, ValueError):
        click.echo(f"任务 ID '{task_id}' 不存在")
        return
    t.assigned_to = agent
    t.assigned_agent_type = agent_type
    if t.status == "todo":
        t.status = "in_progress"
    import datetime
    t.updated_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    store.save_tasks(project_name, tasks)
    click.echo(f"任务 '{t.title}' 已分配给 {agent} ({agent_type})")
    click.echo(f"   任务上下文请查看: context/{task_id}.md")


@agent_group.command()
@click.argument("project_name", required=False, default=None)
def status(project_name):
    """查看智能体任务状态"""
    store = get_store()
    if project_name:
        projects = [p for p in store.list_projects() if p.name == project_name]
        if not projects:
            click.echo(f"项目 '{project_name}' 不存在")
            return
    else:
        projects = store.list_projects()
    if not projects:
        click.echo("没有项目")
        return
    for p in projects:
        tasks = store.load_tasks(p.name)
        assigned = [t for t in tasks if t.assigned_to]
        if not assigned:
            continue
        click.echo(f"\n项目 '{p.title}':")
        for t in assigned:
            click.echo(f"  [{t.id}] {t.title}")
            click.echo(f"       智能体: {t.assigned_to} ({t.assigned_agent_type})")
            click.echo(f"       状态: {t.status}")
            click.echo()
