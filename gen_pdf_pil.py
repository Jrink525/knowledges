#!/usr/bin/env python3
"""
Render bilingual HTML guide as a multi-page PDF using PIL/Pillow.
A4 at 72 dpi = 595x842 points, but we use higher res: 2480x3508 px (~96 dpi)
"""
import re
import html
from PIL import Image, ImageDraw, ImageFont
import os

# Output path
OUTPUT_PDF = '/home/node/.openclaw/workspace/papers/the-hitchhikers-guide-to-agentic-ai/complete_bilingual_guide.pdf'

# Page dimensions (A4 at ~96dpi for good quality)
PAGE_W = 2480
PAGE_H = 3508
MARGIN_L = 140
MARGIN_R = 140
MARGIN_T = 140
MARGIN_B = 140
CONTENT_W = PAGE_W - MARGIN_L - MARGIN_R
CONTENT_H = PAGE_H - MARGIN_T - MARGIN_B

# Colors
BG_COLOR = (255, 255, 255)
TEXT_COLOR = (51, 51, 51)
HEADING1_COLOR = (26, 26, 46)
HEADING2_COLOR = (22, 33, 62)
HEADING3_COLOR = (15, 52, 96)
CODE_BG = (245, 245, 245)
CODE_BORDER = (221, 221, 221)
TABLE_HEADER_BG = (232, 244, 248)
TABLE_ALT_BG = (250, 250, 250)
TABLE_BORDER = (204, 204, 204)
BLOCKQUOTE_BG = (248, 249, 250)
BLOCKQUOTE_BORDER = (0, 123, 255)

# Font sizes (in points)
# PIL requires font size in points
FONT_SIZE_BODY = 11
FONT_SIZE_H1 = 18
FONT_SIZE_H2 = 15
FONT_SIZE_H3 = 12
FONT_SIZE_CODE = 8
FONT_SIZE_SMALL = 9

# Line heights (multiples of font size)
LINE_HEIGHT = 1.5

# Load fonts
font_dir = '/home/node/.openclaw/workspace'
FONT_REGULAR = ImageFont.truetype(os.path.join(font_dir, 'NotoSansSC-Regular.ttf'), FONT_SIZE_BODY)
FONT_H1 = ImageFont.truetype(os.path.join(font_dir, 'NotoSansSC-Regular.ttf'), FONT_SIZE_H1)
FONT_H2 = ImageFont.truetype(os.path.join(font_dir, 'NotoSansSC-Regular.ttf'), FONT_SIZE_H2)
FONT_H3 = ImageFont.truetype(os.path.join(font_dir, 'NotoSansSC-Regular.ttf'), FONT_SIZE_H3)
FONT_CODE = ImageFont.truetype(os.path.join(font_dir, 'NotoSansSC-Regular.ttf'), FONT_SIZE_CODE)
FONT_SMALL = ImageFont.truetype(os.path.join(font_dir, 'NotoSansSC-Regular.ttf'), FONT_SIZE_SMALL)
FONT_BOLD = ImageFont.truetype(os.path.join(font_dir, 'NotoSansSC-Regular.ttf'), FONT_SIZE_BODY)

def parse_html_to_blocks(html_content):
    """Parse HTML into structured blocks (paragraphs, headings, code blocks, etc.)"""
    blocks = []
    
    # Remove <style> and <link> tags and their content
    html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL)
    html_content = re.sub(r'<link[^>]*>', '', html_content)
    
    # Extract content from <body>
    body_match = re.search(r'<body[^>]*>(.*?)</body>', html_content, re.DOTALL)
    if body_match:
        body = body_match.group(1)
    else:
        body = html_content
    
    # Remove <hr> tags
    body = re.sub(r'<hr[^>]*>', '', body)
    
    # Process each line/element
    lines = body.split('\n')
    current_code = []
    in_code = False
    
    for line in lines:
        line = line.strip()
        if not line:
            if in_code:
                continue
            blocks.append(('spacer', 1))
            continue
        
        # Handle <pre><code> blocks
        if '<pre>' in line:
            in_code = True
            # Extract content after <pre>
            code_content = re.sub(r'.*?<pre>(.*?)', r'\1', line, flags=re.DOTALL)
            if code_content:
                current_code.append(code_content)
            continue
        
        if '</pre>' in line and in_code:
            # Extract content before </pre>
            code_content = re.sub(r'(.*?)</pre>.*?', r'\1', line, flags=re.DOTALL)
            if code_content:
                current_code.append(code_content)
            if current_code:
                code_text = '\n'.join(current_code)
                code_text = html.unescape(code_text)
                blocks.append(('code', code_text))
            current_code = []
            in_code = False
            continue
        
        if in_code:
            current_code.append(line)
            continue
        
        # Handle special block-level elements
        # Page breaks become section breaks
        if 'page-break' in line or 'page-break-before' in line:
            blocks.append(('page_break', ''))
            continue
        
        # Headings
        h1_match = re.match(r'<h1>(.*?)</h1>', line)
        if h1_match:
            text = html.unescape(re.sub(r'<[^>]+>', '', h1_match.group(1)))
            blocks.append(('h1', text))
            continue
        
        h2_match = re.match(r'<h2>(.*?)</h2>', line)
        if h2_match:
            text = html.unescape(re.sub(r'<[^>]+>', '', h2_match.group(1)))
            blocks.append(('h2', text))
            continue
        
        h3_match = re.match(r'<h3>(.*?)</h3>', line)
        if h3_match:
            text = html.unescape(re.sub(r'<[^>]+>', '', h3_match.group(1)))
            blocks.append(('h3', text))
            continue
        
        h4_match = re.match(r'<h4>(.*?)</h4>', line)
        if h4_match:
            text = html.unescape(re.sub(r'<[^>]+>', '', h4_match.group(1)))
            blocks.append(('h4', text))
            continue
        
        # Blockquotes
        bq_match = re.match(r'<blockquote>(.*?)</blockquote>', line)
        if bq_match:
            text = html.unescape(re.sub(r'<[^>]+>', '', bq_match.group(1)))
            blocks.append(('blockquote', text.strip()))
            continue
        
        # Regular paragraphs
        p_match = re.match(r'<p>(.*?)</p>', line)
        if p_match:
            text = html.unescape(re.sub(r'<[^>]+>', '', p_match.group(1)))
            blocks.append(('paragraph', text.strip()))
            continue
        
        # List items (from <ul><li> tags)
        li_match = re.match(r'<li>(.*?)</li>', line)
        if li_match:
            text = html.unescape(re.sub(r'<[^>]+>', '', li_match.group(1)))
            blocks.append(('list_item', text.strip()))
            continue
        
        # Div contents
        div_match = re.match(r'<div[^>]*>(.*?)</div>', line)
        if div_match:
            text = html.unescape(re.sub(r'<[^>]+>', '', div_match.group(1)))
            if text.strip():
                blocks.append(('paragraph', text.strip()))
            continue
        
        # Tables
        if '<table>' in line:
            # Extract entire table content
            table_match = re.search(r'<table>(.*?)</table>', body, re.DOTALL)
            if table_match:
                table_html = table_match.group(1)
                rows = re.findall(r'<tr>(.*?)</tr>', table_html, re.DOTALL)
                table_data = []
                for row in rows:
                    cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row, re.DOTALL)
                    row_data = []
                    for cell in cells:
                        cell_text = html.unescape(re.sub(r'<[^>]+>', '', cell.strip()))
                        row_data.append(cell_text)
                    if row_data:
                        table_data.append(row_data)
                if table_data:
                    blocks.append(('table', table_data))
            continue
    
    return blocks


def measure_text_width(text, font):
    """Measure text width in pixels"""
    bbox = font.getbbox(text)
    return bbox[2] - bbox[0]


def wrap_text(text, font, max_width):
    """Wrap text to fit within max_width, returns list of lines"""
    words = text.split(' ')
    lines = []
    current_line = ''
    
    for word in words:
        # Handle very long words (e.g., URLs)
        test_line = f'{current_line} {word}'.strip() if current_line else word
        if measure_text_width(test_line, font) <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            # If single word is too long, hyphenate or just add
            if measure_text_width(word, font) > max_width:
                # Try to break at any character boundary for CJK
                chars = list(word)
                sub_line = ''
                for c in chars:
                    if measure_text_width(sub_line + c, font) <= max_width:
                        sub_line += c
                    else:
                        if sub_line:
                            lines.append(sub_line)
                        sub_line = c
                current_line = sub_line
            else:
                current_line = word
    
    if current_line:
        lines.append(current_line)
    
    return lines


def get_line_height(font, multiplier=1.5):
    """Get line height in pixels"""
    ascent, descent = font.getmetrics()
    return int((ascent + descent) * multiplier)


def render_page(draw, blocks, block_index, font_regular, font_h1, font_h2, font_h3, font_code, font_small):
    """Render content starting from block_index. Returns (page_image, next_block_index) or (None, -1) if done."""
    y = MARGIN_T
    
    # Track block positions
    while block_index < len(blocks):
        block_type, block_content = blocks[block_index]
        
        if block_type == 'page_break':
            block_index += 1
            if y > MARGIN_T:  # Only break if we've rendered something
                break
            continue
        
        if block_type == 'spacer':
            lh = get_line_height(font_regular)
            if y + lh * 0.5 > MARGIN_T + CONTENT_H:
                break
            y += int(lh * 0.5)
            block_index += 1
            continue
        
        if block_type == 'h1':
            lh = get_line_height(font_h1)
            height_needed = lh + 8  # + margin bottom
            if y + height_needed > MARGIN_T + CONTENT_H:
                if y > MARGIN_T:
                    break  # Need new page
            # Underline
            text_width = measure_text_width(block_content, font_h1)
            draw.text((MARGIN_L, y), block_content, fill=HEADING1_COLOR, font=font_h1)
            underline_y = y + lh + 2
            if underline_y < MARGIN_T + CONTENT_H:
                draw.line([(MARGIN_L, underline_y), (MARGIN_L + text_width, underline_y)], 
                         fill=HEADING1_COLOR, width=2)
            y += height_needed
        
        elif block_type == 'h2':
            lh = get_line_height(font_h2)
            height_needed = lh + 6
            if y + height_needed > MARGIN_T + CONTENT_H:
                if y > MARGIN_T:
                    break
            draw.text((MARGIN_L, y), block_content, fill=HEADING2_COLOR, font=font_h2)
            y += height_needed
        
        elif block_type == 'h3':
            lh = get_line_height(font_h3)
            height_needed = lh + 4
            if y + height_needed > MARGIN_T + CONTENT_H:
                if y > MARGIN_T:
                    break
            draw.text((MARGIN_L, y), block_content, fill=HEADING3_COLOR, font=font_h3)
            y += height_needed
        
        elif block_type == 'h4':
            lh = get_line_height(font_h3)  # use h3 size for h4
            height_needed = lh + 3
            if y + height_needed > MARGIN_T + CONTENT_H:
                if y > MARGIN_T:
                    break
            draw.text((MARGIN_L, y), block_content, fill=(83, 52, 131), font=font_h3)
            y += height_needed
        
        elif block_type == 'paragraph':
            lh = get_line_height(font_regular)
            lines = wrap_text(block_content, font_regular, CONTENT_W)
            total_height = len(lines) * lh + int(lh * 0.3)
            if y + total_height > MARGIN_T + CONTENT_H:
                if y > MARGIN_T:
                    break
            for line in lines:
                draw.text((MARGIN_L, y), line, fill=TEXT_COLOR, font=font_regular)
                y += lh
            y += int(lh * 0.3)
        
        elif block_type == 'list_item':
            lh = get_line_height(font_regular)
            # Bullet point
            bullet = '• '
            bullet_width = measure_text_width(bullet, font_regular)
            lines = wrap_text(block_content, font_regular, CONTENT_W - bullet_width)
            total_height = len(lines) * lh + int(lh * 0.2)
            if y + total_height > MARGIN_T + CONTENT_H:
                if y > MARGIN_T:
                    break
            for i, line in enumerate(lines):
                x = MARGIN_L
                if i == 0:
                    draw.text((x, y), bullet + line, fill=TEXT_COLOR, font=font_regular)
                else:
                    draw.text((x + bullet_width, y), line, fill=TEXT_COLOR, font=font_regular)
                y += lh
            y += int(lh * 0.2)
        
        elif block_type == 'code':
            code_lh = get_line_height(font_code, 1.3)
            code_lines = block_content.split('\n')
            code_padding = 10
            code_width_max = max(measure_text_width(line, font_code) for line in code_lines) if code_lines else 0
            block_width = min(code_width_max + code_padding * 2, CONTENT_W)
            total_height = len(code_lines) * code_lh + code_padding * 2 + 4
            
            if y + total_height > MARGIN_T + CONTENT_H:
                if y > MARGIN_T:
                    break
            
            # Draw code background
            draw.rectangle(
                [(MARGIN_L, y), (MARGIN_L + CONTENT_W, y + total_height)],
                fill=CODE_BG, outline=CODE_BORDER
            )
            
            # Render code text
            code_x = MARGIN_L + code_padding
            code_y = y + code_padding
            for code_line in code_lines:
                draw.text((code_x, code_y), code_line, fill=(51, 51, 51), font=font_code)
                code_y += code_lh
            
            y += total_height + 4
        
        elif block_type == 'blockquote':
            lh = get_line_height(font_regular)
            # Blockquote has left border
            left_margin = MARGIN_L + 15
            quote_width = CONTENT_W - 15
            lines = wrap_text(block_content, font_regular, quote_width)
            total_height = len(lines) * lh + 10  # padding
            if y + total_height > MARGIN_T + CONTENT_H:
                if y > MARGIN_T:
                    break
            
            # Background
            draw.rectangle(
                [(MARGIN_L, y), (MARGIN_L + CONTENT_W, y + total_height)],
                fill=BLOCKQUOTE_BG
            )
            # Blue border on left
            draw.rectangle(
                [(MARGIN_L, y), (MARGIN_L + 5, y + total_height)],
                fill=BLOCKQUOTE_BORDER
            )
            
            for line in lines:
                draw.text((left_margin, y + 5), line, fill=(85, 85, 85), font=font_regular)
                y += lh
            y += 5
        
        elif block_type == 'table':
            lh = get_line_height(font_small)
            table_data = block_content
            if not table_data:
                block_index += 1
                continue
            
            # Calculate column widths
            num_cols = max(len(row) for row in table_data)
            col_width = CONTENT_W // num_cols
            
            # Estimate total height
            rows_height = 0
            for row in table_data:
                max_lines = 0
                for cell in row:
                    lines = wrap_text(cell, font_small, col_width - 8)
                    max_lines = max(max_lines, len(lines))
                rows_height += max_lines * lh + 8
            
            total_height = rows_height + 2  # borders
            
            if y + total_height > MARGIN_T + CONTENT_H:
                if y > MARGIN_T:
                    break
            
            # Render table
            table_y = y
            for row_idx, row in enumerate(table_data):
                max_lines = 0
                wrapped_cells = []
                for cell in row:
                    lines = wrap_text(cell, font_small, col_width - 8)
                    wrapped_cells.append(lines)
                    max_lines = max(max_lines, len(lines))
                
                row_height = max_lines * lh + 8
                row_bg = TABLE_HEADER_BG if row_idx == 0 else (TABLE_ALT_BG if row_idx % 2 == 0 else BG_COLOR)
                
                # Draw row background
                draw.rectangle(
                    [(MARGIN_L, table_y), (MARGIN_L + CONTENT_W, table_y + row_height)],
                    fill=row_bg
                )
                
                # Draw cells
                cell_x = MARGIN_L
                for col_idx, cell_lines in enumerate(wrapped_cells):
                    cell_y = table_y + 4
                    for line in cell_lines:
                        draw.text((cell_x + 4, cell_y), line, fill=TEXT_COLOR, font=font_small)
                        cell_y += lh
                    
                    # Draw vertical border
                    if col_idx < num_cols - 1:
                        draw.line(
                            [(cell_x + col_width, table_y), (cell_x + col_width, table_y + row_height)],
                            fill=TABLE_BORDER, width=1
                        )
                    cell_x += col_width
                
                # Draw horizontal border
                draw.line(
                    [(MARGIN_L, table_y + row_height), (MARGIN_L + CONTENT_W, table_y + row_height)],
                    fill=TABLE_BORDER, width=1
                )
                
                table_y += row_height
            
            y = table_y
        
        block_index += 1
    
    if block_index >= len(blocks):
        return block_index, -1  # Done
    
    return block_index, block_index  # Next block to render


def main():
    # Read HTML
    with open('/home/node/.openclaw/workspace/tmp_agentic_ai_guide.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    print(f'HTML size: {len(html_content)} chars')
    
    # Parse into blocks
    blocks = parse_html_to_blocks(html_content)
    print(f'Parsed {len(blocks)} blocks')
    
    # Print structure overview
    type_counts = {}
    for bt, _ in blocks:
        type_counts[bt] = type_counts.get(bt, 0) + 1
    print(f'Block types: {type_counts}')
    
    # Render pages
    pages = []
    block_idx = 0
    page_num = 0
    
    while block_idx < len(blocks):
        page = Image.new('RGB', (PAGE_W, PAGE_H), BG_COLOR)
        draw = ImageDraw.Draw(page)
        
        block_idx, next_idx = render_page(
            draw, blocks, block_idx,
            FONT_REGULAR, FONT_H1, FONT_H2, FONT_H3, FONT_CODE, FONT_SMALL
        )
        
        if next_idx == -1:
            page_num += 1
            pages.append(page)
            break
        
        page_num += 1
        pages.append(page)
        if page_num % 10 == 0:
            print(f'Rendered page {page_num}')
    
    print(f'Total pages rendered: {page_num}')
    
    # Save as PDF
    if pages:
        first_page = pages[0]
        other_pages = pages[1:] if len(pages) > 1 else []
        first_page.save(
            OUTPUT_PDF,
            save_all=True,
            append_images=other_pages,
            resolution=96.0,
            title='The Hitchhiker\'s Guide to Agentic AI (Bilingual)',
            author='Haggai Roitman'
        )
        print(f'PDF saved to {OUTPUT_PDF}')
    else:
        print('ERROR: No pages rendered!')

    # Verification
    import subprocess
    result = subprocess.run(['python3', '-c', f'''
import re
with open("{OUTPUT_PDF}", "rb") as f:
    c = f.read()
print(f"Size: {{len(c)/1024/1024:.1f}} MB")
pages = len(re.findall(b"/Type\\\\s*/Page[^s]", c))
print(f"Pages: {{pages}}")
'''], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)


if __name__ == '__main__':
    main()
