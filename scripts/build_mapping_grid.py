"""Extract NESA's official question -> syllabus-code mapping grid from marking guidelines.

Third member of the ground-truth family, alongside `build_answer_key.py` (Section I answers)
and `build_written_key.py` (written marks + sample answers). Every NESA marking guideline ends
with a **Mapping Grid**: one row per question part giving its marks, its syllabus content code
and its outcome code. That is the official answer to "what topic is this question?" -- so a
port's `category` field can be *derived* rather than guessed.

Why this matters
----------------
CLAUDE.md SS10 and the porting playbook both record the failure this prevents: topic lists
built by keyword-matching a question bank, or by eyeballing a paper, have been wrong twice
(Multimedia, then VET). The grid is NESA's own answer and it is machine-readable.

It is *not* a substitute for reading the syllabus (playbook Stage 2). The grid reflects what
was **examined**, not the syllabus's **scope** -- for Mathematics Advanced the two diverge
sharply: MA-C1 is 10.6% of the syllabus's content dot points and 1.3% of six years' examined
marks, while MA-T3 is 1.7% of scope and 6.8% of marks. Use the grid for per-question
`category`; use the syllabus for topic weighting.

Two extraction traps, both of which cost a wrong number before being found
-------------------------------------------------------------------------
1. **The code can be split across words.** The text layer emits `MA- M1` and `MA- T1` in the
   2023 grid. A `MA-([A-Z]\\d)` regex misses those silently -- same family as the `9-1` + `0`
   mark-range split already documented for `build_written_key.py`.
2. **A row's cell text is vertically centred, so it can start ABOVE its own label line.**
   Reading forward from the label attributes that text to the previous row. Each row's span is
   therefore taken as *(end of the previous label's line, start of the next label's line)*,
   not *(this label, next label)*.

Reconciliation
--------------
Every paper's grid must total the exam's own front-page mark total (100 for Mathematics
Advanced). All six papers 2020-2025 do, with zero rows left uncoded. If a paper does not
reconcile, the output is wrong -- do not use it.

Usage
-----
    python scripts/build_mapping_grid.py <subject-id> [--dry-run]

Needs the local NESA PDFs, which are not in the repo (copyright), so CI can never regenerate
this -- which is exactly why the generated file is committed.
"""

import argparse
import json
import os
import re
import sys

import fitz  # PyMuPDF

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NESA = r"C:\Claude Code Space\CRAMIT QUIZ Code Folder\NESA Exams Folder"
OUT_DIR = os.path.join(REPO, "data", "mapping-grid")

# subject id -> (NESA folder, expected marks per paper from the exam's front page)
#
# Only subjects whose grid states a syllabus CODE are listed. Multimedia and VET Construction
# both have a Mapping Grid, but their Content column carries prose topic names rather than
# codes -- useful, but a different parse, and not what `category` needs.
SUBJECTS = {
    "mathematics-advanced": ("Maths Advanced", 100),
    "mathematics-standard-2": ("Maths Standard 2", 100),
}

LABEL = re.compile(r"^\d{1,2}$")
PART = re.compile(r"\([a-z]+\)|\([ivx]+\)")

# A CONTENT code is two letters, a hyphen, a letter and a digit: MA-C3, MS-F4.
# Tolerates "MA-M1", "MA- M1" and "MA-M 1" -- the text layer splits it all three ways.
CODE = re.compile(r"\b([A-Z]{2})-\s?([A-Z])\s?(\d)\b")
# An OUTCOME code always has digits before the hyphen, which is what separates the two
# shapes cleanly: MA11-1, MA12-10, MS11-4, MS2-12-5.
OUTCOME = re.compile(r"\b([A-Z]{2}\d+-\d{1,2}(?:-\d{1,2})?)\b")

# NESA typos in the source grids, normalised explicitly rather than silently tolerated by a
# loose regex. Each entry is a single occurrence verified against the PDF by eye; a new one
# must be added deliberately, and `build` prints every substitution it makes.
SOURCE_TYPOS = {
    # 2020 Mathematics Standard 2, Q22: written "MS2-F4", which is an outcome prefix with a
    # content suffix. Every other row in six years uses "MS-F4". Q21 directly above it, same
    # topic and same outcome (MS2-12-5), is spelled correctly.
    "MS2-F4": "MS-F4",
}

FURNITURE = re.compile(r"^\s*(NESA\b|Page \d+ of \d+|\d{4} HSC)")
LABEL_MAX_X = 160   # the question column sits in the left margin of the grid


def page_lines(page):
    """Group a page's words into lines keyed by rounded y, each sorted left to right."""
    lines = {}
    for w in page.get_text("words"):
        if w[4].strip():
            lines.setdefault(round(w[1], 1), []).append(w)
    return [(y, sorted(toks, key=lambda t: t[0])) for y, toks in sorted(lines.items())]


def row_rules(page):
    """Y positions of the grid's own horizontal rules, across the Content column.

    The grid is a real ruled table, so its row boundaries are drawn on the page. Using them
    is exact, where inferring a row's extent from the label lines above and below it is not:
    a cell holding two or three codes is vertically CENTRED, so its first line starts above
    its own label line and its last line ends below it. Bracketing by labels therefore leaks
    those lines into the neighbouring rows in BOTH directions -- which is how 2025's 17(b),
    18, 21(a), 27(b), 28(a) and 29(a) each acquired a code NESA never gave them.
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


def parse_grid(pdf_path):
    """Return {question-label: {marks, codes[], outcomes[]}} for one marking-guideline PDF."""
    doc = fitz.open(pdf_path)
    starts = [i for i in range(doc.page_count) if "Mapping Grid" in doc[i].get_text()]
    if not starts:
        return {}, ["no 'Mapping Grid' heading found"]
    pages = [i for i in range(starts[0], doc.page_count) if "-" in doc[i].get_text()
             and CODE.search(doc[i].get_text())]

    rows = []
    for pi in pages:
        for y, toks in page_lines(doc[pi]):
            rows.append((pi, y, toks))

    # Pass 1 -- locate every row label ("11", "14 (a)", "19 (b) (i)") in the left column.
    anchors = []
    for k, (pi, _y, toks) in enumerate(rows):
        words = [t[4] for t in toks]
        if not words or not LABEL.match(words[0]) or toks[0][0] >= LABEL_MAX_X:
            continue
        if FURNITURE.match(" ".join(words)):
            continue
        label, i = words[0], 1
        while i < len(words) and PART.fullmatch(words[i]):
            label += words[i]
            i += 1
        marks = int(words[i]) if i < len(words) and re.fullmatch(r"\d{1,2}", words[i]) else None
        anchors.append((k, pi, label, marks))

    # Pass 2 -- a row owns exactly the lines inside its own ruled band. Falls back to
    # bracketing by neighbouring labels only where a page carries no usable rules.
    rules = {pi: row_rules(doc[pi]) for pi in pages}
    out, problems, fixed = {}, [], []
    for n, (k, pi, label, marks) in enumerate(anchors):
        own = band_of(rows[k][1], rules[pi])
        if own is None:
            lo = anchors[n - 1][0] + 1 if n > 0 and anchors[n - 1][1] == pi else k
            hi = anchors[n + 1][0] if n + 1 < len(anchors) and anchors[n + 1][1] == pi else len(rows)
            span = range(lo, hi)
        else:
            span = range(len(rows))
        codes, outcomes = [], []
        for j in span:
            if rows[j][0] != pi:
                continue
            if own is not None and band_of(rows[j][1], rules[pi]) != own:
                continue
            line = " ".join(t[4] for t in rows[j][2])
            for typo, correct in SOURCE_TYPOS.items():
                if typo in line:
                    line = line.replace(typo, correct)
                    fixed.append("%s: source typo %s -> %s" % (label, typo, correct))
            codes += ["%s-%s%s" % m for m in CODE.findall(line)]
            outcomes += OUTCOME.findall(line)
        entry = out.setdefault(label, {"marks": marks, "codes": [], "outcomes": []})
        if marks is not None and entry["marks"] is None:
            entry["marks"] = marks
        entry["codes"] = sorted(set(entry["codes"] + codes))
        entry["outcomes"] = sorted(set(entry["outcomes"] + outcomes))

    for label, entry in out.items():
        if not entry["codes"]:
            problems.append("%s: no syllabus content code" % label)
        if entry["marks"] is None:
            problems.append("%s: no marks" % label)
    return out, problems, sorted(set(fixed))


def build(subject_id, dry_run=False):
    folder_name, expected_total = SUBJECTS[subject_id]
    folder = os.path.join(NESA, folder_name)
    if not os.path.isdir(folder):
        sys.exit("NESA folder not found (not in the repo, by copyright): " + folder)

    papers, ok = {}, True
    for name in sorted(os.listdir(folder)):
        lowered = name.lower()
        if not lowered.endswith(".pdf") or "feedback" in lowered:
            continue
        if not re.search(r"-mg\b|marking", lowered):
            continue
        year_match = re.match(r"(20\d{2})", name)
        if not year_match:
            print("  SKIP (no year in filename): " + name, file=sys.stderr)
            continue
        year = year_match.group(1)
        grid, problems, fixed = parse_grid(os.path.join(folder, name))
        if not grid:
            print("  NO GRID %s: %s" % (year, "; ".join(problems)), file=sys.stderr)
            continue
        total = sum(e["marks"] or 0 for e in grid.values())
        flag = "OK " if total == expected_total and not problems else "BAD"
        if flag == "BAD":
            ok = False
        print("  %s %s: %3d rows, %3d marks (expected %d)%s"
              % (flag, year, len(grid), total, expected_total,
                 "  << " + "; ".join(problems[:4]) if problems else ""))
        for note in fixed:
            print("       NOTE %s %s" % (year, note))
        papers[year] = grid

    if not ok:
        sys.exit("refusing to write: a paper did not reconcile to its front-page total, "
                 "or a row was left uncoded")

    data = {
        "subject": subject_id,
        "source": "NESA HSC marking guidelines, Mapping Grid (not in repo - copyright)",
        "note": ("Official syllabus content code and outcome code per question part. Use this "
                 "to derive `category` rather than guessing it. It reflects what was EXAMINED, "
                 "not the syllabus's SCOPE - see the module docstring. Regenerate with "
                 "scripts/build_mapping_grid.py; never hand-edit."),
        "papers": papers,
    }
    out_path = os.path.join(OUT_DIR, subject_id + ".json")
    print("  => %d papers -> %s" % (len(papers), out_path))
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
        build(sid, args.dry_run)


if __name__ == "__main__":
    main()
