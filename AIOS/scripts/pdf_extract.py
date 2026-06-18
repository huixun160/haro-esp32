#!/usr/bin/env python3
"""
AIOS PDF Extraction Tool (pdfplumber backend)
TM-36: Extract text from Unisoc knowledgebase PDFs for LLM consumption.

Usage:
    python AIOS/scripts/pdf_extract.py <pdf_path>
    python AIOS/scripts/pdf_extract.py <pdf_path> -o output.md
    python AIOS/scripts/pdf_extract.py --index <directory> -o index.md
    python AIOS/scripts/pdf_extract.py --batch <directory> -o <output_dir>
"""

import sys
import os
import argparse
import traceback


def extract_text(pdf_path, max_pages=None):
    """Extract text from a PDF file using pdfplumber."""
    import pdfplumber

    pages = []
    with pdfplumber.open(pdf_path) as pdf:
        page_count = min(len(pdf.pages), max_pages) if max_pages else len(pdf.pages)
        for i in range(page_count):
            page = pdf.pages[i]
            text = page.extract_text() or ""
            if text.strip():
                pages.append({'page': i + 1, 'text': text.strip()})
    return pages


def get_pdf_info(pdf_path):
    """Get basic PDF metadata."""
    import pdfplumber

    info = {
        'path': pdf_path,
        'filename': os.path.basename(pdf_path),
        'pages': 0,
        'size_kb': os.path.getsize(pdf_path) // 1024,
        'has_text': False,
    }

    with pdfplumber.open(pdf_path) as pdf:
        info['pages'] = len(pdf.pages)
        # Check first 3 pages for extractable text
        for i in range(min(3, len(pdf.pages))):
            text = pdf.pages[i].extract_text() or ""
            if len(text.strip()) > 50:
                info['has_text'] = True
                break

    return info


def format_as_markdown(pages, pdf_path):
    """Format extracted text as markdown."""
    basename = os.path.basename(pdf_path)
    lines = [
        f"# {basename}\n",
        f"> Extracted from: `{pdf_path}`",
        f"> Pages with text: {len(pages)}\n",
        "---\n",
    ]
    for p in pages:
        lines.append(f"\n## Page {p['page']}\n")
        lines.append(p['text'])
        lines.append("")
    return "\n".join(lines)


def generate_index(directory):
    """Generate index of all PDFs in a directory tree."""
    entries = []
    for root, dirs, files in os.walk(directory):
        dirs.sort()
        for f in sorted(files):
            if not f.lower().endswith('.pdf'):
                continue
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, directory)
            category = rel_path.split(os.sep)[0] if os.sep in rel_path else "root"
            try:
                info = get_pdf_info(full_path)
                info['category'] = category
                info['rel_path'] = rel_path
                entries.append(info)
            except Exception as e:
                entries.append({
                    'filename': f,
                    'rel_path': rel_path,
                    'category': category,
                    'error': str(e),
                    'pages': 0,
                    'size_kb': os.path.getsize(full_path) // 1024,
                    'has_text': False,
                })
    return entries


def format_index_markdown(entries, directory):
    """Format index as markdown."""
    lines = [
        "# AIOS Knowledgebase Index\n",
        f"> Source: `{directory}`",
        f"> Total PDFs: {len(entries)}",
        f"> Generated: TM-36 Phase 0\n",
        "---\n",
    ]

    # Group by category
    categories = {}
    for e in entries:
        cat = e.get('category', 'unknown')
        categories.setdefault(cat, []).append(e)

    # Summary table
    lines.append("## Summary\n")
    lines.append("| Category | Count | Total Size | Text Extractable |")
    lines.append("|----------|-------|------------|-----------------|")
    for cat in sorted(categories.keys()):
        items = categories[cat]
        total_size = sum(e.get('size_kb', 0) for e in items)
        text_ok = sum(1 for e in items if e.get('has_text', False))
        err = sum(1 for e in items if 'error' in e)
        label = f"{text_ok}/{len(items)}" + (f" ({err} err)" if err else "")
        lines.append(f"| {cat} | {len(items)} | {total_size:,} KB | {label} |")

    total = len(entries)
    total_size = sum(e.get('size_kb', 0) for e in entries)
    total_text = sum(1 for e in entries if e.get('has_text', False))
    lines.append(f"| **Total** | **{total}** | **{total_size:,} KB** | **{total_text}/{total}** |")

    # Per-category detail
    for cat in sorted(categories.keys()):
        items = categories[cat]
        lines.append(f"\n## {cat}\n")
        lines.append("| # | Document | Pages | Size | Text |")
        lines.append("|---|----------|-------|------|------|")
        for i, e in enumerate(items, 1):
            name = e.get('filename', '?')
            pages = e.get('pages', '?')
            size = e.get('size_kb', 0)
            error = e.get('error', '')
            if error:
                lines.append(f"| {i} | {name} | ? | {size:,} KB | ❌ `{error[:60]}` |")
            else:
                text = "✅" if e.get('has_text') else "❌ (image-only)"
                lines.append(f"| {i} | {name} | {pages} | {size:,} KB | {text} |")

    return "\n".join(lines)


def batch_extract(directory, output_dir, max_pages=None):
    """Batch extract all PDFs to markdown files."""
    os.makedirs(output_dir, exist_ok=True)
    results = []
    for root, dirs, files in os.walk(directory):
        dirs.sort()
        for f in sorted(files):
            if not f.lower().endswith('.pdf'):
                continue
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, directory)
            out_name = rel_path.replace(os.sep, '_').replace('.pdf', '.md').replace('.PDF', '.md')
            out_path = os.path.join(output_dir, out_name)
            try:
                pages = extract_text(full_path, max_pages=max_pages)
                md = format_as_markdown(pages, full_path)
                with open(out_path, 'w', encoding='utf-8') as fout:
                    fout.write(md)
                results.append({'file': f, 'pages': len(pages), 'output': out_path, 'status': 'OK'})
                print(f"  [OK] {f} → {out_name} ({len(pages)} pages)")
            except Exception as e:
                results.append({'file': f, 'status': 'ERROR', 'error': str(e)})
                print(f"  [FAIL] {f}: {e}")
    return results


def main():
    parser = argparse.ArgumentParser(description='AIOS PDF Extraction Tool (TM-36)')
    parser.add_argument('input', nargs='?', help='PDF file or directory')
    parser.add_argument('-o', '--output', help='Output file or directory')
    parser.add_argument('--index', action='store_true', help='Generate PDF index')
    parser.add_argument('--batch', action='store_true', help='Batch extract all PDFs')
    parser.add_argument('--max-pages', type=int, default=None, help='Max pages per PDF')
    args = parser.parse_args()

    if not args.input:
        parser.print_help()
        sys.exit(1)

    if args.index:
        print(f"Generating index for: {args.input}")
        entries = generate_index(args.input)
        md = format_index_markdown(entries, args.input)
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(md)
            print(f"Index written to: {args.output}")
        else:
            print(md)
    elif args.batch:
        output_dir = args.output or os.path.join(args.input, '_extracted')
        print(f"Batch extracting: {args.input} → {output_dir}")
        results = batch_extract(args.input, output_dir, max_pages=args.max_pages)
        ok = sum(1 for r in results if r['status'] == 'OK')
        print(f"\nDone: {ok}/{len(results)} extracted")
    else:
        pages = extract_text(args.input, max_pages=args.max_pages)
        md = format_as_markdown(pages, args.input)
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(md)
            print(f"Written to: {args.output} ({len(pages)} pages)")
        else:
            print(md)


if __name__ == '__main__':
    main()
