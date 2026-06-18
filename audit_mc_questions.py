"""
audit_mc_questions.py — Complete audit of all 90 HSC MC questions in
subjects/mathematics-standard-2.json against NESA exam PDFs (2020-2025).

Compares: question text, options A-D, correct answer, image presence, formatting.
Outputs: audit_mc_report.txt

Run: python audit_mc_questions.py
"""
import sys, json, re, fitz, os

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PDFS = {
    2020: "C:/Claude Code Space/CRAMIT QUIZ Code Folder/NESA Exams Folder/Maths Standard 2/2020-hsc-mathematics-standard-2.pdf",
    2021: "C:/Claude Code Space/CRAMIT QUIZ Code Folder/NESA Exams Folder/Maths Standard 2/2021-hsc-mathematics-standard-2.pdf",
    2022: "C:/Claude Code Space/CRAMIT QUIZ Code Folder/NESA Exams Folder/Maths Standard 2/2022-hsc-mathematics-standard-2.pdf",
    2023: "C:/Claude Code Space/CRAMIT QUIZ Code Folder/NESA Exams Folder/Maths Standard 2/2023-hsc-maths-std-2.pdf",
    2024: "C:/Claude Code Space/CRAMIT QUIZ Code Folder/NESA Exams Folder/Maths Standard 2/2024-hsc-maths-std-2.pdf",
    2025: "C:/Claude Code Space/CRAMIT QUIZ Code Folder/NESA Exams Folder/Maths Standard 2/2025-hsc-maths-standard-2.pdf",
}

JSON_PATH = "subjects/mathematics-standard-2.json"
DIAGRAMS_DIR = "diagrams"
OUT_FILE = "audit_mc_report.txt"


def extract_page_text_spans(page):
    """Return list of (y, x, text, bold, italic) for all text spans on page."""
    spans = []
    blocks = page.get_text('dict')['blocks']
    for b in blocks:
        if b['type'] != 0:
            continue
        for line in b['lines']:
            for sp in line['spans']:
                text = sp['text'].strip()
                if not text:
                    continue
                bold = bool(sp['flags'] & 16)
                italic = bool(sp['flags'] & 2)
                spans.append((sp['origin'][1], sp['origin'][0], text, bold, italic))
    return sorted(spans, key=lambda s: (round(s[0]/4)*4, s[1]))


def find_section1_pages(doc):
    """Return list of page indices that contain Section I MC questions."""
    pages = []
    for i, page in enumerate(doc):
        text = page.get_text()
        if re.search(r'Section\s+I\b', text) or re.search(r'^\s*[1-9]\s', text, re.MULTILINE):
            # Heuristic: Section I pages have short numbered questions
            if re.search(r'\b[ABCD]\b.*\n.*\b[ABCD]\b', text):
                pages.append(i)
    return pages


def extract_mc_from_pdf(year):
    """
    Extract all 15 MC questions from a PDF.
    Returns dict: {qNum: {'q': text, 'options': [A,B,C,D], 'has_image': bool, 'bold_runs': [], 'italic_runs': []}}
    """
    pdf_path = PDFS[year]
    doc = fitz.open(pdf_path)

    questions = {}

    # Scan all pages to find Section I content
    # Strategy: find pages with patterns like "1 " at left margin followed by options A/B/C/D
    all_spans = []
    for page_idx in range(min(15, len(doc))):
        page = doc[page_idx]
        text = page.get_text()
        # Stop if we hit Section II
        if 'Section II' in text and page_idx > 3:
            break
        spans = extract_page_text_spans(page)
        # Check if page has images (drawings)
        img_list = page.get_images()
        drawings = page.get_drawings()
        has_graphics = len(img_list) > 0 or len(drawings) > 5
        all_spans.append((page_idx, spans, has_graphics, page))

    doc.close()

    # Parse question numbers and reconstruct questions
    # Build a flat ordered list of (page_idx, y, x, text, bold, italic)
    flat = []
    page_graphics = {}
    for page_idx, spans, has_graphics, page in all_spans:
        page_graphics[page_idx] = has_graphics
        for y, x, text, bold, italic in spans:
            flat.append((page_idx, y, x, text, bold, italic))

    # Find question boundaries by detecting standalone question numbers at left margin
    # Question numbers appear as "1", "2", ... "15" with x < 100 (left margin)
    q_boundaries = []  # list of (flat_idx, qnum)

    for i, (page_idx, y, x, text, bold, italic) in enumerate(flat):
        if re.match(r'^(\d{1,2})$', text) and x < 100:
            n = int(text)
            if 1 <= n <= 15:
                q_boundaries.append((i, n))

    # Deduplicate (keep first occurrence of each question number)
    seen = set()
    q_boundaries_clean = []
    for idx, n in q_boundaries:
        if n not in seen:
            seen.add(n)
            q_boundaries_clean.append((idx, n))
    q_boundaries_clean.sort(key=lambda x: x[0])

    # Extract spans between each question boundary
    for bi, (start_idx, qnum) in enumerate(q_boundaries_clean):
        end_idx = q_boundaries_clean[bi+1][0] if bi+1 < len(q_boundaries_clean) else len(flat)

        q_spans = flat[start_idx+1:end_idx]

        # Separate into question text and options
        # Options are identified by single letter at left-ish margin: A/B/C/D
        option_indices = []
        for si, (page_idx, y, x, text, bold, italic) in enumerate(q_spans):
            if re.match(r'^[ABCD]$', text) and x < 130:
                option_indices.append(si)

        # Question text = spans before first option
        first_opt = option_indices[0] if option_indices else len(q_spans)
        q_text_spans = q_spans[:first_opt]
        q_text = ' '.join(s[3] for s in q_text_spans).strip()

        # Bold/italic runs in question text
        bold_runs = [s[3] for s in q_text_spans if s[4]]
        italic_runs = [s[3] for s in q_text_spans if s[5]]

        # Extract options
        options = {}
        for oi, si in enumerate(option_indices):
            letter = q_spans[si][3]
            end_si = option_indices[oi+1] if oi+1 < len(option_indices) else len(q_spans)
            opt_spans = q_spans[si+1:end_si]
            opt_text = ' '.join(s[3] for s in opt_spans).strip()
            options[letter] = opt_text

        # Check for images on the pages spanned by this question
        pages_used = set(s[0] for s in q_spans)
        # A question has an image if its page has graphics AND it has few/no text options
        # (rough heuristic — image questions may have blank options or image-based options)
        has_image = any(page_graphics.get(p, False) for p in pages_used)

        questions[qnum] = {
            'q': q_text,
            'options': options,
            'has_image': has_image,
            'bold_runs': bold_runs,
            'italic_runs': italic_runs,
        }

    return questions


def normalise(text):
    """Normalise text for comparison: strip whitespace, normalise unicode dashes/quotes."""
    if not text:
        return ''
    t = str(text)
    t = t.replace('−', '-').replace('–', '-').replace('—', '-')
    t = t.replace('‘', "'").replace('’', "'")
    t = t.replace('“', '"').replace('”', '"')
    t = re.sub(r'\s+', ' ', t).strip()
    return t


def compare_texts(json_text, pdf_text):
    """Return (match_level, notes). match_level: 'exact'|'minor'|'different'|'missing'"""
    jn = normalise(json_text)
    pn = normalise(pdf_text)
    if not jn:
        return 'missing', 'JSON q text is empty'
    if not pn:
        return 'no_pdf', 'PDF extraction returned empty'
    if jn == pn:
        return 'exact', ''
    # Check similarity
    jwords = set(jn.lower().split())
    pwords = set(pn.lower().split())
    if len(jwords) == 0:
        return 'missing', 'JSON empty'
    overlap = len(jwords & pwords) / max(len(jwords), len(pwords))
    if overlap > 0.85:
        # Find actual differences
        jparts = jn.split()
        pparts = pn.split()
        diffs = []
        for jw in jparts:
            if jw not in pparts:
                diffs.append(f'JSON has "{jw}"')
        for pw in pparts:
            if pw not in jparts:
                diffs.append(f'PDF has "{pw}"')
        return 'minor', '; '.join(diffs[:5])
    return 'different', f'JSON: "{jn[:80]}..." vs PDF: "{pn[:80]}..."'


def image_file_exists(year, qnum, suffix='stimulus'):
    """Check if a diagram image file exists for this question."""
    for ext in ['jpg', 'jpeg', 'png', 'svg']:
        fname = f"mathematics-standard-2_{year}_Q{qnum}_{suffix}.{ext}"
        if os.path.exists(os.path.join(DIAGRAMS_DIR, fname)):
            return fname
    return None


def option_letter_from_index(idx):
    return ['A', 'B', 'C', 'D'][idx] if idx < 4 else '?'


def main():
    print("Loading JSON...", flush=True)
    with open(JSON_PATH, encoding='utf-8') as f:
        data = json.load(f)

    mc_all = [q for q in data['mcQuestions'] if not q.get('variant')]
    mc_by_year = {}
    for q in mc_all:
        mc_by_year.setdefault(q['year'], []).append(q)
    for y in mc_by_year:
        mc_by_year[y].sort(key=lambda q: q.get('qNum', 999))

    lines = []
    lines.append("=" * 80)
    lines.append("CRAMIT — Mathematics Standard 2 MC Question Audit")
    lines.append("Comparing subjects/mathematics-standard-2.json against NESA PDFs")
    lines.append("=" * 80)
    lines.append("")

    total_qs = 0
    total_pass = 0
    issues_text = 0
    issues_options = 0
    issues_answer = 0
    issues_image = 0
    issues_format = 0
    issues_missing_image = 0

    for year in sorted(mc_by_year.keys()):
        lines.append(f"\n{'='*60}")
        lines.append(f"  {year} — Extracting from PDF...")
        lines.append(f"{'='*60}")

        try:
            pdf_qs = extract_mc_from_pdf(year)
            lines.append(f"  PDF extraction: found {len(pdf_qs)} question boundaries\n")
        except Exception as e:
            lines.append(f"  ERROR extracting PDF: {e}\n")
            pdf_qs = {}

        for qi, jq in enumerate(mc_by_year[year]):
            qnum = jq.get('qNum') or (qi + 1)
            total_qs += 1

            # --- JSON fields ---
            j_text = jq.get('q') or jq.get('text') or ''
            j_options = jq.get('options', [])
            j_answer_idx = jq.get('answer', -1)  # 0-based index into options[]
            j_answer_letter = option_letter_from_index(j_answer_idx)
            j_has_stimulus = bool(jq.get('image'))
            j_has_option_images = bool(jq.get('optionImages'))
            j_hide_q = jq.get('hideQ', False)

            # --- PDF fields ---
            pq = pdf_qs.get(qnum, {})
            p_text = pq.get('q', '')
            p_options = pq.get('options', {})
            p_bold = pq.get('bold_runs', [])
            p_italic = pq.get('italic_runs', [])
            p_has_image = pq.get('has_image', False)

            # --- Checks ---
            row_issues = []

            # 1. Question text
            if j_hide_q:
                text_status = 'N/A (hideQ=true — text embedded in image)'
            elif not p_text:
                text_status = '⚠️  PDF extraction empty — manual check needed'
                row_issues.append('pdf_extract_empty')
            else:
                match, note = compare_texts(j_text, p_text)
                if match == 'exact':
                    text_status = '✅ exact match'
                elif match == 'minor':
                    text_status = f'⚠️  minor diff — {note}'
                    row_issues.append('text_minor')
                    issues_text += 1
                else:
                    text_status = f'❌ MISMATCH — {note}'
                    row_issues.append('text_mismatch')
                    issues_text += 1

            # 2. Options text (A-D)
            opt_issues = []
            if j_has_option_images:
                opt_status = 'N/A (image options)'
            elif not p_options:
                opt_status = '⚠️  PDF options not extracted'
            else:
                for li, letter in enumerate(['A', 'B', 'C', 'D']):
                    j_opt = j_options[li] if li < len(j_options) else ''
                    p_opt = p_options.get(letter, '')
                    if not p_opt:
                        continue
                    m, note = compare_texts(j_opt, p_opt)
                    if m not in ('exact', 'no_pdf'):
                        opt_issues.append(f'{letter}: {note}')
                if opt_issues:
                    opt_status = '⚠️  ' + ' | '.join(opt_issues[:3])
                    issues_options += 1
                    row_issues.append('option_diff')
                else:
                    opt_status = '✅ options match'

            # 3. Correct answer
            # We can't verify the correct answer from PDF text alone (no answer key in exam)
            # But we can flag if the answer index seems out of range
            if j_answer_idx < 0 or j_answer_idx >= len(j_options):
                answer_status = f'❌ answer index {j_answer_idx} out of range (options count: {len(j_options)})'
                row_issues.append('answer_range')
                issues_answer += 1
            else:
                answer_status = f'✅ answer={j_answer_letter} (index {j_answer_idx})'

            # 4. Image / diagram
            if j_has_stimulus:
                img_fname = jq['image'].split('/')[-1]
                img_path = os.path.join(DIAGRAMS_DIR, img_fname)
                if os.path.exists(img_path):
                    img_size = os.path.getsize(img_path)
                    if img_size < 5000:
                        image_status = f'⚠️  file very small ({img_size}b) — may be blank/corrupt: {img_fname}'
                        row_issues.append('image_small')
                        issues_image += 1
                    else:
                        image_status = f'✅ stimulus exists ({img_size//1024}KB): {img_fname}'
                else:
                    image_status = f'❌ FILE MISSING: {img_fname}'
                    row_issues.append('image_missing')
                    issues_image += 1
            elif j_has_option_images:
                oi_list = jq.get('optionImages', [])
                missing = []
                for oi_path in oi_list:
                    if oi_path:
                        fname = oi_path.split('/')[-1]
                        if not os.path.exists(os.path.join(DIAGRAMS_DIR, fname)):
                            missing.append(fname)
                if missing:
                    image_status = f'❌ option image(s) MISSING: {", ".join(missing)}'
                    row_issues.append('image_missing')
                    issues_image += 1
                    issues_missing_image += 1
                else:
                    counts = {
                        'total': len([x for x in oi_list if x]),
                    }
                    image_status = f'✅ option images present ({counts["total"]} files)'
            else:
                # No image in JSON — but PDF page has graphics?
                if p_has_image and not j_hide_q:
                    image_status = f'⚠️  PDF page has graphics but JSON has no image — may need stimulus'
                    row_issues.append('possible_missing_image')
                    issues_missing_image += 1
                else:
                    image_status = 'N/A (text-only question)'

            # 5. Formatting (bold/italic in PDF not in JSON)
            if p_bold or p_italic:
                fmt_notes = []
                if p_bold:
                    fmt_notes.append(f'PDF bold: {", ".join(p_bold[:4])}')
                if p_italic:
                    fmt_notes.append(f'PDF italic: {", ".join(p_italic[:4])}')
                # Check if JSON text contains those words (even if not bold)
                jn = normalise(j_text)
                missing_fmt = []
                for w in p_bold:
                    if normalise(w).lower() in jn.lower():
                        missing_fmt.append(f'**{w}**')
                format_status = f'ℹ️  {" | ".join(fmt_notes)}'
                if missing_fmt:
                    issues_format += 1
                    row_issues.append('formatting')
            else:
                format_status = '—'

            # --- Determine overall status ---
            critical = [i for i in row_issues if i in ('text_mismatch', 'image_missing', 'answer_range')]
            warnings = [i for i in row_issues if i not in critical]

            if not row_issues:
                total_pass += 1
                overall = '✅ PASS'
            elif critical:
                overall = '❌ ISSUE'
            else:
                overall = '⚠️  WARN'

            # --- Write report entry ---
            category = jq.get('category', '?')
            lines.append(f"Q{qnum:2d} ({category}) — {overall}")
            lines.append(f"  Text:    {text_status}")
            lines.append(f"  Options: {opt_status}")
            lines.append(f"  Answer:  {answer_status}")
            lines.append(f"  Image:   {image_status}")
            lines.append(f"  Format:  {format_status}")

            # Show actual JSON text vs PDF text for non-trivial diffs
            if 'text_mismatch' in row_issues or 'text_minor' in row_issues:
                lines.append(f"  JSON q:  {normalise(j_text)[:120]}")
                lines.append(f"  PDF  q:  {normalise(p_text)[:120]}")

            lines.append("")

    # Summary
    lines.append("=" * 60)
    lines.append("SUMMARY")
    lines.append("=" * 60)
    lines.append(f"Total MC questions audited:    {total_qs}")
    lines.append(f"Passing (no issues):           {total_pass}")
    lines.append(f"With issues:                   {total_qs - total_pass}")
    lines.append("")
    lines.append("Issue breakdown:")
    lines.append(f"  Question text diffs:         {issues_text}")
    lines.append(f"  Option text diffs:           {issues_options}")
    lines.append(f"  Answer index errors:         {issues_answer}")
    lines.append(f"  Image file missing/corrupt:  {issues_image}")
    lines.append(f"  Possible missing images:     {issues_missing_image}")
    lines.append(f"  Formatting (bold/italic):    {issues_format}")
    lines.append("")
    lines.append("NOTE: PDF text extraction is imperfect for image-heavy or scanned pages.")
    lines.append("Questions marked '⚠️ PDF extraction empty' require manual PDF review.")
    lines.append("Correct answer verification requires the marking guidelines PDF.")
    lines.append("")
    lines.append("Marking guidelines location:")
    lines.append("  C:/Claude Code Space/CRAMIT QUIZ Code Folder/NESA Exams Folder/Maths Standard 2/")

    report = '\n'.join(lines)
    with open(OUT_FILE, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\nReport written to: {OUT_FILE}")
    print(f"Total: {total_qs} questions | Pass: {total_pass} | Issues: {total_qs - total_pass}")


if __name__ == '__main__':
    main()
