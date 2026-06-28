#!/usr/bin/env python3
"""Convert markdown to HTML for PDF."""
import re
import html as html_lib

import sys

INPUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp/source.md'
OUTPUT = sys.argv[2] if len(sys.argv) > 2 else '/home/node/.openclaw/workspace/tmp_agentic_ai_guide.html'

CSS = """
<style>
@page { size: A4; margin: 2cm; }
body { font-family: 'Noto Sans SC', 'SimSun', 'Noto Sans', sans-serif; font-size: 10pt; line-height: 1.6; color: #333; }
.page-break { page-break-before: always; }
h1 { font-size: 18pt; font-weight: bold; color: #1a1a2e; margin-top: 1.5em; margin-bottom: 0.5em; border-bottom: 2px solid #1a1a2e; padding-bottom: 4px; }
h2 { font-size: 15pt; font-weight: bold; color: #16213e; margin-top: 1.3em; margin-bottom: 0.4em; border-bottom: 1px solid #ccc; padding-bottom: 3px; }
h3 { font-size: 12pt; font-weight: bold; color: #0f3460; margin-top: 1.2em; margin-bottom: 0.3em; }
h4 { font-size: 10.5pt; font-weight: bold; color: #333; margin-top: 1em; margin-bottom: 0.3em; }
h5 { font-size: 10pt; font-weight: bold; color: #555; margin-top: 0.8em; margin-bottom: 0.2em; }
p { margin: 0.4em 0; text-align: justify; }
pre { background: #f5f5f5; border: 1px solid #ddd; border-radius: 4px; padding: 8px 12px; overflow-x: auto; font-family: 'Consolas','Monaco','Courier New',monospace; font-size: 8pt; line-height: 1.4; white-space: pre-wrap; word-wrap: break-word; }
code { font-family: 'Consolas','Monaco','Courier New',monospace; font-size: 8.5pt; background: #f0f0f0; padding: 1px 3px; border-radius: 2px; }
pre code { background: transparent; padding: 0; font-size: 8pt; }
table { border-collapse: collapse; width: 100%; margin: 0.8em 0; font-size: 8.5pt; }
th, td { border: 1px solid #999; padding: 4px 6px; text-align: left; }
th { background: #e8e8e8; font-weight: bold; }
ul { margin: 0.4em 0; padding-left: 2em; }
li { margin: 0.2em 0; }
hr { border: none; border-top: 1px solid #ccc; margin: 1em 0; }
a { color: #0066cc; text-decoration: none; }
blockquote { border-left: 3px solid #ccc; margin: 0.5em 0; padding-left: 1em; color: #555; }
strong { font-weight: bold; }
em { font-style: italic; }
"""

TPRE = '<!--__TBL__'
PSUF = '__-->'

def inline(s):
    s = s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
    s = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="\2" alt="\1"/>', s)
    s = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', s)
    s = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<em>\1</em>', s)
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    return s

def extract_tables(t):
    tbls = []
    def pr(m):
        tbls.append(m.group(1))
        return f'{TPRE}{len(tbls)-1}{PSUF}'
    cbs = []
    def pc(m):
        cbs.append(m.group(1))
        return f'__CB_{len(cbs)-1}__'
    t = re.sub(r'(```[\s\S]*?```)', pc, t)
    lines = t.split('\n')
    out = []
    i = 0
    while i < len(lines):
        l = lines[i].strip()
        if l.startswith('|') and l.endswith('|') and l.count('|') >= 4:
            if i+1 < len(lines):
                n = lines[i+1].strip()
                if n.startswith('|') and n.count('|') >= 3:
                    c = n.replace(':','').replace('-','').replace('|','').replace('+','').strip()
                    if not c or set(c) <= set():
                        tl = [l]; i += 2
                        while i < len(lines):
                            r = lines[i].strip()
                            if not r or not r.startswith('|'): break
                            tl.append(r); i += 1
                        rr = []
                        rw = tl[0].lstrip('|').rstrip('|')
                        hc = [inline(x.strip()) for x in rw.split('|')]
                        rr.append(f'<tr>{" ".join(f"<th>{c}</th>" for c in hc)}</tr>')
                        for rl in tl[1:]:
                            rw = rl.lstrip('|').rstrip('|')
                            cs = [inline(x.strip()) for x in rw.split('|')]
                            rr.append(f'<tr>{" ".join(f"<td>{c}</td>" for c in cs)}</tr>')
                        tbls.append(f'<table><thead>{"".join(rr[:1])}</thead><tbody>{"".join(rr[1:])}</tbody></table>')
                        out.append(f'{TPRE}{len(tbls)-1}{PSUF}')
                        continue
        out.append(lines[i]); i += 1
    r = '\n'.join(out)
    for i, cb in enumerate(cbs): r = r.replace(f'__CB_{i}__', cb)
    return tbls, r

def md2html(txt, tbls):
    lines = txt.split('\n')
    out = []
    ic, cc, il, li = False, [], False, []
    for rl in lines:
        l = rl
        if TPRE in l:
            if il: out.append(f'<ul>\n'+'\n'.join(f'<li>{x}</li>' for x in li)+'\n</ul>'); il, li = False, []
            m = re.search(rf'{re.escape(TPRE)}(\d+){re.escape(PSUF)}', l)
            if m:
                i = int(m.group(1))
                if i < len(tbls): out.append(tbls[i])
            continue
        if l.strip().startswith('```'):
            if ic: out.append('<pre><code>'+html_lib.escape('\n'.join(cc))+'</code></pre>'); ic, cc = False, []
            else: ic = True
            continue
        if ic: cc.append(rl); continue
        if not l.strip():
            if il: out.append(f'<ul>\n'+'\n'.join(f'<li>{x}</li>' for x in li)+'\n</ul>'); il, li = False, []
            continue
        hm = re.match(r'^(#{1,5})\s+(.+)', l)
        if hm:
            if il: out.append(f'<ul>\n'+'\n'.join(f'<li>{x}</li>' for x in li)+'\n</ul>'); il, li = False, []
            lv = len(hm.group(1)); cn = inline(hm.group(2))
            pb = '<div class="page-break"></div>' if lv == 1 else ''
            out.append(f'{pb}<h{lv}>{cn}</h{lv}>')
            continue
        if re.match(r'^---\s*$', l.strip()):
            if il: out.append(f'<ul>\n'+'\n'.join(f'<li>{x}</li>' for x in li)+'\n</ul>'); il, li = False, []
            out.append('<hr>'); continue
        lm = re.match(r'^[\s]*[-*+]\s+(.+)', l)
        if lm:
            if not il: il, li = True, [inline(lm.group(1))]
            else: li.append(inline(lm.group(1)))
            continue
        if il: out.append(f'<ul>\n'+'\n'.join(f'<li>{x}</li>' for x in li)+'\n</ul>'); il, li = False, []
        out.append(f'<p>{inline(l)}</p>')
    if ic: out.append('<pre><code>'+html_lib.escape('\n'.join(cc))+'</code></pre>')
    if il: out.append(f'<ul>\n'+'\n'.join(f'<li>{x}</li>' for x in li)+'\n</ul>')
    return '\n'.join(out)

def main():
    with open(INPUT, encoding='utf-8') as f: md = f.read()
    print(f'Read {len(md):,} chars')
    tbls, md = extract_tables(md)
    print(f'Tables: {len(tbls)}')
    body = md2html(md, tbls)
    html = f'<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><title>Agentic AI Guide</title>{CSS}</head><body>{body}</body></html>'
    with open(OUTPUT, 'w', encoding='utf-8') as f: f.write(html)
    print(f'Wrote {OUTPUT} ({len(html):,} bytes)')

if __name__ == '__main__': main()
