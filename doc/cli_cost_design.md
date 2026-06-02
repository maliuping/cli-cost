# cli cost design

# 整体目标

做一个：

```Plain Text
终端优先（Terminal First）
本地优先（Local First）
结构化（SQLite）
可视化（Rich/Textual）
云同步（Notion）
```

的个人记账系统。

设计原则：

---

# 一、系统架构

整体：

```Plain Text
┌────────────────────┐
│ CLI 命令层         │
│ Typer / argparse   │
└─────────┬──────────┘
          │
┌─────────▼──────────┐
│ Service 层         │
│ add/list/stat      │
└─────────┬──────────┘
          │
┌─────────▼──────────┐
│ SQLite Repository  │
└─────────┬──────────┘
          │
 ┌────────▼───────┐
 │ SQLite DB      │
 └────────────────┘

额外模块：

- Rich 输出
- Textual TUI
- Notion Sync
- Rule Engine
- Export Engine
```

---

# 二、推荐技术栈

## CLI

推荐：

```Bash
Typer
```

Typer

原因：

- 比 argparse 现代

- 自动 help

- 类型提示舒服

- 非常适合工程化 CLI

---

## 数据库

```Plain Text
SQLite3
```

Python 原生支持：

```Python
import sqlite3
```

无需 ORM。

---

## 终端 UI

## Rich

Rich

负责：

- table

- color

- panel

- progress

---

## Textual

Textual

负责：

- 全屏 TUI

- dashboard

- interactive filtering

---

## Notion SDK

notion\-sdk\-py

---

# 三、项目目录结构

推荐：

```Plain Text
money/

├── m.py
├── pyproject.toml
├── requirements.txt
│
├── config/
│   ├── config.yaml
│   └── rules.yaml
│
├── data/
│   ├── money.db
│   └── backup/
│
├── core/
│   ├── db.py
│   ├── models.py
│   ├── service.py
│   ├── query.py
│   └── stats.py
│
├── cli/
│   ├── add.py
│   ├── list.py
│   ├── stat.py
│   ├── sync.py
│   └── tui.py
│
├── ui/
│   ├── rich_table.py
│   └── dashboard.py
│
├── sync/
│   ├── notion.py
│   └── mapper.py
│
├── export/
│   ├── csv_export.py
│   └── markdown_export.py
│
└── tests/
```

---

# 四、数据库设计（核心）

---

# 表 1：expenses

核心表。

```SQL
CREATE TABLE expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    ts DATETIME NOT NULL,

    amount REAL NOT NULL,

    category TEXT NOT NULL,

    subcategory TEXT,

    note TEXT,

    account TEXT DEFAULT 'cash',

    tags TEXT,

    location TEXT,

    notion_synced INTEGER DEFAULT 0,

    notion_page_id TEXT,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

# 字段说明

---

# 表 2：categories

```SQL
CREATE TABLE categories (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE,
    icon TEXT,
    budget REAL
);
```

---

# 表 3：accounts

```SQL
CREATE TABLE accounts (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE,
    type TEXT
);
```

例如：

```Plain Text
cash
visa
alipay
wechat
```

---

# 五、CLI 设计（重点）

---

# 快速录入

核心体验：

```Bash
m 32 lunch 麦当劳
```

等价于：

```Bash
m add 32 --category lunch --note 麦当劳
```

---

## 解析逻辑

规则：

```Plain Text
第一个数字 -> amount
第二个字段 -> category
剩余 -> note
```

---

## 更多例子

```Bash
m 18 coffee 瑞幸
m 50 taxi 出差
m 120 grocery ntuc
```

---

# 查看

## 今日消费

```Bash
m today
```

输出：

```Plain Text
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Today: 2026-05-23         ┃
┡━━━━━━━━━━╇━━━━━━╇━━━━━━━━━━┩
│ lunch   │ 32   │ 麦当劳   │
│ coffee  │ 18   │ 瑞幸     │
└─────────┴──────┴──────────┘

TOTAL: 50
```

---

## 月统计

```Bash
m month
```

输出：

```Plain Text
food        1200
coffee       380
taxi         520

TOTAL       4500
```

---

## 分类统计

```Bash
m stat category
```

---

## 搜索

```Bash
m grep 瑞幸
```

---

# 六、Rich UI 设计

Rich 负责：

- Table

- Tree

- Panel

- Markdown

- Progress

---

## 今日面板

```Plain Text
╭──── Today ────╮
│ food      50  │
│ coffee    18  │
│ taxi      20  │
╰────────────────╯
```

---

## 月度排行榜

```Plain Text
Top Categories

food      ██████████ 1200
taxi      ████        500
coffee    ██          200
```

---

# 七、Textual TUI 设计

命令：

```Bash
m tui
```

---

# Dashboard 页面

布局：

```Plain Text
┌────────────────────────────┐
│ Header                     │
├─────────────┬──────────────┤
│ Today List  │ Category Pie │
├─────────────┴──────────────┤
│ Monthly Trend              │
└────────────────────────────┘
```

---

# 支持功能

---

# 八、自动分类系统（很重要）

配置：

```YAML
rules:
  瑞幸: coffee
  星巴克: coffee
  麦当劳: food
  KFC: food
  grab: taxi
```

---

## 使用

```Bash
m 18 瑞幸
```

自动：

```Plain Text
category=coffee
```

---

# 九、Notion 同步设计

---

# Notion Database

建议建一个单独的 Notion database，用来承载本地 SQLite 的消费记录。

## 推荐属性

```Plain Text
Name            title        记录标题，建议用 category + amount 组合
Date            date         消费时间
Amount          number       金额
Category        rich_text    一级分类
Note            rich_text    备注
Account         select       账户
Tags            rich_text    标签
Location        rich_text    地点
SQLite ID       number       本地主键，便于追踪
Synced          checkbox     是否已同步
Page ID         rich_text    Notion 页面 ID
```

## 本地字段映射

```Plain Text
SQLite expenses.ts            -> Notion Date
SQLite expenses.amount        -> Notion Amount
SQLite expenses.category      -> Notion Category
SQLite expenses.note          -> Notion Note
SQLite expenses.notion_synced -> Notion Synced
SQLite expenses.notion_page_id -> Notion Page ID
```

当前代码里只实现了最小映射：

- `Date`
- `Amount`
- `Category`
- `Note`

后续可以继续补 `Account`、`Tags`、`Location`，但同步主流程不依赖它们。

---

# Sync 流程

```Plain Text
SQLite
   ↓
读取 notion_synced=0
   ↓
调用 Notion API 创建 page
   ↓
记录 notion_page_id
   ↓
标记 synced=1
```

## 同步策略

- 默认只同步 `notion_synced = 0` 的记录。
- 每条记录创建一个 Notion page。
- 如果页面创建成功，就写回 `notion_page_id`，然后把 `notion_synced` 标记为 `1`。
- 如果中途失败，已经成功同步的记录保持已同步状态，失败项下次可继续重试。
- 如果传入 `--limit`，只处理最早的若干条未同步记录，便于分批迁移。

## 命令行为

```Bash
m sync
```

等价于：

```Bash
m sync notion
```

输出示例：

```Plain Text
Synced 12 records
```

失败时应给出可操作的错误：

```Plain Text
Missing Notion config. Set NOTION_TOKEN and NOTION_DATABASE_ID.
```

## 配置来源

推荐两层配置：

1. `config.yaml` 作为项目级默认配置。
2. 环境变量作为覆盖项，适合本地开发和 CI。

```YAML
notion:
  token: xxx
  database_id: xxx
```

当前实现优先使用环境变量：

```Plain Text
NOTION_TOKEN
NOTION_DATABASE_ID
```

后续如果引入 `config.yaml`，建议保持环境变量优先级更高，避免在不同机器间手工修改配置文件。

---

# sync 命令

```Bash
m sync
```

输出：

```Plain Text
Synced 12 records
```

如果想只同步一部分记录：

```Bash
m sync --limit 10
```

或者显式调用：

```Bash
m sync notion --limit 10
```

---

# 十、配置文件设计

config\.yaml

```YAML
currency: SGD

default_account: visa

notion:
  token: xxx
  database_id: xxx
```

建议把这些值当成“运行时配置”，而不是硬编码在代码里。实际部署时，优先使用环境变量覆盖敏感信息，避免把 token 提交到仓库。

---

# 十一、导出设计

---

# CSV

```Bash
m export csv
```

生成：

```Plain Text
export/2026-05.csv
```

---

# Markdown

```Bash
m export md
```

适合：

- Obsidian

- GitHub

- 周报

---

# 十二、备份策略

---

# 自动备份

每次写入：

```Plain Text
money.db
↓
backup/money-20260523.db
```

---

# Git 管理（推荐）

```Bash
git init
```

然后：

```Bash
git commit -am "daily update"
```

非常适合纯文本财务系统。

---

# 十三、后续高级扩展

---

# OCR 小票

```Bash
m scan receipt.jpg
```

提取：

- 金额

- 商户

- 时间

---

# AI 自动分类

未来：

```Plain Text
“海底捞” -> food
“Grab” -> taxi
```

---

# Web Dashboard

未来：

```Plain Text
FastAPI + SQLite
```

---

# 多币种

增加：

```SQL
currency TEXT
exchange_rate REAL
```

---

# 十四、推荐开发顺序（非常关键）

不要一开始搞复杂。

---

# Phase 1（1 天）

先完成：

```Plain Text
SQLite
CLI add/list
Rich table
```

命令：

```Bash
m 32 lunch
m today
m month
```

---

# Phase 2

增加：

```Plain Text
rules auto category
export csv
```

---

# Phase 3

增加：

```Plain Text
Notion Sync
```

---

# Phase 4

增加：

```Plain Text
Textual TUI
```

---

# 十五、推荐最终体验

最终你会得到：

---

## 录入

```Bash
m 25 lunch
m 18 coffee
m 120 grocery ntuc
```

---

## 查看

```Bash
m today
m week
m month
m trend
```

---

## 同步

```Bash
m sync
```

---

## TUI

```Bash
m tui
```

---

# 十六、最关键的工程建议

## 不要：

```Plain Text
Notion-first
```

因为：

- API 慢

- 网络依赖

- 查询麻烦

- CLI 不舒服

---

## 一定：

```Plain Text
SQLite-first
Notion-second
```

这是整个系统最正确的架构。
