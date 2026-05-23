# AI Task Manager

通过 Claude Code 对话管理开发项目的任务管理系统。支持项目/任务 CRUD、子智能体自动分配、HTML 看板进度展示，以及本地文件化存储以减少 token 消耗。

## 安装

```bash
# 进入项目目录
cd ai-task-manager

# 安装依赖
pip install -r requirements.txt

# 验证安装
python taskman.py --help
```

## 操作流程

### 一、创建项目

**对话方式：**
> "新建一个项目叫 website-redesign，标题是官网改版，代码放在 D:/projects/website-redesign"

系统会自动：
1. 创建 `projects/website-redesign/` 数据目录
2. 生成 `project.json`
3. 初始化空的 `tasks.json`
4. （可选）在指定路径创建项目脚手架

**CLI 方式：**
```bash
python taskman.py project create website-redesign \
  --title "官网改版" \
  --path "D:/projects/website-redesign"
```

### 二、添加任务

**对话方式：**
> "给 website-redesign 项目加一个任务：实现导航栏响应式布局，高优先级"

**CLI 方式：**
```bash
python taskman.py task add website-redesign \
  --title "实现导航栏响应式布局" \
  --priority high
```

### 三、分配子智能体

> "把导航栏任务分配给 agent 去实现"

工作流：
1. 系统标记任务为 `in_progress` 并记录分配的 agent
2. 系统生成任务上下文文件（包含描述、相关文件、验收标准）
3. 你确认后启动子 agent
4. 子 agent 完成后确认结果
5. 系统自动更新任务状态为 `done`，进度重新计算

### 四、查看进度

**对话方式：**
> "给我看 website-redesign 的进度"

**CLI 方式：**
```bash
python taskman.py report website-redesign
python taskman.py report open website-redesign   # 生成并打开浏览器
```

生成静态 HTML 看板（Kanban 四列布局），浏览器直接打开。

### 五、记录项目上下文

**对话方式：**
> "记录一条决策：前端使用 React + Tailwind CSS"

**CLI 方式：**
```bash
python taskman.py task note website-redesign <task-id> \
  --text "前端使用 React + Tailwind CSS"
```

Notes 存储在 `tasks.json` 中，作为后续开发记忆。

## 命令速查

### 项目管理

| 命令 | 说明 |
|------|------|
| `project create <name>` | 创建项目 |
| `project list` | 列出所有项目 |
| `project update <name> --status <s>` | 更新项目状态 |
| `project delete <name>` | 删除项目 |

### 任务管理

| 命令 | 说明 |
|------|------|
| `task add <project> --title <t>` | 添加任务 |
| `task list <project>` | 列出任务 |
| `task update <project> <id> --status <s>` | 更新任务状态 |
| `task delete <project> <id>` | 删除任务 |
| `task note <project> <id> --text <n>` | 添加笔记 |

### 子智能体

| 命令 | 说明 |
|------|------|
| `agent assign <project> <id> --agent <a>` | 分配 agent |
| `agent status [project]` | 查看 agent 任务状态 |

### 报告

| 命令 | 说明 |
|------|------|
| `report [project]` | 生成 HTML 看板 |
| `report open [project]` | 生成并打开浏览器 |

## 项目结构

```
ai-task-manager/
├── taskman.py                  # 主入口
├── commands/                   # CLI 命令模块
│   ├── project.py
│   ├── task.py
│   ├── agent.py
│   └── report.py
├── models/                     # 数据模型
├── storage/                    # JSON 存储层
├── templates/
│   └── kanban.html             # 看板模板
├── projects/                   # 项目数据
│   └── <project-name>/
│       ├── project.json
│       ├── tasks.json
│       └── context/            # 项目上下文
├── reports/                    # HTML 报告输出
├── requirements.txt
└── README.md
```

## Token 优化说明

数据以 JSON 文件在本地分层存储，智能体按需加载：

1. **目录扫描** — 仅看文件列表，了解项目存在
2. **摘要加载** — 读 `project.json`（< 1KB/个）
3. **按需加载** — 具体项目才读 `tasks.json`
4. **细粒度按需** — 提及任务时才加载 `context/` 文件

避免每次对话都加载全部数据，只在需要时读取对应文件。
