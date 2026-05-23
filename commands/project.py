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
    click.echo(f"✅ 项目 '{name}' 已更新 (状态: {status})")


@project_group.command()
@click.argument("name")
@click.confirmation_option(prompt="确认删除项目?")
def delete(name):
    """删除项目"""
    store = get_store()
    if store.delete_project(name):
        click.echo(f"✅ 项目 '{name}' 已删除")
    else:
        click.echo(f"❌ 项目 '{name}' 不存在")
