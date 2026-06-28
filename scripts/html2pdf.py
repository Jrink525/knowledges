#!/usr/bin/env python3
"""Convert the HTML file to PDF using WeasyPrint."""
import sys
import os

sys.path.insert(0, '/home/node/.openclaw/workspace/pylib/lib')

import weasyprint

html_path = '/tmp/agentic_ai_guide.html'
pdf_dir = '/home/node/.openclaw/workspace/papers/the-hitchhikers-guide-to-agentic-ai'
pdf_path = os.path.join(pdf_dir, 'complete_bilingual_guide.pdf')

os.makedirs(pdf_dir, exist_ok=True)

print(f'Reading HTML from: {html_path}')
print(f'HTML size: {os.path.getsize(html_path):,} bytes')

print('Generating PDF...')
doc = weasyprint.HTML(filename=html_path).render()
print(f'Pages: {len(doc.pages)}')

doc.write_pdf(pdf_path)

file_size = os.path.getsize(pdf_path)
print(f'PDF written to: {pdf_path}')
print(f'PDF size: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)')
