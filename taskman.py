#!/usr/bin/env python3
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
