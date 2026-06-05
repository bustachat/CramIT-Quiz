#!/usr/bin/env python3
"""
apply_question_text_fixes.py
-----------------------------
Reads question_text_fixes.json, filters out bad PDF extractions,
and applies the clean fixes to index.html.

A fix is SKIPPED if the extracted NESA text:
  - Is shorter than 40 characters
  - Starts with a lone digit (diagram number leaked into extraction)
  - Starts with copyright notice
  - Starts with option artifacts like "1 C." / "1 D."
  - Has fewer than 6 words (not a real sentence)
  - Contains mostly numeric/punctuation content

Run:
  python apply_question_text_fixes.py

Outputs:
  - Modifies index.html in-place
  - Prints a summary of applied vs skipped fixes
  - Saves apply_log.txt for your records
"""

import sys, re, json
sys.stdout.reconfigure(encoding='utf-8')

FIXES_PATH  = r"C:\Claude Code Space\CRAMIT QUIZ Code Folder\CODE\CramIT-Quiz\question_text_fixes.json"
INDEX_PATH  = r"C:\Claude Code Space\CRAMIT QUIZ Code Folder\CODE\CramIT-Quiz\index.html"
LOG_PATH    = r"C:\Claude Code Space\CRAMIT QUIZ Code Folder\CODE\CramIT-Quiz\apply_log.txt"


# ── Quality filter ────────────────────────────────────────────────────────────

def is_good_extraction(text):
    """Returns True only if the extracted NESA text is clean, complete question text."""
    t = text.strip()

    # ── Hard length / content rules ──────────────────────────────────────────
    if len(t) < 60:
        return False, f"too short ({len(t)} chars)"

    words = t.split()
    if len(words) < 10:
        return False, f"too few words ({len(words)})"

    # Starts with a page number, lone digit, or option artifact
    if re.match(r'^\d{1,2}\s', t):
        return False, "starts with number (page/diagram artifact)"
    if re.match(r'^\d{1,2}$', t.split()[0]):
        return False, "starts with lone digit"
    if t.startswith('©'):
        return False, "copyright notice"

    # ── Artifact patterns — garbled PDF text ─────────────────────────────────
    # Spaced-out characters like "M u l t i p l e" or "Gr a ph"
    if re.search(r'\b\w\s\w\s\w\s\w\b', t):
        return False, "spaced-out characters (garbled PDF)"

    # Trailing number fragments (e.g. "...PV of the investment? 150 000")
    if re.search(r'\s\d[\d\s]*$', t) and not re.search(r'\d\s*(years?|hours?|days?|cm|km|%)\s*$', t):
        return False, "trailing number fragment"

    # Ends mid-sentence without punctuation (truncated extraction)
    last_char = t[-1]
    if last_char not in '.?':
        return False, f"truncated — ends with '{last_char}' not sentence-ending punctuation"

    # Option text leaked in (e.g. "...best value? 24 L $46.70")
    if re.search(r'\?\s+\d', t):
        return False, "option text leaked after question mark"

    # Table headers leaked (e.g. "Pia's mark Year 10 mean Year 10 standard deviation English")
    if re.search(r'(mean|standard deviation|median)\s+(English|Maths|Science|History)', t, re.I):
        return False, "table header leaked into text"

    # Mostly non-alphabetic
    alpha_chars = sum(1 for c in t if c.isalpha())
    if alpha_chars / len(t) < 0.5:
        return False, "mostly non-alphabetic"

    # Ends with option label
    if re.search(r'\b[A-D]\.\s*$', t):
        return False, "ends with option label"

    return True, "ok"


# ── Apply fixes ───────────────────────────────────────────────────────────────

def escape_for_js_string(s):
    """Escape text for embedding inside a JS double-quoted string."""
    s = s.replace('\\', '\\\\')
    s = s.replace('"', '\\"')
    return s


def apply_fixes(fixes, html_content):
    applied = []
    skipped = []

    for fix in fixes:
        year    = fix['year']
        q_num   = fix['q_num']
        old_q   = fix['old_q']
        new_q   = fix['new_q']

        # Clean up known PDF extraction artifacts before quality check
        new_q = re.sub(r'\b(Gr\s*a\s*ph|G\s*r\s*a\s*p\s*h)\b', '', new_q, flags=re.I)
        new_q = re.sub(r'\b(Mu\s*l\s*ti?\s*ple\s*ch\s*oic\s*e\s*(gr\s*a\s*ph\s*s?|networks?|diagrams?|s)?)\b', '', new_q, flags=re.I)
        new_q = re.sub(r'\b(Bea\s*rin\s*g\s*dia\s*gra\s*m)\b', '', new_q, flags=re.I)
        # Remove formula rendering artifacts like "BAC Time = . 0.015"
        new_q = re.sub(r'\bBAC\s+Time\s*=\s*\.\s*0\.015\b', 'BAC/0.015', new_q)
        # Remove table/graph label text that leaks after image reference
        new_q = re.sub(r'\s+(t\s+h\s*=.*?$)', '', new_q, flags=re.DOTALL)
        # Remove trailing artifacts like "t 12 of"
        new_q = re.sub(r'\s+t\s+\d+\s+of\s*$', '', new_q).strip()
        # Collapse multiple spaces
        new_q = re.sub(r'  +', ' ', new_q).strip()

        good, reason = is_good_extraction(new_q)
        if not good:
            skipped.append({'year': year, 'q_num': q_num, 'reason': reason,
                            'nesa': new_q, 'app': old_q})
            continue

        # Build the exact search string as it appears in index.html
        old_escaped = escape_for_js_string(old_q)
        new_escaped = escape_for_js_string(new_q)

        search  = f',q:"{old_escaped}"'
        replace = f',q:"{new_escaped}"'

        if search not in html_content:
            # Try without escaping (in case already escaped differently)
            search2 = f',q:"{old_q}"'
            if search2 in html_content:
                search, replace = search2, f',q:"{new_escaped}"'
            else:
                skipped.append({'year': year, 'q_num': q_num,
                                'reason': 'not found in HTML (may already be updated)',
                                'nesa': new_q, 'app': old_q})
                continue

        # Count occurrences — only apply if exactly one match (safe)
        count = html_content.count(search)
        if count != 1:
            skipped.append({'year': year, 'q_num': q_num,
                            'reason': f'ambiguous — {count} matches in HTML',
                            'nesa': new_q, 'app': old_q})
            continue

        html_content = html_content.replace(search, replace, 1)
        applied.append({'year': year, 'q_num': q_num, 'old': old_q, 'new': new_q})

    return html_content, applied, skipped


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    with open(FIXES_PATH, 'r', encoding='utf-8') as f:
        fixes = json.load(f)
    print(f"Loaded {len(fixes)} proposed fixes from question_text_fixes.json")

    with open(INDEX_PATH, 'r', encoding='utf-8') as f:
        html = f.read()

    html, applied, skipped = apply_fixes(fixes, html)

    # Write updated index.html
    with open(INDEX_PATH, 'w', encoding='utf-8') as f:
        f.write(html)

    # Build log
    log_lines = []
    log_lines.append("=" * 72)
    log_lines.append("QUESTION TEXT FIX APPLICATION LOG")
    log_lines.append("=" * 72)
    log_lines.append("")
    log_lines.append(f"APPLIED ({len(applied)}):")
    log_lines.append("-" * 50)
    for a in applied:
        log_lines.append(f"  ✅ {a['year']} Q{a['q_num']:02d}")
        log_lines.append(f"     OLD: {a['old']}")
        log_lines.append(f"     NEW: {a['new']}")
        log_lines.append("")

    log_lines.append(f"SKIPPED ({len(skipped)}):")
    log_lines.append("-" * 50)
    for s in skipped:
        log_lines.append(f"  ⏭️  {s['year']} Q{s['q_num']:02d}  [{s['reason']}]")
        log_lines.append(f"     NESA: {s['nesa']}")
        log_lines.append(f"     APP:  {s['app']}")
        log_lines.append("")

    log_lines.append("=" * 72)
    log_lines.append(f"TOTAL: {len(applied)} applied, {len(skipped)} skipped")

    log_text = '\n'.join(log_lines)
    print(log_text)

    with open(LOG_PATH, 'w', encoding='utf-8') as f:
        f.write(log_text)

    print(f"\nindex.html updated.")
    print(f"Log saved to: apply_log.txt")
    print(f"\nNext step: review apply_log.txt, then commit.")


if __name__ == '__main__':
    main()
