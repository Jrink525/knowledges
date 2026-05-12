---
name: read-content-from-web
description: Read long-form content from paywalled or login-walled sites. Supports Medium articles (via freedium mirror), X/Twitter long-form articles (via fxtwitter API), and general web pages. When user shares any URL for reading/extraction/note-taking, handle everything automatically without asking for repeated instructions.
---

# Read Content from Web

## ⚡ Default Behavior (No Questions Asked)

When the user shares a URL and asks to read/extract/note/summarize it:

1. **Auto-detect** the site type (Medium / X / other)
2. **Fetch full content** using the best available method
3. **Translate to Chinese** (if English original) with natural, idiomatic flow
4. **Enhance** — clarify, structure, add glosses, extract key points
5. **Save** to `knowledges/<category>/` with proper YAML frontmatter
6. **Classify & push** — run `_organize.py` to auto-classify and push to GitHub

No need to ask the user "should I translate?" or "where should I save?" — these are the defaults.

---

## Supported Sites & Fetch Methods

### Medium

**Primary:** Freedium mirror
```
web_fetch(url="https://freedium.cfd/https://medium.com/...", maxChars=100000)
```

**Fallback chain** (try in order):
```
1. https://freedium.cfd/https://medium.com/...
2. https://freedium-mirror.cfd/https://medium.com/...
3. https://freedium-tnrt.onrender.com/https://medium.com/...
4. https://webcache.googleusercontent.com/search?q=cache:https://medium.com/...
```

### X/Twitter

**For long-form articles** (detect by checking if response has `tweet.article`):
```
https://api.fxtwitter.com/{username}/status/{tweet_id}
```

Content extraction (Python):
```python
import json, sys
data = json.loads(sys.stdin.read())
# Long-form article
blocks = data['tweet']['article']['content']['blocks']
# Regular tweet
text = data['tweet']['text']
```

**For regular tweets** — same fxtwitter API, extract `tweet.text`.

**Fallback:** `https://api.vxtwitter.com/{username}/status/{tweet_id}`

### General Web Pages

`web_fetch` with appropriate `maxChars` (default 100000 for articles, 15000 for quick lookups).

---

## OpenClaw Tool Notes & Workarounds

### web_fetch truncation

`web_fetch` has a hard cap (~100-400KB depending on content). For articles that may exceed this:

1. First try `web_fetch(url="...", maxChars=100000)`
2. If truncated (detect by incomplete sentence at end or missing closing content), use `exec` + `curl` + Python for full extraction:

```python
# Full extraction via curl
import subprocess, json
result = subprocess.run([
    "curl", "-s",
    "https://api.fxtwitter.com/{username}/status/{tweet_id}"
], capture_output=True, text=True, timeout=15)
data = json.loads(result.stdout)
# Now extract blocks even if large
```

### curl SSL issues

If curl returns SSL errors, add `-k` flag:
```
curl -sk "https://..."
```

---

## Translation Principles

- **No literal/机械翻译** — produce natural, idiomatic Chinese
- Preserve technical terms in English when appropriate (add Chinese gloss on first use)
- Keep code blocks in original language (only translate comments)
- For author voice/personality, preserve the tone
- For technical concepts: accuracy over elegance

---

## Enhancement Patterns

Apply automatically after fetching + translating:

| Content Type | Enhancement |
|-------------|-------------|
| Technical article | Add code examples, best practices, interview Q&A |
| Comparison/review | Reorganize as comparison table |
| Tutorial | Add prerequisite notes, common pitfalls |
| News/announcement | Add context, significance analysis |
| Long-form analysis | Structured summary with key takeaways |

---

## Output Structure

When saving to knowledge base, use this format:

```markdown
---
title: "Translated Title"
tags:
  - auto-detected-tags
date: YYYY-MM-DD
source: "original-url"
authors: "author-name"
---

# Chinese Title

> **来源：** [original-title](original-url)

Translated and enhanced content...

---

*Processed on {date} from {source-url}*
```

---

## GitHub Push

After saving to `knowledges/`:

```bash
cd /home/node/.openclaw/workspace/knowledges
python3 _organize.py
```

This auto-classifies, updates README, and pushes to GitHub. No manual git steps needed.

---

## 📂 Directory Size Management

### Threshold Rule

When any knowledge base directory (including subdirectories) exceeds **20 files**, automatically trigger a re-classification/split into finer-grained subdirectories.

### Current Subdirectory Structure (ai-tools example)

```
ai-tools/
├── agent-engineering/   (agent architecture, patterns, survival guide)
├── claude/              (Claude Code specific guides)
├── frameworks/          (agent framework comparisons)
└── ml-research/         (ML/RL papers)
```

### When to Split

| Threshold | Action |
|-----------|--------|
| > 20 files in any dir | Analyze content themes → create subdirectories → move files → update `_organize.py` subdirectory profiles |
| > 40 files in a subdir | Further split: e.g. `agent-engineering/` → `agent-engineering/patterns/` + `agent-engineering/practice/` |

### Implementation

During `_organize.py` execution, after classification:

```python
# Pseudo-logic
for directory in classified_dirs:
    count = len(list((KNOWLEDGES_DIR / directory).rglob("*.md")))
    if count > 20:
        print(f"  ⚠️  {directory}/ 达到 {count} 篇，建议拆分")
        # Trigger subdirectory audit or split routine
```

### When It Runs

- After every `_organize.py` run (implicitly checked)
- Also check explicitly when adding files manually
- The threshold is per-directory, not total — `agent-engineering/` 18 篇 + `spring/` 5 篇 = 各自独立计算

---

## Quick Reference: URL Detection

| URL Pattern | Site | Method |
|-------------|------|--------|
| `medium.com/...` | Medium | Freedium mirror |
| `towardsdatascience.com/...` | Medium (custom domain) | Freedium mirror |
| `x.com/.../status/...` | X/Twitter | fxtwitter API |
| `twitter.com/.../status/...` | X/Twitter | fxtwitter API |
| anything else | General | web_fetch |
