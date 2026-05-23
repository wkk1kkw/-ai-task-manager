# AI Task Manager - 设计文档

> 通过 Claude Code 对话管理开发项目的 AI 任务管理系统
> 日期: 2026-05-23

## 1. 概述

AI Task Manager 是一个通过自然语言对话驱动的开发项目管理工具。用户可以与 Claude Code 对话来创建/管理项目和子任务，分配子智能体执行任务，并通过 HTML 看板直观查看进度。所有数据以 JSON 文件形式存储在本地，支持按需加载以优化 token 消耗。

### 核心能力

- 通过对话 + CLI 混合模式管理项目和任务
- 自动初始化新项目（创建目录结构、Git 仓库等）
- 分配子智能体（agent）自动执行任务
- 生成 HTML 看板展示项目进度
- 关联文件按需加载，减少 token 消耗

## 2. 架构

### 整体方案

Python CLI 工具（Click + Jinja2），零服务端依赖。

```
ai-task-manager/
├── taskman.py              # 主 CLI 入口
├── commands/
│   ├── __init__.py
│   ├── project.py          # 项目 CRUD
│   ├── task.py             # 任务 CRUD
│   ├── agent.py            # 子智能体分配
│   └── report.py           # HTML 报告生成
├── models/
│   ├── __init__.py
│   ├── project.py          # 项目数据模型
│   └── task.py             # 任务数据模型
├── storage/
│   ├── __init__.py
│   └── json_store.py       # JSON 文件读写
├── templates/
│   └── kanban.html         # Jinja2 看板模板
├── projects/               # 项目数据存储根目录
├── reports/                # HTML 报告输出目录
└── requirements.txt        # 依赖: jinja2, click
```

### 设计原则

- **高内聚低耦合**：每个命令模块独立，通过 storage 层访问数据
- **按需加载**：从不加载全部数据到内存，精确控制 token 消耗
- **不可变性**：所有数据操作读取后写入新文件，不原地修改
- **混合交互**：支持完整参数的非交互模式和问答式的交互模式

## 3. 数据模型

### Project（项目）

```json
{
  "name": "website-redesign",
  "title": "官网改版",
  "description": "公司官网重新设计",
  "local_path": "D:/projects/website-redesign",
  "status": "active",
  "created_at": "2026-05-23T10:00:00",
  "updated_at": "2026-05-23T10:00:00",
  "progress": 0.6
}
```

状态: `active` / `paused` / `completed` / `archived`

### Task（任务）

```json
{
  "id": "<uuid-or-slug>",
  "title": "实现导航栏响应式布局",
  "description": "在 mobile/tablet/desktop 三端适配导航栏",
  "status": "in_progress",
  "priority": "high",
  "assigned_to": "agent-1",
  "assigned_agent_type": "general-purpose",
  "project": "website-redesign",
  "created_at": "2026-05-23T10:00:00",
  "updated_at": "2026-05-23T10:00:00",
  "completed_at": null,
  "related_files": ["D:/projects/website-redesign/src/components/Nav.tsx"],
  "notes": [
    {
      "author": "user",
      "content": "注意 mobile 端需要汉堡菜单",
      "timestamp": "2026-05-23T10:05:00"
    }
  ]
}
```

状态: `todo` / `in_progress` / `review` / `done`

进度: `project.progress = done 任务数 / 总任务数`

## 4. 存储架构

### 文件组织

```
ai-task-manager/
└── projects/
    └── <project-name>/
        ├── project.json        # 项目元信息
        ├── tasks.json          # 任务列表
        └── context/            # 项目上下文
            ├── decisions.md
            ├── architecture.md
            └── learnings/
```

### Token 优化策略

1. **目录扫描** — 仅读文件列表，了解存在哪些项目
2. **摘要加载** — 读所有 `project.json`，了解概览（每文件 < 1KB）
3. **按需加载** — 具体项目才读 `tasks.json`
4. **细粒度按需** — 提及特定任务时加载对应 `context/` 文件
5. **任务上下文打包** — 子 agent 启动前生成仅含该任务所需信息的上下文文件

## 5. CLI 命令设计

```
# 项目管理
taskman project create <name> --title <title> --path <dir>
taskman project list
taskman project update <name> --status <status>
taskman project delete <name>

# 任务管理
taskman task add <project> --title <title> --priority <p>
taskman task list <project>
taskman task update <project> <task-id> --status <s>
taskman task delete <project> <task-id>
taskman task note <project> <task-id> --text <note>

# 子智能体分配
taskman agent assign <project> <task-id> --agent <agent>
taskman agent status [project]

# HTML 报告
taskman report [project]
taskman report open [project]
```

所有命令支持交互模式（无参数时自动进入问答）。

### 子智能体工作流

1. 用户指令 → 系统标记任务 `assigned_to: "agent-X"`, `status: "in_progress"`
2. 生成任务上下文文件（描述 + 相关文件路径 + 验收标准）
3. 用户确认 → 启动子 agent 执行
4. 子 agent 完成 → 用户确认结果
5. 更新任务 `status: "done"`，进度自动重算

## 6. HTML 看板

基于 Jinja2 模板生成纯静态 HTML，浏览器直接打开，无服务端依赖。

### 视图层级

1. **全局概览** — 所有项目列表 + 进度条
2. **项目看板** — Kanban 四列布局（待办/进行中/审查中/已完成）
3. **任务详情** — 点击卡片展开详情

### 功能

- Kanban 四列布局，按任务状态分组
- 颜色编码（高优先级红色标记）
- 每个任务卡片显示：标题、优先级、负责人、关联文件、进度
- 全局项目概览页
- 自包含 HTML，无需服务端

### 文件产出

```
reports/
├── index.html                  # 全局项目看板
└── <project-name>/
    └── kanban.html             # 单个项目看板
```

## 7. README

项目根目录包含 `README.md`，涵盖以下内容：

- **项目简介** — AI Task Manager 是什么、解决什么问题
- **安装说明** — 依赖安装、CLI 配置
- **操作流程** — 从创建项目到完成任务的全流程指引（对话交互方式）
- **命令速查** — 所有 CLI 命令及参数快速参考
- **项目结构** — 本地文件组织说明
- **Token 优化说明** — 解释按需加载策略，帮助用户理解数据存储方式

## 8. 依赖

- `click` — CLI 命令框架
- `jinja2` — HTML 模板引擎

## 8. 后续规划

实现阶段按以下顺序迭代：

1. **存储层 + 数据模型** — JSON 读写、项目/任务 CRUD
2. **CLI 命令** — 项目管理、任务管理命令
3. **HTML 报告** — 看板生成
4. **子智能体集成** — agent 分配和任务上下文打包
5. **初始化能力** — 新项目脚手架（目录结构、Git 初始化）
