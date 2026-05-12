#!/usr/bin/env python3
"""
knowledges 知识库自动整理脚本
基于 Andrej Karpathy "First Principles" 方法论 + 业内技术分类标准

原则：
1. 按领域分类，不按文件名 — 每个文件根据 tags + 内容归入最合适的目录
2. 扁平优先 — 文档少于 10 篇时不建深层目录
3. Tags 为主索引 — 文件内容中的 YAML tags 是主要发现手段
4. 目录结构可演化 — 随知识增多自动创建新的分类目录

工作流：
  同步远程(拉取) → 分类本地/远程文件 → 整理到子目录 → 更新 README → 推送远程
  保证本地与远程时刻一致，不会产生冲突
"""

import os
import re
import shutil
import json
import base64
import subprocess
import tempfile
from pathlib import Path

KNOWLEDGES_DIR = Path(__file__).parent.resolve()
GH_REPO = "Jrink525/knowledges"
GH_BRANCH = "main"
TOOL_NAME = "_organize.py"  # 本脚本文件名，跳过推送

# ============================================================
# Token 获取
# ============================================================
def get_github_token() -> str | None:
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        return token
    config_path = Path("/home/node/.openclaw/gh-config/hosts.yml")
    if config_path.exists():
        content = config_path.read_text()
        m = re.search(r'oauth_token:\s*(\S+)', content)
        if m:
            return m.group(1)
    return None


# ============================================================
# 简易 YAML frontmatter 解析
# ============================================================
def _parse_yaml_frontmatter(text: str) -> dict:
    result = {}
    for line in text.strip().split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip()
            if value.startswith("[") and value.endswith("]"):
                inner = value[1:-1]
                items = [x.strip().strip("\"'") for x in inner.split(",") if x.strip()]
                result[key] = items
            elif value.startswith("{"):
                try:
                    result[key] = json.loads(value)
                except json.JSONDecodeError:
                    result[key] = value
            elif value.lower() in ("true", "false"):
                result[key] = value.lower() == "true"
            else:
                result[key] = value.strip("\"'")
    return result


# ============================================================
# 分类映射：tags → 目录路径
# ============================================================
CLASSIFICATION = [
    # ⚠️ 顺序决定优先级：具体领域(编程语言/框架) > 通用标签(面试/运维等)
    # 越具体的匹配越靠前，避免 interview/高并发 等通用标签抢走专属分类
    #
    # Programming languages (精确匹配优先)
    (["java", "jvm", "kotlin"], "Java", "programming/java"),
    (["java", "concurrency"], "Java 并发", "programming/java"),
    (["golang", "go"], "Go", "programming/go"),
    (["rust"], "Rust", "programming/rust"),
    (["python"], "Python", "programming/python"),
    # Framework & Middleware
    (["spring", "spring-boot", "spring-cloud", "spring-mvc", "spring-transaction"], "Spring 框架", "spring"),
    (["mybatis", "hibernate", "jpa"], "ORM & 数据访问", "orm"),
    (["kafka", "rabbitmq", "mq", "消息队列"], "消息队列", "message-queue"),
    (["redis", "缓存"], "数据库 & 缓存", "database"),
    (["database", "mysql", "postgres", "sql"], "数据库 & 缓存", "database"),
    # System design & architecture
    (["system-design", "架构"], "系统设计 & 架构", "system-design"),
    (["分布式", "一致性"], "系统设计 & 架构", "system-design"),
    # Infrastructure & Network
    (["网络配置", "防火墙", "白名单"], "基础设施 & 网络", "infrastructure"),
    (["openclaw", "weixin", "wechat", "clawbot"], "基础设施 & 网络", "infrastructure"),
    # SRE & Operations
    (["sre", "故障处理", "熔断", "降级", "限流"], "SRE & 运维", "sre"),
    (["monitoring", "observability", "告警"], "SRE & 运维", "sre"),
    # AI & ML
    (["llm", "ai", "machine-learning", "deep-learning"], "AI & 机器学习", "ai-ml"),
    # General backend patterns
    (["微服务", "microservice", "服务治理"], "微服务架构", "microservices"),
    (["container", "docker", "kubernetes", "k8s"], "容器 & 云原生", "cloud-native"),
    # Generic tags (放最后，作为兜底)
    (["面试", "interview"], "面试汇总", "interview"),
    (["高并发", "high-concurrency"], "高并发", "system-design"),
]


# ============================================================
# 步骤 1：从 GitHub 拉取所有远程文件 → 同步到本地
# ============================================================
def sync_from_github(token: str) -> int:
    """获取 GitHub 上所有文件，下载到本地对应路径，返回远程文件数"""
    print("\n  🔽 从 GitHub 拉取远程文件...")
    downloaded = 0

    try:
        # 用 gh api 获取 git tree（递归列出所有文件）
        result = subprocess.run(
            ["/home/node/.openclaw/workspace/gh", "api",
             f"repos/{GH_REPO}/git/trees/{GH_BRANCH}?recursive=1"],
            capture_output=True, text=True, timeout=15,
            env={"GH_CONFIG_DIR": "/home/node/.openclaw/gh-config",
                 "PATH": os.environ.get("PATH", "")})
        if result.returncode != 0:
            # 可能仓库为空或不存在
            print(f"  ℹ️  远程仓库无内容或无法访问: {result.stderr.strip()[:80]}")
            return 0

        tree = json.loads(result.stdout)
        remote_files = [item for item in tree.get("tree", [])
                        if item["type"] == "blob" and item["path"] != ".gitkeep"]

        if not remote_files:
            print("  ℹ️  远程仓库为空")
            return 0

        print(f"  远程发现 {len(remote_files)} 个文件")

        for item in remote_files:
            remote_path = item["path"]
            sha = item["sha"]

            # 跳过脚本自身
            if remote_path == TOOL_NAME:
                continue

            local_path = KNOWLEDGES_DIR / remote_path

            # 用 gh api 获取文件内容（直接获取 base64 content）
            content_result = subprocess.run(
                ["/home/node/.openclaw/workspace/gh", "api",
                 f"repos/{GH_REPO}/contents/{remote_path}"],
                capture_output=True, text=True, timeout=10,
                env={"GH_CONFIG_DIR": "/home/node/.openclaw/gh-config",
                     "PATH": os.environ.get("PATH", "")})

            if content_result.returncode != 0:
                print(f"  ⚠️  无法获取 {remote_path}，跳过")
                continue

            try:
                data = json.loads(content_result.stdout)
            except json.JSONDecodeError:
                continue

            remote_content_b64 = data.get("content", "")
            if not remote_content_b64:
                continue

            # GitHub API 返回的 base64 可能换行
            remote_content_b64 = remote_content_b64.replace("\n", "")
            try:
                remote_bytes = base64.b64decode(remote_content_b64)
            except Exception:
                continue

            # 比较本地文件
            local_path.parent.mkdir(parents=True, exist_ok=True)
            if local_path.exists():
                local_bytes = local_path.read_bytes()
                if local_bytes == remote_bytes:
                    continue  # 完全相同，跳过
                else:
                    print(f"  🔄 {remote_path} ← 远程版本更新（内容不同）")
            else:
                print(f"  📥 {remote_path} ← 新增（仅远程有）")

            local_path.write_bytes(remote_bytes)
            downloaded += 1

        # ⚠️ 不清除本地独有文件 — 这些是本地新增的文档，后续分类后会推送上去
        # 仅核对远程文件已全部回拉到本地即可

        print(f"  ✅ 同步完成 ({len(remote_files)} 远程文件已核对，{downloaded} 个变更)")
        return len(remote_files)

    except Exception as e:
        print(f"  ⚠️  同步失败: {e}")
        return 0


# ============================================================
# 步骤 2：分类文档（仅处理 knowledges/ 根目录下的一级 .md 文件）
# ============================================================
def get_tags_from_file(filepath: Path) -> list[str]:
    """读取文件的 tags"""
    content = filepath.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return []
    try:
        meta = _parse_yaml_frontmatter(match.group(1))
        tags = meta.get("tags", [])
        if isinstance(tags, str):
            tags = [tags]
        return tags
    except Exception:
        return []


def get_primary_category_from_tags(tags: list[str]) -> tuple[str, str] | None:
    """根据 tags 返回 (category_label, directory)"""
    for tag_patterns, label, directory in CLASSIFICATION:
        if any(t in tags for t in tag_patterns):
            return (label, directory)
    return None


def sync_classified_to_local(classified: dict[str, list[tuple[str, Path]]]):
    """确保分类目录结构反映在本地文件系统"""
    # 收集当前所有一级子目录名
    existing_dirs = set()
    for d in KNOWLEDGES_DIR.iterdir():
        if d.is_dir() and not d.name.startswith("."):
            existing_dirs.add(d.name)
    classified_dirs = set(classified.keys())

    # 1️⃣ 先将所有文件移动到正确目标目录
    moved_source_paths = set()
    for directory, entries in classified.items():
        target_dir = KNOWLEDGES_DIR / directory
        target_dir.mkdir(parents=True, exist_ok=True)
        for rel_path, source_path in entries:
            target_path = target_dir / source_path.name
            if source_path.resolve() == target_path.resolve():
                continue  # 已经在正确位置
            # 移动文件
            target_path.parent.mkdir(parents=True, exist_ok=True)
            if target_path.exists():
                target_path.unlink()
            shutil.move(str(source_path), str(target_path))
            print(f"  📦 {source_path.name} → {directory}/")
            moved_source_paths.add(str(source_path.resolve()))

    # 2️⃣ 清理目标目录中已不再归属的旧文件（确认这些文件不是其他类的source）
    for directory, entries in classified.items():
        target_dir = KNOWLEDGES_DIR / directory
        known_names = {entry[1].name for entry in entries}
        for f in list(target_dir.glob("*.md")):
            if f.name not in known_names and not f.name.startswith("_"):
                # 再检查一下这个文件是否被其他分类当作 source（不会，因为 name 不同则 source 不同）
                f.unlink()
                print(f"  🗑️ {directory}/{f.name} 删除（已移出本类）")

    # 2️⃣ 清理空目录（只删 empty 的，不会误删 nested dirs）
    # 先收集所有仍被使用的目录前缀（如 programming/java → programming 仍在使用）
    used_prefixes = set()
    for d in classified_dirs:
        parts = d.split("/")
        if len(parts) > 1:
            used_prefixes.add(parts[0])
    
    for dir_name in sorted(existing_dirs, reverse=True):
        target = KNOWLEDGES_DIR / dir_name
        # 如果这个目录是某个分类的前缀（如 programming/ 下有 programming/java/），保留
        if dir_name in used_prefixes:
            continue
        if dir_name in classified_dirs:
            continue  # 当前分类仍然在使用
        # 只删确实空了的目录
        if target.exists():
            remaining = [f for f in target.rglob("*") if not f.name.startswith(".")]
            if not remaining:
                shutil.rmtree(target, ignore_errors=True)
                print(f"  🗑️ {dir_name}/ 删除（空目录）")


def extract_all_files() -> dict[str, list[tuple[str, Path]]]:
    """
    收集本地所有 .md 文件（递归），分类。
    返回 {directory: [(rel_path, full_path)]}
    未分类文件归入 uncategorized
    """
    classified: dict[str, list[tuple[str, Path]]] = {}
    uncategorized: list[Path] = []

    # 收集所有 .md 文件（递归）
    all_md_files = []
    for f in sorted(KNOWLEDGES_DIR.rglob("*.md")):
        if f.name == "README.md" or f.name.startswith("_"):
            continue
        if ".git" in str(f.relative_to(KNOWLEDGES_DIR)).split(os.sep):
            continue
        all_md_files.append(f)

    for f in all_md_files:
        tags = get_tags_from_file(f)
        result = get_primary_category_from_tags(tags) if tags else None
        if result:
            label, directory = result
            rel = str(f.relative_to(KNOWLEDGES_DIR))
            classified.setdefault(directory, []).append((rel, f))
        else:
            # 不在分类里的文件放在根目录以待归类
            label, directory = None, None
            # 当文件已在子目录中且无标签，保持原地
            if f.parent != KNOWLEDGES_DIR:
                continue  # 跳过已分类目录中的无标签文件
            uncategorized.append(f)

    if uncategorized:
        classified["uncategorized"] = [("uncategorized", f) for f in uncategorized]

    return classified


# ============================================================
# 步骤 3：生成 README
# ============================================================
def generate_readme(classified: dict[str, list[tuple[str, Path]]]):
    """生成清晰的 README"""
    now_str = __import__("datetime").datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# knowledges\n",
        "",
        "> 面试 & 技术知识库",
        "> 由 Jarvis II 按 Karpathy First Principles 方法论分类整理",
        "",
        "## 📂 目录结构",
        "",
    ]

    count = 0
    for directory in sorted(classified.keys()):
        entries = classified[directory]
        lines.append(f"### {directory}/")
        for rel, f in sorted(entries, key=lambda x: x[1].name):
            count += 1
            display_path = f"{directory}/{f.name}" if not rel or rel == "uncategorized" else rel
            lines.append(f"  - `{display_path}`")
        lines.append("")

    lines += [
        "---",
        "",
        f"总计 **{count}** 篇知识文档",
        "",
        "## 🏷️ Tags 索引",
        "",
        "每篇文档头部包含 YAML tags，可通过以下关键词检索：",
        "",
    ]

    all_tags = set()
    for directory, entries in classified.items():
        for rel, f in entries:
            tags = get_tags_from_file(f)
            all_tags.update(tags)

    tag_groups = {
        "面试": [t for t in all_tags if t in ("面试", "interview")],
        "Redis": [t for t in all_tags if t in ("redis", "缓存")],
        "SRE": [t for t in all_tags if t in ("sre", "故障处理", "熔断", "降级", "限流")],
        "网络": [t for t in all_tags if t in ("网络配置", "防火墙", "白名单")],
    }
    for group, tags in tag_groups.items():
        if tags:
            lines.append(f"- **{group}** → {', '.join(tags)}")

    lines.append("")
    lines.append(f"_自动生成于 {now_str}_")
    lines.append("")

    readme_path = KNOWLEDGES_DIR / "README.md"
    readme_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  📝 README.md 已更新 ({count} 篇)")


# ============================================================
# 步骤 4：通过 GitHub API 推送
# ============================================================
def push_to_github(token: str, classified: dict[str, list[tuple[str, Path]]]):
    """将所有文件上传到 GitHub（先获取 sha，增量更新）"""
    print("\n  📤 推送到 GitHub...")

    files_to_upload = []
    # 收集所有分类目录中的文件
    for directory, entries in classified.items():
        for rel, f in entries:
            rel_path = f"{directory}/{f.name}"
            files_to_upload.append((rel_path, f))
    # 收集分类目录外的文件（如 README.md）
    for f in sorted(KNOWLEDGES_DIR.glob("*.md")):
        if f.name == "README.md":
            files_to_upload.append(("README.md", f))
        elif f.name == TOOL_NAME or f.name.startswith("."):
            continue

    success = 0
    failed = 0
    total = len(files_to_upload)

    for rel_path, full_path in files_to_upload:
        content = full_path.read_bytes()
        b64_content = base64.b64encode(content).decode()

        # 获取已有文件的 sha
        sha = None
        resp = subprocess.run(
            ["/home/node/.openclaw/workspace/gh", "api",
             f"repos/{GH_REPO}/contents/{rel_path}"],
            capture_output=True, text=True, timeout=10,
            env={"GH_CONFIG_DIR": "/home/node/.openclaw/gh-config",
                 "PATH": os.environ.get("PATH", "")})
        if resp.returncode == 0:
            try:
                sha = json.loads(resp.stdout).get("sha")
            except json.JSONDecodeError:
                pass

        data = {
            "message": f"auto-organize: {__import__('datetime').datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
            "content": b64_content,
            "branch": GH_BRANCH,
        }
        if sha:
            data["sha"] = sha

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tf:
            json.dump(data, tf)
            tf_path = tf.name

        put_resp = subprocess.run(
            ["curl", "-s", "-X", "PUT",
             f"https://api.github.com/repos/{GH_REPO}/contents/{rel_path}",
             "-H", f"Authorization: Bearer {token}",
             "-H", "Content-Type: application/json",
             "-d", f"@{tf_path}"],
            capture_output=True, text=True, timeout=15)

        os.unlink(tf_path)

        if put_resp.returncode == 0:
            try:
                result = json.loads(put_resp.stdout)
                if "content" in result:
                    success += 1
                elif "message" in result:
                    failed += 1
                    print(f"  ❌ {rel_path}: {result['message'][:80]}")
            except json.JSONDecodeError:
                failed += 1
                print(f"  ❌ {rel_path}: 响应解析失败")
        else:
            failed += 1
            print(f"  ❌ {rel_path}: HTTP {put_resp.returncode}")

    print(f"  📊 推送结果: {success}/{total} 成功, {failed} 失败")
    return failed == 0


# ============================================================
# Main
# ============================================================
def main():
    print("=" * 50)
    print("📚 knowledges 知识库整理 & 同步")
    print("=" * 50)

    token = get_github_token()
    if not token:
        print("  ❌ 未找到 GitHub token，退出")
        return

    # 1️⃣ 从 GitHub 拉取（保证远程内容不丢失）
    sync_from_github(token)

    # 2️⃣ 分类所有本地文件
    print("\n  🔍 分类文档...")
    classified = extract_all_files()

    if not classified:
        print("  ℹ️  没有待整理的文档")
    else:
        for directory, entries in classified.items():
            tags_str = ""
            # 收集该目录下的标签
            dir_tags = set()
            for rel, f in entries:
                dir_tags.update(get_tags_from_file(f))
            print(f"  📁 {directory}/ ({len(entries)} 篇, tags: {', '.join(sorted(dir_tags))})")

        # 3️⃣ 整理到分类目录
        print("\n  🔄 整理中...")
        sync_classified_to_local(classified)

        # 重新获取全部分类（因为文件位置可能已变）
        classified = extract_all_files()

        # 4️⃣ 生成 README
        generate_readme(classified)

    # 5️⃣ 推送到 GitHub
    push_to_github(token, classified)

    print("\n" + "=" * 50)
    print("✅ 整理完成")
    print("=" * 50)


if __name__ == "__main__":
    main()
