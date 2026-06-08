#!/usr/bin/env python3
"""
📚 知识库自动整理 & 同步脚本

核心变化（vs 旧版）：
  ✅ Git Tree/Commit API 批量推送 — 一次 API 调用推送所有文件，告别逐文件 PUT
  ✅ Git Tree API 批量清理远程旧文件 — 新树不包含要删除的文件即可
  ✅ 并发 blob 创建 — 使用 ThreadPoolExecutor 并行上传文件内容
  ✅ 无 SIGALRM 全局超时 — 改用 cooperative 超时检查，不会中间杀死进程
  ✅ 自适应 API 节流 — 跟踪剩余请求配额，动态调整速率
  ✅ 单次 tree API 构建 SHA 缓存 — 复用已有逻辑

工作流：
  同步远程（树 API）→ 内容分析分类 → 整理到子目录 → 更新 README
  → 创建 Git Tree（批量） → 创建 Commit → 更新分支引用 → 可选清理
"""

import os
import re
import shutil
import json
import base64
import subprocess
import tempfile
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone

KNOWLEDGES_DIR = Path(__file__).parent.resolve()
GH_REPO = "Jrink525/knowledges"
GH_BRANCH = "master"
TOOL_NAME = "_organize.py"

GH_BIN = "/home/node/.openclaw/workspace/gh"
GH_CONFIG_ENV = {
    "GH_CONFIG_DIR": "/home/node/.openclaw/gh-config",
    "PATH": os.environ.get("PATH", ""),
}

# ── 超时（大幅提升，适应大规模推送） ─────────────────
API_TIMEOUT = 30          # 单次 API 调用超时
API_TIMEOUT_SHORT = 10    # 单次 API 存在性检查超时
GLOBAL_TIMEOUT = 600      # 整个操作超时秒数
MAX_WORKERS = 5           # 并发 API 调用数

KNOWN_IMG_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"}

# ── 运行时文件/目录跳过列表（不归类、不操作） ─────
# 🚫 这些是 OpenClaw 运行时文件，只存本地磁盘，绝不操作、绝不提交到 Git。
SKIP_FILES = frozenset({
    "AGENTS.md", "SOUL.md", "TOOLS.md", "USER.md", "IDENTITY.md",
    "HEARTBEAT.md", "MEMORY.md", "_organize.py",
})
SKIP_DIRS = frozenset({
    "memory", "scripts", "skills", "node_modules", "chrome-deps", "reading-output",
})


def _is_skip_path(path: Path) -> bool:
    """True if the path is a runtime file/dir that should never be touched."""
    if path.name in SKIP_FILES:
        return True
    for parent in path.parents:
        if parent.name in SKIP_DIRS:
            return True
    return False


# ── 自适应节流 ──────────────────────────────────────
_API_LOCK = threading.Lock()
_API_LAST_TICK = time.monotonic()
_API_RATE_LIMIT_REMAINING: int | None = None
_API_RATE_LIMIT_RESET: int | None = None
_MIN_INTERVAL = 0.05   # 快速模式（高配额时）
_MAX_INTERVAL = 1.0    # 慢速模式（低配额时）


def _api_tick():
    """自适应 API 节流：根据剩余配额动态调整间隔"""
    global _API_LAST_TICK, _API_RATE_LIMIT_REMAINING
    with _API_LOCK:
        # 计算动态间隔
        if _API_RATE_LIMIT_REMAINING is not None and _API_RATE_LIMIT_REMAINING < 50:
            interval = _MAX_INTERVAL
        elif _API_RATE_LIMIT_REMAINING is not None and _API_RATE_LIMIT_REMAINING < 200:
            interval = _MAX_INTERVAL * 0.3
        else:
            interval = _MIN_INTERVAL

        elapsed = time.monotonic() - _API_LAST_TICK
        if elapsed < interval:
            time.sleep(interval - elapsed)
        _API_LAST_TICK = time.monotonic()


_DEADLINE = time.monotonic() + GLOBAL_TIMEOUT


def _check_timeout(label=""):
    if time.monotonic() > _DEADLINE:
        raise TimeoutError(f"全局超时（{GLOBAL_TIMEOUT}s）{' - ' + label if label else ''}")


# ── Token ────────────────────────────────────────────

def get_github_token() -> str | None:
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        return token
    config_path = Path("/home/node/.openclaw/gh-config/hosts.yml")
    if config_path.exists():
        from email.message import Message
        content = config_path.read_text()
        m = re.search(r'oauth_token:\s*(\S+)', content)
        if m:
            return m.group(1)
    return None


# ── Helpers ──────────────────────────────────────────

def call_gh(api_path: str, method: str = "GET", body: str | None = None,
            timeout: int = API_TIMEOUT) -> tuple[int, str, dict]:
    """调用 gh CLI，返回 (returncode, stdout, response_headers)"""
    cmd = [GH_BIN, "api", api_path]
    if method != "GET":
        cmd.extend(["--method", method])
        if body:
            cmd.extend(["--input", "-"])
    try:
        r = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout,
            input=body, env=GH_CONFIG_ENV)
        _api_tick()
        rh = _parse_gh_headers(r.stderr)
        _update_rate_limit(rh)
        return r.returncode, r.stdout, rh
    except FileNotFoundError:
        print(f"  ❌ 未找到 gh 二进制: {GH_BIN}")
        return -1, "", {}
    except subprocess.TimeoutExpired:
        print(f"  ⚠️ gh api 超时 ({timeout}s): {api_path[:60]}")
        return -1, "", {}
    except Exception as e:
        print(f"  ⚠️ gh 异常: {e}")
        return -1, "", {}


def _parse_gh_headers(stderr: str) -> dict:
    """从 gh stderr 提取响应头"""
    headers = {}
    for line in stderr.split("\n"):
        line = line.strip()
        if ":" in line.lower() and ("x-ratelimit" in line.lower() or "x-request-id" in line.lower()):
            parts = line.split(":", 1)
            if len(parts) == 2:
                headers[parts[0].strip()] = parts[1].strip()
    return headers


def _update_rate_limit(headers: dict):
    """从响应头更新速率限制状态"""
    global _API_RATE_LIMIT_REMAINING, _API_RATE_LIMIT_RESET
    for k, v in headers.items():
        kl = k.lower().replace("-", "").replace("_", "")
        if kl == "xratelimitremaining":
            try:
                _API_RATE_LIMIT_REMAINING = int(v)
            except ValueError:
                pass
        elif kl == "xratelimitreset":
            try:
                _API_RATE_LIMIT_RESET = int(v)
            except ValueError:
                pass


def safe_read_bytes(path: Path) -> bytes:
    try:
        return path.read_bytes()
    except (OSError, PermissionError):
        return b""


def safe_write(path: Path, content: bytes):
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    except (OSError, PermissionError) as e:
        print(f"  ⚠️ 写入失败 {path}: {e}")


def build_sha_map() -> dict[str, str]:
    """获取远程所有文件 SHA"""
    code, stdout, _ = call_gh(
        f"repos/{GH_REPO}/git/trees/{GH_BRANCH}?recursive=1",
        timeout=API_TIMEOUT_SHORT)
    if code != 0:
        print("  ⚠️ 获取远程文件树失败")
        return {}
    try:
        tree = json.loads(stdout)
    except json.JSONDecodeError:
        print("  ⚠️ 解析远程文件树失败")
        return {}

    sha_map = {}
    for item in tree.get("tree", []):
        if item["type"] == "blob" and item.get("sha"):
            sha_map[item["path"]] = item["sha"]
    return sha_map


# ── YAML frontmatter ────────────────────────────────

def parse_yaml_frontmatter(text: str) -> dict:
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
                items = [x.strip().strip("\"'") for x in value[1:-1].split(",") if x.strip()]
                result[key] = items
            elif value.lower() in ("true", "false"):
                result[key] = value.lower() == "true"
            else:
                result[key] = value.strip("\"'")
    return result


def get_tags_from_file(filepath: Path) -> list[str]:
    content = safe_read_bytes(filepath).decode("utf-8", errors="replace")
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return []
    meta = parse_yaml_frontmatter(match.group(1))
    tags = meta.get("tags", [])
    return tags if isinstance(tags, list) else [tags]


# ── YAML category → domain 别名映射（子目录路径 → 主领域） ──
CATEGORY_ALIASES = {
    # spring/ 子目录
    "spring/ai-agent": "spring",
    "spring/code-snippets": "spring",
    "spring/core": "spring",
    "spring/dynamic-bean": "spring",
    "spring/performance": "spring",
    "spring/utilities": "spring",
    # ai-tools/ 子目录
    "ai-tools/agent-engineering": "ai-tools",
    "ai-tools/agent-engineering/autoresearch": "ai-tools",
    "ai-tools/agent-engineering/patterns": "ai-tools",
    "ai-tools/agent-engineering/tooling": "ai-tools",
    "ai-tools/agents": "ai-tools",
    "ai-tools/autoresearch": "ai-tools",
    "ai-tools/career": "ai-tools",
    "ai-tools/claude": "ai-tools",
    "ai-tools/claude-code": "ai-tools",
    "ai-tools/database-experiments": "ai-tools",
    "ai-tools/enterprise": "ai-tools",
    "ai-tools/frameworks": "ai-tools",
    "ai-tools/harness": "ai-tools",
    "ai-tools/inference": "ai-tools",
    "ai-tools/ml-research": "ai-tools",
    "ai-tools/obsidian": "ai-tools",
    "ai-tools/patterns": "ai-tools",
    "ai-tools/skills": "ai-tools",
    "ai-tools/spring-ai": "ai-tools",
    "ai-tools/tooling": "ai-tools",
    # database/ 子目录
    "database/codex": "database",
    "database/database-experiments": "database",
    "database/inference": "database",
    "database/tooling": "database",
    "database/career": "database",
    "database/harness": "database",
    # programming/ 子目录
    "programming": "programming/java",
    # 其他
    "papers": "system-design",
}


def resolve_category(cat: str) -> str | None:
    """将 YAML category 解析为 DOMAIN_PROFILES 中的 key。"""
    cat = cat.strip()
    if cat in DOMAIN_PROFILES:
        return cat
    if cat in CATEGORY_ALIASES:
        return CATEGORY_ALIASES[cat]
    print(f"  ⚠️ YAML category '{cat}' 不在已知领域配置中（忽略）")
    return None


def get_category_override(filepath: Path) -> str | None:
    content = safe_read_bytes(filepath).decode("utf-8", errors="replace")
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return None
    meta = parse_yaml_frontmatter(match.group(1))
    cat = meta.get("category")
    if cat and isinstance(cat, str) and cat.strip():
        return resolve_category(cat.strip())
    return None


# ── Domain profiles ──────────────────────────────────

DOMAIN_PROFILES = {
    "programming/java": {
        "label": "Java",
        "keywords": {
            "jvm", "jdk", "bytecode", "classloader", "metaspace", "young generation",
            "old generation", "eden", "survivor", "full gc", "stop-the-world",
            "oom", "stack overflow", "string pool", "constant pool",
            "garbage collection", "gc root", "mark-sweep", "copying", "g1", "cms",
            "synchronized", "volatile", "thread", "lock", "monitor", "reentrantlock",
            "readwritelock", "aqs", "abstractqueuedsynchronizer", "cas", "compare and swap",
            "threadlocal", "threadpool", "threadpoolexecutor", "executorservice",
            "callable", "future", "completablefuture", "countdownlatch", "cyclicbarrier",
            "semaphore", "concurrenthashmap", "copyonwritearraylist", "blockingqueue",
            "java memory model", "happens-before", "memory barrier", "cache coherence",
            "mesi", "lock prefix", "bus snooping",
        },
    },
    "spring": {
        "label": "Spring 框架",
        "keywords": {
            "spring framework", "ioc", "inversion of control", "dependency injection",
            "bean", "@bean", "@configuration", "@component", "@service", "@repository",
            "@autowired", "@qualifier", "@primary", "@scope", "@lazy",
            "applicationcontext", "beanfactory", "bean definition",
            "aop", "@aspect", "@pointcut", "@advice", "@around", "@before", "@after",
            "join point", "proxy", "cglib", "jdk dynamic proxy",
            "@controller", "@restcontroller", "@requestmapping",
            "@getmapping", "@postmapping", "@putmapping", "@deletemapping",
            "@requestbody", "@responsebody", "@pathvariable", "@requestparam",
            "@transactional", "platformtransactionmanager", "transactionstatus",
            "transactiondefinition", "propagation", "isolation level",
            "@springbootapplication", "@enableautoconfiguration", "@conditionalonclass",
            "@conditionalonmissingbean", "@conditionalonproperty", "@conditionalonwebapplication",
            "autoconfigurationimportselector", "spring.factories", "spring boot starter",
            "@autoconfigureorder", "@autoconfigurebefore", "@autoconfigureafter",
            "spring security", "securityfilterchain", "@enablewebsecurity",
            "passwordencoder", "bcryptpasswordencoder", "password hashing",
            "jwt", "jwt token", "json web token", "jjwt",
            "rs256", "es256", "hmac", "hmacsha256",
            "refresh token", "access token",
            "authentication", "authorization",
            "@preauthorize", "@secured", "hasrole", "hasauthority",
            "oauth2", "oauth2 resource server",
            "@enablediscoveryclient", "@enablefeignclients", "@enablecircuitbreaker",
            "eureka", "nacos", "consul", "etcd", "zookeeper",
            "gateway", "feign client", "loadbalancer", "ribbon",
            "service discovery", "service registry", "service registration",
            "服务发现", "服务注册", "注册中心",
            "heartbeat", "健康检查", "health check",
            "rpc server", "rpc client",
            "serviceinstance", "serviceregistry",
            "hystrix", "sentinel", "config server", "bus",
            "jpatemplate", "spring data", "jdbctemplate", "namedparameterjdbctemplate",
            "datasource", "hikari", "druid", "mybatis", "mybatis-plus",
        },
    },
    "database": {
        "label": "数据库 & 缓存",
        "keywords": {
            "redis", "jedis", "lettuce", "redisson", "redis-cli",
            "pub/sub", "stream", "bitmap", "hyperloglog", "geo",
            "rdb", "aof", "主从", "sentinel", "cluster",
            "缓存穿透", "缓存击穿", "缓存雪崩", "缓存一致性",
            "io multiplexing", "epoll", "reactor",
            "mysql", "innodb", "myisam", "b+ tree",
            "聚簇索引", "二级索引", "覆盖索引", "最左前缀",
            "mvcc", "undo log", "redo log", "binlog",
            "gap lock", "next-key lock",
            "explain", "慢查询", "分库分表", "sharding", "读写分离",
            "postgresql", "postgres", "pg_hba",
            "nosql", "mongodb", "elasticsearch",
            "vector database", "vector db", "faiss", "chroma",
            "zset", "sorted set", "ttl", "内存淘汰", "lru",
            "数据分片", "shard", "replica set",
            "连接池", "hikari", "druid",
            "缓存策略", "cache aside", "read through",
        },
    }
    "sre": {
        "label": "SRE & 运维",
        "keywords": {
            "sre", "sla", "slo", "sli", "error budget", "mtbf", "mttr", "mttd",
            "availability", "reliability", "resilience",
            "circuit breaker", "bulkhead", "rate limiting", "限流", "熔断", "降级",
            "timeout", "retry", "fallback", "graceful degradation",
            "shed load", "load shedding", "backpressure",
            "monitoring", "alerting", "prometheus", "grafana", "datadog",
            "metrics", "tracing", "logging", "opentelemetry", "jaeger",
            "链路追踪", "apm", "health check",
            "chaos engineering", "混沌工程", "chaos monkey",
            "load testing", "stress test", "benchmark",
            "deployment", "canary", "blue-green", "rolling update",
            "incident response", "应急预案", "on-call", "pagerduty",
            "backup", "restore", "disaster recovery", "容灾",
        },
    },
    "ai-tools": {
        "label": "AI 工具 & 编程助手",
        "keywords": {
            "claude", "claude code", "anthropic",
            "subagent", "sub-agents", "plan mode",
            "custom slash command", "slash command",
            "mcp", "model context protocol",
            "academic research", "academic researcher", "academic writing",
            "dissertation", "thesis", "monograph", "literature review",
            "prompt", "ai agent", "ai assistant",
            "llm", "large language model", "context window",
            "cursor", "copilot", "github copilot", "codex", "windsurf",
            "agent", "scheduled task",
            "connector", "mcp server",
        },
    },
    "infrastructure": {
        "label": "基础设施 & 网络",
        "keywords": {
            "firewall", "nat", "vpc", "vpn", "dns", "cdn", "负载均衡",
            "nginx", "haproxy", "反向代理", "ssl", "tls", "https",
            "tcp", "udp", "http", "websocket", "quic", "dns",
            "白名单", "网络策略", "网络隔离", "ip白名单",
            "aws", "aliyun", "azure", "gcp", "tencent cloud", "vpc",
            "安全组", "acl", "terraform", "ansible",
            "docker", "kubernetes", "k8s", "pod", "service", "ingress",
            "istio", "envoy", "service mesh", "sidecar",
            "linux", "systemd", "cgroup", "namespace", "ulimit",
            "sysctl", "tcpdump", "iptables", "netfilter",
            "openclaw", "weixin", "wechat", "clawbot", "ilink",
        },
    },
    "system-design": {
        "label": "系统设计 & 架构",
        "keywords": {
            "微服务", "microservice", "分布式", "distributed", "架构设计",
            "system design", "design interview", "系统设计",
            "高并发", "high concurrency", "高性能", "高可用", "高可靠",
            "scalability", "availability", "consistency", "partition tolerance",
            "cap theorem", "base", "eventual consistency", "强一致性",
            "最终一致性", "分布式事务", "seata", "tcc", "saga",
            "rpc", "grpc", "dubbo", "thrift", "rest", "restful",
            "消息队列", "message queue", "kafka", "rabbitmq", "rocketmq", "pulsar",
            "设计模式", "singleton", "factory", "observer", "策略模式",
            "ddd", "domain driven", "clean architecture", "六边形架构", "cqs", "cqrs",
            "对象存储", "s3", "oss", "分布式存储", "ceph",
        },
    },
}


# ── Content classification ───────────────────────────

def extract_content_text(filepath: Path) -> str:
    content = safe_read_bytes(filepath).decode("utf-8", errors="replace")
    content = re.sub(r"^---\s*\n.*?\n---\s*\n", "", content, flags=re.DOTALL)
    return content.lower()


def _kw_count(text: str, keyword: str) -> int:
    """使用 \b 词边界匹配关键词计数，避免子串误中。"""
    try:
        pattern = re.compile(rf"\b{re.escape(keyword)}\b", re.IGNORECASE)
        return len(pattern.findall(text))
    except re.error:
        # 某些关键词含特殊字符回退到原逻辑
        return text.lower().count(keyword.lower())


def classify_by_content(filepath: Path) -> tuple[str, str] | None:
    override = get_category_override(filepath)
    if override:
        return (DOMAIN_PROFILES[override]["label"], override)

    content_text = extract_content_text(filepath)
    tags = get_tags_from_file(filepath)

    scores: dict[str, float] = {}
    for domain, profile in DOMAIN_PROFILES.items():
        score = 0.0
        for keyword in profile["keywords"]:
            count = _kw_count(content_text, keyword)
            if count > 0:
                score += count

        if tags:
            for tag in tags:
                tl = tag.lower()
                for kw in profile["keywords"]:
                    if tl == kw or tl.startswith(kw) or (len(tl) > 3 and _kw_count(tl, kw)):
                        score += 3.0
                        break

        title_match = re.search(r"^#\s+(.+)$", content_text, re.MULTILINE)
        if title_match:
            title = title_match.group(1).lower()
            for kw in profile["keywords"]:
                if _kw_count(title, kw) > 0:
                    score += 5.0

        if score > 0:
            scores[domain] = score

    if not scores:
        return None
    best = max(scores, key=scores.get)
    if scores[best] < 2.0:
        return None
    return (DOMAIN_PROFILES[best]["label"], best)


# ── Sync from GitHub ────────────────────────────────

def sync_from_github(token: str) -> int:
    print("\n  🔽 从 GitHub 拉取远程文件...")

    # ── 快速跳过：local git 与 remote 已是同一 commit ──
    try:
        res = subprocess.run(
            ["git", "fetch", "origin", GH_BRANCH],
            capture_output=True, text=True, timeout=15,
            cwd=KNOWLEDGES_DIR)
        local_head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=5,
            cwd=KNOWLEDGES_DIR).stdout.strip()
        remote_head = subprocess.run(
            ["git", "rev-parse", f"origin/{GH_BRANCH}"],
            capture_output=True, text=True, timeout=5,
            cwd=KNOWLEDGES_DIR).stdout.strip()
        if local_head == remote_head:
            print("  ✅ Git 已是最新（local == origin），跳过文件级同步")
            return 0
    except Exception as e:
        print(f"  ⚠️ Git 同步检查失败 ({e})，继续文件级同步...")

    downloaded = 0

    sha_map = build_sha_map()
    if not sha_map:
        print("  ℹ️ 远程仓库无内容或无法访问")
        return 0

    remote_files = [p for p in sha_map.keys()
                    if p != ".gitkeep" and not p.startswith(".")]
    if not remote_files:
        print("  ℹ️ 远程仓库为空")
        return 0

    print(f"  远程发现 {len(remote_files)} 个文件")

    for idx, remote_path in enumerate(remote_files):
        _check_timeout("sync")
        if idx > 0 and idx % 20 == 0:
            print(f"  ⏳ 进度: {idx}/{len(remote_files)}")

        if remote_path == TOOL_NAME:
            continue

        local_path = KNOWLEDGES_DIR / remote_path

        code, content_out, _ = call_gh(
            f"repos/{GH_REPO}/contents/{remote_path}",
            timeout=API_TIMEOUT_SHORT)
        if code != 0:
            print(f"  ⚠️ 无法获取 {remote_path}，跳过")
            continue

        try:
            data = json.loads(content_out)
        except json.JSONDecodeError:
            continue

        remote_b64 = (data.get("content") or "").replace("\n", "")
        if not remote_b64:
            continue
        try:
            remote_bytes = base64.b64decode(remote_b64)
        except Exception:
            continue

        local_path.parent.mkdir(parents=True, exist_ok=True)
        if local_path.exists():
            local_bytes = safe_read_bytes(local_path)
            if local_bytes == remote_bytes:
                continue
            print(f"  🔄 {remote_path} ← 保留本地版本")
            continue

        safe_write(local_path, remote_bytes)
        downloaded += 1
        print(f"  📥 {remote_path}")

    print(f"  ✅ 同步完成（{len(remote_files)} 文件核对，{downloaded} 新增）")
    return len(remote_files)


# ── Local classification & organization ─────────────

def deduplicate_files():
    """
    检测并清理重复文件（同名 + 内容完全一致的项目）。
    策略：
      - 找到所有同名（basename 一致）的文件
      - 如果内容完全相同（byte 级），只保留最深路径的那一份
      - 如果内容不同，保留所有（文件名冲突但内容不同）
      - 对保留副本生成 hardlink → 节省空间
    返回清理了多少组重复。
    """
    from collections import defaultdict

    # 收集所有 md 文件，按 basename 分组
    by_name: dict[str, list[Path]] = defaultdict(list)
    for f in sorted(KNOWLEDGES_DIR.rglob("*.md")):
        if f.name in ("README.md", TOOL_NAME) or f.name.startswith("_"):
            continue
        if ".git" in str(f.relative_to(KNOWLEDGES_DIR)).split(os.sep):
            continue
        if _is_skip_path(f):
            continue
        by_name[f.name].append(f)

    # 对 image 目录也做同样扫描
    for f in sorted(KNOWLEDGES_DIR.rglob("*")):
        ext = f.suffix.lower()
        if ext not in KNOWN_IMG_EXTS:
            continue
        if _is_skip_path(f):
            continue
        by_name[f.name].append(f)

    cleaned_groups = 0
    total_removed = 0

    for name, paths in by_name.items():
        if len(paths) < 2:
            continue

        # 按内容分组（相同内容归为一组）
        content_groups: dict[str, list[Path]] = defaultdict(list)
        for p in paths:
            try:
                content = safe_read_bytes(p)
                content_groups[content].append(p)
            except Exception:
                content_groups[repr(p)].append(p)

        for content_key, same_content_paths in content_groups.items():
            if len(same_content_paths) < 2:
                continue

            # 按路径深度排序（deepest first → 从最深的子目录里选保留文件）
            same_content_paths.sort(key=lambda p: len(p.relative_to(KNOWLEDGES_DIR).parts),
                                    reverse=True)

            # 保留最深的那一份
            keeper = same_content_paths[0]
            to_remove = same_content_paths[1:]

            for dup in to_remove:
                try:
                    dup.unlink()
                    dup_rel = str(dup.relative_to(KNOWLEDGES_DIR))
                    print(f"  🗑️ 重复删除: {dup_rel}（同 {str(keeper.relative_to(KNOWLEDGES_DIR))}）")
                    total_removed += 1
                except Exception as e:
                    dup_rel = str(dup.relative_to(KNOWLEDGES_DIR))
                    print(f"  ⚠️ 删除失败 {dup_rel}: {e}")

            cleaned_groups += 1

    if cleaned_groups > 0:
        print(f"  ✅ 去重完成: {cleaned_groups} 组, 删除 {total_removed} 个重复文件")
    return cleaned_groups


def extract_all_files() -> dict[str, list[tuple[str, Path]]]:
    classified: dict[str, list[tuple[str, Path]]] = {}
    image_dir = KNOWLEDGES_DIR / "image"

    for f in sorted(KNOWLEDGES_DIR.rglob("*.md")):
        if f.name in ("README.md", TOOL_NAME) or f.name.startswith("_"):
            continue
        if ".git" in str(f.relative_to(KNOWLEDGES_DIR)).split(os.sep):
            continue
        if image_dir in f.parents:
            continue
        if _is_skip_path(f):
            continue

        result = classify_by_content(f)
        if result:
            label, directory = result
            rel = str(f.relative_to(KNOWLEDGES_DIR))
            classified.setdefault(directory, []).append((rel, f))
        elif f.parent == KNOWLEDGES_DIR:
            classified.setdefault("uncategorized", []).append(("uncategorized", f))

    return classified


def sync_classified_to_local(classified: dict[str, list[tuple[str, Path]]]):
    for directory, entries in classified.items():
        target_base = KNOWLEDGES_DIR / directory
        target_base.mkdir(parents=True, exist_ok=True)
        for rel_path, source_path in entries:
            rel = Path(rel_path)
            if str(rel).startswith(directory + "/"):
                sub = str(rel.relative_to(directory))
                target_path = target_base / sub
            else:
                target_path = target_base / source_path.name

            if source_path.resolve() == target_path.resolve():
                continue
            target_path.parent.mkdir(parents=True, exist_ok=True)
            if target_path.exists():
                target_path.unlink()
            try:
                shutil.move(str(source_path), str(target_path))
                display = str(target_path.relative_to(KNOWLEDGES_DIR))
                print(f"  📦 {display}")
            except Exception as e:
                print(f"  ⚠️ 移动失败 {source_path} → {target_path}: {e}")

    # 清空可能因移动而遗弃的文件（仅同一目录内的残留）
    for directory, entries in classified.items():
        target_dir = KNOWLEDGES_DIR / directory
        known = set()
        for rel_path, source_path in entries:
            rel = Path(rel_path)
            if str(rel).startswith(directory + "/"):
                known.add(str(rel.relative_to(directory)))
            else:
                known.add(source_path.name)
        for f in list(target_dir.glob("*.md")):
            if f.name.startswith("_"):
                continue
            rel_f = str(f.relative_to(target_dir))
            if rel_f not in known:
                try:
                    f.unlink()
                    print(f"  🗑️ {directory}/{rel_f} 删除（已移出本类）")
                except Exception as e:
                    print(f"  ⚠️ 删除失败 {directory}/{rel_f}: {e}")

    # 清理空目录
    def clean_empty_dirs(path):
        for child in sorted(path.iterdir(), reverse=True):
            if child.is_dir():
                clean_empty_dirs(child)
                if not any(True for _ in child.rglob("*")):
                    shutil.rmtree(child, ignore_errors=True)
    for d in list(KNOWLEDGES_DIR.iterdir()):
        if d.is_dir() and not d.name.startswith("."):
            clean_empty_dirs(d)


# ── README ──────────────────────────────────────────

def generate_readme(classified: dict[str, list[tuple[str, Path]]]):
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# 📚 知识库\n",
        "",
        "> 面试 & 技术知识库",
        "> 由 Jarvis II 按文件内容动态分类",
        "",
        "## 📂 目录结构",
        "",
    ]
    count = 0
    for directory in sorted(classified.keys()):
        entries = classified[directory]
        label = DOMAIN_PROFILES.get(directory, {}).get("label", directory)
        lines.append(f"### {directory}/ (`{label}`)")
        subdir_groups: dict[str, list[str]] = {}
        root_files: list[str] = []
        for rel, f in sorted(entries, key=lambda x: x[1].name):
            count += 1
            display_path = f"{directory}/{f.name}" if not rel or rel == "uncategorized" else rel
            rel_obj = Path(rel)
            has_sub = False
            try:
                if str(rel_obj).startswith(directory + "/"):
                    sub = str(rel_obj.relative_to(directory))
                    if "/" in sub:
                        subdir = sub.split("/")[0]
                        subdir_groups.setdefault(subdir, []).append(f"    - `{display_path}`")
                        has_sub = True
            except ValueError:
                pass
            if not has_sub:
                root_files.append(f"  - `{display_path}`")

        for line in root_files:
            lines.append(line)
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
        "本文档库按**内容关键词分析**自动分类（非 Tags 依赖）：",
        "",
        "1. 读取每个文档的**完整内容**（含代码示例）",
        "2. 提取技术关键词，对各领域**打分**",
        "3. Tags 作为**加分项**（+3/标签），不是主要条件",
        "4. 标题关键词额外加分（+5）",
        "5. 得分最高者胜出",
        "",
        f"_[自动生成于 {now_str}]_",
        "",
    ]

    readme_path = KNOWLEDGES_DIR / "README.md"
    safe_write(readme_path, ("\n".join(lines) + "\n").encode("utf-8"))
    print(f"  📝 README.md 已更新 ({count} 篇)")


# ── Push via Git Tree API（批量！） ─────────────────

def create_blob(content: bytes) -> str | None:
    """
    创建 Git Blob，返回 SHA。
    这是唯一必须逐文件调用的 API，但允许并发。
    """
    b64 = base64.b64encode(content).decode()
    body = json.dumps({"content": b64, "encoding": "base64"})
    code, out, _ = call_gh(
        f"repos/{GH_REPO}/git/blobs",
        method="POST", body=body)
    if code != 0:
        return None
    try:
        return json.loads(out).get("sha")
    except json.JSONDecodeError:
        return None


def push_via_tree_api(
    token: str,
    files_to_upload: list[tuple[str, Path]],
    local_paths: set[str],
    sha_map: dict[str, str],
) -> bool:
    """
    批量推送：并发创建 blob → 单次 tree → 单次 commit → 更新 ref。
    清理旧文件：新 tree 不包含要删除的文件即可。
    """
    total = len(files_to_upload)

    # ── 阶段 1: 并发创建 blob ──
    print(f"\n  ⚡ 并发上传 {total} 个文件 blobs（{MAX_WORKERS} 线程）...")
    tree_entries: list[dict] = []
    blob_failures = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_map = {}
        for rel_path, full_path in files_to_upload:
            content = safe_read_bytes(full_path)
            if not content:
                print(f"  ⚠️ 读取失败 {rel_path}")
                blob_failures += 1
                continue
            future = executor.submit(create_blob, content)
            future_map[future] = rel_path

        done = 0
        for future in as_completed(future_map):
            done += 1
            rel_path = future_map[future]
            sha = future.result()
            if sha:
                tree_entries.append({
                    "path": rel_path,
                    "mode": "100644",
                    "type": "blob",
                    "sha": sha,
                })
            else:
                print(f"  ❌ 上传失败: {rel_path}")
                blob_failures += 1

            if done % 10 == 0 or done == total:
                print(f"  ⏳ blob: {done}/{total}")

    if blob_failures > 0:
        print(f"  ⚠️ {blob_failures} 个文件 blob 创建失败")

    if not tree_entries:
        print("  ❌ 没有成功创建任何 blob，放弃推送")
        return False

    # ── 保留远程已有但本地没有的文件 ──
    for path, sha in sha_map.items():
        if path == ".gitignore" or path in local_paths:
            continue
        tree_entries.append({
            "path": path,
            "mode": "100644",
            "type": "blob",
            "sha": sha,
        })

    _check_timeout("create tree")

    # ── 阶段 2: 创建新 tree ──
    print(f"  🌳 创建 Git Tree（{len(tree_entries)} 条目）...")
    tree_body = json.dumps({"tree": tree_entries})
    code, out, _ = call_gh(
        f"repos/{GH_REPO}/git/trees",
        method="POST", body=tree_body,
        timeout=API_TIMEOUT)
    if code != 0:
        print(f"  ❌ 创建 tree 失败")
        return False
    try:
        tree_data = json.loads(out)
        tree_sha = tree_data.get("sha")
    except json.JSONDecodeError:
        print(f"  ❌ 解析 tree 响应失败")
        return False

    if not tree_sha:
        print(f"  ❌ 未获取到 tree SHA")
        return False

    _check_timeout("create commit")

    # ── 阶段 3: 获取 HEAD commit ──
    code, out, _ = call_gh(
        f"repos/{GH_REPO}/git/refs/heads/{GH_BRANCH}",
        timeout=API_TIMEOUT_SHORT)
    if code != 0:
        print(f"  ❌ 获取 HEAD ref 失败")
        return False
    try:
        head_data = json.loads(out)
        head_sha = head_data["object"]["sha"]
    except (json.JSONDecodeError, KeyError):
        print(f"  ❌ 解析 HEAD ref 失败")
        return False

    # ── 阶段 4: 创建 commit ──
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    commit_body = json.dumps({
        "message": f"auto-organize: batch update ({timestamp}) [{total} files]",
        "tree": tree_sha,
        "parents": [head_sha],
    })
    code, out, _ = call_gh(
        f"repos/{GH_REPO}/git/commits",
        method="POST", body=commit_body,
        timeout=API_TIMEOUT)
    if code != 0:
        print(f"  ❌ 创建 commit 失败")
        return False
    try:
        commit_data = json.loads(out)
        commit_sha = commit_data.get("sha")
    except json.JSONDecodeError:
        print(f"  ❌ 解析 commit 响应失败")
        return False

    _check_timeout("update ref")

    # ── 阶段 5: 更新分支 ref ──
    ref_body = json.dumps({
        "sha": commit_sha,
        "force": False,
    })
    code, out, _ = call_gh(
        f"repos/{GH_REPO}/git/refs/heads/{GH_BRANCH}",
        method="PATCH", body=ref_body,
        timeout=API_TIMEOUT_SHORT)
    if code != 0:
        print(f"  ❌ 更新分支引用失败")
        return False

    print(f"  ✅ 推送成功！Commit: {commit_sha[:12]}")
    print(f"  📊 {total} 文件 → 1 commit（含 blob 失败 {blob_failures}）")
    return True


def push_to_github_fallback(token: str, rel_file_map: dict[str, Path], sha_map: dict[str, str]):
    """
    回退方案：逐文件 API 推送（仅在新推送方法失败时使用）。
    与旧版逻辑相同但增加了并发。
    """
    print("\n  ⚠️ 回退到逐文件推送...")
    success = 0
    failed = 0
    total = len(rel_file_map)

    def upload_one(rel_path, full_path):
        nonlocal success, failed
        content = safe_read_bytes(full_path)
        if not content:
            return False
        b64_content = base64.b64encode(content).decode()
        sha = sha_map.get(rel_path)
        data = {
            "message": f"auto-organize: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
            "content": b64_content,
            "branch": GH_BRANCH,
        }
        if sha:
            data["sha"] = sha

        body = json.dumps(data)
        code, out, _ = call_gh(
            f"repos/{GH_REPO}/contents/{rel_path}",
            method="PUT", body=body)
        if code != 0 or "content" not in out:
            return False
        return True

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(upload_one, rel_path, full_path): rel_path
            for rel_path, full_path in rel_file_map.items()
        }
        for future in as_completed(futures):
            rel_path = futures[future]
            if future.result():
                success += 1
            else:
                print(f"  ❌ {rel_path}")
                failed += 1

    print(f"  📊 回退推送: {success}/{total} 成功, {failed} 失败")
    return failed == 0


# ── 子域细分类配置（SUBDOMAIN_PROFILES）────────────────────
# 用于 auto_split_oversized_dirs 的第二阶段分类
SUBDOMAIN_PROFILES: dict[str, dict[str, list[str]]] = {
    "harness": {
        "label": "Agent Harness / 代理框架",
        "keywords": [
            "harness", "agent-harness", "owon", "thinharness", "skillopt",
            "skills add", "langsmith", "skillify", "skill-engineering",
            "npx skills", "agent builder", "agent engineering",
            "mcp server", "build your own agent", "oz multi",
            "orchestration", "agent sandbox", "jini", "agent middleware",
            "agent runtime", "agent hooks", "deterministic control",
        ],
    },
    "patterns": {
        "label": "Agent Patterns / 代理模式",
        "keywords": [
            "agent pattern", "workflow pattern", "multi-agent",
            "agent pipeline", "agent complexity", "ratchet",
            "content production system", "vibe coding",
            "agentic workflow", "agent collaboration",
            "agent communication", "agent coordination",
        ],
    },
    "career": {
        "label": "Career & Skills / 职业发展",
        "keywords": [
            "agent engineer", "survival guide", "roadmap",
            "ai-first team", "don't outsource", "forward deployed",
            "engineering 101", "founders playbook", "startup",
            "senior developers", "zero to ai engineer",
            "career", "job", "hire", "talent", "team building",
            "software engineer", "leading", "engineering culture",
        ],
    },
    "tooling": {
        "label": "Tooling / 开发工具",
        "keywords": [
            "claude code", "cursor", "windsurfer", "copilot",
            "dev tools", "application", "claude desktop",
            "coding tools", "cowork", "work mode",
            "max usage", "claude-switch",
            "code review", "code generation", "debugging",
        ],
    },
    "autoresearch": {
        "label": "Auto Research / 自动研究",
        "keywords": [
            "autoresearch", "autonomous research", "self-improving",
            "agentic research", "research agent", "evo",
            "self-improving agent", "morning brief",
            "agent discovery", "automated research",
            "research automation", "paper reading agent",
        ],
    },
    "inference": {
        "label": "Inference / 推理与部署",
        "keywords": [
            "inference", "llm inference", "gpu memory", "memory bandwidth",
            "rag pipeline", "local ai", "ollama", "vllm",
            "model serving", "quantization", "prompt engineering",
            "decoding", "token", "attention", "transformer",
            "distillation", "sft", "rl", "continual learning",
        ],
    },
    "enterprise": {
        "label": "Enterprise / 企业级实践",
        "keywords": [
            "enterprise", "context layer", "infrastructure",
            "databases vs skills", "evopaw",
            "production", "scaling", "enterprise-grade",
            "enterprise guide", "cloud deployment",
            "security", "compliance", "governance",
        ],
    },
    "codex": {
        "label": "Codex / 代理编码",
        "keywords": [
            "codex", "max", "claude code memory", "agent harness",
            "multi-agent workflows", "builder course",
            "agentic coding", "code generation agent",
            "autonomous coding", "software development agent",
        ],
    },
    "database-experiments": {
        "label": "Database Experiments / 数据库实验",
        "keywords": [
            "database filesystem", "skill", "aparna",
            "experiment", "benchmark", "comparison",
            "database vs", "storage", "filesystem",
        ],
    },
    "ml-research": {
        "label": "ML Research / 机器学习研究",
        "keywords": [
            "papers", "research paper", "arxiv",
            "deepxiv", "huggingface papers",
            "deep learning", "machine learning paper",
            "top papers", "conference paper",
            "model architecture", "training",
            "representation learning", "embedding",
        ],
    },
}

def auto_split_oversized_dirs(classified: dict[str, list]) -> None:
    """Second-pass classification for directories > 20 files.
    Moves files to appropriate subdomain directories based on keyword scoring.
    """
    oversize_threshold = 20
    import shutil

    for directory, entries in list(classified.items()):
        if len(entries) <= oversize_threshold:
            continue

        print(f"  📂 {directory}/ ({len(entries)} 篇，超过阈值，开始细分类...)")
        root_dir = KNOWLEDGES_DIR / directory
        root_dir.mkdir(parents=True, exist_ok=True)

        root_level = []
        nested = []
        for rel, f in entries:
            # A file is "root-level" if its rel path has at most 2 parts: domain/file.md
            rel_parts = Path(rel).parts
            if len(rel_parts) <= 2:
                root_level.append((rel, f))
            else:
                nested.append((rel, f))

        # Score each root-level file against subdomain profiles
        root_rels = {rel for rel, _ in root_level}
        remaining = []
        moved = 0

        for rel, f in root_level:
            content = safe_read_bytes(f).decode("utf-8", errors="replace")
            content_lower = content.lower()
            filename_lower = f.stem.lower()

            best_subdir = None
            best_score = 0
            for subdir, profile in SUBDOMAIN_PROFILES.items():
                score = 0
                for kw in profile["keywords"]:
                    # 词边界匹配，避免 "es" 误中 "these/claudesetup" 等
                    try:
                        kw_pat = re.compile(rf"\b{re.escape(kw)}\b", re.IGNORECASE)
                        fn_hits = len(kw_pat.findall(filename_lower))
                        content_hits = len(kw_pat.findall(content_lower))
                    except re.error:
                        fn_hits = 1 if kw in filename_lower else 0
                        content_hits = content_lower.count(kw)
                    score += fn_hits * 2 + content_hits
                if score > best_score:
                    best_score = score
                    best_subdir = subdir

            if best_subdir and best_score >= 1:
                best_full = f"{directory}/{best_subdir}"
                target_path = KNOWLEDGES_DIR / best_full / f.name
                target_path.parent.mkdir(parents=True, exist_ok=True)
                if target_path.exists():
                    target_path.unlink()
                shutil.move(str(f), str(target_path))
                print(f"    📦 {best_full}/{f.name} (score={best_score})")
                moved += 1
                new_rel = f"{best_full}/{f.name}"
                classified.setdefault(best_full, []).append((new_rel, target_path))
            else:
                remaining.append((rel, f))

        # Update classified for this directory — keep nested entries + remaining root-level
        in_sub = [e for e in entries if e[0] not in root_rels]
        classified[directory] = in_sub + remaining
        print(f"  ✅ 细分类完成: {moved} 个文件移动到子域, {len(remaining)} 个保留在原目录")
# ── Main ────────────────────────────────────────────

def main():
    start_time = time.monotonic()
    global _DEADLINE
    _DEADLINE = time.monotonic() + GLOBAL_TIMEOUT

    print("=" * 50)
    print("📚 知识库整理 & 同步（优化版）")
    print(f"   全局超时: {GLOBAL_TIMEOUT}s | 并发: {MAX_WORKERS} 线程")
    print("=" * 50)

    token = get_github_token()
    if not token:
        print("  ❌ 未找到 GitHub token，退出")
        return

    img_dir = KNOWLEDGES_DIR / "image"
    img_dir.mkdir(exist_ok=True)
    (img_dir / ".gitkeep").write_text("")

    # ── 同步远程 → 本地 ──
    try:
        sync_from_github(token)
    except TimeoutError:
        print("  ⚠️ 同步超时，跳过同步进入本地整理阶段")
    except Exception as e:
        print(f"  ⚠️ 同步异常: {e}")

    # ── 去重 ──
    print("\n  🧹 扫描重复文件...")
    deduplicate_files()

    # ── 本地分类整理 ──
    print("\n  🔍 基于内容分类文档...")
    classified = extract_all_files()

    if not classified:
        print("  ℹ️ 没有待整理的文档")
    else:
        for directory, entries in classified.items():
            label = DOMAIN_PROFILES.get(directory, {}).get("label", directory)
            print(f"  📁 {directory}/ ({label}, {len(entries)} 篇)")
            for rel, f in entries:
                print(f"    - {f.name}")

        subdir_counts = Counter()
        for directory, entries in classified.items():
            for rel, f in entries:
                rel_parts = Path(rel).parts
                sub = f"{rel_parts[0]}/{rel_parts[1]}" if len(rel_parts) > 2 else directory
                subdir_counts[sub] += 1
        oversized = []
        for sub, count in sorted(subdir_counts.items()):
            if count > 20:
                oversized.append(sub)
                print(f"  🚀 {sub}/ ({count} 篇) 超过 20 篇限制，自动细分类中...")
        if not oversized:
            print(f"  ✅ 所有子目录文件数未超过 20 篇阈值")

        if oversized:
            auto_split_oversized_dirs(classified)

        print("\n  🔄 整理移动文件...")
        sync_classified_to_local(classified)
        # 如果 auto_split 已执行，files 已在正确位置，不需要重新分类
        if not oversized:
            classified = extract_all_files()
        generate_readme(classified)

    # ── 收集待上传文件 ──
    files_to_upload: list[tuple[str, Path]] = []
    for directory, entries in classified.items():
        for rel, f in entries:
            rel_path = rel if rel and rel != "uncategorized" else f"{directory}/{f.name}"
            files_to_upload.append((rel_path, f))

    readme_path = KNOWLEDGES_DIR / "README.md"
    files_to_upload.append(("README.md", readme_path))

    image_dir = KNOWLEDGES_DIR / "image"
    if image_dir.exists():
        for img_file in sorted(image_dir.rglob("*")):
            if img_file.is_dir() or img_file.name == ".gitkeep" or img_file.name.startswith("."):
                continue
            if not KNOWN_IMG_EXTS.intersection({img_file.suffix.lower()}):
                continue
            rel_img = str(img_file.relative_to(KNOWLEDGES_DIR))
            files_to_upload.append((rel_img, img_file))

    if not files_to_upload:
        print("\n  ℹ️ 没有文件需要上传")
        elapsed = time.monotonic() - start_time
        print(f"\n✅ 整理完成（耗时 {elapsed:.1f}s）")
        return

    # ── 推送 ──
    local_paths = {p for p, _ in files_to_upload}
    local_paths.add(TOOL_NAME)
    sha_map = build_sha_map()

    try:
        ok = push_via_tree_api(token, files_to_upload, local_paths, sha_map)
        if not ok:
            print("  ⚠️ 批量推送失败，尝试回退方案...")
            rel_file_map = {p: f for p, f in files_to_upload}
            push_to_github_fallback(token, rel_file_map, sha_map)
    except TimeoutError as e:
        print(f"\n  ⚠️ {e}")
        print("  尝试回退方案...")
        rel_file_map = {p: f for p, f in files_to_upload}
        push_to_github_fallback(token, rel_file_map, sha_map)
    except Exception as e:
        print(f"\n  ⚠️ 推送异常: {e}")

    elapsed = time.monotonic() - start_time
    print(f"\n" + "=" * 50)
    print(f"✅ 整理完成（耗时 {elapsed:.1f}s）")
    print("=" * 50)


if __name__ == "__main__":
    main()
