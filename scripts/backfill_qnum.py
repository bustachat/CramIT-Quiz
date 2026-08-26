#!/usr/bin/env python3
"""
Propose (and optionally write) the `qNum` field on original MC questions by
matching them against the NESA exam paper.

WHY THIS EXISTS
---------------
`scripts/check_answer_key.cjs` can only check a question that says which exam
question it is. Getting that mapping wrong is worse than not having it: the
check then compares a question against some *other* question's official answer
and reports a confident false pass. Several earlier attempts at this mapping
used similarity scores and produced a different answer every run -- see
docs/HISTORY.md, 2026-08-26 and 2026-08-27.

So this script does not score anything. A question is matched only when all
four of its options are character-for-character identical to a paper question's
options after normalisation, and that paper question matches nothing else.
Everything it cannot resolve that way is printed for a human to confirm against
the rendered page, never guessed.

Two facts that make the naive approaches fail, both load-bearing:

1. **Array position is not the question number.** `multimedia.json` 2022 stores
   its ten questions in the order 1, 3, 4, 5, 6, 8, 9, 10, 7, 2.
2. **A linear read of the PDF text mis-associates questions.** NESA sets the
   question number in its own left-margin text column (x ~= 70) with the stem
   and options indented (x ~= 99 / 127), so `get_text()` emits every number on
   a page before any of the body text. This script reads by (page, y) instead.

USAGE
-----
    python scripts/backfill_qnum.py multimedia            # report only
    python scripts/backfill_qnum.py multimedia --write    # write exact matches

Requires PyMuPDF (`pip install pymupdf`) and the NESA papers at NESA_ROOT.
The papers are not in the repo (copyright), so CI can never run this -- the
`qNum` values it produces are committed, exactly like data/answer-key/.
"""

from __future__ import annotations

import io
import json
import os
import re
import sys
import unicodedata

try:
    import fitz  # PyMuPDF
except ImportError:
    sys.exit("PyMuPDF is required:  pip install pymupdf")

NESA_ROOT = r"C:\Claude Code Space\CRAMIT QUIZ Code Folder\NESA Exams Folder"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# subject id -> (folder under NESA_ROOT, multiple-choice questions per paper)
SUBJECTS = {
    "mathematics-standard-2": ("Maths Standard 2", 15),
    "multimedia": ("Industrial Technology - Multimedia", 10),
    "vet-construction": ("VET - Construction", 15),
}

NUM_X_MAX = 92.0   # left-margin column holding the question number
Y_TOL = 3.0        # points; lines within this are the same visual row
OPT_RE = re.compile(r"^([A-D])\.$")

# Page furniture that sits below the last option on a page and would otherwise
# be swallowed into that question's option D. Kept deliberately narrow --
# a bare 4-digit rule would have eaten VET 2024 Q11's option "2900".
FURNITURE_RE = re.compile(
    r"^(?:[\u2013\u2014-]\s*\d{1,3}\s*[\u2013\u2014-]|\u00a9.*|BLANK PAGE)$", re.I
)


def norm(text: str) -> str:
    """Lowercase, strip markup, punctuation and spacing; unify dashes/quotes."""
    text = unicodedata.normalize("NFKD", text or "")
    text = re.sub(r"<[^>]+>", " ", text)
    for a, b in [("\u2013", "-"), ("\u2014", "-"), ("\u2018", "'"),
                 ("\u2019", "'"), ("\u201c", '"'), ("\u201d", '"'),
                 ("\u00d7", "x"), ("\u00a0", " ")]:
        text = text.replace(a, b)
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def visual_rows(page):
    """Text lines grouped into visual rows, ordered top-to-bottom."""
    items = []
    for block in page.get_text("dict")["blocks"]:
        if block["type"] != 0:
            continue
        for line in block["lines"]:
            text = "".join(span["text"] for span in line["spans"]).strip()
            if text and not FURNITURE_RE.match(text):
                items.append((round(line["bbox"][1], 1), round(line["bbox"][0], 1), text))
    items.sort(key=lambda t: (t[0], t[1]))

    rows: list[tuple[float, list[tuple[float, str]]]] = []
    for y, x, text in items:
        if rows and abs(y - rows[-1][0]) <= Y_TOL:
            rows[-1][1].append((x, text))
        else:
            rows.append((y, [(x, text)]))
    for _, cells in rows:
        cells.sort()
    return rows


def read_section_one(pdf_path: str, mc_count: int) -> dict[int, dict]:
    """{question number: {'page', 'stem', 'options'}} for Section I."""
    doc = fitz.open(pdf_path)
    questions: dict[int, dict] = {}
    current = current_option = None
    started = False

    for pageno in range(doc.page_count):
        for _, cells in visual_rows(doc[pageno]):
            first_x, first_text = cells[0]
            joined = " ".join(t for _, t in cells).strip()

            if started and re.match(r"^Section II\b", joined):
                return finalise(questions)

            if first_x <= NUM_X_MAX and re.fullmatch(r"\d{1,2}", first_text):
                number = int(first_text)
                if 1 <= number <= mc_count and number not in questions:
                    started, current, current_option = True, number, None
                    rest = [t for _, t in cells[1:]]
                    questions[number] = {"page": pageno + 1,
                                         "stem": [" ".join(rest)] if rest else [],
                                         "options": {}}
                    continue

            if current is None:
                continue

            marker = OPT_RE.match(first_text)
            if marker:
                current_option = marker.group(1)
                questions[current]["options"][current_option] = [
                    " ".join(t for _, t in cells[1:])
                ]
            elif current_option:
                questions[current]["options"][current_option].append(joined)
            else:
                questions[current]["stem"].append(joined)

    return finalise(questions)


def finalise(questions):
    return {
        n: {
            "page": d["page"],
            "stem": " ".join(p.strip() for p in d["stem"] if p.strip()),
            "options": {k: " ".join(p.strip() for p in v if p.strip())
                        for k, v in d["options"].items()},
        }
        for n, d in questions.items()
    }


def papers_by_year(folder: str) -> dict[int, str]:
    """year -> exam paper filename (marking guidelines and feedback excluded)."""
    directory = os.path.join(NESA_ROOT, folder)
    if not os.path.isdir(directory):
        sys.exit(f"No such folder: {directory}")
    found = {}
    for name in sorted(os.listdir(directory)):
        lowered = name.lower()
        if not lowered.endswith(".pdf"):
            continue
        if "feedback" in lowered or re.search(r"-mg\b|marking", lowered):
            continue
        year = re.match(r"(20\d{2})", name)
        if year:
            found[int(year.group(1))] = name
    return found


def flat(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text or "")).strip()


def write_qnum(subject_id: str, assignments: dict[int, int]) -> None:
    """Insert "qNum" after each mcQuestions "year" line, in place.

    Line-level edit rather than json.dump: these files are 180-220 KB and a
    reserialise rewrites every line, burying the change in the diff.
    """
    path = os.path.join(REPO_ROOT, "subjects", f"{subject_id}.json")
    with io.open(path, encoding="utf-8") as handle:
        original = json.load(handle)
    questions = original["mcQuestions"]
    if any("qNum" in q for q in questions):
        sys.exit(f"{subject_id}: some questions already carry qNum -- refusing to rewrite")
    if len(assignments) != len(questions):
        sys.exit(f"{subject_id}: {len(assignments)} of {len(questions)} resolved; "
                 "--write needs all of them (resolve the rest by hand first)")

    raw = io.open(path, encoding="utf-8", newline="").read()
    newline = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.replace("\r\n", "\n").split("\n")

    start = next(i for i, l in enumerate(lines) if l == '  "mcQuestions": [')
    end = next(i for i, l in enumerate(lines) if i > start and l in ("  ],", "  ]"))
    year_line = re.compile(r'^      "year": (\d{4}),$')
    hits = [i for i in range(start, end) if year_line.match(lines[i])]
    if len(hits) != len(questions):
        sys.exit(f"{subject_id}: found {len(hits)} year lines for {len(questions)} questions")

    out, k = [], 0
    for i, line in enumerate(lines):
        out.append(line)
        if k < len(hits) and i == hits[k]:
            out.append('      "qNum": %d,' % assignments[k])
            k += 1
    io.open(path, "w", encoding="utf-8", newline="").write(newline.join(out))

    updated = json.load(io.open(path, encoding="utf-8"))
    for after, before in zip(updated["mcQuestions"], questions):
        assert {k2: v for k2, v in after.items() if k2 != "qNum"} == before
    print(f"  wrote qNum on {len(questions)} questions in subjects/{subject_id}.json")


def run(subject_id: str, do_write: bool) -> None:
    folder, mc_count = SUBJECTS[subject_id]
    bank = json.load(io.open(os.path.join(REPO_ROOT, "subjects", f"{subject_id}.json"),
                             encoding="utf-8"))["mcQuestions"]
    papers = papers_by_year(folder)

    assignments: dict[int, int] = {}
    unresolved: list[tuple[int, int]] = []

    print(f"=== {subject_id}")
    for year in sorted(papers):
        parsed = read_section_one(os.path.join(NESA_ROOT, folder, papers[year]), mc_count)
        indices = [i for i, q in enumerate(bank) if q["year"] == year and not q.get("variant")]

        # a paper question is a candidate only if its own option set is unique
        by_options: dict[tuple, list[int]] = {}
        for number, data in parsed.items():
            if len(data["options"]) == 4:
                key = tuple(norm(data["options"][L]) for L in "ABCD")
                by_options.setdefault(key, []).append(number)

        pending = []
        for index in indices:
            key = tuple(norm(o) for o in bank[index]["options"])
            hits = by_options.get(key, [])
            if len(hits) == 1:
                assignments[index] = hits[0]
            else:
                pending.append(index)

        taken = {assignments[i] for i in indices if i in assignments}
        if len(taken) != len([i for i in indices if i in assignments]):
            sys.exit(f"{year}: two questions matched the same qNum -- aborting")
        free = [n for n in range(1, mc_count + 1) if n not in taken]
        unresolved.extend((index, year) for index in pending)

        print(f"  {year}: parsed {len(parsed)}/{mc_count}, "
              f"matched {len(taken)}, unresolved {len(pending)}")

        for index in pending:
            question = bank[index]
            print(f"    UNRESOLVED bank[{index}] {flat(question['q'])[:78]}")
            for letter, option in zip("ABCD", question["options"]):
                print(f"        {letter}. {flat(option)[:66]}")
            print(f"      free question numbers this year: {free}")
            for number in free:
                data = parsed[number]
                print(f"        paper Q{number} (p{data['page']}): {flat(data['stem'])[:66]}")

    total = len(bank)
    print(f"  -> {len(assignments)}/{total} resolved by exact option match, "
          f"{len(unresolved)} need a human")
    if unresolved:
        print("     Render those pages and read them; do not guess. "
              "A wrong qNum is worse than no qNum.")

    if do_write:
        write_qnum(subject_id, assignments)


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    do_write = "--write" in sys.argv[1:]
    wanted = args or list(SUBJECTS)
    unknown = [s for s in wanted if s not in SUBJECTS]
    if unknown:
        sys.exit(f"Unknown subject(s): {unknown}. Known: {list(SUBJECTS)}")
    for subject_id in wanted:
        run(subject_id, do_write)


if __name__ == "__main__":
    main()
