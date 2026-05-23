# AI Task Manager

此项目是一个通过 Claude Code 对话驱动的开发项目管理 CLI 工具。

## 核心指令

当用户提出任何与项目管理、任务管理、进度查看相关的请求时，**不要启动 brainstorming 或创建实现计划**，而是直接使用 `taskman` CLI 工具。

### 命令映射

| 用户意图 | 执行命令 |
|---------|---------|
| 创建/新建项目 | `python taskman.py project create <name> --title <title> --path <path>` |
| 查看所有项目 | `python taskman.py project list` |
| 更新项目状态 | `python taskman.py project update <name> --status <status>` |
| 删除项目 | `python taskman.py project delete <name>` |
| 添加任务 | `python taskman.py task add <project> --title <title> --priority <p>` |
| 查看任务列表 | `python taskman.py task list <project>` |
| 更新任务状态 | `python taskman.py task update <project> <id> --status <s>` |
| 删除任务 | `python taskman.py task delete <project> <id>` |
| 添加笔记 | `python taskman.py task note <project> <id> --text <note>` |
| 分配子智能体 | `python taskman.py agent assign <project> <task-id> --agent <name>` |
| 查看智能体状态 | `python taskman.py agent status [project]` |
| 生成看板 | `python taskman.py report generate [project]` |

### 注意事项

- 使用 `python3 taskman.py` 或完整路径的 Python，取决于环境
- 所有命令支持交互模式（不传必要参数时会自动提示输入）
- 项目数据存储在 `projects/` 目录（JSON 格式）
- 如果用户意图明显是项目管理操作，**直接执行命令**，无需反问确认

## 项目信息

- 工具路径：`C:\工作\1_AI任务管理\taskman.py`
- Python 路径：`/c/Users/Administrator/AppData/Local/Programs/Python/Launcher/py`
