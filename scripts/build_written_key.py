"""Extract the official WRITTEN-question mark allocations from NESA marking guidelines.

Companion to `build_answer_key.py`, which does the same for Section I multiple choice.
Official marks never change, so they are derived once, committed to
`data/answer-key/written/`, and enforced in CI by `scripts/check_written_key.cjs`.
CI can never regenerate this: the PDFs are not in the repo, by copyright.

What is extracted, and what is not
----------------------------------
For every question part the guidelines define, this records the **maximum mark**, the
official **sample answer** text, and the official **criteria rows** (each band's wording
beside the mark it earns). Only the mark is machine-checkable and only the mark is
enforced; the sample answer and criteria are stored for human reference, because prose
cannot be compared for equality. Storing them is still worthwhile -- they are the source
a reviewer needs when a bank answer looks wrong, and the criteria rows are the ONLY
ground truth for a question's `bandDescriptors` (added 2026-09-01, for the VET written
review; before that, band descriptors could be reviewed for plausibility but not against
NESA).

Why the criteria rows are bracketed by the table's drawn rules
--------------------------------------------------------------
A criteria row's mark is vertically CENTRED in its cell, so a row whose wording runs over
three lines has its mark on the middle line -- see 2024 VET Q16(a), where "2" sits beside
the word "OR" between the two clauses it applies to. Bracketing a row by the mark lines
above and below it therefore leaks wording in BOTH directions, which is exactly the bug
`build_mapping_grid.py` was fixed for on 2026-08-28. These tables are really ruled, so
`row_rules()`/`band_of()` (same technique, same reason) read the boundaries the page
itself draws. Where a table has no usable rules, each mark-bearing line falls back to
being its own row -- reported by shape, never silently merged.

Why the marks are read positionally
-----------------------------------
The guidelines lay each part out as `Question N (a)` -> a `Criteria`/`Marks` table ->
`Sample answer:`. The marks live in a right-hand column at x ~ 485. Reading that column
positionally, and stopping at `Sample answer`, is what keeps the count honest: a naive
digit regex over the whole block picks up stray digits in the sample working and
over-counts (2020 Maths Section II reads 117 that way, against a true 85).

Two header shapes must be discarded, or they become phantom questions: the Section I
answer key's `Question / Answer` table on page 1, and the `Question / Marks / Content /
Syllabus outcomes` mapping grid at the end. Both are rejected by requiring the token
after `Question` to be a number. Note the mapping grid also carries a `Marks` column
header, at x ~ 136 -- hence the x > 400 test rather than "find the Marks column".

Anything that cannot be parsed is REPORTED, never guessed: a part whose criteria table
yields no mark is written to stderr and omitted from the output.

Usage
-----
    python scripts/build_written_key.py <subject-id> [--dry-run]
    python scripts/build_written_key.py all

Subject ids: mathematics-standard-2, multimedia, vet-construction.
(Health and Movement Science has no past papers -- 2026 is its first HSC year.)
"""

import argparse
import glob
import json
import os
import re
import sys

import fitz  # PyMuPDF

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NESA = r"C:\Claude Code Space\CRAMIT QUIZ Code Folder\NESA Exams Folder"
OUT_DIR = os.path.join(REPO, "data", "answer-key", "written")

SUBJECTS = {
    "mathematics-advanced": "Maths Advanced",
    "mathematics-standard-2": "Maths Standard 2",
    "multimedia": "Industrial Technology - Multimedia",
    "vet-construction": "VET - Construction",
}

MARKS_COL_MIN_X = 440   # the mapping grid's Marks column sits at x~136; the real one at x~472
HEADER_MAX_X = 110      # "Question" starts in the left margin

# A stacked fraction's bar. ⚠️ "Shorter than row_rules()' 100 pt" is NOT a sufficient
# test, and assuming it was cost this extractor 145 of its 234 Maths Advanced parts on the
# first run: the criteria table is TWO cells, so every row is ruled twice -- once across
# the criteria column (~380 pt) and once across the Marks column (70.32 pt). The second is
# short, so it posed as a fraction bar and folded the mark digits of adjacent rows into
# "1/2" tokens, emptying the marks column. A table rule is recognised by SHARING ITS Y with
# the full-width rule of the same row, which needs no assumption about column widths.
FRAC_BAR_MIN_W = 4.0
FRAC_BAR_MAX_W = 60.0
ROW_RULE_MIN_W = 100.0  # must match row_rules(); a rule this wide brackets a criteria row

# Page furniture. This must be filtered out of the CRITERIA scan as well as the answer
# text: "Page 18 of 23" puts a 23 in the marks column, which is where 2022 Maths Q35
# picked up a phantom 23-mark part.
RUNNING = re.compile(r"^\s*(NESA\b|Page \d+ of \d+|\u2013 \d+ \u2013)", re.I)

# The criteria table ends at the official answer, which is headed either "Sample answer"
# or "Answers could include" depending on the question. Missing the second spelling lets
# the marks scan run on into the answer body and the page footer.
ANSWER_HEAD = re.compile(r"^\s*(Sample answer|Answers? could include)\b:?\s*", re.I)

# A criteria row's mark is either a single number or a band range ("9-10", "1-2").
# Ranges are used for extended-response questions; the part's maximum is the top of the
# highest band. Note the text layer can split a range across two words on the same line
# ("9-1" + "0"), which is why the marks column is joined per line before parsing.
MARK_VALUE = re.compile(r"^(\d+)(?:\s*[\u2013\u2212-]\s*(\d+))?$")

# The criteria bullet glyph has no Unicode mapping in these PDFs and extracts as U+FFFD
# (or, in some years, a literal bullet). It is layout, not wording -- strip it so a
# descriptor authored from a criteria row does not inherit a replacement character.
BULLET = re.compile("[\ufffd\u2022\u25cf\u25aa\uf0b7]" + r"\s*")


# Reassembling a line left-to-right can leave a space in front of punctuation, because the
# piece that now sits before the comma used to sit after it -- "as 20/40 , or equivalent".
# That is an artefact of the reassembly, never NESA's typesetting, and it also trips the
# damage heuristics that read these rows downstream.
TIGHTEN_PUNCT = re.compile(r"\s+([,.;:])")


def tidy(text):
    """Collapse whitespace and pull punctuation back onto the word before it."""
    return TIGHTEN_PUNCT.sub(r"\1", re.sub(r"\s+", " ", text)).strip()


def is_guidelines(name):
    """True for a marking-guidelines PDF, mirroring build_answer_key.find_papers().

    Filenames are not consistent across subjects: Maths Standard 2, Multimedia and
    VET use `{year}-hsc-...-mg.pdf`, while Maths Advanced uses
    `{year}_marking_guidelines.pdf`. An `-mg.pdf$` test alone matches only the
    former and exits "no marking-guideline PDFs" on the latter.

    `feedback` is tested FIRST and excluded: the marking-centre notes are a third
    PDF per year in some folders, named either `{year}_marking_feedback.pdf` or
    `{year} ... HSC Marking Feedback.pdf` -- both of which contain "marking" and
    would otherwise be parsed as guidelines.
    """
    lowered = name.lower()
    if "feedback" in lowered:
        return False
    return bool(re.search(r"-mg\b|marking", lowered))


def frac_bars(page):
    """The page's stacked-fraction bars: short horizontal rules that are NOT table rules.

    On 2020 Maths Advanced p4 the bar of 20/40 is a 13.97 pt rect at x 360.3-374.3, sitting
    exactly over its two digits. The trap is the Marks column's row rule at 70.32 pt --
    also short, and it fooled the first version of this function. Both cells of a ruled row
    are drawn at the SAME y, so a short rule level with a full-width one is a table rule and
    is dropped. See FRAC_BAR_MAX_W.
    """
    short, wide = [], []
    for drawing in page.get_drawings():
        for item in drawing["items"]:
            if item[0] == "l":
                a, b = item[1], item[2]
                if abs(a.y - b.y) >= 0.6:
                    continue
                y, w, x0, x1 = a.y, abs(a.x - b.x), min(a.x, b.x), max(a.x, b.x)
            elif item[0] == "re" and item[1].height < 1.5:
                r = item[1]
                y, w, x0, x1 = r.y0, r.width, r.x0, r.x1
            else:
                continue
            if w > ROW_RULE_MIN_W:
                wide.append(y)
            elif FRAC_BAR_MIN_W < w <= FRAC_BAR_MAX_W:
                short.append((y, x0, x1))
    return sorted(b for b in short if not any(abs(b[0] - y) < 1.5 for y in wide))


def assemble_fractions(words, bars, body_h):
    """Fold each stacked fraction into ONE token, `num/den`, sitting on its own bar.

    A stacked fraction is the one damage shape that no line-grouping rule can fix, because
    its numerator genuinely IS above the line and its denominator genuinely IS below it --
    see 2020 Maths Advanced Q14(c), where "as 20/40," extracted as a leading "20", the
    sentence, then a stranded "40" ("20 Obtains the probability ... as , or equivalent 40
    merit"). Reading order cannot be recovered from the glyph boxes alone; it comes from
    the bar the page draws between them.

    Tokens are claimed at most once, so a nested fraction's inner bar (processed first,
    bars being sorted top-down) keeps its own digits.
    """
    words = list(words)
    for by, bx0, bx1 in bars:
        near = [w for w in words
                if w[0] >= bx0 - 2 and w[2] <= bx1 + 2
                and abs((w[1] + w[3]) / 2 - by) <= 0.9 * body_h]
        num = sorted((w for w in near if (w[1] + w[3]) / 2 < by), key=lambda w: w[0])
        den = sorted((w for w in near if (w[1] + w[3]) / 2 > by), key=lambda w: w[0])
        if not num or not den:
            continue          # a rule that is not a fraction bar (a box edge, an underline)
        # A real bar is drawn to the width of what it divides. Requiring the digits to
        # span most of it rejects a rule that merely happens to have text above and below.
        span = max(w[2] for w in num + den) - min(w[0] for w in num + den)
        if span < 0.4 * (bx1 - bx0):
            continue
        text = "".join(w[4] for w in num) + "/" + "".join(w[4] for w in den)
        for w in num + den:
            words.remove(w)
        words.append((bx0, by - body_h / 2, bx1, by + body_h / 2, text))
    return words


def join_split_words(toks):
    """Rejoin a word the text layer split mid-way, e.g. "studyin"+"g", "equiv"+"alent".

    These are span boundaries, not spaces: get_text("words") splits on whitespace, so two
    tokens whose boxes touch had no space between them. Real word gaps on these pages are
    ~3 pt, so the 0.2 pt threshold cannot swallow one.
    """
    out = []
    for t in toks:
        if out and 0 <= t[0] - out[-1][2] <= 0.2:
            p = out[-1]
            out[-1] = (p[0], min(p[1], t[1]), t[2], max(p[3], t[3]), p[4] + t[4])
        else:
            out.append(t)
    return out


def page_lines(page):
    """Group a page's words into visual lines, each sorted LEFT TO RIGHT.

    ⚠️ Lines are grouped by vertical CENTRE, not by top-y. Keying on `round(y0, 1)` (what
    this did until 2026-09-05) makes every inline superscript its own "line", and since
    the lines are then emitted in y order the fragment is hoisted in front of the sentence
    it belongs inside: 2020 Maths Advanced Q13 read "sec2 Finds the anti-derivative of x"
    for "Finds the anti-derivative of sec2 x". The two share a centre to within 0.7 pt
    while their tops differ by 2.0 pt, which is exactly why the centre is the right key.

    The tolerance is 0.6 x the page's own median glyph height. Consecutive real lines on
    these pages are ~22 pt apart with ~12 pt glyphs, so they never overlap and cannot be
    merged. An odd-height token (a tall integral sign, a bracket spanning three lines)
    attaches to the nearest line but NEVER becomes the line's anchor, so it cannot chain
    two lines together.
    """
    words = [w for w in page.get_text("words") if w[4].strip()]
    if not words:
        return []
    heights = sorted(w[3] - w[1] for w in words)
    body_h = heights[len(heights) // 2] or 12.0
    words = assemble_fractions(words, frac_bars(page), body_h)

    # ⚠️ An IMAGE's label is reported with the image's own box, not a glyph box, so it is
    # enormous and its centre is meaningless -- 2020 Maths Advanced p5 has "solution"
    # /"diagram" 138 pt tall (11x body), centred on the NEXT question's first criteria row,
    # and 2020 Standard 2 p2 has "spanning"/"trees" 313 pt tall starting at y = -79.9, off
    # the top of the page. Grouping either by centre files NESA's picture caption inside a
    # criteria row, which is then shown to a student as band wording. Measured over all 23
    # guideline PDFs, > 5x body height selects exactly these 63 tokens and nothing else
    # (real oversize tops out at 4.7x, on the mapping-grid page this parser discards).
    # They are kept -- "solution diagram" tells a reviewer the official answer has a
    # picture -- but as their own line, ordered by their TOP, which is where they visually
    # begin and which is the block they belong to.
    oversize = [w for w in words if (w[3] - w[1]) > 5 * body_h]
    words = [w for w in words if (w[3] - w[1]) <= 5 * body_h]

    normal = lambda w: 0.6 * body_h <= (w[3] - w[1]) <= 1.4 * body_h
    lines = []          # [anchor-centre, anchored?, [tokens]]
    for w in sorted(words, key=lambda w: ((w[1] + w[3]) / 2, w[0])):
        yc = (w[1] + w[3]) / 2
        if lines and abs(yc - lines[-1][0]) <= 0.6 * body_h:
            lines[-1][2].append(w)
            if normal(w) and not lines[-1][1]:
                lines[-1][0], lines[-1][1] = yc, True
        else:
            lines.append([yc, normal(w), [w]])
    out = [(anchor, join_split_words(sorted(toks, key=lambda t: t[0])))
           for anchor, _anchored, toks in lines]
    for w in oversize:
        out.append((w[1], [w]))
    return [(round(y, 1), toks) for y, toks in sorted(out, key=lambda r: r[0])]


def marks_cell(toks, gap=15.0):
    """The line's Marks-column text: the RIGHTMOST cluster of tokens past MARKS_COL_MIN_X.

    Not simply everything past the boundary. A criteria sentence can wrap so that its
    last word spills over it while the real mark sits further right -- 2021 VET Q20's
    fifth band ends "...something to do with a" at x 441.9-447.9 with its "1-3" at
    x 479.1, and joining the two yields "a1-3", which MARK_VALUE rejects. The mark was
    then lost and, because criteria_rows() drops a bandless row, that band vanished
    from the criteria table entirely (the part's own `marks` survived only because it
    is a max() over the other bands).

    Clustering on a gap keeps the case the join exists for: a range split across two
    words on the same line ("9-1" + "0") is contiguous, so it stays in one cluster.

    Returns (text, tokens) so the caller can define the criteria wording by EXCLUSION --
    a wrapped sentence's last word must stay in the wording, not be dropped with the mark.
    """
    right = sorted((t for t in toks if t[0] > MARKS_COL_MIN_X), key=lambda t: t[0])
    if not right:
        return "", []
    cluster = [right[-1]]
    for tok in reversed(right[:-1]):
        if cluster[0][0] - tok[2] > gap:
            break
        cluster.insert(0, tok)
    return "".join(t[4] for t in cluster).strip(), cluster


def row_rules(page):
    """Y positions of the criteria table's own horizontal rules on this page.

    Mirrors build_mapping_grid.row_rules(). The width test (> 100 pt) keeps cell-border
    stubs and the page's header/footer hairlines from inventing bands; those two rules do
    appear, but they sit outside every criteria block and so bracket nothing.
    """
    ys = []
    for drawing in page.get_drawings():
        for item in drawing["items"]:
            if item[0] == "l":
                a, b = item[1], item[2]
                if abs(a.y - b.y) < 0.6 and abs(a.x - b.x) > 100:
                    ys.append(a.y)
            elif item[0] == "re":
                r = item[1]
                if r.height < 1.5 and r.width > 100:
                    ys.append(r.y0)
    ys.sort()
    merged = []
    for y in ys:
        if not merged or y - merged[-1] > 1.5:
            merged.append(y)
    return merged


def band_of(y, rules):
    """Index of the ruled band containing y, or None when the rules do not bracket it."""
    if len(rules) < 3 or y < rules[0] or y > rules[-1]:
        return None
    lo, hi = 0, len(rules) - 1
    while lo < hi - 1:
        mid = (lo + hi) // 2
        if rules[mid] <= y:
            lo = mid
        else:
            hi = mid
    return lo


def criteria_rows(lines):
    """Collapse scanned criteria lines into official rows: [{marks, text}], top band first.

    `lines` is [(page-index, y, ruled-band-index or None, criteria-text, mark or None)] in
    page order. Lines sharing a (page, band) are one row. A line the rules do not bracket
    stands alone, so an unruled table degrades to one row per mark-bearing line rather
    than merging rows that were never merged.
    """
    groups, order = {}, []
    for i, (pi, _y, band, text, mark) in enumerate(lines):
        key = (pi, band) if band is not None else ("solo", i)
        if key not in groups:
            groups[key] = {"text": [], "marks": None}
            order.append(key)
        if text:
            groups[key]["text"].append(text)
        if mark is not None and groups[key]["marks"] is None:
            groups[key]["marks"] = mark
    rows = []
    for key in order:
        g = groups[key]
        text = tidy(" ".join(g["text"]))
        text = BULLET.sub("", text).strip()
        if g["marks"] is None or not text:
            continue          # the "Criteria / Marks" header band, and any empty spacer
        rows.append({"marks": g["marks"], "text": text})
    return rows


def parse_paper(pdf_path):
    """Return ([{question, part, marks, sampleAnswer, criteria}], [unresolved-labels])."""
    doc = fitz.open(pdf_path)
    rows, rules = [], {}
    for pi in range(doc.page_count):
        rules[pi] = row_rules(doc[pi])
        for y, toks in page_lines(doc[pi]):
            rows.append((pi, y, toks))

    # Locate question headers: "Question 16", "Question 16 (a)", "Question 16 (a) (i)".
    headers = []
    for i, (pi, y, toks) in enumerate(rows):
        if toks[0][4] != "Question" or toks[0][0] >= HEADER_MAX_X:
            continue
        if len(toks) < 2 or not re.fullmatch(r"\d+", toks[1][4]):
            continue  # "Question Answer" key table, "Question Marks Content ..." grid
        parts = []
        for t in toks[2:]:
            m = re.fullmatch(r"\(([a-z]+|[ivx]+)\)", t[4])
            if not m:
                break
            parts.append(m.group(1))
        headers.append((i, int(toks[1][4]), parts))

    out, unresolved = [], []
    for n, (idx, qnum, parts) in enumerate(headers):
        end = headers[n + 1][0] if n + 1 < len(headers) else len(rows)
        marks, sample, in_sample = [], [], False
        crit_lines = []
        for j in range(idx + 1, end):
            pi, y, toks = rows[j]
            text = " ".join(t[4] for t in toks)
            if RUNNING.match(text):
                continue
            if not in_sample and ANSWER_HEAD.match(text):
                in_sample = True
                rest = ANSWER_HEAD.sub("", text).strip()
                if rest:
                    sample.append(rest)
                continue
            if in_sample:
                sample.append(text)
                continue
            # Criteria row: join the marks column left-to-right before parsing, so a
            # range split across two words ("9-1" + "0") reads as one value.
            col, cell_toks = marks_cell(toks)
            m = MARK_VALUE.match(col)
            value = int(m.group(2) or m.group(1)) if m else None
            if m:
                marks.append(value)
            # The row's WORDING is every token that is NOT in the marks cell, collected
            # with the line's ruled band so criteria_rows() can rejoin a row split over
            # 2-3 lines. Defined by exclusion rather than by the x threshold so a
            # criteria sentence that wraps past MARKS_COL_MIN_X keeps its last word.
            crit_lines.append((pi, y, band_of(y, rules[pi]),
                               " ".join(t[4] for t in toks if t not in cell_toks).strip(),
                               value))

        label = "Q%d%s" % (qnum, "".join("(%s)" % p for p in parts))
        if not marks:
            unresolved.append(label)
            continue
        out.append({
            "question": qnum,
            "part": ".".join(parts) if parts else None,
            "marks": max(marks),
            "sampleAnswer": tidy(" ".join(sample)),
            "criteria": criteria_rows(crit_lines),
        })
    return out, unresolved


def build_subject(subject_id, dry_run=False):
    folder = os.path.join(NESA, SUBJECTS[subject_id])
    if not os.path.isdir(folder):
        sys.exit("NESA folder not found (not in the repo, by copyright): " + folder)

    pdfs = sorted(p for p in glob.glob(os.path.join(folder, "*.pdf"))
                  if is_guidelines(os.path.basename(p)))
    if not pdfs:
        sys.exit("no marking-guideline PDFs in " + folder)

    papers, total_parts = {}, 0
    for pdf in pdfs:
        name = os.path.basename(pdf)
        m = re.match(r"(\d{4})", name)
        if not m:
            print("  SKIP (no year in filename): " + name, file=sys.stderr)
            continue
        year = m.group(1)
        parts, unresolved = parse_paper(pdf)
        if not parts:
            print("  NOT WRITTEN %s: no question parts parsed from %s" % (year, name), file=sys.stderr)
            continue
        for label in unresolved:
            print("  UNRESOLVED %s %s: no mark found in its criteria table" % (year, label),
                  file=sys.stderr)
        papers[year] = parts
        total_parts += len(parts)
        print("  %s: %3d parts, %3d marks  (%s)"
              % (year, len(parts), sum(p["marks"] for p in parts), name))

    data = {
        "subject": subject_id,
        "source": "NESA HSC marking guidelines (not in repo - copyright)",
        "note": ("Official maximum marks per question part, plus the official sample answer "
                 "and criteria rows for reference. Marks are enforced by "
                 "scripts/check_written_key.cjs; sample answers and criteria are not - prose "
                 "cannot be compared for equality. The criteria rows are the ground truth a "
                 "question's bandDescriptors are authored from. "
                 "Regenerate with scripts/build_written_key.py; never hand-edit."),
        "papers": papers,
    }
    out_path = os.path.join(OUT_DIR, subject_id + ".json")
    print("  => %d parts across %d papers -> %s" % (total_parts, len(papers), out_path))
    if dry_run:
        print("  dry run - nothing written")
        return
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("subject", help="subject id, or the word all")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    targets = list(SUBJECTS) if args.subject == "all" else [args.subject]
    for sid in targets:
        if sid not in SUBJECTS:
            sys.exit("unknown subject '%s'. Known: %s" % (sid, ", ".join(SUBJECTS)))
        print(sid + ":")
        build_subject(sid, args.dry_run)


if __name__ == "__main__":
    main()
