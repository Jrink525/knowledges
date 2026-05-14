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
web_fetch(url="https://freedium-mirror.cfd/https://medium.com/...", maxChars=100000)
```

**Fallback chain** (try in order):
```
1. https://freedium-mirror.cfd/https://medium.com/...
2. https://freedium.cfd/https://medium.com/...
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

### Image Extraction (X/Twitter)

fxtwitter API returns media in `tweet.media.all` (array) for tweet-level images, and `tweet.article.content.media` (array) for article-level images. Each entry has:
- `url`: direct image URL
- `type`: mime type (e.g. `image/jpeg`, `image/png`)
- `altText`: optional alt text
- `width` / `height`: dimensions

**Extraction pattern:**

```python
media = []
# Tweet-level media
if 'media' in tweet and 'all' in tweet['media']:
    media.extend(tweet['media']['all'])
# Article-level media
if 'article' in tweet and 'content' in tweet['article'] and 'media' in tweet['article']['content']:
    media.extend(tweet['article']['content']['media'])
```

For general web pages, extract `<img>` src URLs from HTML content.

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

## 🖼️ Image Handling — Extract, Save, Reference

### Image Storage

Images from articles are saved to a unified directory:
```
knowledges/image/
```

This directory is excluded from `_organize.py` classification (images are not articles).

### Naming Convention

```
{article-slug}-{n}.{ext}
```

Where `article-slug` is the markdown filename without `.md`, `n` is a 1-based index, and `ext` is the original extension (`jpg`, `png`, `gif`).

### Step-by-Step Flow

1. **Extract** image URLs from the fetched content
2. **Download** via `curl -s -o <path> <url>`
3. **Save** to `knowledges/image/`
4. **Reference** in markdown with relative path: `![description](../image/filename.jpg)`

### X/Twitter Image Extraction

From fxtwitter JSON response, extract media URLs:

```python
import json, subprocess, os

def extract_and_save_images(tweet_data, article_slug):
    """
    Extract image URLs from fxtwitter response and save them.
    Returns list of (local_path, alt_text) tuples for markdown insertion.
    """
    images = []
    tweet = tweet_data.get('tweet', {})
    image_dir = '/home/node/.openclaw/workspace/knowledges/image'
    os.makedirs(image_dir, exist_ok=True)
    
    # 1. Collect media from tweet-level (all media types)
    if 'media' in tweet and 'all' in tweet['media']:
        for m in tweet['media']['all']:
            if m.get('type', '').startswith('image'):
                images.append({
                    'url': m['url'],
                    'alt': m.get('altText', ''),
                    'ext': m['url'].rsplit('.', 1)[-1].split('?')[0]
                })
    
    # 2. Collect media from article-level content
    if ('article' in tweet and 'content' in tweet['article'] 
            and 'media' in tweet['article']['content']):
        for m in tweet['article']['content']['media']:
            if m.get('type', '').startswith('image'):
                images.append({
                    'url': m['url'],
                    'alt': m.get('altText', ''),
                    'ext': m['url'].rsplit('.', 1)[-1].split('?')[0]
                })
    
    # 3. Deduplicate by URL
    seen_urls = set()
    unique_images = []
    for img in images:
        if img['url'] not in seen_urls:
            seen_urls.add(img['url'])
            unique_images.append(img)
    
    # 4. Download and save
    saved = []
    for i, img in enumerate(unique_images):
        filename = f"{article_slug}-{i+1}.{img['ext']}"
        local_path = os.path.join(image_dir, filename)
        subprocess.run([
            "curl", "-s", "-o", local_path,
            img['url']
        ], capture_output=True, timeout=15)
        
        if os.path.exists(local_path) and os.path.getsize(local_path) > 100:
            saved.append({
                'rel_path': f"../image/{filename}",
                'alt': img['alt']
            })
            print(f"  🖼️  Saved: image/{filename}")
        else:
            print(f"  ⚠️  Failed to save: {img['url']}")
    
    return saved


# Usage after fetching article:
# saved_images = extract_and_save_images(data, "article-slug-here")
# Then use saved_images in markdown: f"![alt]({img['rel_path']})"
```

### General Web Page Images

For non-X articles (Medium, general web):
1. Scan the fetched markdown content for image URLs
2. Download relevant images (infographics, diagrams, screenshots — skip avatars, icons, ads)
3. Save to `knowledges/image/`
4. Replace absolute URLs in markdown with relative paths

### Link Format in Markdown

```markdown
<!-- Article images use relative paths from their category subdirectory -->

![Claude Code Routines architecture](../image/claude-code-routines-full-course-1.jpg)

<!-- The ../image/ path works because articles are in subdirectories like:
     ai-tools/claude/article.md → ../image/image.jpg → knowledges/image/image.jpg -->
```

### Push to GitHub

When using `_organize.py push`, images in `knowledges/image/` are NOT auto-uploaded via the GitHub API (binary content). Use git directly for the initial seed:

```bash
cd /home/node/.openclaw/workspace/knowledges
git add image/
git commit -m "feat: add article images"
git push
```

For subsequent pushes with `_organize.py`, images can be committed via the same git flow alongside the API-based push, or add a post-push script to the organize script to `git push` the images dir separately if the API approach is used.

---

## GitHub Push

After saving to `knowledges/`:

```bash
cd /home/node/.openclaw/workspace/knowledges
python3 _organize.py
```

This auto-classifies, updates README, and pushes to GitHub. No manual git steps needed.

### Push with Images

Since `_organize.py` uses the GitHub Content API (no git client needed for markdown), images must be pushed via git when present:

```bash
cd /home/node/.openclaw/workspace/knowledges
# Markdown files: use organize script API push
python3 _organize.py push
# Images: use git directly
GH_CONFIG_DIR=/home/node/.openclaw/gh-config git add image/
GH_CONFIG_DIR=/home/node/.openclaw/gh-config git commit -m "feat: add article images"
GH_CONFIG_DIR=/home/node/.openclaw/gh-config git push
```

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
