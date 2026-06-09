#!/usr/bin/env python3
"""
_organize.py — 知识库自动分类 & README 更新 & Git Push

工作目录：/home/node/.openclaw/workspace （= 知识库根目录）

职责：
  1. 将新文件自动分类到对应子目录（基于内容关键词打分）
  2. 更新 README.md 目录树
  3. Git add / commit / push（排除 OpenClaw 运行时文件）

安全规则：
  - spring/ 和 programming/ 跳过子域分类（历史保护）
  - 已有子目录中的文件不重新分类
  - 绝不提交：AGENTS.md, SOUL.md, TOOLS.md, USER.md, IDENTITY.md,
    HEARTBEAT.md, MEMORY.md, memory/, .openclaw/, .gitignore 等运行时文件
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# ──────────────────────────────────────────────
# 配置
# ──────────────────────────────────────────────

WORKSPACE = Path("/home/node/.openclaw/workspace")
GIT_REMOTE = "origin"
GIT_BRANCH = "master"

# 顶级领域及其说明
DOMAIN_PROFILES = {
    "ai-tools":       "AI 工具 & 编程助手",
    "database":       "数据库 & 缓存",
    "spring":         "Spring 框架",
    "sre":            "SRE & 运维",
    "system-design":  "系统设计 & 架构",
    "programming":    "编程语言 & 范式",
    "infrastructure": "基础设施 & 网络",
    "papers":         "论文笔记",
    "skills":         "OpenClaw Skills",
    "scripts":        "工具脚本",
    "image":          "文章图片",
}

# ai-tools 子域分类配置
SUBDOMAIN_PROFILES = {
    "harness": {
        "label": "agent Harness & 架构模式",
        "keywords": [
            "harness", "orchestrat", "agent loop", "workflow", "pipeline",
            "multi-agent", "agent orchestration", "claude code agent",
            "agent system", "agent stack", "agent infrastructure",
            "production agent", "scale agent", "agent architecture",
            "dynamic workflow", "mcp", "tool calling", "tool use",
            "function calling", "codex agent", "agentic workflow",
        ],
    },
    "inference": {
        "label": "推理 & 模型原理",
        "keywords": [
            "llm", "inference", "model", "gpu", "memory bandwidth",
            "token", "context window", "prompt engineering", "prompting",
            "transformer", "attention", "rag", "retrieval", "embedding",
            "fine-tun", "training", "sft", "rl", "reinforcement",
            "karpathy", "ai engineer", "roadmap", "ml",
        ],
    },
    "tooling": {
        "label": "工具配置 & 工作流",
        "keywords": [
            "claude code", "setup", "config", "trick", "hack",
            "plugin", "skill", "template", "workflow", "obsidian",
            "npx", "guide", "tips", "tutorial", "how to", "beginner",
            "cowork", "routines", "memory system", "hooks",
            "automation", "deploy", "sandbox", "isolation",
            "vibe coding", "cursor",
        ],
    },
    "autoresearch": {
        "label": "自动研究 & Agent",
        "keywords": [
            "autoresearch", "research agent", "morning brief",
            "self-improv", "evo", "evolving agent", "continual learn",
            "agent memory", "agent state", "persistence",
            "sleep", "diary", "reflection", "self-evaluat",
        ],
    },
    "career": {
        "label": "职业 & 工程实践",
        "keywords": [
            "career", "engineer", "senior", "promotion", "skill",
            "learn", "forward deployed", "consulting",
            "communication", "expertise", "fail",
            "agent engineer", "fullstack ai", "role",
        ],
    },
    "enterprise": {
        "label": "企业级方案",
        "keywords": [
            "enterprise", "production", "sandbox", "infrastructure",
            "security", "compliance", "governance", "privacy",
            "context layer", "data pipeline", "etl",
            "content production", "internal tool",
        ],
    },
    "patterns": {
        "label": "设计模式 & 最佳实践",
        "keywords": [
            "pattern", "best practice", "design pattern",
            "architecture pattern", "anti-pattern", "refactor",
            "testing strategy", "evaluation", "observability",
        ],
    },
    "ml-research": {
        "label": "ML 研究 & 论文",
        "keywords": [
            "paper", "arxiv", "research", "experiment",
            "benchmark", "state of the art", "sota",
            "dataset", "evaluation metric", "ablation",
        ],
    },
}

# 保护目录：这些目录下的文件不被重新分类到子域
SKIP_SUBDOMAIN_CLASSIFY = {"spring", "programming", "papers", "skills", "scripts", "image"}

# 绝不提交的路径模式（glob 相对路径）
EXCLUDE_PATTERNS = [
    "AGENTS.md", "SOUL.md", "TOOLS.md", "USER.md", "IDENTITY.md",
    "HEARTBEAT.md", "MEMORY.md",
    "memory/*.md",
    ".openclaw/**",
    ".gitignore",
    ".git/**",
    ".github/**",
    "node_modules/**",
    "browsers/**",
    "downloads/**",
    "TOOLS.md",
]

# git status
GIT_USER_NAME = "Jarvis II"
GIT_USER_EMAIL = "jarvis@openclaw.ai"


# ──────────────────────────────────────────────
# 核心函数
# ──────────────────────────────────────────────

def should_exclude(path: str) -> bool:
    """检查路径是否应被 git 排除"""
    for pat in EXCLUDE_PATTERNS:
        import fnmatch
        if fnmatch.fnmatch(path, pat):
            return True
    return False


def classify_by_content(filepath: Path, profiles: dict) -> str | None:
    """基于文件内容关键词打分，返回最佳匹配的子域 key"""
    try:
        text = filepath.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return None

    text_lower = text.lower()
    title = filepath.stem.lower().replace("-", " ")

    scores = {}
    for key, profile in profiles.items():
        score = 0
        for kw in profile["keywords"]:
            kw_lower = kw.lower()
            # 内容匹配
            count = text_lower.count(kw_lower)
            score += count
            # 标题额外加分
            if kw_lower in title:
                score += 5
        scores[key] = score

    # 没有关键词匹配
    if all(s == 0 for s in scores.values()):
        return None

    return max(scores, key=scores.get)


def get_all_markdown_files(base_dir: Path) -> list[Path]:
    """获取所有 .md 文件，排除 memory/ 和 workspace 根目录下运行时文件"""
    results = []
    for p in base_dir.rglob("*.md"):
        rel = p.relative_to(WORKSPACE).as_posix()
        if should_exclude(rel):
            continue
        # 排除根目录的运行时文件
        if p.parent == WORKSPACE and p.name in {
            "AGENTS.md", "SOUL.md", "TOOLS.md", "USER.md",
            "IDENTITY.md", "HEARTBEAT.md", "MEMORY.md", "README.md",
        }:
            continue
        results.append(p)
    return sorted(results)


def classify_new_root_files():
    """将 ai-tools/ 根部的 .md 文件移动到合适的子目录
    
    注意：只有 ai-tools/ 有子域分类配置，其他目录保持扁平。
    """
    moves = []
    for domain in DOMAIN_PROFILES:
        if domain != "ai-tools":
            continue
        domain_dir = WORKSPACE / domain
        if not domain_dir.is_dir():
            continue
        if domain in SKIP_SUBDOMAIN_CLASSIFY:
            continue

        # 只处理 domain 直接子级的 .md 文件（不在子目录中的）
        for f in sorted(domain_dir.glob("*.md")):
            if f.name == "README.md":
                continue
            sub_key = classify_by_content(f, SUBDOMAIN_PROFILES)
            if sub_key:
                target_dir = domain_dir / sub_key
                target_dir.mkdir(parents=True, exist_ok=True)
                target = target_dir / f.name
                if target.exists():
                    print(f"  ⚠️  目标已存在，跳过: {target}")
                    continue
                f.rename(target)
                moves.append((f.name, domain, sub_key))
                print(f"  📦 {domain}/{f.name} → {domain}/{sub_key}/")

    return moves


def generate_readme_tree(files: list[Path]) -> str:
    """生成 README.md 目录树"""
    lines = ["# 📚 知识库\n", "", "> 面试 & 技术知识库", "> 由 Jarvis II 按文件内容动态分类\n"]

    lines.append("## 📂 目录结构\n")

    # 按 DOMAIN_PROFILES 顺序输出
    seen_domains = set()
    for domain, desc in DOMAIN_PROFILES.items():
        domain_dir = WORKSPACE / domain
        if not domain_dir.is_dir():
            continue

        # 收集这个 domain 下的文件
        domain_files = [f for f in files if f.parent == domain_dir or domain_dir in f.parents]

        # 获取子目录结构
        subdirs = sorted(d for d in domain_dir.iterdir() if d.is_dir() and not d.name.startswith("."))

        if not subdirs:
            # 扁平目录
            items = sorted(f for f in domain_files if f.parent == domain_dir)
            if items:
                lines.append(f"### {domain}/ (`{desc}`)")
                for item in items:
                    rel = item.relative_to(WORKSPACE).as_posix()
                    lines.append(f"  - `{rel}`")
                lines.append("")
        else:
            # 有子目录 → 先输出根目录文件，再按子目录分组
            root_items = sorted(f for f in domain_files if f.parent == domain_dir)
            if root_items:
                lines.append(f"### {domain}/ (`{desc}`)")
                for item in root_items:
                    rel = item.relative_to(WORKSPACE).as_posix()
                    lines.append(f"  - `{rel}`")
                lines.append("")

            for sd in subdirs:
                sd_items = sorted(f for f in domain_files if f.parent == sd)
                if not sd_items:
                    continue
                rel_sd = sd.relative_to(WORKSPACE).as_posix()
                lines.append(f"### {rel_sd}/ (`{rel_sd}`)")
                for item in sd_items:
                    rel = item.relative_to(WORKSPACE).as_posix()
                    lines.append(f"  - `{rel}`")
                lines.append("")

        seen_domains.add(domain)

    # 处理不在 DOMAIN_PROFILES 中的目录
    for d in sorted(WORKSPACE.iterdir()):
        if not d.is_dir() or d.name.startswith("."):
            continue
        if d.name in seen_domains:
            continue
        items = sorted(f for f in files if f.parent == d)
        if not items:
            continue
        lines.append(f"### {d.name}/")
        for item in items:
            rel = item.relative_to(WORKSPACE).as_posix()
            lines.append(f"  - `{rel}`")
        lines.append("")

    # 总计
    total = len(files)
    lines.append(f"---\n")
    lines.append(f"总计 **{total}** 篇知识文档\n")

    # 分类说明
    lines.append("## 🤖 分类说明\n")
    lines.append("本文档库按**内容关键词分析**自动分类（非 Tags 依赖）：\n")
    lines.append("1. 读取每个文档的**完整内容**（含代码示例）")
    lines.append("2. 提取技术关键词，对各领域**打分**")
    lines.append("3. Tags 作为**加分项**（+3/标签），不是主要条件")
    lines.append("4. 标题关键词额外加分（+5）")
    lines.append("5. 得分最高者胜出\n")

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines.append(f"_[自动生成于 {ts}]_\n")

    return "\n".join(lines) + "\n"


def update_readme(files: list[Path]):
    """更新 README.md"""
    content = generate_readme_tree(files)
    readme_path = WORKSPACE / "README.md"
    readme_path.write_text(content, encoding="utf-8")
    print(f"  ✅ README.md 已更新（{len(files)} 篇）")


def git_commit_and_push(moves: list, classify_count: int):
    """Git add / commit / push，排除运行时文件"""
    os.chdir(str(WORKSPACE))

    # git add — 只添加知识库文件 + skills + scripts
    # 先列出变动
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True, timeout=15
    )

    changes = []
    for line in result.stdout.strip().split("\n"):
        if not line.strip():
            continue
        status = line[:2].strip()
        path = line[3:].strip()
        if should_exclude(path):
            continue
        if path.startswith(".git") or path == "README.md":
            # README.md 会由我们手动 add
            continue
        changes.append((status, path))

    if not changes and not moves:
        print("  ℹ️  没有需要提交的变更")
        return

    # git add
    add_paths = ["README.md"]
    for _, path in changes:
        add_paths.append(path)

    if add_paths:
        subprocess.run(["git", "add", "--"] + add_paths, capture_output=True, timeout=15)

    # 检查是否有 staged 变更
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True, text=True, timeout=15
    )
    staged = result.stdout.strip()
    if not staged:
        print("  ℹ️  staged 为空，跳过 commit")
        return

    # commit
    commit_lines = ["chore: auto-organize knowledge base"]
    if moves:
        commit_lines.append("")
        for name, domain, sub in moves:
            commit_lines.append(f"- Move {domain}/{name} → {domain}/{sub}/")
    if classify_count > 0:
        commit_lines.append(f"- Auto-classified {classify_count} file(s)")

    commit_msg = "\n".join(commit_lines)

    subprocess.run(
        ["git", "-c", f"user.name={GIT_USER_NAME}",
         "-c", f"user.email={GIT_USER_EMAIL}",
         "commit", "-m", commit_msg],
        capture_output=True, timeout=15
    )
    print(f"  ✅ Commit 完成")

    # push
    result = subprocess.run(
        ["git", "push", GIT_REMOTE, GIT_BRANCH],
        capture_output=True, text=True, timeout=60
    )
    if result.returncode == 0:
        print(f"  ✅ Push 成功 → {GIT_REMOTE}/{GIT_BRANCH}")
    else:
        print(f"  ⚠️  Push 失败: {result.stderr.strip()}")
        print(f"  提示：可能需要配置 git credentials")


# ──────────────────────────────────────────────
# 主流程
# ──────────────────────────────────────────────

def main():
    print("=" * 50)
    print("📚 _organize.py — 知识库自动整理")
    print(f"   工作目录: {WORKSPACE}")
    print(f"   git remote: {GIT_REMOTE}")
    print("=" * 50)
    print()

    # Step 1: 分类新文件
    print("🔍 Step 1: 分类新文件...")
    moves = classify_new_root_files()
    print(f"   🔀 移动了 {len(moves)} 个文件\n")

    # Step 2: 收集所有文件
    print("📂 Step 2: 扫描知识库...")
    all_files = get_all_markdown_files(WORKSPACE)
    print(f"   📄 共 {len(all_files)} 篇文档\n")

    # Step 3: 更新 README
    print("📝 Step 3: 更新 README.md...")
    update_readme(all_files)
    print()

    # Step 4: Git commit & push
    print("🚀 Step 4: Git commit & push...")
    git_commit_and_push(moves, len(moves))
    print()

    print("✅ 完成！")
    return 0


if __name__ == "__main__":
    sys.exit(main())
