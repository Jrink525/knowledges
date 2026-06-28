#!/usr/bin/env python3
"""
Efficient PIL-based PDF renderer for large bilingual HTML document.
Uses the pylib environment for PIL + fontconfig.
"""
import re
import html
import os
import sys
import subprocess
import tempfile
import shutil

# Ensure PIL is available
sys.path.insert(0, '/home/node/.openclaw/workspace/pylib/lib')
from PIL import Image, ImageDraw, ImageFont

OUTPUT_PDF = '/home/node/.openclaw/workspace/papers/the-hitchhikers-guide-to-agentic-ai/complete_bilingual_guide.pdf'

# A4 at ~96 dpi
PAGE_W = 2480
PAGE_H = 3508
ML = 150  # margin left
MR = 150  # margin right
MT = 150  # margin top
MB = 150  # margin bottom
CW = PAGE_W - ML - MR  # content width
CH = PAGE_H - MT - MB  # content height

BG = (255, 255, 255)
TC = (51, 51, 51)
H1C = (26, 26, 46)
H2C = (22, 33, 62)
H3C = (15, 52, 96)
CBC = (245, 245, 245)
CBO = (221, 221, 221)
BQB = (248, 249, 250)
BQC = (0, 123, 255)
THC = (232, 244, 248)
TAC = (250, 250, 250)
TBC = (204, 204, 204)

FD = '/home/node/.openclaw/workspace'

def fonts():
    return {
        'body': ImageFont.truetype(f'{FD}/NotoSansSC-Regular.ttf', 11),
        'h1': ImageFont.truetype(f'{FD}/NotoSansSC-Regular.ttf', 18),
        'h2': ImageFont.truetype(f'{FD}/NotoSansSC-Regular.ttf', 15),
        'h3': ImageFont.truetype(f'{FD}/NotoSansSC-Regular.ttf', 12),
        'code': ImageFont.truetype(f'{FD}/NotoSansSC-Regular.ttf', 8),
        'small': ImageFont.truetype(f'{FD}/NotoSansSC-Regular.ttf', 9),
    }

def tw(text, font):
    b = font.getbbox(text)
    return b[2] - b[0]

def lh(font, mul=1.5):
    a, d = font.getmetrics()
    return int((a + d) * mul)

def wrap(text, font, mx):
    lines = []
    cur = ''
    for w in text.split(' '):
        t = f'{cur} {w}'.strip() if cur else w
        if tw(t, font) <= mx:
            cur = t
        else:
            if cur:
                lines.append(cur)
            if tw(w, font) > mx:
                sub = ''
                for c in w:
                    if tw(sub + c, font) <= mx:
                        sub += c
                    else:
                        if sub: lines.append(sub)
                        sub = c
                cur = sub
            else:
                cur = w
    if cur:
        lines.append(cur)
    return lines

def parse(html_content):
    """Fast block extraction from structured HTML."""
    blocks = []
    bs = html_content.find('<body')
    if bs >= 0:
        bs = html_content.find('>', bs) + 1
        be = html_content.rfind('</body>')
        body = html_content[bs:be]
    else:
        body = html_content

    in_code = False
    code_buf = []
    table_buf = []
    
    for line in body.split('\n'):
        line = line.strip()
        if not line:
            if in_code: continue
            if blocks and blocks[-1][0] != 's':
                blocks.append(('s', 1))
            continue

        if line.startswith('<pre>'):
            in_code = True
            r = line[5:]
            if r: code_buf.append(r)
            continue
        if line.startswith('</pre>'):
            if code_buf:
                blocks.append(('code', '\n'.join(code_buf)))
                code_buf = []
            in_code = False
            continue
        if in_code:
            code_buf.append(line)
            continue

        # Check for page-break div (possibly combined with heading on same line)
        pb_pos = line.find('page-break')
        if pb_pos >= 0:
            blocks.append(('pb', ''))
            # Strip the page-break div to check what's after it
            remaining = re.sub(r'<div[^>]*page-break[^>]*></div>', '', line).strip()
            if remaining:
                line = remaining
            else:
                continue

        if line.startswith('<h1>') and line.endswith('</h1>'):
            blocks.append(('h1', html.unescape(line[4:-5]))); continue
        if line.startswith('<h2>') and line.endswith('</h2>'):
            blocks.append(('h2', html.unescape(line[4:-5]))); continue
        if line.startswith('<h3>') and line.endswith('</h3>'):
            blocks.append(('h3', html.unescape(line[4:-5]))); continue
        if line.startswith('<h4>') and line.endswith('</h4>'):
            blocks.append(('h4', html.unescape(line[4:-5]))); continue

        if line.startswith('<p>') and line.endswith('</p>'):
            t = html.unescape(line[3:-4]).strip()
            if t: blocks.append(('p', t))
            continue

        if line.startswith('<blockquote>') and line.endswith('</blockquote>'):
            t = html.unescape(line[12:-13]).strip()
            if t: blocks.append(('bq', t))
            continue

        if line.startswith('<li>') and line.endswith('</li>'):
            t = html.unescape(line[4:-5]).strip()
            if t: blocks.append(('li', t))
            continue

        if line.startswith('<div') and line.endswith('</div>'):
            t = html.unescape(re.sub(r'<[^>]+>', '', line)).strip()
            if t: blocks.append(('p', t))
            continue

        if line.startswith('<tr>') and line.endswith('</tr>'):
            cells = [html.unescape(c[4:-5] if c.startswith('<td>') else c[4:-5])
                     for c in re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', line)]
            table_buf.append(cells)
            continue

        if line.startswith('</table>'):
            if table_buf:
                blocks.append(('tbl', table_buf))
                table_buf = []
            continue

        if table_buf:
            continue

        t = re.sub(r'<[^>]+>', '', line).strip()
        t = html.unescape(t)
        if t:
            blocks.append(('p', t))

    return blocks

def render_block(dr, bt, bc, y, f):
    """Render a block. Returns new y or -1 if doesn't fit."""
    def space_needed(nlines, lh_):
        return nlines * lh_

    if bt == 'pb':
        return y
    
    if bt == 's':
        return y + int(lh(f['body']) * 0.5)

    if bt == 'h1':
        _lh = lh(f['h1'])
        h = _lh + 8
        if y + h > MT + CH: return -1
        dr.text((ML, y), bc, fill=H1C, font=f['h1'])
        uy = y + _lh + 2
        if uy < MT + CH:
            dr.line([(ML, uy), (ML + tw(bc, f['h1']), uy)], fill=H1C, width=2)
        return y + h

    if bt == 'h2':
        _lh = lh(f['h2'])
        h = _lh + 6
        if y + h > MT + CH: return -1
        dr.text((ML, y), bc, fill=H2C, font=f['h2'])
        return y + h

    if bt in ('h3', 'h4'):
        _lh = lh(f['h3'])
        h = _lh + 4
        if y + h > MT + CH: return -1
        dr.text((ML, y), bc, fill=H3C, font=f['h3'])
        return y + h

    if bt == 'code':
        cl = bc.split('\n')
        _lh = lh(f['code'], 1.3)
        total = len(cl) * _lh + 24
        if y + total > MT + CH: return -1
        dr.rectangle([(ML, y), (ML + CW, y + total)], fill=CBC, outline=CBO)
        cy = y + 12
        for cline in cl:
            dr.text((ML + 12, cy), cline, fill=TC, font=f['code'])
            cy += _lh
        return y + total

    if bt == 'p':
        _lh = lh(f['body'])
        lines = wrap(bc, f['body'], CW)
        h = len(lines) * _lh + int(_lh * 0.3)
        if y + h > MT + CH: return -1
        for line in lines:
            dr.text((ML, y), line, fill=TC, font=f['body'])
            y += _lh
        return y + int(_lh * 0.3)

    if bt == 'li':
        _lh = lh(f['body'])
        bw = tw('• ', f['body'])
        lines = wrap(bc, f['body'], CW - bw)
        h = len(lines) * _lh + int(_lh * 0.2)
        if y + h > MT + CH: return -1
        for i, line in enumerate(lines):
            x = ML
            if i == 0:
                dr.text((x, y), '• ' + line, fill=TC, font=f['body'])
            else:
                dr.text((x + bw, y), line, fill=TC, font=f['body'])
            y += _lh
        return y + int(_lh * 0.2)

    if bt == 'bq':
        _lh = lh(f['body'])
        qw = CW - 15
        lines = wrap(bc, f['body'], qw)
        h = len(lines) * _lh + 10
        if y + h > MT + CH: return -1
        dr.rectangle([(ML, y), (ML + CW, y + h)], fill=BQB)
        dr.rectangle([(ML, y), (ML + 5, y + h)], fill=BQC)
        by = y + 5
        for line in lines:
            dr.text((ML + 15, by), line, fill=(85, 85, 85), font=f['body'])
            by += _lh
        return y + h

    if bt == 'tbl':
        _lh = lh(f['small'])
        nc = max(len(r) for r in bc) if bc else 1
        cw = CW // nc
        
        wrapped = []
        rrh = []
        for row in bc:
            wc = []
            mx = 0
            for cell in row:
                cl = wrap(cell, f['small'], cw - 8)
                wc.append(cl)
                mx = max(mx, len(cl))
            wrapped.append(wc)
            rh = mx * _lh + 10
            rrh.append(rh)
        
        total = sum(rrh) + 2
        if y + total > MT + CH: return -1
        
        ty = y
        for ri, row in enumerate(wrapped):
            rh = rrh[ri]
            bg = THC if ri == 0 else (TAC if ri % 2 == 0 else BG)
            dr.rectangle([(ML, ty), (ML + CW, ty + rh)], fill=bg)
            cx = ML
            for ci, clines in enumerate(row):
                cy = ty + 5
                for line in clines:
                    dr.text((cx + 4, cy), line, fill=TC, font=f['small'])
                    cy += _lh
                if ci < nc - 1:
                    dr.line([(cx + cw, ty), (cx + cw, ty + rh)], fill=TBC, width=1)
                cx += cw
            dr.line([(ML, ty + rh), (ML + CW, ty + rh)], fill=TBC, width=1)
            ty += rh
        return ty

    return y

def main():
    with open(f'{FD}/tmp_agentic_ai_guide.html', 'r', encoding='utf-8') as f:
        html_content = f.read()

    print(f'HTML: {len(html_content)/1024/1024:.1f} MB')
    blocks = parse(html_content)
    print(f'Blocks: {len(blocks)}')

    counts = {}
    for bt, _ in blocks:
        counts[bt] = counts.get(bt, 0) + 1
    print(f'Types: {counts}')

    f = fonts()
    pages = []
    bi = 0
    pn = 0

    while bi < len(blocks):
        img = Image.new('RGB', (PAGE_W, PAGE_H), BG)
        dr = ImageDraw.Draw(img)
        y = MT

        while bi < len(blocks):
            bt, bc = blocks[bi]
            if bt == 'pb' and y > MT:
                bi += 1
                break
            ny = render_block(dr, bt, bc, y, f)
            if ny == -1:
                break
            y = ny
            bi += 1

        pn += 1
        pages.append(img)
        if pn % 20 == 0:
            print(f'Page {pn} (block {bi}/{len(blocks)})')

    print(f'Total: {pn} pages')

    # Save as multi-page TIFF or individual PNGs, then convert to PDF
    print('Converting to PDF...')
    tmp = tempfile.mkdtemp()
    pngs = []
    for i, pg in enumerate(pages):
        pp = os.path.join(tmp, f'{i:04d}.png')
        pg.save(pp, 'PNG')
        pngs.append(pp)

    # Use PIL to create PDF from PNG images (convert to RGB first)
    rgb_pages = [Image.open(p).convert('RGB') for p in pngs]
    rgb_pages[0].save(OUTPUT_PDF, save_all=True, append_images=rgb_pages[1:],
                      resolution=96.0,
                      title="The Hitchhiker's Guide to Agentic AI (Bilingual)",
                      author='Haggai Roitman')
    
    shutil.rmtree(tmp, ignore_errors=True)
    print(f'PDF: {OUTPUT_PDF}')

    # Verify
    r = subprocess.run(['python3', '-c', fr'''
import re
with open("{OUTPUT_PDF}", "rb") as f:
    c = f.read()
print(f"Size: {{len(c)/1024/1024:.1f}} MB")
pages = len(re.findall(b"/Type\s*/Page[^s]", c))
print(f"Pages: {{pages}}")
'''], capture_output=True, text=True, env={**os.environ, 'LD_LIBRARY_PATH': os.environ.get('LD_LIBRARY_PATH', '')})
    out = r.stdout.strip()
    err = r.stderr.strip()
    if out: print(out)
    if err: print(err)

if __name__ == '__main__':
    main()
