#!/usr/bin/env node
/**
 * Convert HTML file to PDF using pdfkit (pure JS, no native deps)
 * Usage: node html2pdf.js <input.html> <output.pdf>
 */

const fs = require('fs');
const path = require('path');
const PDFDocument = require('pdfkit');

const inputFile = process.argv[2] || '/tmp/agentic_ai_guide.html';
const outputFile = process.argv[3] || '/tmp/agentic_ai_guide.pdf';

const html = fs.readFileSync(inputFile, 'utf-8');

// Parse HTML structure - extract text content with basic formatting
// We'll process line by line from the markdown-derived HTML
function extractPageBreaks(html) {
  // Find all div.page-break markers and content between them
  const sections = html.split(/<div class="page-break"><\/div>/);
  return sections.map(section => {
    // Extract title from h1/h2
    const titleMatch = section.match(/<h([12])[^>]*>(.*?)<\/h\1>/);
    const title = titleMatch ? titleMatch[2].replace(/<[^>]+>/g, '') : '';
    return { title, html: section };
  });
}

const sections = extractPageBreaks(html);
console.log(`Found ${sections.length} sections`);

function stripTags(text) {
  return text.replace(/<[^>]+>/g, '').trim();
}

function stripTagsKeepNewlines(html) {
  // Replace block tags with newlines then strip remaining tags
  return html
    .replace(/<\/(h[1-5]|p|div|li|tr|td|pre|code|table)>/gi, '\n')
    .replace(/<br\s*\/?>/gi, '\n')
    .replace(/<[^>]+>/g, '')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .trim();
}

// Process HTML to plain text with formatting indicators
function htmlToStyledText(html, doc) {
  // Process headings
  html = html.replace(/<h1[^>]*>(.*?)<\/h1>/gs, (match, content) => {
    const text = stripTags(content);
    doc.fontSize(16).font('Helvetica-Bold');
    doc.text(text, { paragraphGap: 12 });
    doc.moveDown(0.5);
    return '';
  });

  html = html.replace(/<h2[^>]*>(.*?)<\/h2>/gs, (match, content) => {
    const text = stripTags(content);
    doc.fontSize(13).font('Helvetica-Bold');
    doc.text(text, { paragraphGap: 10 });
    doc.moveDown(0.3);
    return '';
  });

  html = html.replace(/<h3[^>]*>(.*?)<\/h3>/gs, (match, content) => {
    const text = stripTags(content);
    doc.fontSize(11).font('Helvetica-Bold');
    doc.text(text, { paragraphGap: 8 });
    doc.moveDown(0.2);
    return '';
  });

  html = html.replace(/<h[45][^>]*>(.*?)<\/h[45]>/gs, (match, content) => {
    const text = stripTags(content);
    doc.fontSize(10).font('Helvetica-BoldOblique');
    doc.text(text, { paragraphGap: 6 });
    return '';
  });

  // Code blocks
  html = html.replace(/<pre><code>(.*?)<\/code><\/pre>/gs, (match, content) => {
    const text = stripTags(content);
    doc.fontSize(7.5).font('Courier');
    const lines = text.split('\n');
    for (const line of lines) {
      // Indent code blocks
      doc.text('  ' + line, { indent: 10, continued: false });
    }
    doc.moveDown(0.3);
    return '';
  });

  // Inline code
  html = html.replace(/<code>(.*?)<\/code>/g, (match, content) => {
    // We'll handle in text processing
    return content;
  });

  // Strong
  html = html.replace(/<strong>(.*?)<\/strong>/g, '$1');
  
  // Links
  html = html.replace(/<a[^>]*>(.*?)<\/a>/g, '$1');

  // Tables - crude table handling
  html = html.replace(/<table>[\s\S]*?<\/table>/g, (match) => {
    const rows = match.match(/<tr>[\s\S]*?<\/tr>/g) || [];
    for (const row of rows) {
      const cells = row.match(/<t[dh][^>]*>(.*?)<\/t[dh]>/g) || [];
      const cellTexts = cells.map(c => stripTags(c).trim());
      doc.fontSize(8).font('Helvetica');
      doc.text('| ' + cellTexts.join(' | ') + ' |', { indent: 5 });
    }
    doc.moveDown(0.2);
    return '';
  });

  // HR
  html = html.replace(/<hr\s*\/?>/g, () => {
    doc.moveDown(0.3);
    const y = doc.y;
    doc.moveTo(doc.page.margins.left, y)
       .lineTo(doc.page.width - doc.page.margins.left, y)
       .stroke('#cccccc');
    doc.moveDown(0.3);
    return '';
  });

  // Regular paragraphs and remaining text
  const remaining = stripTagsKeepNewlines(html);
  const paragraphs = remaining.split('\n').filter(p => p.trim());
  
  doc.fontSize(9).font('Helvetica');
  for (const para of paragraphs) {
    const trimmed = para.trim();
    if (trimmed) {
      doc.text(trimmed, {
        align: 'left',
        lineGap: 1,
        paragraphGap: 4
      });
    }
  }
}

// Generate PDF
console.log('Generating PDF...');
const doc = new PDFDocument({
  size: 'A4',
  margins: { top: 50, bottom: 50, left: 50, right: 50 },
  info: {
    Title: 'The Hitchhiker\'s Guide to Agentic AI - 中英双语版',
    Author: 'Translated by AI',
    Subject: 'Agentic AI Guide',
  }
});

const writeStream = fs.createWriteStream(outputFile);
doc.pipe(writeStream);

// Title page
doc.fontSize(24).font('Helvetica-Bold');
doc.text('The Hitchhiker\'s Guide to Agentic AI', { align: 'center' });
doc.moveDown(0.5);
doc.fontSize(16).font('Helvetica');
doc.text('中英双语完整版', { align: 'center' });
doc.moveDown(2);
doc.fontSize(10);
doc.text('全部 30 章完整翻译', { align: 'center' });
doc.text('Generated: ' + new Date().toISOString(), { align: 'center' });

doc.addPage();

// Process each section
let pageCount = 1;
for (let i = 0; i < sections.length; i++) {
  const section = sections[i];
  if (section.title && i > 0) {
    doc.fontSize(11).font('Helvetica-Bold');
    doc.text(section.title, { paragraphGap: 8 });
    doc.moveDown(0.3);
  }
  
  try {
    htmlToStyledText(section.html, doc);
  } catch (e) {
    console.error(`Error processing section ${i}: ${e.message}`);
  }
  
  // Check if we need a new page
  if (doc.y > doc.page.height - 100) {
    doc.addPage();
  }
}

doc.end();

writeStream.on('finish', () => {
  const stats = fs.statSync(outputFile);
  console.log(`PDF generated: ${outputFile}`);
  console.log(`Size: ${(stats.size / 1024 / 1024).toFixed(2)} MB`);
  console.log(`Pages: ~${doc.bufferedPageRange().count}`);
});

writeStream.on('error', (err) => {
  console.error('Error writing PDF:', err.message);
  process.exit(1);
});
