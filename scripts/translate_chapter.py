#!/usr/bin/env python3
"""
Translate a single LaTeX chapter file into bilingual (English/Chinese) markdown.
Uses the OpenAI-compatible API (DeepSeek by default).

Usage:
    python3 translate_chapter.py --input /path/to/chapter.tex --output /path/to/out.md [--api-base URL] [--model MODEL]
"""
import os, sys, re, json, time, argparse
from pathlib import Path

# Add the parent dir of this script to path
SCRIPT_DIR = Path(__file__).parent.absolute()

def setup_api():
    """Get API config from environment or OpenClaw config."""
    api_key = os.environ.get("OPENAI_API_KEY")
    api_base = os.environ.get("OPENAI_BASE_URL", "https://api.deepseek.com/v1")
    
    # Try to read from openclaw config
    if not api_key:
        config_path = Path.home() / ".openclaw" / "openclaw.json"
        if config_path.exists():
            try:
                import json
                config = json.loads(config_path.read_text())
                # Look for OpenAI API key in config...
                pass
            except:
                pass
    
    if not api_key:
        print("ERROR: OPENAI_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    
    return api_key, api_base


def translate_chunk(chunk_text, chapter_title, api_key, api_base, model="deepseek-v4-flash", retries=3):
    """Translate a chunk of LaTeX text to bilingual markdown."""
    from openai import OpenAI
    
    client = OpenAI(api_key=api_key, base_url=api_base)
    
    prompt = f"""You are a technical translator specializing in AI/ML content. Translate the following LaTeX chapter excerpt from English to Simplified Chinese using the **interleaved bilingual** format.

## Translation Rules (CRITICAL):

1. **Paragraph-level bilingual**: Each English paragraph MUST be immediately followed by its Chinese translation.
2. **Titles**: Translate \section{{Title}}, \subsection{{Title}}, \subsubsection{{Title}} headers as:
   ```
   ## Original Title
   ## 中文标题
   ```
3. **LaTeX preservation**: Keep ALL LaTeX commands, equations ($...$, $$...$$), \cite{{...}}, \label{{...}}, \ref{{...}}, \textbf{{...}}, \emph{{...}} exactly as-is. Do NOT translate content inside \cite{{}}.
4. **Code blocks** (\\begin{{lstlisting}}): Translate comments only. Keep code symbols as-is.
5. **Tables**: Keep table structure; translate headers and cell content.
6. **Math**: Keep all math symbols in $...$ or $$...$$ as-is. Optionally add a brief Chinese comment after the equation.
7. **Technical terms**: First occurrence -> "English (中文)". E.g., "Proximal Policy Optimization (PPO)".
8. **Formatting**: Preserve \\textbf, \\emph, \\texttt wrapping within paragraphs.
9. **bullet points/enumeration**: Each \\item in English -> followed by \\item in Chinese.
10. **keybox/intuitionbox/examplebox/warningbox**: Translate the title. Keep the box environment intact. Translate content within the box bilingually.
11. **DO NOT**: Summarize, compress, skip, or paraphrase. Every sentence must be translated.
12. **DO**: Keep \\newpage, \\clearpage, \\vspace, \\hspace, \\begin{{figure}}, \\end{{figure}} as-is.

## Output Format:
```markdown
## Section Title
## 章节标题

English paragraph text with $math$ and **bold** formatting.
中文翻译段落，包含对应的 $math$ 和 **粗体** 格式。

...
```

## Chapter Context:
The chapter being translated is: {chapter_title}

## Content to Translate:
{chunk_text}

Now produce the bilingual translation following ALL rules above. Start directly with the translated content (no preamble)."""

    for attempt in range(retries):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=8192,
                timeout=300,
            )
            return resp.choices[0].message.content
        except Exception as e:
            print(f"  Attempt {attempt+1} failed: {e}", file=sys.stderr)
            if attempt < retries - 1:
                time.sleep(5 * (attempt + 1))
    
    return f"\n\n<!-- TRANSLATION FAILED for chunk -->\n\n"


def main():
    parser = argparse.ArgumentParser(description="Translate a LaTeX chapter to bilingual markdown")
    parser.add_argument("--input", "-i", required=True, help="Input .tex file")
    parser.add_argument("--output", "-o", required=True, help="Output .md file")
    parser.add_argument("--api-base", default=None, help="OpenAI API base URL")
    parser.add_argument("--model", default="deepseek-v4-flash", help="Model name")
    parser.add_argument("--chunk-size", type=int, default=8000, help="Chunk size in chars")
    args = parser.parse_args()
    
    api_key, api_base = setup_api()
    if args.api_base:
        api_base = args.api_base
    
    # Read input
    with open(args.input, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Get chapter title from first \section or filename
    chapter_title = Path(args.input).stem.replace('_', ' ').title()
    m = re.search(r'\\section\{(.+?)\}', text)
    if m:
        chapter_title = m.group(1)
    
    total_chars = len(text)
    print(f"Translating: {Path(args.input).name}", file=sys.stderr)
    print(f"  Title: {chapter_title}", file=sys.stderr)
    print(f"  Size: {total_chars:,} chars", file=sys.stderr)
    
    # Split into manageable chunks at paragraph boundaries
    # Try to split at \n\n or \section boundaries
    paragraphs = re.split(r'(?<=\n\n)(?=\S)', text)
    
    chunks = []
    current_chunk = ""
    for para in paragraphs:
        if len(current_chunk) + len(para) > args.chunk_size and current_chunk:
            chunks.append(current_chunk)
            current_chunk = para
        else:
            current_chunk += para + "\n"
    if current_chunk:
        chunks.append(current_chunk)
    
    # Ensure we have the openai library
    try:
        import openai
    except ImportError:
        print("Installing openai package...", file=sys.stderr)
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "openai", "-q"])
        import openai
    
    print(f"  Split into {len(chunks)} chunks", file=sys.stderr)
    
    # Translate each chunk
    all_results = []
    for i, chunk in enumerate(chunks):
        print(f"  Chunk {i+1}/{len(chunks)} ({len(chunk):,} chars)...", file=sys.stderr)
        result = translate_chunk(chunk, chapter_title, api_key, api_base, args.model)
        all_results.append(result)
        print(f"  Chunk {i+1} done ({len(result):,} chars)", file=sys.stderr)
        time.sleep(0.5)  # Rate limiting
    
    # Write output
    output = "\n\n".join(all_results)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(output)
    
    print(f"Output: {args.output} ({len(output):,} chars)", file=sys.stderr)


if __name__ == "__main__":
    main()
