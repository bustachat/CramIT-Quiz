"""Extract the official WRITTEN-question mark allocations from NESA marking guidelines.

Companion to `build_answer_key.py`, which does the same for Section I multiple choice.
Official marks never change, so they are derived once, committed to
`data/answer-key/written/`, and enforced in CI by `scripts/check_written_key.cjs`.
CI can never regenerate this: the PDFs are not in the repo, by copyright.

What is extracted, and what is not
----------------------------------
For every question part the guidelines define, this records the **maximum mark** and the
official **sample answer** text. Only the mark is machine-checkable and only the mark is
enforced; the sample answer is stored for human reference, because prose cannot be
compared for equality. Storing it is still worthwhile -- it is the source a reviewer
needs when a bank answer looks wrong.

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


def page_lines(page):
    """Group a page's words into lines keyed by rounded y, each sorted left to right."""
    lines = {}
    for w in page.get_text("words"):
        if w[4].strip():
            lines.setdefault(round(w[1], 1), []).append(w)
    return [(y, sorted(toks, key=lambda t: t[0])) for y, toks in sorted(lines.items())]


def parse_paper(pdf_path):
    """Return ([{question, part, marks, sampleAnswer}], [unresolved-labels])."""
    doc = fitz.open(pdf_path)
    rows = []
    for pi in range(doc.page_count):
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
        for j in range(idx + 1, end):
            _, _, toks = rows[j]
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
            col = "".join(t[4] for t in toks if t[0] > MARKS_COL_MIN_X).strip()
            m = MARK_VALUE.match(col)
            if m:
                marks.append(int(m.group(2) or m.group(1)))

        label = "Q%d%s" % (qnum, "".join("(%s)" % p for p in parts))
        if not marks:
            unresolved.append(label)
            continue
        out.append({
            "question": qnum,
            "part": ".".join(parts) if parts else None,
            "marks": max(marks),
            "sampleAnswer": re.sub(r"\s+", " ", " ".join(sample)).strip(),
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
                 "for reference. Marks are enforced by scripts/check_written_key.cjs; sample "
                 "answers are not - prose cannot be compared for equality. "
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
