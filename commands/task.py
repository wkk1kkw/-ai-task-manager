import click
from storage.json_store import JsonStore
from utils.console import echo
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
        echo(f"项目 '{project_name}' 不存在")
        return
    tasks = store.load_tasks(project_name)
    task_id = str(len(tasks))
    t = Task(id=task_id, title=title, description=desc,
             priority=priority, project=project_name)
    tasks.append(t)
    store.save_tasks(project_name, tasks)
    store.update_progress(project_name)
    echo(f"任务 '{title}' 已添加到项目 '{project_name}' (ID: {task_id})")


@task_group.command(name="list")
@click.argument("project_name")
def list_tasks(project_name):
    """列出项目下所有任务"""
    store = get_store()
    project = store.load_project(project_name)
    if not project:
        echo(f"项目 '{project_name}' 不存在")
        return
    tasks = store.load_tasks(project_name)
    if not tasks:
        echo(f"项目 '{project_name}' 下没有任务")
        return
    priority_icon = {"high": "[高]", "medium": "[中]", "low": "[低]"}
    status_icon = {"todo": "[待办]", "in_progress": "[进行中]", "review": "[审查]", "done": "[完成]"}
    echo(f"\n项目 '{project.title}' 的任务列表:\n")
    for t in tasks:
        pi = priority_icon.get(t.priority, "")
        si = status_icon.get(t.status, "")
        agent = f"  [负责人: {t.assigned_to}]" if t.assigned_to else ""
        echo(f"  [{t.id}] {si} {t.title} {pi}{agent}")
        echo(f"       状态: {t.status}")
        if t.related_files:
            echo(f"       关联文件: {', '.join(t.related_files)}")
        echo()


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
        echo(f"项目 '{project_name}' 不存在或没有任务")
        return
    try:
        t = tasks[int(task_id)]
    except (IndexError, ValueError):
        echo(f"任务 ID '{task_id}' 不存在")
        return
    t.status = status
    if title:
        t.title = title
    if status == "done":
        import datetime
        t.completed_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    import datetime
    t.updated_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    store.save_tasks(project_name, tasks)
    store.update_progress(project_name)
    echo(f"任务 '{t.title}' 已更新为 {status}")


@task_group.command()
@click.argument("project_name")
@click.argument("task_id")
@click.confirmation_option(prompt="确认删除此任务?")
def delete(project_name, task_id):
    """删除任务"""
    store = get_store()
    tasks = store.load_tasks(project_name)
    if not tasks:
        echo(f"项目 '{project_name}' 不存在或没有任务")
        return
    try:
        t = tasks.pop(int(task_id))
    except (IndexError, ValueError):
        echo(f"任务 ID '{task_id}' 不存在")
        return
    store.save_tasks(project_name, tasks)
    store.update_progress(project_name)
    echo(f"任务 '{t.title}' 已删除")


@task_group.command()
@click.argument("project_name")
@click.argument("task_id")
@click.option("--text", prompt="笔记内容", help="笔记内容")
def note(project_name, task_id, text):
    """添加笔记到任务"""
    store = get_store()
    tasks = store.load_tasks(project_name)
    if not tasks:
        echo(f"项目 '{project_name}' 不存在或没有任务")
        return
    try:
        t = tasks[int(task_id)]
    except (IndexError, ValueError):
        echo(f"任务 ID '{task_id}' 不存在")
        return
    from models.task import Note
    t.notes.append(Note(author="user", content=text))
    import datetime
    t.updated_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    store.save_tasks(project_name, tasks)
    echo(f"笔记已添加到任务 '{t.title}'")
