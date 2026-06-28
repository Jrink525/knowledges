#!/usr/bin/env python3
"""
Efficient PIL-based PDF renderer for large bilingual HTML document.
"""
import re
import html
from PIL import Image, ImageDraw, ImageFont
import os
import sys

OUTPUT_PDF = '/home/node/.openclaw/workspace/papers/the-hitchhikers-guide-to-agentic-ai/complete_bilingual_guide.pdf'

# Page dimensions (A4 at 96dpi)
PAGE_W = 2480
PAGE_H = 3508
MARGIN_L = 150
MARGIN_R = 150
MARGIN_T = 150
MARGIN_B = 150
CONTENT_W = PAGE_W - MARGIN_L - MARGIN_R
CONTENT_H = PAGE_H - MARGIN_T - MARGIN_B

# Colors
BG_COLOR = (255, 255, 255)
TEXT_COLOR = (51, 51, 51)
H1_COLOR = (26, 26, 46)
H2_COLOR = (22, 33, 62)
H3_COLOR = (15, 52, 96)
CODE_BG = (245, 245, 245)
CODE_BORDER = (221, 221, 221)

FONT_DIR = '/home/node/.openclaw/workspace'

def load_fonts():
    return {
        'body': ImageFont.truetype(f'{FONT_DIR}/NotoSansSC-Regular.ttf', 11),
        'h1': ImageFont.truetype(f'{FONT_DIR}/NotoSansSC-Regular.ttf', 18),
        'h2': ImageFont.truetype(f'{FONT_DIR}/NotoSansSC-Regular.ttf', 15),
        'h3': ImageFont.truetype(f'{FONT_DIR}/NotoSansSC-Regular.ttf', 12),
        'code': ImageFont.truetype(f'{FONT_DIR}/NotoSansSC-Regular.ttf', 8),
        'small': ImageFont.truetype(f'{FONT_DIR}/NotoSansSC-Regular.ttf', 9),
    }


def tw(text, font):
    b = font.getbbox(text)
    return b[2] - b[0]


def lh(font, mul=1.5):
    a, d = font.getmetrics()
    return int((a + d) * mul)


def wrap_text(text, font, max_w):
    """Wrap text to fit max_width, returns list of lines. Handles CJK."""
    lines = []
    cur = ''
    for word in text.split(' '):
        test = f'{cur} {word}'.strip() if cur else word
        if tw(test, font) <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            # Single word too long - break by character
            if tw(word, font) > max_w:
                sub = ''
                for c in word:
                    if tw(sub + c, font) <= max_w:
                        sub += c
                    else:
                        if sub:
                            lines.append(sub)
                        sub = c
                cur = sub
            else:
                cur = word
    if cur:
        lines.append(cur)
    return lines


def extract_blocks_fast(html_content):
    """
    Fast block extraction. The HTML has a specific structure:
    one tag per line. Parse each line with minimal overhead.
    """
    blocks = []
    
    # Find body content
    body_start = html_content.find('<body')
    if body_start >= 0:
        body_start = html_content.find('>', body_start) + 1
        body_end = html_content.rfind('</body>')
        body = html_content[body_start:body_end]
    else:
        body = html_content
    
    in_code = False
    code_buf = []
    table_buf = []
    in_table = False
    
    for line in body.split('\n'):
        line = line.strip()
        if not line:
            if in_code:
                continue
            if blocks and blocks[-1][0] != 'spacer':
                blocks.append(('spacer', 1))
            continue
        
        # Fast tag detection using startswith
        if line.startswith('<pre>'):
            in_code = True
            # Check if content after <pre>
            remaining = line[5:]
            if remaining:
                code_buf.append(remaining)
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
        
        # Page break
        if 'page-break' in line or 'page-break-before' in line:
            blocks.append(('page_break', ''))
            continue
        
        # Headings
        if line.startswith('<h1>') and line.endswith('</h1>'):
            text = html.unescape(line[4:-5])
            blocks.append(('h1', text))
            continue
        if line.startswith('<h2>') and line.endswith('</h2>'):
            text = html.unescape(line[4:-5])
            blocks.append(('h2', text))
            continue
        if line.startswith('<h3>') and line.endswith('</h3>'):
            text = html.unescape(line[4:-5])
            blocks.append(('h3', text))
            continue
        if line.startswith('<h4>') and line.endswith('</h4>'):
            text = html.unescape(line[4:-5])
            blocks.append(('h4', text))
            continue
        
        # Direct tag matching
        if line.startswith('<p>') and line.endswith('</p>'):
            text = html.unescape(line[3:-4])
            if text.strip():
                blocks.append(('p', text.strip()))
            continue
        
        if line.startswith('<blockquote>') and line.endswith('</blockquote>'):
            text = html.unescape(line[12:-13])
            blocks.append(('bq', text.strip()))
            continue
        
        if line.startswith('<li>') and line.endswith('</li>'):
            text = html.unescape(line[4:-5])
            blocks.append(('li', text.strip()))
            continue
        
        if line.startswith('<div') and line.endswith('</div>'):
            text = html.unescape(re.sub(r'<[^>]+>', '', line))
            if text.strip():
                blocks.append(('p', text.strip()))
            continue
        
        if line.startswith('<tr>') and line.endswith('</tr>'):
            # Table row
            cells = [html.unescape(c[4:-5] if c.startswith('<td>') else c[4:-5]) 
                    for c in re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', line)]
            table_buf.append(cells)
            in_table = True
            continue
        
        if line.startswith('</table>'):
            if table_buf:
                blocks.append(('table', table_buf))
                table_buf = []
            in_table = False
            continue
        
        if in_table:
            continue
        
        # Fallback: extract text between any remaining tags
        text = re.sub(r'<[^>]+>', '', line).strip()
        text = html.unescape(text)
        if text:
            blocks.append(('p', text))
    
    return blocks


def measure_block_height(block_type, content, fonts):
    """Estimate height needed for a block (no wrap)."""
    f = fonts
    if block_type in ('h1',):
        return lh(f['h1']) + 8
    if block_type in ('h2',):
        return lh(f['h2']) + 6
    if block_type in ('h3', 'h4'):
        return lh(f['h3']) + 4
    if block_type == 'code':
        lines = content.split('\n')
        return len(lines) * lh(f['code'], 1.3) + 24
    if block_type == 'p':
        return lh(f['body']) * 2 + int(lh(f['body']) * 0.3)  # estimate 2 lines
    if block_type == 'li':
        return lh(f['body']) * 2 + int(lh(f['body']) * 0.2)
    if block_type == 'bq':
        return lh(f['body']) * 2 + 10
    if block_type == 'table':
        return len(content) * (lh(f['small']) + 10)
    if block_type == 'spacer':
        return int(lh(f['body']) * 0.5)
    if block_type == 'page_break':
        return 0
    return 20


def render_block(draw, block_type, content, y, fonts):
    """Render a block at position y. Returns new y position or -1 if doesn't fit."""
    f = fonts
    
    if block_type == 'page_break':
        return y
    
    if block_type == 'spacer':
        return y + int(lh(f['body']) * 0.5)
    
    if block_type == 'h1':
        txt = content
        _lh = lh(f['h1'])
        needed = _lh + 8
        if y + needed > MARGIN_T + CONTENT_H:
            return -1
        draw.text((MARGIN_L, y), txt, fill=H1_COLOR, font=f['h1'])
        uy = y + _lh + 2
        if uy < MARGIN_T + CONTENT_H:
            draw.line([(MARGIN_L, uy), (MARGIN_L + tw(txt, f['h1']), uy)], fill=H1_COLOR, width=2)
        return y + needed
    
    if block_type == 'h2':
        txt = content
        _lh = lh(f['h2'])
        needed = _lh + 6
        if y + needed > MARGIN_T + CONTENT_H:
            return -1
        draw.text((MARGIN_L, y), txt, fill=H2_COLOR, font=f['h2'])
        return y + needed
    
    if block_type in ('h3', 'h4'):
        txt = content
        _lh = lh(f['h3'])
        needed = _lh + 4
        if y + needed > MARGIN_T + CONTENT_H:
            return -1
        draw.text((MARGIN_L, y), txt, fill=H3_COLOR, font=f['h3'])
        return y + needed
    
    if block_type == 'code':
        txt = content
        code_lines = txt.split('\n')
        _lh = lh(f['code'], 1.3)
        total = len(code_lines) * _lh + 24
        if y + total > MARGIN_T + CONTENT_H:
            return -1
        
        draw.rectangle([(MARGIN_L, y), (MARGIN_L + CONTENT_W, y + total)], fill=CODE_BG, outline=CODE_BORDER)
        cy = y + 12
        for cl in code_lines:
            draw.text((MARGIN_L + 12, cy), cl, fill=TEXT_COLOR, font=f['code'])
            cy += _lh
        return y + total
    
    if block_type == 'p':
        _lh = lh(f['body'])
        lines = wrap_text(content, f['body'], CONTENT_W)
        needed = len(lines) * _lh + int(_lh * 0.3)
        if y + needed > MARGIN_T + CONTENT_H:
            return -1
        for line in lines:
            draw.text((MARGIN_L, y), line, fill=TEXT_COLOR, font=f['body'])
            y += _lh
        return y + int(_lh * 0.3)
    
    if block_type == 'li':
        _lh = lh(f['body'])
        bullet_w = tw('• ', f['body'])
        lines = wrap_text(content, f['body'], CONTENT_W - bullet_w)
        needed = len(lines) * _lh + int(_lh * 0.2)
        if y + needed > MARGIN_T + CONTENT_H:
            return -1
        for i, line in enumerate(lines):
            x = MARGIN_L
            if i == 0:
                draw.text((x, y), '• ' + line, fill=TEXT_COLOR, font=f['body'])
            else:
                draw.text((x + bullet_w, y), line, fill=TEXT_COLOR, font=f['body'])
            y += _lh
        return y + int(_lh * 0.2)
    
    if block_type == 'bq':
        _lh = lh(f['body'])
        qw = CONTENT_W - 15
        lines = wrap_text(content, f['body'], qw)
        needed = len(lines) * _lh + 10
        if y + needed > MARGIN_T + CONTENT_H:
            return -1
        
        draw.rectangle([(MARGIN_L, y), (MARGIN_L + CONTENT_W, y + needed)], fill=(248, 249, 250))
        draw.rectangle([(MARGIN_L, y), (MARGIN_L + 5, y + needed)], fill=(0, 123, 255))
        
        by = y + 5
        for line in lines:
            draw.text((MARGIN_L + 15, by), line, fill=(85, 85, 85), font=f['body'])
            by += _lh
        return y + needed
    
    if block_type == 'table':
        _lh = lh(f['small'])
        num_cols = max(len(r) for r in content) if content else 1
        col_w = CONTENT_W // num_cols
        
        rows_height = 0
        row_heights = []
        wrapped_data = []
        for row in content:
            wcells = []
            max_l = 0
            for cell in row:
                cl = wrap_text(cell, f['small'], col_w - 8)
                wcells.append(cl)
                max_l = max(max_l, len(cl))
            wrapped_data.append(wcells)
            rh = max_l * _lh + 10
            row_heights.append(rh)
            rows_height += rh
        
        total = rows_height + 2
        if y + total > MARGIN_T + CONTENT_H:
            return -1
        
        ty = y
        for ri, row in enumerate(wrapped_data):
            rh = row_heights[ri]
            bg = (232, 244, 248) if ri == 0 else ((250, 250, 250) if ri % 2 == 0 else BG_COLOR)
            
            draw.rectangle([(MARGIN_L, ty), (MARGIN_L + CONTENT_W, ty + rh)], fill=bg)
            
            cx = MARGIN_L
            for ci, clines in enumerate(row):
                c_y = ty + 5
                for line in clines:
                    draw.text((cx + 4, c_y), line, fill=TEXT_COLOR, font=f['small'])
                    c_y += _lh
                if ci < num_cols - 1:
                    draw.line([(cx + col_w, ty), (cx + col_w, ty + rh)], fill=(204, 204, 204), width=1)
                cx += col_w
            
            draw.line([(MARGIN_L, ty + rh), (MARGIN_L + CONTENT_W, ty + rh)], fill=(204, 204, 204), width=1)
            ty += rh
        
        return ty
    
    return y


def main():
    with open('/home/node/.openclaw/workspace/tmp_agentic_ai_guide.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    print(f'HTML size: {len(html_content)/1024/1024:.1f} MB')
    blocks = extract_blocks_fast(html_content)
    print(f'Blocks: {len(blocks)}')
    
    type_counts = {}
    for bt, _ in blocks:
        type_counts[bt] = type_counts.get(bt, 0) + 1
    print(f'Types: {type_counts}')
    
    fonts = load_fonts()
    pages = []
    bi = 0
    pn = 0
    last_report = 0
    
    while bi < len(blocks):
        img = Image.new('RGB', (PAGE_W, PAGE_H), BG_COLOR)
        dr = ImageDraw.Draw(img)
        
        y = MARGIN_T
        
        while bi < len(blocks):
            bt, bc = blocks[bi]
            if bt == 'page_break' and y > MARGIN_T:
                bi += 1
                break
            
            ny = render_block(dr, bt, bc, y, fonts)
            if ny == -1:
                break
            
            y = ny
            bi += 1
        
        pn += 1
        pages.append(img)
        if pn - last_report >= 20:
            print(f'Rendered page {pn}, block {bi}/{len(blocks)}')
            last_report = pn
    
    print(f'Total pages: {pn}')
    
    if pages:
        pages[0].save(
            OUTPUT_PDF,
            save_all=True,
            append_images=pages[1:],
            resolution=96.0,
            title="The Hitchhiker's Guide to Agentic AI (Bilingual)",
            author='Haggai Roitman'
        )
        print(f'PDF saved: {OUTPUT_PDF}')
    else:
        print('ERROR: No pages!')
        sys.exit(1)
    
    # Verify
    import subprocess
    r = subprocess.run(['python3', '-c', f'''
import re
with open("{OUTPUT_PDF}", "rb") as f:
    c = f.read()
print(f"Size: {{len(c)/1024/1024:.1f}} MB")
pages = len(re.findall(b"/Type\\\\s*/Page[^s]", c))
print(f"Pages: {{pages}}")
'''], capture_output=True, text=True)
    print(r.stdout.strip())
    if r.stderr:
        print(r.stderr.strip())


if __name__ == '__main__':
    main()
