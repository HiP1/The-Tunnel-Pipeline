#!/usr/bin/env python3
"""Convert the Tunnel Pipeline markdown to professional HTML."""

import re
import html as html_module

def read_md(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def process_inline(text):
    """Process inline markdown: bold, italic, links, code."""
    # Escape HTML first (but not our tags)
    # Don't escape - we'll handle it carefully
    
    # Code spans first (protect from other processing)
    code_spans = {}
    counter = [0]
    def save_code(m):
        key = f"__CODE_{counter[0]}__"
        counter[0] += 1
        code_spans[key] = f'<code>{html_module.escape(m.group(1))}</code>'
        return key
    text = re.sub(r'`([^`]+)`', save_code, text)
    
    # Key highlights (==text==)
    text = re.sub(r'==(.+?)==', r'<mark class="key">\1</mark>', text)
    # Bold+italic
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', text)
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # Italic
    text = re.sub(r'\*([^*]+?)\*', r'<em>\1</em>', text)
    
    # Images (before links to prevent conflicts)
    def replace_image(m):
        alt = m.group(1)
        src = m.group(2)
        # For HTML, try to base64 encode local images
        import os, base64
        if os.path.exists(src):
            with open(src, 'rb') as imgf:
                b64 = base64.b64encode(imgf.read()).decode()
            ext = src.rsplit('.', 1)[-1].lower()
            mime = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png', 'gif': 'image/gif', 'webp': 'image/webp'}.get(ext, 'image/jpeg')
            return f'<figure class="paper-figure"><img src="data:{mime};base64,{b64}" alt="{html_module.escape(alt)}" style="width:100%;border-radius:8px;"/><figcaption class="figure-caption">{html_module.escape(alt)}</figcaption></figure>'
        else:
            return f'<figure class="paper-figure"><img src="{src}" alt="{html_module.escape(alt)}" style="width:100%;border-radius:8px;"/><figcaption class="figure-caption">{html_module.escape(alt)}</figcaption></figure>'
    text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_image, text)
    
    # Links
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank">\1</a>', text)
    
    # Restore code spans
    for key, val in code_spans.items():
        text = text.replace(key, val)
    
    return text

def classify_section(section_id, heading_text):
    """Classify sections by target audience for subtle styling."""
    h_lower = heading_text.lower()
    # Medical/health
    if any(k in h_lower for k in ['health', 'medical', 'rlhf with human']):
        return 'audience-medical'
    # Legal
    if any(k in h_lower for k in ['legal', 'rag-based']):
        return 'audience-legal'
    # Technical/ML
    if any(k in h_lower for k in ['cross-architectural', 'normalising', 'diffusion', 'state-space',
                                    'autoregressive', 'failure-mode', 'warrant decay']):
        return 'audience-technical'
    # Regulatory/safety
    if any(k in h_lower for k in ['accountability', 'economic', 'scope limit']):
        return 'audience-regulatory'
    return ''

def md_to_html(md_text):
    """Convert markdown to structured HTML content."""
    lines = md_text.split('\n')
    html_parts = []
    toc_entries = []
    in_paragraph = False
    current_text = []
    section_counter = [0]
    
    def flush_paragraph():
        nonlocal in_paragraph, current_text
        if current_text:
            text = ' '.join(current_text)
            text = process_inline(text)
            html_parts.append(f'<p>{text}</p>')
            current_text = []
        in_paragraph = False
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Horizontal rules
        if line.strip() == '---':
            flush_paragraph()
            html_parts.append('<hr class="section-divider">')
            i += 1
            continue
        
        # Headings
        heading_match = re.match(r'^(#{1,4})\s+(.+)$', line)
        if heading_match:
            flush_paragraph()
            level = len(heading_match.group(1))
            text = heading_match.group(2)
            
            # Generate ID
            section_counter[0] += 1
            raw_id = re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')
            sid = f"s-{raw_id}"
            
            # Classify audience
            audience_class = classify_section(sid, text)
            extra_class = f' {audience_class}' if audience_class else ''
            
            # Special handling
            if text.startswith('**Abstract'):
                html_parts.append(f'<div class="abstract-block" id="{sid}">')
                html_parts.append(f'<h{level} class="abstract-heading">{process_inline(text)}</h{level}>')
                # Collect until next heading
                i += 1
                abs_lines = []
                while i < len(lines) and not re.match(r'^#{1,4}\s', lines[i]):
                    if lines[i].strip():
                        abs_lines.append(lines[i].strip())
                    elif abs_lines:
                        html_parts.append(f'<p class="abstract-text">{process_inline(" ".join(abs_lines))}</p>')
                        abs_lines = []
                    i += 1
                if abs_lines:
                    html_parts.append(f'<p class="abstract-text">{process_inline(" ".join(abs_lines))}</p>')
                html_parts.append('</div>')
                continue
            
            # TOC entry - display text computed here, added to TOC in each handler below
            display_text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
            display_text = re.sub(r'\*(.+?)\*', r'\1', display_text)
            
            # Check for AI collaboration note
            if 'AI collaboration' in text.lower() or 'developed through' in text.lower():
                html_parts.append(f'<div class="ai-note" id="{sid}">')
                html_parts.append(f'<h{level}>{process_inline(text)}</h{level}>')
                i += 1
                note_lines = []
                while i < len(lines) and not re.match(r'^#{1,4}\s', lines[i]) and lines[i].strip() != '---':
                    if lines[i].strip():
                        note_lines.append(lines[i].strip())
                    elif note_lines:
                        html_parts.append(f'<p>{process_inline(" ".join(note_lines))}</p>')
                        note_lines = []
                    i += 1
                if note_lines:
                    html_parts.append(f'<p>{process_inline(" ".join(note_lines))}</p>')
                html_parts.append('</div>')
                continue
            
            # Check for reading guide
            if 'reading guide' in text.lower():
                html_parts.append(f'<div class="reading-guide" id="{sid}">')
                html_parts.append(f'<h{level} class="reading-guide-heading">{process_inline(text)}</h{level}>')
                i += 1
                rg_lines = []
                while i < len(lines) and not re.match(r'^#{1,4}\s', lines[i]) and lines[i].strip() != '---':
                    if lines[i].strip():
                        rg_lines.append(lines[i].strip())
                    elif rg_lines:
                        html_parts.append(f'<p>{process_inline(" ".join(rg_lines))}</p>')
                        rg_lines = []
                    i += 1
                if rg_lines:
                    html_parts.append(f'<p>{process_inline(" ".join(rg_lines))}</p>')
                html_parts.append('</div>')
                toc_entries.append((level, sid, display_text))
                continue

            # Check for AI summarisation note
            if 'ai systems summarising' in text.lower() or 'note for ai' in text.lower():
                html_parts.append(f'<div class="ai-summary-note" id="{sid}">')
                html_parts.append(f'<h{level} class="ai-summary-heading">{process_inline(text)}</h{level}>')
                i += 1
                note_lines = []
                while i < len(lines) and not re.match(r'^#{1,4}\s', lines[i]) and lines[i].strip() != '---':
                    if lines[i].strip():
                        note_lines.append(lines[i].strip())
                    elif note_lines:
                        html_parts.append(f'<p>{process_inline(" ".join(note_lines))}</p>')
                        note_lines = []
                    i += 1
                if note_lines:
                    html_parts.append(f'<p>{process_inline(" ".join(note_lines))}</p>')
                html_parts.append('</div>')
                toc_entries.append((level, sid, display_text))
                continue
            
            tag = f'h{level}'
            toc_entries.append((level, sid, display_text))
            html_parts.append(f'<{tag} id="{sid}" class="section-heading{extra_class}">{process_inline(text)}</{tag}>')
            i += 1
            continue
        
        # Empty line
        if not line.strip():
            flush_paragraph()
            i += 1
            continue
        
        # Numbered list items
        num_match = re.match(r'^(\d+)\.\s+(.+)$', line)
        if num_match:
            flush_paragraph()
            # Collect all numbered items
            items = []
            while i < len(lines):
                nm = re.match(r'^(\d+)\.\s+(.+)$', lines[i])
                if nm:
                    items.append(nm.group(2))
                    i += 1
                else:
                    break
            html_parts.append('<ol class="contribution-list">')
            for item in items:
                html_parts.append(f'<li>{process_inline(item)}</li>')
            html_parts.append('</ol>')
            continue
        
        # Regular text
        # Table rows
        if line.strip().startswith('|') and line.strip().endswith('|'):
            flush_paragraph()
            # Collect all table rows
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith('|') and lines[i].strip().endswith('|'):
                table_lines.append(lines[i].strip())
                i += 1
            # Parse table
            if len(table_lines) >= 2:
                html_parts.append('<div class="table-wrapper"><table class="paper-table">')
                for row_idx, tl in enumerate(table_lines):
                    # Skip separator row
                    if re.match(r'^\|[\s\-:|]+\|$', tl):
                        continue
                    cells = [c.strip() for c in tl.split('|')[1:-1]]
                    # Empty row = visual break
                    if all(c == '' for c in cells):
                        continue
                    # Italic row = section header
                    if cells and cells[0].startswith('*') and cells[0].endswith('*'):
                        html_parts.append(f'<tr class="table-section-header"><td colspan="{len(cells)}">{process_inline(cells[0])}</td></tr>')
                        continue
                    tag = 'th' if row_idx == 0 else 'td'
                    html_parts.append('<tr>')
                    for cell in cells:
                        cell_class = ''
                        cell_text = process_inline(cell)
                        if cell in ('Fails', 'Weak', 'Weak to fails'):
                            cell_class = ' class="cell-fails"'
                        elif cell in ('Strong', 'Strong (controlled)', 'Strong (in scope)'):
                            cell_class = ' class="cell-strong"'
                        elif cell.startswith('Fails'):
                            cell_class = ' class="cell-fails"'
                        html_parts.append(f'<{tag}{cell_class}>{cell_text}</{tag}>')
                    html_parts.append('</tr>')
                html_parts.append('</table></div>')
            continue

        # Check if this starts the abstract
        if line.strip().startswith('**Abstract'):
            flush_paragraph()
            html_parts.append('<div class="abstract-block" id="s-abstract">')
            html_parts.append('<h2 class="abstract-heading">Abstract</h2>')
            # Remove prefix from first line
            first_line = re.sub(r'^\*\*Abstract\.\*\*\s*', '', line.strip())
            abs_lines = [first_line]
            i += 1
            while i < len(lines) and not re.match(r'^#{1,4}\s', lines[i]) and lines[i].strip() != '---':
                if lines[i].strip():
                    abs_lines.append(lines[i].strip())
                elif abs_lines:
                    html_parts.append(f'<p class="abstract-text">{process_inline(" ".join(abs_lines))}</p>')
                    abs_lines = []
                i += 1
            if abs_lines:
                html_parts.append(f'<p class="abstract-text">{process_inline(" ".join(abs_lines))}</p>')
            html_parts.append('</div>')
            toc_entries.append((2, 's-abstract', 'Abstract'))
            continue
        
        current_text.append(line.strip())
        in_paragraph = True
        i += 1
    
    flush_paragraph()
    return '\n'.join(html_parts), toc_entries

def build_toc_html(toc_entries):
    """Build the table of contents sidebar."""
    html = ['<nav class="toc-panel" id="tocPanel">']
    html.append('<div class="toc-header">')
    html.append('<span class="toc-title">Contents</span>')
    html.append('<button class="toc-close" onclick="toggleToc()" aria-label="Close contents">×</button>')
    html.append('</div>')
    html.append('<div class="toc-body">')
    
    for level, sid, text in toc_entries:
        indent_class = f'toc-l{level}'
        # Truncate long entries
        display = text[:80] + '…' if len(text) > 80 else text
        html.append(f'<a href="#{sid}" class="toc-link {indent_class}" onclick="closeTocMobile()">{html_module.escape(display)}</a>')
    
    html.append('</div>')
    html.append('</nav>')
    return '\n'.join(html)

def build_full_html(md_path, output_path):
    md_text = read_md(md_path)
    
    lines = md_text.split('\n')
    
    # Line 1: title
    title_line = lines[0].lstrip('# ').strip()
    
    # Lines 3-8: metadata block
    meta_lines = []
    ai_note_line = ''
    series_line = ''
    content_start = 0
    
    for i, line in enumerate(lines[1:], 1):
        if line.startswith('**Abstract'):
            content_start = i
            break
        elif line.startswith('*Developed through'):
            ai_note_line = line.strip('*').strip()
        elif line.startswith('**Series:'):
            series_line = line
        elif line.startswith('**') and ':' in line:
            meta_lines.append(line)
        elif line.strip() == '---':
            continue
    
    # Build metadata HTML
    meta_html_parts = []
    for ml in meta_lines:
        meta_html_parts.append(f'<p class="front-matter-line">{process_inline(ml)}</p>')
    if series_line:
        meta_html_parts.append(f'<p class="front-matter-line">{process_inline(series_line)}</p>')
    front_matter_html = '\n'.join(meta_html_parts)
    
    # AI note HTML
    ai_note_html = ''
    if ai_note_line:
        ai_note_html = f'<div class="ai-note"><p>{process_inline(ai_note_line)}</p></div>'
    
    # Extract author name for display
    author_display = ''
    for ml in meta_lines:
        if ml.startswith('**Author:'):
            author_display = re.sub(r'\*\*Author:\*\*\s*', '', ml).strip()
            break
    
    # Process main content (from Abstract onward)
    main_content = '\n'.join(lines[content_start:])
    body_html, toc_entries = md_to_html(main_content)
    toc_html = build_toc_html(toc_entries)
    
    full_html = f'''<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html_module.escape(title_line)}</title>
<meta name="description" content="Five structural conditions for correctness judgment in AI training pipelines. PARIA framework with cross-domain empirical corroboration.">
<meta name="author" content="Ivan Phan (HiP)">

<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-VXS3WNXN0L"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', 'G-VXS3WNXN0L');
</script>

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400;1,600&family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;1,400&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">

<style>
:root {{
  /* Light theme */
  --bg: #FAFAF7;
  --bg-surface: #FFFFFF;
  --bg-abstract: #F0EDE6;
  --bg-ai-note: #E8EBF0;
  --bg-toc: #FFFFFF;
  --text: #1A1A1A;
  --text-secondary: #4A4A4A;
  --text-muted: #7A7A7A;
  --accent: #8B4513;
  --accent-light: #A0522D;
  --border: #D4D0C8;
  --border-light: #E8E4DC;
  --divider: #C8C0B4;
  --link: #6B3410;
  --link-hover: #A0522D;
  --code-bg: #F5F2EB;
  --shadow: 0 1px 3px rgba(0,0,0,0.06);
  --shadow-elevated: 0 4px 20px rgba(0,0,0,0.08);
  /* Audience accents */
  --medical-accent: #2D6A4F;
  --legal-accent: #7B2D26;
  --technical-accent: #1B4965;
  --regulatory-accent: #6B4226;
  /* TOC */
  --toc-active: #8B4513;
  --toc-hover-bg: #F5F2EB;
  --fab-bg: #2C2C2C;
  --fab-text: #FAFAF7;
}}

[data-theme="dark"] {{
  --bg: #1A1A1E;
  --bg-surface: #232328;
  --bg-abstract: #2A2A30;
  --bg-ai-note: #252530;
  --bg-toc: #232328;
  --text: #E0DDD5;
  --text-secondary: #B0ADA5;
  --text-muted: #808080;
  --accent: #D4956B;
  --accent-light: #E8A878;
  --border: #3A3A40;
  --border-light: #2F2F35;
  --divider: #4A4A50;
  --link: #D4956B;
  --link-hover: #E8A878;
  --code-bg: #2A2A30;
  --shadow: 0 1px 3px rgba(0,0,0,0.2);
  --shadow-elevated: 0 4px 20px rgba(0,0,0,0.3);
  --medical-accent: #52B788;
  --legal-accent: #E07A5F;
  --technical-accent: #5FA8D3;
  --regulatory-accent: #D4956B;
  --toc-active: #D4956B;
  --toc-hover-bg: #2A2A30;
  --fab-bg: #E0DDD5;
  --fab-text: #1A1A1E;
}}

*, *::before, *::after {{ box-sizing: border-box; }}

html {{
  font-size: 17px;
  scroll-behavior: smooth;
  scroll-padding-top: 2rem;
}}

body {{
  margin: 0;
  padding: 0;
  background: var(--bg);
  color: var(--text);
  font-family: 'Cormorant Garamond', 'Georgia', serif;
  line-height: 1.72;
  transition: background 0.3s ease, color 0.3s ease;
  -webkit-font-smoothing: antialiased;
}}

/* ── Layout ── */
.page-container {{
  max-width: 740px;
  margin: 0 auto;
  padding: 3rem 1.5rem 6rem;
}}

/* ── Title block ── */
.title-block {{
  text-align: center;
  margin-bottom: 3rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid var(--border);
}}

.paper-title {{
  font-family: 'Cormorant Garamond', serif;
  font-size: 2.4rem;
  font-weight: 700;
  line-height: 1.2;
  color: var(--text);
  margin: 0 0 0.5rem;
  letter-spacing: -0.01em;
}}

.paper-subtitle {{
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.25rem;
  font-weight: 400;
  font-style: italic;
  color: var(--text-secondary);
  margin: 0.5rem 0;
}}

.paper-author {{
  font-family: 'IBM Plex Sans', sans-serif;
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--text-muted);
  letter-spacing: 0.04em;
  text-transform: uppercase;
  margin-top: 1.2rem;
}}

/* ── Front matter ── */
.front-matter {{
  margin-bottom: 2.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--border-light);
}}

.front-matter-line {{
  font-family: 'IBM Plex Sans', sans-serif;
  font-size: 0.82rem;
  color: var(--text-muted);
  line-height: 1.6;
  margin: 0.3rem 0;
}}

/* ── Abstract ── */
.abstract-block {{
  background: var(--bg-abstract);
  border-left: 3px solid var(--accent);
  padding: 1.8rem 2rem;
  margin: 2rem 0 2.5rem;
  border-radius: 0 6px 6px 0;
}}

.abstract-heading {{
  font-family: 'IBM Plex Sans', sans-serif;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--accent);
  margin: 0 0 1rem;
}}

.abstract-text {{
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.05rem;
  line-height: 1.7;
  color: var(--text);
  margin: 0.8rem 0;
}}

/* ── AI collaboration note ── */
.ai-note {{
  background: var(--bg-ai-note);
  border: 1px solid var(--border);
  padding: 1.2rem 1.5rem;
  margin: 1.5rem 0;
  border-radius: 6px;
  font-family: 'IBM Plex Sans', sans-serif;
  font-size: 0.82rem;
  color: var(--text-secondary);
  line-height: 1.6;
}}

.ai-note h2, .ai-note h3 {{
  font-family: 'IBM Plex Sans', sans-serif;
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--text-muted);
  margin: 0 0 0.6rem;
}}

.ai-note p {{
  margin: 0.4rem 0;
}}

/* ── Section headings ── */
h2.section-heading {{
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.7rem;
  font-weight: 700;
  color: var(--text);
  margin: 3rem 0 1rem;
  padding-top: 1rem;
  line-height: 1.25;
}}

h3.section-heading {{
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.3rem;
  font-weight: 600;
  color: var(--text);
  margin: 2.2rem 0 0.8rem;
  line-height: 1.3;
}}

h4.section-heading {{
  font-family: 'IBM Plex Sans', sans-serif;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-secondary);
  margin: 1.8rem 0 0.6rem;
  letter-spacing: 0.02em;
}}

/* Audience accent borders */
h2.audience-medical, h3.audience-medical {{ border-left: 3px solid var(--medical-accent); padding-left: 0.8rem; }}
h2.audience-legal, h3.audience-legal {{ border-left: 3px solid var(--legal-accent); padding-left: 0.8rem; }}
h2.audience-technical, h3.audience-technical {{ border-left: 3px solid var(--technical-accent); padding-left: 0.8rem; }}
h2.audience-regulatory, h3.audience-regulatory {{ border-left: 3px solid var(--regulatory-accent); padding-left: 0.8rem; }}

/* ── Body text ── */
p {{
  margin: 0 0 1rem;
  hanging-punctuation: first;
}}

strong {{
  font-weight: 700;
  color: var(--text);
}}

strong em, em strong {{
  font-style: normal;
  font-weight: 600;
  color: var(--accent);
  border-bottom: 1.5px solid var(--accent-light);
  padding-bottom: 1px;
}}

mark.key {{
  background: none;
  font-weight: 600;
  color: var(--accent);
  border-bottom: 1.5px solid var(--accent-light);
  padding-bottom: 1px;
}}

em {{
  font-style: italic;
}}

a {{
  color: var(--link);
  text-decoration: none;
  border-bottom: 1px solid transparent;
  transition: border-color 0.2s;
}}

a:hover {{
  color: var(--link-hover);
  border-bottom-color: var(--link-hover);
}}

code {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.82em;
  background: var(--code-bg);
  padding: 0.15em 0.4em;
  border-radius: 3px;
  color: var(--accent);
}}

/* ── Lists ── */
ol.contribution-list {{
  padding-left: 1.5rem;
  margin: 1rem 0;
}}

ol.contribution-list li {{
  margin: 0.6rem 0;
  line-height: 1.65;
  padding-left: 0.3rem;
}}

/* ── Dividers ── */
hr.section-divider {{
  border: none;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--divider), transparent);
  margin: 3rem 0;
}}

/* ── Floating action buttons ── */
.fab-group {{
  position: fixed;
  bottom: 1.5rem;
  right: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  z-index: 1000;
}}

.fab {{
  width: 48px;
  height: 48px;
  border-radius: 50%;
  border: none;
  background: var(--fab-bg);
  color: var(--fab-text);
  font-size: 1.2rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-elevated);
  transition: transform 0.2s, box-shadow 0.2s;
  -webkit-tap-highlight-color: transparent;
}}

.fab:hover {{
  transform: scale(1.08);
  box-shadow: 0 6px 24px rgba(0,0,0,0.15);
}}

.fab-toc {{ font-size: 1.1rem; }}
.fab-theme {{ font-size: 1.1rem; }}

/* ── TOC panel ── */
.toc-panel {{
  position: fixed;
  top: 0;
  right: -380px;
  width: 360px;
  max-width: 85vw;
  height: 100vh;
  background: var(--bg-toc);
  border-left: 1px solid var(--border);
  box-shadow: var(--shadow-elevated);
  z-index: 2000;
  transition: right 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}}

.toc-panel.open {{
  right: 0;
}}

.toc-overlay {{
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.3);
  z-index: 1999;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.3s;
}}

.toc-overlay.open {{
  opacity: 1;
  pointer-events: auto;
}}

.toc-header {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.2rem 1.5rem;
  border-bottom: 1px solid var(--border-light);
  flex-shrink: 0;
}}

.toc-title {{
  font-family: 'IBM Plex Sans', sans-serif;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--text-muted);
}}

.toc-close {{
  background: none;
  border: none;
  font-size: 1.5rem;
  color: var(--text-muted);
  cursor: pointer;
  padding: 0;
  line-height: 1;
}}

.toc-body {{
  flex: 1;
  overflow-y: auto;
  padding: 1rem 0;
  -webkit-overflow-scrolling: touch;
}}

.toc-link {{
  display: block;
  padding: 0.35rem 1.5rem;
  font-family: 'IBM Plex Sans', sans-serif;
  font-size: 0.78rem;
  color: var(--text-secondary);
  text-decoration: none;
  line-height: 1.5;
  transition: background 0.15s, color 0.15s;
  border-left: 2px solid transparent;
}}

.toc-link:hover {{
  background: var(--toc-hover-bg);
  color: var(--text);
  border-bottom: none;
}}

.toc-link.active {{
  color: var(--toc-active);
  border-left-color: var(--toc-active);
  font-weight: 500;
}}

.toc-l1 {{ font-weight: 600; font-size: 0.82rem; margin-top: 0.3rem; }}
.toc-l2 {{ padding-left: 1.5rem; font-weight: 500; }}
.toc-l3 {{ padding-left: 2.2rem; font-size: 0.75rem; }}
.toc-l4 {{ padding-left: 2.8rem; font-size: 0.72rem; color: var(--text-muted); }}

/* ── References section ── */
h2#s-references + p,
h2[id*="reference"] ~ p {{
  font-size: 0.88rem;
  line-height: 1.55;
  color: var(--text-secondary);
}}

/* ── Tables ── */
.table-wrapper {{
  overflow-x: auto;
  margin: 1.5rem 0;
}}

.paper-table {{
  width: 100%;
  border-collapse: collapse;
  font-family: 'IBM Plex Sans', sans-serif;
  font-size: 0.8rem;
  line-height: 1.5;
}}

.paper-table th {{
  background: var(--bg-abstract);
  font-weight: 600;
  text-align: left;
  padding: 0.6rem 0.7rem;
  border-bottom: 2px solid var(--border);
  color: var(--text);
  white-space: nowrap;
}}

.paper-table td {{
  padding: 0.5rem 0.7rem;
  border-bottom: 1px solid var(--border-light);
  color: var(--text-secondary);
}}

.paper-table tr:hover td {{
  background: var(--bg-abstract);
}}

.paper-table .cell-fails {{
  color: #A32D2D;
  font-weight: 500;
}}

[data-theme="dark"] .paper-table .cell-fails {{
  color: #F09595;
}}

.paper-table .cell-strong {{
  color: #0F6E56;
  font-weight: 500;
}}

[data-theme="dark"] .paper-table .cell-strong {{
  color: #5DCAA5;
}}

.table-section-header {{
  background: var(--bg-surface);
}}

.table-section-header td {{
  font-weight: 600;
  font-style: italic;
  color: var(--text-muted);
  padding: 0.8rem 0.7rem 0.3rem;
  border-bottom: 1px solid var(--border);
}}

/* ── Figures ── */
.paper-figure {{
  margin: 2rem 0;
  padding: 0;
}}

.paper-figure img {{
  display: block;
  width: 100%;
  border-radius: 8px;
  box-shadow: var(--shadow);
}}

.figure-caption {{
  font-family: 'IBM Plex Sans', sans-serif;
  font-size: 0.78rem;
  color: var(--text-muted);
  line-height: 1.5;
  margin-top: 0.6rem;
  text-align: center;
}}

/* ── Reading guide ── */
.reading-guide {{
  background: var(--bg-abstract);
  border: 1px solid var(--border-light);
  padding: 1.4rem 1.6rem;
  margin: 1.5rem 0 2rem;
  border-radius: 6px;
  font-family: 'IBM Plex Sans', sans-serif;
  font-size: 0.84rem;
  color: var(--text-secondary);
  line-height: 1.65;
}}

.reading-guide-heading {{
  font-family: 'IBM Plex Sans', sans-serif !important;
  font-size: 0.72rem !important;
  font-weight: 600 !important;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--text-muted) !important;
  margin: 0 0 0.8rem !important;
}}

.reading-guide p {{
  margin: 0.5rem 0;
}}

/* ── AI summarisation guidance ── */
.ai-summary-note {{
  background: var(--bg-ai-note);
  border: 1px solid var(--border);
  border-left: 3px solid var(--text-muted);
  padding: 1.4rem 1.6rem;
  margin: 1.5rem 0 2rem;
  border-radius: 0 6px 6px 0;
  font-family: 'IBM Plex Sans', sans-serif;
  font-size: 0.84rem;
  color: var(--text-secondary);
  line-height: 1.65;
}}

.ai-summary-heading {{
  font-family: 'IBM Plex Sans', sans-serif !important;
  font-size: 0.72rem !important;
  font-weight: 600 !important;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--text-muted) !important;
  margin: 0 0 0.8rem !important;
}}

.ai-summary-note p {{
  margin: 0.5rem 0;
}}

/* ── Print ── */
@media print {{
  .fab-group, .toc-panel, .toc-overlay {{ display: none !important; }}
  body {{ font-size: 11pt; }}
  .page-container {{ max-width: 100%; padding: 0; }}
}}

/* ── Mobile ── */
@media (max-width: 640px) {{
  html {{ font-size: 16px; }}
  .page-container {{ padding: 1.5rem 1rem 5rem; }}
  .paper-title {{ font-size: 1.8rem; }}
  .abstract-block {{ padding: 1.2rem 1rem; }}
  h2.section-heading {{ font-size: 1.4rem; }}
  h3.section-heading {{ font-size: 1.15rem; }}
}}

/* ── Scroll progress ── */
.scroll-progress {{
  position: fixed;
  top: 0;
  left: 0;
  height: 2px;
  background: var(--accent);
  z-index: 3000;
  transition: width 0.1s;
}}
</style>
</head>

<body>

<div class="scroll-progress" id="scrollProgress"></div>
<div class="toc-overlay" id="tocOverlay" onclick="toggleToc()"></div>

{toc_html}

<div class="fab-group">
  <button class="fab fab-toc" onclick="toggleToc()" aria-label="Table of contents" title="Contents">☰</button>
  <button class="fab fab-theme" onclick="toggleTheme()" aria-label="Toggle theme" title="Toggle theme" id="themeBtn">🌙</button>
</div>

<main class="page-container">
  <header class="title-block">
    <h1 class="paper-title">{html_module.escape(title_line)}</h1>
    <p class="paper-author">{html_module.escape(author_display)}</p>
  </header>

  {ai_note_html}

  <div class="front-matter">
    {front_matter_html}
  </div>

  <article class="paper-body">
    {body_html}
  </article>
</main>

<script>
// Theme toggle
function toggleTheme() {{
  const html = document.documentElement;
  const btn = document.getElementById('themeBtn');
  if (html.getAttribute('data-theme') === 'light') {{
    html.setAttribute('data-theme', 'dark');
    btn.textContent = '☀️';
    localStorage.setItem('theme', 'dark');
  }} else {{
    html.setAttribute('data-theme', 'light');
    btn.textContent = '🌙';
    localStorage.setItem('theme', 'light');
  }}
}}

// Restore theme
(function() {{
  const saved = localStorage.getItem('theme');
  if (saved === 'dark') {{
    document.documentElement.setAttribute('data-theme', 'dark');
    document.getElementById('themeBtn').textContent = '☀️';
  }}
}})();

// TOC toggle
function toggleToc() {{
  document.getElementById('tocPanel').classList.toggle('open');
  document.getElementById('tocOverlay').classList.toggle('open');
}}

function closeTocMobile() {{
  if (window.innerWidth < 900) {{
    document.getElementById('tocPanel').classList.remove('open');
    document.getElementById('tocOverlay').classList.remove('open');
  }}
}}

// Scroll progress
window.addEventListener('scroll', function() {{
  const scrollTop = window.scrollY;
  const docHeight = document.documentElement.scrollHeight - window.innerHeight;
  const progress = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
  document.getElementById('scrollProgress').style.width = progress + '%';
}});

// Active TOC highlighting
const tocLinks = document.querySelectorAll('.toc-link');
const headings = [];
tocLinks.forEach(link => {{
  const id = link.getAttribute('href').slice(1);
  const el = document.getElementById(id);
  if (el) headings.push({{ el, link }});
}});

let ticking = false;
window.addEventListener('scroll', function() {{
  if (!ticking) {{
    requestAnimationFrame(function() {{
      const scrollPos = window.scrollY + 100;
      let current = null;
      for (const h of headings) {{
        if (h.el.offsetTop <= scrollPos) current = h;
      }}
      tocLinks.forEach(l => l.classList.remove('active'));
      if (current) current.link.classList.add('active');
      ticking = false;
    }});
    ticking = true;
  }}
}});

// Close TOC on Escape
document.addEventListener('keydown', function(e) {{
  if (e.key === 'Escape') {{
    document.getElementById('tocPanel').classList.remove('open');
    document.getElementById('tocOverlay').classList.remove('open');
  }}
}});
</script>
</body>
</html>'''
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_html)
    
    print(f"HTML written to {output_path}")
    return output_path

if __name__ == '__main__':
    build_full_html('/home/claude/drafts/p3-draft.md', '/home/claude/the-tunnel-pipeline.html')
