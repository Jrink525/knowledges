#!/usr/bin/env python3
"""
knowledges 知识库自动整理脚本
基于文件实际内容分析（Content-based），而非静态 Tags 匹配

核心逻辑：
  读取每个 .md 文件的全文 → 提取技术关键词 → 对各领域打分 → 归入最佳分类
  Tags 仅作为加分项（+3 分），不依赖 tags 判断

工作流：
  同步远程(拉取) → 内容分析分类 → 整理到子目录 → 更新 README → 推送远程 → 清理远程旧文件
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
TOOL_NAME = "_organize.py"

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
# 分类映射 — 基于内容关键词的动态分类
# 每个领域定义一组该领域文档中高频出现的技术关键词
# 关键词来源于真实技术文档内容，而非人为定义
# ============================================================
DOMAIN_PROFILES = {
    "programming/java": {
        "label": "Java",
        "keywords": {
            # Core Java / JVM
            "jvm", "jdk", "bytecode", "classloader", "metaspace", "young generation",
            "old generation", "eden", "survivor", "full gc", "stop-the-world",
            "oom", "stack overflow", "string pool", "constant pool",
            "garbage collection", "gc root", "mark-sweep", "copying", "g1", "cms",
            # Concurrency
            "synchronized", "volatile", "thread", "lock", "monitor", "reentrantlock",
            "readwritelock", "aqs", "abstractqueuedsynchronizer", "cas", "compare and swap",
            "threadlocal", "threadpool", "threadpoolexecutor", "executorservice",
            "callable", "future", "completablefuture", "countdownlatch", "cyclicbarrier",
            "semaphore", "concurrenthashmap", "copyonwritearraylist", "blockingqueue",
            # Memory model
            "java memory model", "happens-before", "memory barrier", "cache coherence",
            "mesi", "lock prefix", "bus snooping",
        },
    },
    "spring": {
        "label": "Spring 框架",
        "keywords": {
            # Core Spring
            "spring framework", "ioc", "inversion of control", "dependency injection",
            "bean", "@bean", "@configuration", "@component", "@service", "@repository",
            "@autowired", "@qualifier", "@primary", "@scope", "@lazy",
            "applicationcontext", "beanfactory", "bean definition",
            # AOP
            "aop", "@aspect", "@pointcut", "@advice", "@around", "@before", "@after",
            "join point", "proxy", "cglib", "jdk dynamic proxy",
            # MVC
            "@controller", "@restcontroller", "@requestmapping",
            "@getmapping", "@postmapping", "@putmapping", "@deletemapping",
            "@requestbody", "@responsebody", "@pathvariable", "@requestparam",
            # Transaction
            "@transactional", "platformtransactionmanager", "transactionstatus",
            "transactiondefinition", "propagation", "isolation level",
            # Auto Configuration
            "@springbootapplication", "@enableautoconfiguration", "@conditionalonclass",
            "@conditionalonmissingbean", "@conditionalonproperty", "@conditionalonwebapplication",
            "autoconfigurationimportselector", "spring.factories", "spring boot starter",
            "@autoconfigureorder", "@autoconfigurebefore", "@autoconfigureafter",
            # Spring Security
            "spring security", "securityfilterchain", "@enablewebsecurity",
            "passwordencoder", "bcryptpasswordencoder", "password hashing",
            "jwt", "jwt token", "json web token", "jjwt",
            "rs256", "es256", "hmac", "hmacsha256",
            "refresh token", "access token",
            # AuthN / AuthZ
            "authentication", "authorization",
            "@preauthorize", "@secured", "hasrole", "hasauthority",
            "oauth2", "oauth2 resource server",
            # Spring Cloud
            "@enablediscoveryclient", "@enablefeignclients", "@enablecircuitbreaker",
            "eureka", "nacos", "consul", "etcd", "zookeeper",
            "gateway", "feign client", "loadbalancer", "ribbon",
            "service discovery", "service registry", "service registration",
            "服务发现", "服务注册", "注册中心",
            "heartbeat", "健康检查", "health check",
            "rpc server", "rpc client",
            "serviceinstance", "serviceregistry",
            "hystrix", "sentinel", "config server", "bus",
            # Data
            "jpatemplate", "spring data", "jdbctemplate", "namedparameterjdbctemplate",
            "datasource", "hikari", "druid", "mybatis", "mybatis-plus",
        },
    },
    "database": {
        "label": "数据库 & 缓存",
        "keywords": {
            # Redis
            "redis", "jedis", "lettuce", "redisson", "redis-cli",
            "string", "hash", "list", "set", "zset", "sorted set",
            "pub/sub", "stream", "bitmap", "hyperloglog", "geo",
            "rdb", "aof", "持久化", "主从", "sentinel", "cluster",
            "缓存穿透", "缓存击穿", "缓存雪崩", "缓存一致性",
            "io multiplexing", "epoll", "reactor",
            # MySQL / SQL
            "mysql", "innodb", "myisam", "b+ tree", "索引",
            "聚簇索引", "二级索引", "覆盖索引", "最左前缀",
            "事务", "acid", "mvcc", "undo log", "redo log", "binlog",
            "锁", "gap lock", "next-key lock", "死锁",
            "explain", "慢查询", "分库分表", "sharding", "读写分离",
            # SQL
            "sql", "select", "join", "index", "query optimization",
            # PostgreSQL
            "postgresql", "postgres", "pg_hba",
            # General DB
            "acid", "base", "cap", "nosql", "sql", "database",
        },
    },
    "sre": {
        "label": "SRE & 运维",
        "keywords": {
            # Reliability
            "sre", "sla", "slo", "sli", "error budget", "mtbf", "mttr", "mttd",
            "availability", "reliability", "resilience",
            # Fault tolerance
            "circuit breaker", "bulkhead", "rate limiting", "限流", "熔断", "降级",
            "timeout", "retry", "fallback", "graceful degradation",
            "shed load", "load shedding", "backpressure",
            # Monitoring
            "monitoring", "alerting", "prometheus", "grafana", "datadog",
            "metrics", "tracing", "logging", "opentelemetry", "jaeger",
            "链路追踪", "apm", "health check",
            # Chaos & Testing
            "chaos engineering", "混沌工程", "chaos monkey",
            "load testing", "stress test", "benchmark",
            # Operations
            "deployment", "canary", "blue-green", "rolling update",
            "incident response", "应急预案", "on-call", "pagerduty",
            "backup", "restore", "disaster recovery", "容灾",
        },
        },
    "ai-tools": {
        "label": "AI 工具 & 编程助手",
        "keywords": {
            # Claude Code
            "claude", "claude code", "anthropic",
            "subagent", "sub-agents", "plan mode",
            "custom slash command", "slash command",
            "mcp", "model context protocol",
            # Research & academia
            "academic research", "academic researcher", "academic writing",
            "dissertation", "thesis", "monograph", "literature review",
            # AI / LLM general
            "prompt", "ai agent", "ai assistant",
            "llm", "large language model", "context window",
            # Coding assistants
            "cursor", "copilot", "github copilot", "codex", "windsurf",
            # Agent/hook/task
            "agent",
            "scheduled task",
            # Connector / integration
            "connector", "mcp server",
        },
    },
    "infrastructure": {
        "label": "基础设施 & 网络",
        "keywords": {
            # Network
            "firewall", "nat", "vpc", "vpn", "dns", "cdn", "负载均衡",
            "nginx", "haproxy", "反向代理", "ssl", "tls", "https",
            "tcp", "udp", "http", "websocket", "quic", "dns",
            "白名单", "网络策略", "网络隔离", "ip白名单",
            # Cloud
            "aws", "aliyun", "azure", "gcp", "tencent cloud", "vpc",
            "安全组", "acl", "terraform", "ansible",
            # Container
            "docker", "kubernetes", "k8s", "pod", "service", "ingress",
            "istio", "envoy", "service mesh", "sidecar",
            # OS
            "linux", "systemd", "cgroup", "namespace", "ulimit",
            "sysctl", "tcpdump", "iptables", "netfilter",
            # OpenClaw/WeChat specific
            "openclaw", "weixin", "wechat", "clawbot", "ilink",
        },
    },
    "system-design": {
        "label": "系统设计 & 架构",
        "keywords": {
            # Architecture
            "微服务", "microservice", "分布式", "distributed", "架构设计",
            "system design", "design interview", "系统设计",
            "高并发", "high concurrency", "高性能", "高可用", "高可靠",
            "scalability", "availability", "consistency", "partition tolerance",
            # CAP
            "cap theorem", "base", "eventual consistency", "强一致性",
            "最终一致性", "分布式事务", "seata", "tcc", "saga",
            # Communication
            "rpc", "grpc", "dubbo", "thrift", "rest", "restful",
            "消息队列", "message queue", "kafka", "rabbitmq", "rocketmq", "pulsar",
            # Design Pattern
            "设计模式", "singleton", "factory", "observer", "策略模式",
            "ddd", "domain driven", "clean architecture", "六边形架构", "cqs", "cqrs",
            # Storage
            "对象存储", "s3", "oss", "分布式存储", "ceph",
        },
    },
}


# ============================================================
# 步骤 1：从 GitHub 拉取所有远程文件 → 同步到本地
# ============================================================
def sync_from_github(token: str) -> int:
    """获取 GitHub 上所有文件，下载到本地对应路径，返回远程文件数"""
    print("\n  🔽 从 GitHub 拉取远程文件...")
    downloaded = 0

    try:
        result = subprocess.run(
            ["/home/node/.openclaw/workspace/gh", "api",
             f"repos/{GH_REPO}/git/trees/{GH_BRANCH}?recursive=1"],
            capture_output=True, text=True, timeout=15,
            env={"GH_CONFIG_DIR": "/home/node/.openclaw/gh-config",
                 "PATH": os.environ.get("PATH", "")})
        if result.returncode != 0:
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
            if remote_path == TOOL_NAME:
                continue

            local_path = KNOWLEDGES_DIR / remote_path

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

            remote_content_b64 = remote_content_b64.replace("\n", "")
            try:
                remote_bytes = base64.b64decode(remote_content_b64)
            except Exception:
                continue

            local_path.parent.mkdir(parents=True, exist_ok=True)
            if local_path.exists():
                local_bytes = local_path.read_bytes()
                if local_bytes == remote_bytes:
                    continue
                else:
                    # 本地文件更新 → 保留本地修改，不覆盖
                    print(f"  🔄 {remote_path} ← 本地版本更新，保留本地（不覆盖）")
                    continue
            else:
                print(f"  📥 {remote_path} ← 新增（仅远程有）")
                local_path.write_bytes(remote_bytes)
                downloaded += 1

        print(f"  ✅ 同步完成 ({len(remote_files)} 远程文件已核对，{downloaded} 个变更)")
        return len(remote_files)

    except Exception as e:
        print(f"  ⚠️  同步失败: {e}")
        return 0


# ============================================================
# 步骤 2：基于文件内容分类（核心）
# 读完整内容 → 提取关键词 → 对各领域打分 → 最佳匹配
# ============================================================

# 读取 YAML frontmatter 中的 tags（仅用于加分）
def get_tags_from_file(filepath: Path) -> list[str]:
    """读取文件的 tags（YAML frontmatter）"""
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


def extract_content_text(filepath: Path) -> str:
    """读取文件内容，返回小写的纯文本（去掉代码块和 YAML frontmatter）"""
    content = filepath.read_text(encoding="utf-8", errors="replace")
    
    # 去掉 YAML frontmatter
    content = re.sub(r"^---\s*\n.*?\n---\s*\n", "", content, flags=re.DOTALL)
    
    # 保留代码块内容（代码中的关键词有强信号）
    # 但去掉行号、纯数字等噪音
    # 代码块本身保留，不需要特殊处理
    
    return content.lower()


def classify_by_content(filepath: Path) -> tuple[str, str] | None:
    """
    基于文件实际内容分类（核心函数）
    返回 (label, directory) 或 None
    
    算法：
    1. 读全文
    2. 对每个领域的关键词集合做计数匹配
    3. Tags 作为加分项（+3 分/标签）
    4. 得分最高者为最佳分类
    """
    content_text = extract_content_text(filepath)
    tags = get_tags_from_file(filepath)
    
    scores: dict[str, float] = {}
    
    for domain, profile in DOMAIN_PROFILES.items():
        score = 0.0
        
        # 内容关键词计数匹配
        for keyword in profile["keywords"]:
            count = content_text.count(keyword.lower())
            if count > 0:
                score += count
        
        # Tags 加分（已明确标注的领域 +3 分/标签）
        if tags:
            for tag in tags:
                tag_lower = tag.lower()
                for kw in profile["keywords"]:
                    # 双向匹配：tag 含 keyword 或 keyword 含 tag
                    # 如 tag="spring" 匹配 keyword="spring framework" ✓
                    # 如 tag="spring-boot" 匹配 keyword="spring boot" ✓
                    if tag_lower == kw or \
                       tag_lower.startswith(kw) or \
                       (len(tag_lower) >= 2 and kw.startswith(tag_lower)) or \
                       (len(tag_lower) > 3 and kw in tag_lower):
                        score += 3.0
                        break
        
        # 标题关键词特别重要（标题匹配 +5 分）
        title_match = re.search(r"^#\s+(.+)$", content_text, re.MULTILINE)
        if title_match:
            title = title_match.group(1).lower()
            for keyword in profile["keywords"]:
                if keyword in title:
                    score += 5.0
        
        if score > 0:
            scores[domain] = score
    
    if not scores:
        return None
    
    # 取最高分
    best = max(scores, key=scores.get)
    # 如果最高分太低（< 2 分），认为无法分类
    if scores[best] < 2.0:
        return None
    
    return (DOMAIN_PROFILES[best]["label"], best)


# ============================================================
# 步骤 3：文件整理到分类目录
# ============================================================
def sync_classified_to_local(classified: dict[str, list[tuple[str, Path]]]):
    """确保分类目录结构反映在本地文件系统（支持子目录）"""
    existing_dirs = set()
    for d in KNOWLEDGES_DIR.iterdir():
        if d.is_dir() and not d.name.startswith("."):
            existing_dirs.add(d.name)
    classified_dirs = set(classified.keys())

    # 1️⃣ 移动所有文件到正确目录（保留子目录结构）
    for directory, entries in classified.items():
        target_base = KNOWLEDGES_DIR / directory
        target_base.mkdir(parents=True, exist_ok=True)
        for rel_path, source_path in entries:
            # 计算子目录路径：如果 rel_path 以 domain 开头，保留其子目录
            rel = Path(rel_path)
            if str(rel).startswith(directory + "/"):
                # 已有子目录：ai-tools/claude/foo.md → claude/foo.md
                sub = str(rel.relative_to(directory))
                target_path = target_base / sub
            else:
                # 没有子目录：直接用文件名
                target_path = target_base / source_path.name

            if source_path.resolve() == target_path.resolve():
                continue
            target_path.parent.mkdir(parents=True, exist_ok=True)
            if target_path.exists():
                target_path.unlink()
            shutil.move(str(source_path), str(target_path))
            display = str(target_path.relative_to(KNOWLEDGES_DIR))
            print(f"  📦 {display}")

    # 2️⃣ 清理目标目录中不再归属的旧文件（递归）
    for directory, entries in classified.items():
        target_dir = KNOWLEDGES_DIR / directory
        # 收集已知路径（相对 domain 目录的子路径）
        known = set()
        for rel_path, source_path in entries:
            rel = Path(rel_path)
            if str(rel).startswith(directory + "/"):
                known.add(str(rel.relative_to(directory)))
            else:
                known.add(source_path.name)
        for f in list(target_dir.rglob("*.md")):
            if f.name.startswith("_"):
                continue
            rel_f = str(f.relative_to(target_dir))
            if rel_f not in known:
                f.unlink()
                print(f"  🗑️ {directory}/{rel_f} 删除（已移出本类）")

    # 3️⃣ 清理空目录（递归）
    def clean_empty_dirs(path):
        for child in sorted(path.iterdir(), reverse=True):
            if child.is_dir():
                clean_empty_dirs(child)
                if not any(True for _ in child.rglob("*")):
                    shutil.rmtree(child, ignore_errors=True)
    for d in list(KNOWLEDGES_DIR.iterdir()):
        if d.is_dir() and not d.name.startswith("."):
            clean_empty_dirs(d)


def extract_all_files() -> dict[str, list[tuple[str, Path]]]:
    """
    收集本地所有 .md 文件（递归），基于内容分类。
    返回 {directory: [(rel_path, full_path)]}
    """
    classified: dict[str, list[tuple[str, Path]]] = {}
    uncategorized: list[Path] = []

    all_md_files = []
    for f in sorted(KNOWLEDGES_DIR.rglob("*.md")):
        if f.name == "README.md" or f.name.startswith("_"):
            continue
        if ".git" in str(f.relative_to(KNOWLEDGES_DIR)).split(os.sep):
            continue
        all_md_files.append(f)

    for f in all_md_files:
        result = classify_by_content(f)
        if result:
            label, directory = result
            rel = str(f.relative_to(KNOWLEDGES_DIR))
            classified.setdefault(directory, []).append((rel, f))
        else:
            if f.parent != KNOWLEDGES_DIR:
                continue
            uncategorized.append(f)

    if uncategorized:
        classified["uncategorized"] = [("uncategorized", f) for f in uncategorized]

    return classified


# ============================================================
# 步骤 4：生成 README
# ============================================================
def generate_readme(classified: dict[str, list[tuple[str, Path]]]):
    now_str = __import__("datetime").datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# knowledges\n",
        "",
        "> 面试 & 技术知识库",
        "> 由 Jarvis II 按文件内容动态分类（Karpathy First Principles 方法论）",
        "",
        "## 📂 目录结构",
        "",
    ]

    count = 0
    for directory in sorted(classified.keys()):
        entries = classified[directory]
        label = DOMAIN_PROFILES.get(directory, {}).get("label", directory)
        lines.append(f"### {directory}/ (`{label}`)")

        # 按子目录分组显示
        subdir_groups: dict[str, list[str]] = {}
        root_files: list[str] = []
        for rel, f in sorted(entries, key=lambda x: x[1].name):
            count += 1
            display_path = f"{directory}/{f.name}" if not rel or rel == "uncategorized" else rel
            # 判断是否有子目录
            rel_obj = Path(rel)
            if "/" in str(rel_obj.relative_to(directory)) if str(rel_obj).startswith(directory + "/") else False:
                # 提取子目录名
                sub = str(rel_obj.relative_to(directory))
                if "/" in sub:
                    subdir = sub.split("/")[0]
                    subdir_groups.setdefault(subdir, []).append(f"    - `{display_path}`")
                else:
                    root_files.append(f"  - `{display_path}`")
            else:
                root_files.append(f"  - `{display_path}`")

        # 先输出根目录文件
        for line in root_files:
            lines.append(line)
        # 再按子目录分组输出
        for subdir in sorted(subdir_groups.keys()):
            lines.append(f"  📁 **{subdir}/**")
            lines.extend(subdir_groups[subdir])
        lines.append("")

    lines += [
        "---",
        "",
        f"总计 **{count}** 篇知识文档",
        "",
        "## 🤖 分类说明",
        "",
        "本文档库按**内容关键词分析**自动分类（非 Tags 依赖），分类算法：",
        "",
        "1. 读取每个文档的**完整内容**（含代码示例）",
        "2. 提取技术关键词，对 7 个领域分别**打分**",
        "3. Tags 作为**加分项**（+3/标签），不是主要条件",
        "4. 标题关键词额外加分（+5）",
        "5. 得分最高者胜出",
        "",
        "_[自动生成于 {now_str}]_",
        "",
    ]

    readme_path = KNOWLEDGES_DIR / "README.md"
    readme_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  📝 README.md 已更新 ({count} 篇)")


# ============================================================
# 步骤 5：推送 + 远程清理
# ============================================================
def push_to_github(token: str, classified: dict[str, list[tuple[str, Path]]]):
    """将所有文件上传到 GitHub，再清理远程旧文件（支持子目录）"""
    print("\n  📤 推送到 GitHub...")

    files_to_upload = []
    for directory, entries in classified.items():
        for rel, f in entries:
            # 使用 rel（相对路径），保留子目录结构
            rel_path = rel if rel and rel != "uncategorized" else f"{directory}/{f.name}"
            files_to_upload.append((rel_path, f))
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

    # 🧹 清理远程旧文件
    print("\n  🧹 清理远程旧文件...")
    local_paths = {p for p, _ in files_to_upload}
    local_paths.add("_organize.py")

    tree_resp = subprocess.run(
        ["/home/node/.openclaw/workspace/gh", "api",
         f"repos/{GH_REPO}/git/trees/{GH_BRANCH}?recursive=1"],
        capture_output=True, text=True, timeout=15,
        env={"GH_CONFIG_DIR": "/home/node/.openclaw/gh-config",
             "PATH": os.environ.get("PATH", "")})

    if tree_resp.returncode == 0:
        try:
            tree_data = json.loads(tree_resp.stdout)
            cleaned = 0
            for item in tree_data.get("tree", []):
                path = item.get("path", "")
                typ = item.get("type", "")
                if not path or typ != "blob":
                    continue
                if path == ".gitignore" or path in local_paths:
                    continue
                sha = item.get("sha")
                if not sha:
                    continue
                del_payload = json.dumps({
                    "message": "cleanup: remove outdated file (reorganized)",
                    "sha": sha,
                    "branch": GH_BRANCH,
                })
                with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tf:
                    tf.write(del_payload)
                    tf_path = tf.name
                del_resp = subprocess.run(
                    ["curl", "-s", "-X", "DELETE",
                     f"https://api.github.com/repos/{GH_REPO}/contents/{path}",
                     "-H", f"Authorization: Bearer {token}",
                     "-H", "Content-Type: application/json",
                     "-d", f"@{tf_path}"],
                    capture_output=True, text=True, timeout=15)
                os.unlink(tf_path)
                try:
                    dr = json.loads(del_resp.stdout)
                    if "commit" in dr:
                        cleaned += 1
                        print(f"  🗑️ {path}")
                except json.JSONDecodeError:
                    pass
            if cleaned > 0:
                print(f"  🧹 已清理 {cleaned} 个远程旧文件")
            else:
                print(f"  ✅ 远程文件无残留")
        except json.JSONDecodeError:
            print("  ⚠️  解析远程文件树失败")
    else:
        print(f"  ⚠️  获取远程文件列表失败 (exit={tree_resp.returncode})")

    print(f"\n  📊 推送结果: {success}/{total} 成功, {failed} 失败")
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

    sync_from_github(token)

    print("\n  🔍 基于内容分类文档...")
    classified = extract_all_files()

    if not classified:
        print("  ℹ️  没有待整理的文档")
    else:
        for directory, entries in classified.items():
            label = DOMAIN_PROFILES.get(directory, {}).get("label", directory)
            print(f"  📁 {directory}/ ({label}, {len(entries)} 篇)")
            for rel, f in entries:
                print(f"    - {f.name}")

        # 检查各目录文件数，超过 20 篇告警
        print()
        threshold_alerted = False
        for directory, entries in classified.items():
            count = len(entries)
            if count > 20:
                print(f"  ⚠️  {directory}/ 达到 {count} 篇，超出 20 篇阈值，建议拆分到子目录！")
                threshold_alerted = True
        if not threshold_alerted:
            print(f"  ✅ 所有目录文件数未超过 20 篇阈值")

        print("\n  🔄 整理中...")
        sync_classified_to_local(classified)

        classified = extract_all_files()
        generate_readme(classified)

    push_to_github(token, classified)

    print("\n" + "=" * 50)
    print("✅ 整理完成")
    print("=" * 50)


if __name__ == "__main__":
    main()
