---
title: "npx skills add 完整流程解析 —— Skill 安装机制的源码剖析"
tags:
  - skills
  - npx-skills
  - skill-installation
  - vercel-labs
  - claude-code
  - agent-tools
  - skill-discovery
  - source-code-analysis
date: 2026-05-12
source: "https://github.com/vercel-labs/skills"
authors: "@lijigang"
---

# npx skills add 完整流程解析

> 基于 [vercel-labs/skills](https://github.com/vercel-labs/skills) npm 包 (v1.5.6) 源码分析

## 一、源码位置

| 文件 | 职责 |
|------|------|
| `bin/cli.mjs` | CLI 入口点 |
| `src/cli.ts` | 命令注册与参数解析 |
| `src/add.ts` | `add` 命令核心逻辑 (~58KB) |
| `src/installer.ts` | 文件安装（符号链接/复制） (~28KB) |
| `src/skills.ts` | Skill 发现与解析 (~8KB) |
| `src/agents.ts` | 51+ AI Agent 定义与检测 (~13KB) |
| `src/source-parser.ts` | 来源解析（GitHub/URL/本地路径） (~10KB) |
| `src/git.ts` | Git 仓库克隆 (~3KB) |
| `src/constants.ts` | 常量定义 |

## 二、完整执行流程

```
用户执行: npx skills add github.com/lijigang/ljg-skills
    │
    ▼
┌─────────────────────────────┐
│  1. 解析来源 (source-parser) │  github shorthand / URL / 本地路径
│     parseSource()           │  支持 #branch @skill-name 语法
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  2. Git 克隆 (git.ts)       │  git clone --depth 1 到临时目录
│     cloneRepo()             │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  3. 发现 Skills (skills.ts) │  递归搜索 SKILL.md / .md / .org 文件
│     discoverSkills()        │  解析 YAML frontmatter (name + description)
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  4. 检测已安装的 Agents      │  扫描机器上 51+ AI Agent
│     detectInstalledAgents() │  如: Claude Code, Copilot, Cursor...
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  5. 交互选择（如未指定参数）  │  选择 skills → 选择 agents → 选择 scope
│     promptForAgents() 等    │  全局(global) 或 项目(project)
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  6. 安装到文件系统           │  symlink 模式(默认) 或 copy 模式
│     installSkillForAgent()  │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  7. 更新锁文件              │  写入 skill-lock.json 记录安装状态
│                             │  支持 skills update 更新
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  8. Claude Code 启动时      │  扫描 ~/.claude/skills/ 和 .claude/skills/
│     自动注册斜杠命令         │  每个 skill 子目录 → /skill-name 命令
└─────────────────────────────┘
```

## 三、各步骤详解

### 3.1 来源解析 (`src/source-parser.ts`)

`parseSource()` 支持多种输入格式：

| 输入格式 | 示例 | 解析结果 |
|----------|------|----------|
| GitHub 简写 | `owner/repo` | `https://github.com/owner/repo` |
| GitHub URL | `github.com/owner/repo` | 完整 Git URL |
| 带 branch | `owner/repo#main` | 指定分支克隆 |
| 带 skill 过滤 | `owner/repo@skill-name` | 只安装指定 skill |
| 本地路径 | `./my-skills` | 直接使用本地目录 |
| GitLab | `gitlab.com/owner/repo` | GitLab 仓库 |

### 3.2 Skill 发现 (`src/skills.ts`)

`discoverSkills()` 的搜索优先级：

1. **优先目录**（按顺序搜索）：
   - 仓库根目录
   - `skills/`
   - `skills/.curated/`
   - `.claude/skills/`
   - 其他 25+ Agent 特定目录（如 `.github/prompts/`, `.cursor/rules/` 等）

2. **回退策略**：若优先目录未找到，递归搜索（最大深度 5）

3. **Skill 文件格式**：
   - 标准：`SKILL.md`，需包含 YAML frontmatter：
     ```yaml
     ---
     name: my-skill
     description: 描述信息
     ---
     skill 内容...
     ```
   - 非标准：普通 `.md` 或 `.org` 文件（如 ljg-skills 的格式），通过递归搜索回退机制发现

4. **解析器**：使用 `gray-matter` 库解析 frontmatter，验证 `name` 和 `description` 为必填字段

### 3.3 Agent 检测 (`src/agents.ts`)

定义了 51+ AI Agent，每个包含：

```typescript
{
  displayName: "Claude Code",
  skillsDir: ".claude/skills/",      // 项目级路径
  globalSkillsDir: "~/.claude/skills/" // 全局路径
}
```

`detectInstalledAgents()` 通过检查 Agent 的特征文件/目录判断是否已安装。

**通用 Agent**（amp, replit 等）直接读取 canonical 目录 `~/.agents/skills/`，无需额外安装步骤。

### 3.4 安装逻辑 (`src/installer.ts`)

#### 安装模式

| 模式 | 行为 | 适用场景 |
|------|------|----------|
| **Symlink**（默认） | 文件复制到 canonical 目录 → 从 Agent 目录创建符号链接 | 保持单一数据源，更新方便 |
| **Copy** | 文件直接复制到每个 Agent 目录 | 需要独立副本，或符号链接不可用 |

#### Symlink 模式流程

```
源文件 (git clone 临时目录)
    │
    ▼ 复制
Canonical 目录: ~/.agents/skills/ljg-paper/
    │
    ▼ 符号链接
Agent 目录: ~/.claude/skills/ljg-paper/ → ~/.agents/skills/ljg-paper/
```

#### Copy 模式流程

```
源文件 (git clone 临时目录)
    │
    ▼ 复制
Agent 目录: ~/.claude/skills/ljg-paper/
```

#### 安全检查

- `sanitizeName()`: 防止路径遍历攻击，转为 kebab-case，限制 255 字符
- `isPathSafe()`: 验证路径不超出目标基础目录
- 复制时排除: `.git`, `__pycache__`, `metadata.json`, dotfiles

### 3.5 锁文件 (`skill-lock.json`)

安装完成后在目标目录写入锁文件，记录：

```json
{
  "skills": [
    {
      "name": "ljg-paper",
      "source": "github.com/lijigang/ljg-skills",
      "installedAt": "2026-05-12T...",
      "version": "abc123..."  // git commit hash
    }
  ]
}
```

用途：支持 `skills update` 命令增量更新。

### 3.6 Claude Code 集成

安装完成后，Claude Code 的工作方式：

1. **启动时扫描**：Claude Code 启动时扫描 `~/.claude/skills/`（全局）和 `.claude/skills/`（项目级）
2. **注册命令**：每个 skill 子目录注册为一个斜杠命令
3. **执行时加载**：用户输入 `/ljg-paper` 时，Claude Code 读取对应目录下的 skill 文件内容作为 prompt 注入

```
~/.claude/skills/
├── ljg-paper/
│   └── ljg-paper.org (或 .md)
├── ljg-card/
│   └── ljg-card.org
└── ...

Claude Code 启动 → 扫描 → 注册:
  /ljg-paper  → 加载 ljg-paper.org 内容作为 prompt
  /ljg-card   → 加载 ljg-card.org 内容作为 prompt
```

## 四、关键路径映射

| 概念 | 路径 |
|------|------|
| Canonical 全局目录 | `~/.agents/skills/` |
| Canonical 项目目录 | `.agents/skills/` |
| Claude Code 全局目录 | `~/.claude/skills/` |
| Claude Code 项目目录 | `.claude/skills/` |
| Copilot 项目目录 | `.github/skills/` |
| Cursor 项目目录 | `.cursor/skills/` |
| 锁文件 | `skill-lock.json`（在 canonical 目录或 Agent 目录中） |

## 五、ljg-skills 为什么能工作

ljg-skills 仓库结构（非标准 SKILL.md 格式）：

```
ljg-skills/
├── ljg-paper.org
├── ljg-card.org
├── ljg-learn.org
└── ... (共 18 个 skill)
```

虽然不使用标准的 `SKILL.md` + YAML frontmatter 格式，但 `discoverSkills()` 的**递归搜索回退机制**会在优先目录找不到结果后，以最大深度 5 搜索整个仓库，发现这些 `.org` 文件并尝试解析。

安装后，这些文件被复制/symlink 到 `~/.claude/skills/ljg-paper/` 等目录，Claude Code 启动时扫描注册为 `/ljg-paper` 等斜杠命令。

## 六、`--all` 标志

```bash
npx skills add owner/repo --all
```

等价于：`--skill '*' --agent '*' -y`，即安装所有 skill 到所有检测到的 Agent，跳过交互确认。

---

## 与知识库其他文章的关联

- **[SKILLIFY: Skill Engineering Guide](skillify-skill-engineering-guide.md)** — 本文提供了 Skillify 理论的底层实现机制。Skillify 讨论的是怎样写出好的 Skill（约束 vs 文档、描述即路由器、三层成本模型等）。本文解析的是这些 Skill 文件如何通过 `npx skills` 系统安装到机器上、如何跨 51+ Agent 分发、如何通过符号链接保持单一数据源。两者构成
