#!/bin/bash
# Fetch top 10 GitHub trending repositories (today)
# Output: JSON array of {name, url, description, language, stars_today, stars_total}

set -euo pipefail

# Use JinAI reader to bypass any restrictions
data=$(curl -sL --max-time 20 \
  "https://r.jina.ai/https://github.com/trending" \
  -H "Content-Type: application/json" \
  -d '{}' 2>/dev/null)

if [ -z "$data" ]; then
  # Fallback: direct fetch
  data=$(curl -sL --max-time 15 \
    -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" \
    "https://github.com/trending" 2>/dev/null)
fi

# Parse the data to extract repo info
# GitHub trending page has articles with h2 containing repo names
echo "$data" | python3 -c "
import re, sys, json

text = sys.stdin.read()

# Try to extract from markdown/content
repos = []

# Pattern 1: Look for repo links like owner/name
# From JinAI output or raw HTML
if 'github.com' in text:
    # Find all repo references
    lines = text.split('\n')
    current_repo = None
    current_desc = ''
    current_lang = ''
    current_stars = ''
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Match repository name patterns like 'owner/repo'
        repo_match = re.match(r'^([a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+)\s*$', line)
        if repo_match:
            name = repo_match.group(1)
            # Skip if not a valid repo name (has common words)
            if re.match(r'^[A-Z][a-z]+/[A-Z]', name) and name.count('/') == 1:
                desc = lines[i+1].strip() if i+1 < len(lines) else ''
                # Clean desc
                desc = re.sub(r'\s+', ' ', desc).strip()
                repos.append({
                    'name': name,
                    'description': desc[:200],
                    'language': '',
                    'stars_today': '',
                    'stars_total': '',
                    'url': f'https://github.com/{name}'
                })

# If empty, try regex on full text
if not repos:
    repo_pattern = re.findall(r'([a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+)', text)
    seen = set()
    for r in repo_pattern:
        # Filter: must have exactly one slash, not too short
        if r.count('/') == 1 and len(r) > 3 and r not in seen:
            seen.add(r)
            # Basic validation: not common words
            common = {'Trending', 'JavaScript', 'Python', 'TypeScript', 'Go', 'Rust', 'Java'}
            parts = r.split('/')
            if len(parts) == 2 and parts[0] not in common and len(parts[0]) > 1:
                repos.append({
                    'name': r,
                    'description': '',
                    'language': '',
                    'stars_today': '',
                    'stars_total': '',
                    'url': f'https://github.com/{r}'
                })

# Deduplicate and limit to 10
seen_names = set()
unique = []
for r in repos:
    if r['name'] not in seen_names:
        seen_names.add(r['name'])
        unique.append(r)

json.dump(unique[:10], sys.stdout, ensure_ascii=False, indent=2)
" 2>/dev/null

exit 0
