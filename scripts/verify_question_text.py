#!/usr/bin/env python3
"""
verify_question_text.py
-----------------------
Extracts the exact question text for Section I (Q1–Q15) from each NESA
Maths Standard 2 exam PDF and compares it against the q:"..." fields
currently in index.html.

Outputs two files:
  question_text_diff.txt   — human-readable diff for review
  question_text_fixes.json — machine-readable list of proposed updates

Usage:
  python verify_question_text.py
"""

import sys, re, json, fitz
sys.stdout.reconfigure(encoding='utf-8')

# ── Config ────────────────────────────────────────────────────────────────────
PDF_DIR   = r"C:\Claude Code Space\CRAMIT QUIZ Code Folder\NESA Exams Folder\Maths Standard 2"
INDEX_HTML = r"C:\Claude Code Space\CRAMIT QUIZ Code Folder\CODE\CramIT-Quiz\index.html"

PAPERS = {
    2020: f"{PDF_DIR}\\2020-hsc-mathematics-standard-2.pdf",
    2021: f"{PDF_DIR}\\2021-hsc-mathematics-standard-2.pdf",
    2022: f"{PDF_DIR}\\2022-hsc-mathematics-standard-2.pdf",
    2023: f"{PDF_DIR}\\2023-hsc-maths-std-2.pdf",
    2024: f"{PDF_DIR}\\2024-hsc-maths-std-2.pdf",
    2025: f"{PDF_DIR}\\2025-hsc-maths-standard-2.pdf",
}

# ── Step 1: Extract questions from PDF ───────────────────────────────────────

def extract_section1_text(pdf_path):
    """
    Extracts full page text for Section I pages.
    Returns dict: {q_num (1-15): question_text_string}
    """
    doc = fitz.open(pdf_path)

    # The actual Section I start page contains "Use the multiple-choice answer sheet"
    # (the cover page mentions both Section I and II so we avoid it)
    # Stop when we hit a page mentioning "Section II" that's NOT the cover page
    section1_pages = []
    in_section1 = False
    for i in range(doc.page_count):
        text = doc[i].get_text('text')
        # Real start of Section I — this line only appears on the actual question page
        if 'Use the multiple-choice answer sheet for Questions 1' in text:
            in_section1 = True
        # Section II header page — stop collecting (use page index > 5 to skip cover)
        if in_section1 and i > 5 and 'Section II' in text and ('Attempt Questions 16' in text or '85 marks' in text):
            break
        if in_section1:
            section1_pages.append(text)

    full_text = '\n'.join(section1_pages)

    # Split on standalone question numbers (1–15).
    # In the PDF text, numbers appear as e.g. "\n1\n" or "\n10   \n"
    questions = {}
    parts = re.split(r'\n\s*(\d{1,2})\s*\n', full_text)

    # parts is: [preamble, "1", q1_body, "2", q2_body, ...]
    i = 1
    while i < len(parts) - 1:
        num_str = parts[i].strip()
        if num_str.isdigit():
            q_num = int(num_str)
            if 1 <= q_num <= 15:
                raw = parts[i + 1] if i + 1 < len(parts) else ''
                questions[q_num] = clean_question_text(raw)
        i += 2

    return questions


def clean_question_text(raw):
    """
    Takes raw text between question number and the next question.
    Removes option labels (A./B./C./D. and their text), page footers,
    diagram placeholders, and trailing whitespace.
    Returns the cleaned question stem only.
    """
    lines = raw.split('\n')
    result = []
    skip_next = False

    for line in lines:
        stripped = line.strip()

        # Skip blank lines at start
        if not result and not stripped:
            continue

        # Stop at option A — everything from here is answer options
        if re.match(r'^A[\.\s]', stripped) or stripped in ('A.', 'A'):
            break

        # Skip page numbers / footers like "– 3 –" or "1100"
        if re.match(r'^[-–]\s*\d+\s*[-–]', stripped):
            continue
        if re.match(r'^\d{4}$', stripped):  # standalone 4-digit year
            continue

        # Skip diagram/graph labels that PyMuPDF picks up
        if re.match(r'^(Graph|Diagram|Table|Chart|Multiple choice diagrams)$', stripped, re.I):
            continue

        # Skip option images text artifacts like "Mul\ntiple choice diagrams"
        if 'tiple choice' in stripped.lower():
            continue

        result.append(stripped)

    text = ' '.join(result)
    # Collapse multiple spaces
    text = re.sub(r'  +', ' ', text).strip()
    # Remove trailing page reference artifacts
    text = re.sub(r'\s*[-–]\s*\d+\s*[-–]\s*$', '', text).strip()
    return text


# ── Step 2: Parse index.html for existing q:"..." fields ─────────────────────

def parse_index_html(html_path):
    """
    Extracts original HSC questions (not variants) from the mcQuestions array.
    Returns dict: {(year, position): {'q': str, 'has_image': bool, 'line': int}}
    where position is the 1-based order within that year (≈ question number on paper).
    """
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Match question objects for original HSC questions (no variant:true)
    # Pattern: {year:YYYY, category:'...', q:"...", ...}  without variant:true nearby
    # We'll extract all non-variant questions grouped by year
    questions = {}

    # Find all question object starts: {year:YYYY,
    pattern = re.compile(
        r'\{year:(\d{4}),category:\'[^\']+\','
        r'(?!.*?variant:true)'   # exclude variants — lookahead not reliable here
        r'q:"((?:[^"\\]|\\.)*?)"'
        r'.*?'
        r'(image:"[^"]*")?',
        re.DOTALL
    )

    # Simpler approach: line by line, find year:YYYY entries without variant:true
    year_counters = {}
    for lineno, line in enumerate(content.split('\n'), 1):
        m = re.search(r'\{year:(\d{4}),category:', line)
        if not m:
            continue
        if 'variant:true' in line:
            continue
        year = int(m.group(1))
        if year < 2020 or year > 2025:
            continue

        # Extract q:"..."
        qm = re.search(r',q:"((?:[^"\\]|\\.)*?)"', line)
        if not qm:
            continue
        q_text = qm.group(1)
        q_text = q_text.replace('\\"', '"').replace('\\\\', '\\')

        has_image = 'image:"' in line or "image:'" in line

        year_counters[year] = year_counters.get(year, 0) + 1
        pos = year_counters[year]
        questions[(year, pos)] = {
            'q':         q_text,
            'has_image': has_image,
            'line':      lineno,
        }

    return questions


# ── Step 3: Compare and produce report ───────────────────────────────────────

def normalise(s):
    """Lowercase, collapse whitespace, strip punctuation for fuzzy compare."""
    s = s.lower()
    s = re.sub(r'[^\w\s]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def compare(year, pdf_questions, html_questions):
    """
    Compares PDF-extracted questions against HTML questions for one year.
    Returns list of result dicts.
    """
    results = []
    for q_num in range(1, 16):
        html_key = (year, q_num)
        pdf_text  = pdf_questions.get(q_num, '')
        html_data = html_questions.get(html_key)

        if not html_data:
            results.append({
                'year': year, 'q_num': q_num,
                'status': 'NOT_IN_HTML',
                'pdf': pdf_text, 'html': '',
                'line': 0,
            })
            continue

        html_text = html_data['q']
        has_image = html_data['has_image']
        line      = html_data['line']

        if not pdf_text:
            results.append({
                'year': year, 'q_num': q_num,
                'status': 'PDF_NO_TEXT' if not has_image else 'IMAGE_ONLY',
                'pdf': '', 'html': html_text, 'line': line,
            })
            continue

        # Compare normalised versions
        if normalise(pdf_text) == normalise(html_text):
            status = 'MATCH'
        else:
            # Check if HTML text is a substring / summary of PDF text
            pdf_norm  = normalise(pdf_text)
            html_norm = normalise(html_text)
            # Count word overlap
            pdf_words  = set(pdf_norm.split())
            html_words = set(html_norm.split())
            overlap = len(pdf_words & html_words) / max(len(pdf_words), 1)
            status = 'CLOSE' if overlap > 0.7 else 'MISMATCH'

        results.append({
            'year': year, 'q_num': q_num,
            'status': status,
            'pdf': pdf_text,
            'html': html_text,
            'line': line,
        })

    return results


# ── Step 4: Write output files ────────────────────────────────────────────────

def write_report(all_results):
    diff_lines = []
    fixes = []

    counts = {'MATCH': 0, 'CLOSE': 0, 'MISMATCH': 0, 'IMAGE_ONLY': 0,
              'PDF_NO_TEXT': 0, 'NOT_IN_HTML': 0}

    for r in all_results:
        counts[r['status']] = counts.get(r['status'], 0) + 1

    diff_lines.append("=" * 72)
    diff_lines.append("NESA QUESTION TEXT ACCURACY REPORT — Maths Standard 2")
    diff_lines.append("=" * 72)
    diff_lines.append("")

    for r in all_results:
        s = r['status']
        if s == 'MATCH':
            diff_lines.append(f"✅ {r['year']} Q{r['q_num']:02d}  MATCH")
            continue
        if s == 'IMAGE_ONLY':
            diff_lines.append(f"🖼️  {r['year']} Q{r['q_num']:02d}  IMAGE — text in image, not comparable")
            continue
        if s == 'PDF_NO_TEXT':
            diff_lines.append(f"⚠️  {r['year']} Q{r['q_num']:02d}  PDF text not extracted (may be image-only in PDF)")
            continue
        if s == 'NOT_IN_HTML':
            diff_lines.append(f"❓  {r['year']} Q{r['q_num']:02d}  NOT FOUND in index.html")
            continue

        # CLOSE or MISMATCH
        marker = "🔶" if s == 'CLOSE' else "❌"
        diff_lines.append("")
        diff_lines.append(f"{marker} {r['year']} Q{r['q_num']:02d}  {s}  (index.html line ~{r['line']})")
        diff_lines.append(f"  NESA: {r['pdf']}")
        diff_lines.append(f"  APP:  {r['html']}")

        if s == 'MISMATCH':
            fixes.append({
                'year':    r['year'],
                'q_num':   r['q_num'],
                'line':    r['line'],
                'old_q':   r['html'],
                'new_q':   r['pdf'],
            })

    diff_lines.append("")
    diff_lines.append("=" * 72)
    diff_lines.append("SUMMARY")
    diff_lines.append("=" * 72)
    for status, count in sorted(counts.items()):
        diff_lines.append(f"  {status:15s}: {count}")
    diff_lines.append(f"  {'TOTAL':15s}: {sum(counts.values())}")
    diff_lines.append("")
    diff_lines.append(f"{len(fixes)} questions need text updates (MISMATCH only).")
    diff_lines.append("CLOSE matches may be acceptable — review individually.")

    report_path = r"C:\Claude Code Space\CRAMIT QUIZ Code Folder\CODE\CramIT-Quiz\question_text_diff.txt"
    fixes_path  = r"C:\Claude Code Space\CRAMIT QUIZ Code Folder\CODE\CramIT-Quiz\question_text_fixes.json"

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(diff_lines))

    with open(fixes_path, 'w', encoding='utf-8') as f:
        json.dump(fixes, f, indent=2, ensure_ascii=False)

    print('\n'.join(diff_lines))
    print(f"\nReport saved to: question_text_diff.txt")
    print(f"Fixes saved to:  question_text_fixes.json")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("Parsing index.html...")
    html_questions = parse_index_html(INDEX_HTML)
    print(f"  Found {len(html_questions)} original HSC questions in index.html")

    all_results = []

    for year, pdf_path in sorted(PAPERS.items()):
        print(f"\nProcessing {year} PDF...")
        try:
            pdf_questions = extract_section1_text(pdf_path)
            print(f"  Extracted {len(pdf_questions)} questions from PDF")
            results = compare(year, pdf_questions, html_questions)
            all_results.extend(results)
        except Exception as e:
            print(f"  ERROR: {e}")

    write_report(all_results)


if __name__ == '__main__':
    main()
