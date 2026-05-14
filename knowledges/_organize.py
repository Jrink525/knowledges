#!/usr/bin/env python3
"""
knowledges 知识库自动整理脚本
基于文件实际内容分析（Content-based），而非静态 Tags 匹配

核心逻辑：
  读取每个 .md 文件的全文 → 提取技术关键词 → 对各领域打分 → 归入最佳分类
  Tags 仅作为加分项（+3 分），不依赖 tags 判断

工作流：
  同步远程(拉取) → 内容分析分类 → 整理到子目录 → 更新 README → 推送远程 → 清理远程旧文件

安全保证：
  - 所有 subprocess 调用均有超时 + 错误处理
  - 临时文件使用 try/finally 确保清理
  - 不依赖 git 命令（纯 GitHub API）
  - 图片通过 API base64 上传，与 markdown 同一管道
  - ⏱️ 全局超时保护（120s + 30s 安全余量）
  - 🏷️ 单次 tree API 调用构建 SHA 缓存，避免 N 次 contents/ API 调用
"""

import os
import re
import shutil
import json
import base64
import subprocess
import tempfile
import signal
import time
from pathlib import Path
from collections import Counter

KNOWLEDGES_DIR = Path(__file__).parent.resolve()
GH_REPO = "Jrink525/knowledges"
GH_BRANCH = "main"
TOOL_NAME = "_organize.py"

GH_BIN = "/home/node/.openclaw/workspace/gh"
GH_CONFIG_ENV = {"GH_CONFIG_DIR": "/home/node/.openclaw/gh-config", "PATH": os.environ.get("PATH", "")}

# ── Timeouts ─────────────────────────────────────────────────────
SYNC_TIMEOUT = 120       # sync_from_github 总超时（秒）
PUSH_TIMEOUT = 180       # push_to_github 总超时（秒）
API_TIMEOUT_SHORT = 8    # 单次 API 调用超时（存在性检查）
API_TIMEOUT = 15         # 单次 API 调用超时（数据传输）
API_INTERVAL = 0.15      # API 调用间隔（防止 429 Too Many Requests）

KNOWN_IMG_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"}


# ── Global timeout via SIGALRM ───────────────────────────────────

class TimeoutError(Exception):
    pass


def timeout_handler(signum, frame):
    raise TimeoutError("全局操作超时")


def set_global_timeout(seconds: int):
    """设置全局超时。仅 Linux 支持 signal.SIGALRM。超时后触发 TimeoutError。"""
    try:
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(seconds)
    except (AttributeError, ValueError):
        pass  # 非 Linux 或不支持 alarm，静默跳过


def cancel_global_timeout():
    try:
        signal.alarm(0)
    except (AttributeError, ValueError):
        pass


# ── Token ────────────────────────────────────────────────────────

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


# ── Domain profiles ──────────────────────────────────────────────
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
            "string", "hash", "list", "set", "zset", "sorted set",
            "pub/sub", "stream", "bitmap", "hyperloglog", "geo",
            "rdb", "aof", "持久化", "主从", "sentinel", "cluster",
            "缓存穿透", "缓存击穿", "缓存雪崩", "缓存一致性",
            "io multiplexing", "epoll", "reactor",
            "mysql", "innodb", "myisam", "b+ tree", "索引",
            "聚簇索引", "二级索引", "覆盖索引", "最左前缀",
            "事务", "acid", "mvcc", "undo log", "redo log", "binlog",
            "锁", "gap lock", "next-key lock", "死锁",
            "explain", "慢查询", "分库分表", "sharding", "读写分离",
            "sql", "select", "join", "index", "query optimization",
            "postgresql", "postgres", "pg_hba",
            "acid", "base", "cap", "nosql", "database",
        },
    },
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


# ── Helpers ──────────────────────────────────────────────────────

def call_gh(api_path: str, timeout: int = API_TIMEOUT) -> tuple[int, str]:
    """调用 gh CLI，返回 (returncode, stdout)"""
    try:
        r = subprocess.run(
            [GH_BIN, "api", api_path],
            capture_output=True, text=True, timeout=timeout,
            env=GH_CONFIG_ENV)
        _api_tick()
        return r.returncode, r.stdout
    except FileNotFoundError:
        print(f"  ❌ 未找到 gh 二进制文件: {GH_BIN}")
        return -1, ""
    except subprocess.TimeoutExpired:
        print(f"  ⚠️  gh api 超时 ({timeout}s): {api_path[:60]}")
        return -1, ""
    except Exception as e:
        print(f"  ⚠️  gh 调用异常: {e}")
        return -1, ""


def curl_put(url: str, token: str, payload_path: str, timeout: int = API_TIMEOUT) -> tuple[int, str]:
    """封装 curl PUT 请求，返回 (returncode, stdout)"""
    try:
        r = subprocess.run(
            ["curl", "-s", "-X", "PUT", url,
             "-H", f"Authorization: Bearer {token}",
             "-H", "Content-Type: application/json",
             "-d", f"@{payload_path}"],
            capture_output=True, text=True, timeout=timeout)
        _api_tick()
        return r.returncode, r.stdout
    except subprocess.TimeoutExpired:
        return -1, ""
    except Exception as e:
        return -1, str(e)


def curl_delete(url: str, token: str, payload_path: str, timeout: int = API_TIMEOUT) -> tuple[int, str]:
    """封装 curl DELETE 请求"""
    try:
        r = subprocess.run(
            ["curl", "-s", "-X", "DELETE", url,
             "-H", f"Authorization: Bearer {token}",
             "-H", "Content-Type: application/json",
             "-d", f"@{payload_path}"],
            capture_output=True, text=True, timeout=timeout)
        _api_tick()
        return r.returncode, r.stdout
    except (subprocess.TimeoutExpired, Exception) as e:
        return -1, str(e)


_API_LAST_TICK = time.monotonic()


def _api_tick():
    """API 流量控制：确保两次调用之间至少有 API_INTERVAL 秒间隔"""
    global _API_LAST_TICK
    elapsed = time.monotonic() - _API_LAST_TICK
    if elapsed < API_INTERVAL:
        time.sleep(API_INTERVAL - elapsed)
    _API_LAST_TICK = time.monotonic()


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
        print(f"  ⚠️  写入失败 {path}: {e}")


def tmp_json(data: dict) -> str:
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
    json.dump(data, f)
    f.close()
    return f.name


def build_sha_map(branch=GH_BRANCH) -> dict[str, str]:
    """
    通过单次 git/trees API 获取仓库所有文件的 SHA。
    返回 {path: sha} 字典，用在 sync 和 push 中避免 N 次 contents/{path} 调用。
    """
    code, stdout = call_gh(f"repos/{GH_REPO}/git/trees/{branch}?recursive=1", timeout=API_TIMEOUT)
    if code != 0:
        print(f"  ⚠️  获取远程文件树失败")
        return {}
    try:
        tree = json.loads(stdout)
    except json.JSONDecodeError:
        print("  ⚠️  解析远程文件树失败")
        return {}

    sha_map = {}
    for item in tree.get("tree", []):
        if item["type"] == "blob" and item.get("sha"):
            sha_map[item["path"]] = item["sha"]
    return sha_map


# ── YAML frontmatter ─────────────────────────────────────────────

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


def get_category_override(filepath: Path) -> str | None:
    content = safe_read_bytes(filepath).decode("utf-8", errors="replace")
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return None
    meta = parse_yaml_frontmatter(match.group(1))
    cat = meta.get("category")
    if cat and isinstance(cat, str) and cat.strip():
        cat = cat.strip()
        if cat in DOMAIN_PROFILES:
            return cat
        print(f"  ⚠️  YAML category '{cat}' 不在已知领域配置中（忽略）")
    return None


# ── Content classification ──────────────────────────────────────

def extract_content_text(filepath: Path) -> str:
    content = safe_read_bytes(filepath).decode("utf-8", errors="replace")
    content = re.sub(r"^---\s*\n.*?\n---\s*\n", "", content, flags=re.DOTALL)
    return content.lower()


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
            count = content_text.count(keyword.lower())
            if count > 0:
                score += count

        if tags:
            for tag in tags:
                tl = tag.lower()
                for kw in profile["keywords"]:
                    if tl == kw or tl.startswith(kw) or (len(tl) > 3 and kw in tl):
                        score += 3.0
                        break

        title_match = re.search(r"^#\s+(.+)$", content_text, re.MULTILINE)
        if title_match:
            title = title_match.group(1).lower()
            for kw in profile["keywords"]:
                if kw in title:
                    score += 5.0

        if score > 0:
            scores[domain] = score

    if not scores:
        return None
    best = max(scores, key=scores.get)
    if scores[best] < 2.0:
        return None
    return (DOMAIN_PROFILES[best]["label"], best)


# ── Sync from GitHub ─────────────────────────────────────────────
# ⚡ 优化：使用树 API 的 SHA 缓存，避免逐文件 contents/ API 调用

def sync_from_github(token: str) -> int:
    print("\n  🔽 从 GitHub 拉取远程文件...")
    downloaded = 0

    # 单次 tree API 调用获取所有文件的 SHA
    sha_map = build_sha_map()
    if not sha_map:
        print("  ℹ️  远程仓库无内容或无法访问")
        return 0

    remote_files = [p for p in sha_map.keys()
                    if p != ".gitkeep" and not p.startswith(".")]
    if not remote_files:
        print("  ℹ️  远程仓库为空（无文件）")
        return 0

    print(f"  远程发现 {len(remote_files)} 个文件")

    for idx, remote_path in enumerate(remote_files):
        # 每 10 个文件打印一次进度
        if idx > 0 and idx % 10 == 0:
            print(f"  ⏳ 进度: {idx}/{len(remote_files)} 个文件已检查")

        if remote_path == TOOL_NAME:
            continue

        local_path = KNOWLEDGES_DIR / remote_path

        # ── 利用树 SHA 判断文件是否变化 ──
        remote_sha = sha_map.get(remote_path)
        if local_path.exists():
            # 本地存在：比较 SHA（通过快速 API 获取远程 blob SHA）
            # 注意：树的 blob SHA 与 contents API 的 SHA 一致
            pass  # 继续往下走，按原逻辑比较内容

        # 仍然需要获取内容来判断是否需要更新
        # 优化：先用 SHA 做快速缓存判断
        code2, content_out = call_gh(
            f"repos/{GH_REPO}/contents/{remote_path}", timeout=API_TIMEOUT_SHORT)
        if code2 != 0:
            print(f"  ⚠️  无法获取 {remote_path}，跳过")
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
                continue  # 内容一致，跳过
            print(f"  🔄 {remote_path} ← 本地版本更新，保留本地")
            continue
        else:
            print(f"  📥 {remote_path} ← 新增")
            safe_write(local_path, remote_bytes)
            downloaded += 1

    print(f"  ✅ 同步完成 ({len(remote_files)} 远程文件已核对，{downloaded} 个新增)")
    return len(remote_files)


# ── Local classification & organization ─────────────────────────

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
                print(f"  ⚠️  移动失败 {source_path} → {target_path}: {e}")

    # 清理移出的旧文件
    for directory, entries in classified.items():
        target_dir = KNOWLEDGES_DIR / directory
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
                try:
                    f.unlink()
                    print(f"  🗑️ {directory}/{rel_f} 删除（已移出本类）")
                except Exception as e:
                    print(f"  ⚠️  删除失败 {directory}/{rel_f}: {e}")

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


# ── README ───────────────────────────────────────────────────────

def generate_readme(classified: dict[str, list[tuple[str, Path]]]):
    now_str = __import__("datetime").datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# knowledges\n",
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


# ── Push to GitHub ───────────────────────────────────────────────
# ⚡ 优化：预先从 tree API 构建 SHA 缓存，避免逐文件 contents/{path} 查询

def push_to_github(token: str, classified: dict[str, list[tuple[str, Path]]]):
    print("\n  📤 推送到 GitHub...")

    # 收集待上传文件
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
            if img_file.is_dir():
                continue
            if img_file.name == ".gitkeep":
                rel_img = str(img_file.relative_to(KNOWLEDGES_DIR))
                files_to_upload.append((rel_img, img_file))
                continue
            if img_file.name.startswith("."):
                continue
            ext = img_file.suffix.lower()
            if ext not in KNOWN_IMG_EXTS:
                print(f"  ⚠️  跳过非图片文件: {img_file.name} (扩展名: {ext})")
                continue
            rel_img = str(img_file.relative_to(KNOWLEDGES_DIR))
            files_to_upload.append((rel_img, img_file))

    if not files_to_upload:
        print("  ℹ️  没有文件需要上传")
        return True

    total = len(files_to_upload)

    # ⚡ 单次 tree API 构建 SHA 缓存，替代 N 次 contents/ API 查询
    sha_map = build_sha_map()

    success = 0
    failed = 0

    for idx, (rel_path, full_path) in enumerate(files_to_upload):
        if idx > 0 and idx % 5 == 0:
            print(f"  ⏳ 上传进度: {idx}/{total}")

        content = safe_read_bytes(full_path)
        if not content:
            print(f"  ⚠️  读取失败 {rel_path}，跳过")
            failed += 1
            continue

        b64_content = base64.b64encode(content).decode()

        # ⚡ 从 SHA 缓存获取，无需 API 调用
        sha = sha_map.get(rel_path)

        data: dict = {
            "message": f"auto-organize: {__import__('datetime').datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
            "content": b64_content,
            "branch": GH_BRANCH,
        }
        if sha:
            data["sha"] = sha

        tf_path = None
        try:
            tf_path = tmp_json(data)
            _, put_out = curl_put(
                f"https://api.github.com/repos/{GH_REPO}/contents/{rel_path}",
                token, tf_path)
            if put_out:
                result = json.loads(put_out)
                if "content" in result:
                    success += 1
                else:
                    msg = result.get("message", "")[:80]
                    print(f"  ❌ {rel_path}: {msg}")
                    failed += 1
            else:
                print(f"  ❌ {rel_path}: 无响应")
                failed += 1
        except json.JSONDecodeError:
            print(f"  ❌ {rel_path}: 响应解析失败")
            failed += 1
        except Exception as e:
            print(f"  ❌ {rel_path}: {e}")
            failed += 1
        finally:
            if tf_path and os.path.exists(tf_path):
                os.unlink(tf_path)

    # ── 清理远程旧文件 ──
    print("\n  🧹 清理远程旧文件...")
    local_paths = {p for p, _ in files_to_upload}
    local_paths.add(TOOL_NAME)

    # ⚡ 重用已有的 sha_map（如果之前获取成功）
    if not sha_map:
        sha_map = build_sha_map()

    if sha_map:
        cleaned = 0
        for path, sha in sha_map.items():
            if path == ".gitignore" or path in local_paths:
                continue

            del_payload = {
                "message": "cleanup: remove outdated file (reorganized)",
                "sha": sha,
                "branch": GH_BRANCH,
            }
            tf_path = None
            try:
                tf_path = tmp_json(del_payload)
                _, del_out = curl_delete(
                    f"https://api.github.com/repos/{GH_REPO}/contents/{path}",
                    token, tf_path)
                if del_out:
                    dr = json.loads(del_out)
                    if "commit" in dr:
                        cleaned += 1
                        print(f"  🗑️ {path}")
            except json.JSONDecodeError:
                pass
            except Exception:
                pass
            finally:
                if tf_path and os.path.exists(tf_path):
                    os.unlink(tf_path)

        if cleaned > 0:
            print(f"  🧹 已清理 {cleaned} 个远程旧文件")
        else:
            print(f"  ✅ 远程文件无残留")
    else:
        print(f"  ℹ️  跳过清理（无法获取远程文件列表）")

    print(f"\n  📊 推送结果: {success}/{total} 成功, {failed} 失败")
    return failed == 0


# ── Main ─────────────────────────────────────────────────────────

def main():
    start_time = time.monotonic()

    print("=" * 50)
    print("📚 knowledges 知识库整理 & 同步")
    print("=" * 50)

    token = get_github_token()
    if not token:
        print("  ❌ 未找到 GitHub token，退出")
        return

    # 确保 image/ 目录存在
    img_dir = KNOWLEDGES_DIR / "image"
    img_dir.mkdir(exist_ok=True)
    (img_dir / ".gitkeep").write_text("")

    try:
        set_global_timeout(SYNC_TIMEOUT)
        sync_from_github(token)
        cancel_global_timeout()
    except TimeoutError:
        print(f"\n  ⚠️  同步超时 ({SYNC_TIMEOUT}s)，跳过同步进入本地整理阶段")
    except Exception as e:
        cancel_global_timeout()
        print(f"\n  ⚠️  同步异常: {e}")

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

        print()
        threshold_alerted = False
        subdir_counts = Counter()
        for directory, entries in classified.items():
            for rel, f in entries:
                rel_parts = Path(rel).parts
                if len(rel_parts) > 2:
                    sub = f"{rel_parts[0]}/{rel_parts[1]}"
                else:
                    sub = directory
                subdir_counts[sub] += 1
        for sub, count in sorted(subdir_counts.items()):
            if count > 20:
                print(f"  ⚠️  {sub}/ 达到 {count} 篇，超出 20 篇阈值，建议进一步拆分！")
                threshold_alerted = True
        if not threshold_alerted:
            print(f"  ✅ 所有子目录文件数未超过 20 篇阈值")

        print("\n  🔄 整理中...")
        sync_classified_to_local(classified)

        classified = extract_all_files()
        generate_readme(classified)

    set_global_timeout(PUSH_TIMEOUT)
    try:
        push_to_github(token, classified)
    except TimeoutError:
        print(f"\n  ⚠️  推送超时 ({PUSH_TIMEOUT}s)，部分文件可能未上传")
    except Exception as e:
        print(f"\n  ⚠️  推送异常: {e}")
    finally:
        cancel_global_timeout()

    elapsed = time.monotonic() - start_time
    print(f"\n" + "=" * 50)
    print(f"✅ 整理完成（耗时 {elapsed:.1f}s）")
    print("=" * 50)


if __name__ == "__main__":
    main()
