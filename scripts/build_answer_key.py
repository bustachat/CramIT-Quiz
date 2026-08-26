#!/usr/bin/env python3
"""
Build the official HSC answer-key database from NESA marking guideline PDFs.

WHY THIS EXISTS
---------------
Official HSC answers never change. Re-deriving them by reading a PDF (by hand or
by model) every time we want to check the question bank has produced a different
answer each time it was attempted -- see docs/HISTORY.md, 2026-08-26. So we
derive them ONCE, commit the result, and let CI enforce it forever after.

The NESA PDFs are NOT in the repo (copyright), so CI cannot re-run this script.
That is deliberate: the generated JSON is the committed artefact, and
scripts/check_answer_key.cjs compares the question bank against it with no PDF
access at all.

SOURCE OF TRUTH
---------------
Page 1 of every "* Marking Guidelines" PDF carries a "Multiple-choice Answer Key"
table: a question number and a letter, one per line. That table is the only thing
this script reads. It does not parse exam papers, question text, or options --
those text layers are unreliable (some pages are re-typeset or garbled) and are
handled separately.

USAGE
-----
    python scripts/build_answer_key.py                     # all configured subjects
    python scripts/build_answer_key.py mathematics-standard-2

Requires PyMuPDF (`pip install pymupdf`) and the NESA papers at NESA_ROOT below.
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone

try:
    import fitz  # PyMuPDF
except ImportError:
    sys.exit("PyMuPDF is required:  pip install pymupdf")

NESA_ROOT = r"C:\Claude Code Space\CRAMIT QUIZ Code Folder\NESA Exams Folder"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(REPO_ROOT, "data", "answer-key")

# subject id (matches subjects/{id}.json) -> where its papers live and how many
# multiple-choice questions each paper is expected to have.
SUBJECTS = {
    "mathematics-standard-2": {
        "name": "Mathematics Standard 2",
        "folder": "Maths Standard 2",
        "mc_count": 15,
    },
    "multimedia": {
        "name": "Industrial Technology - Multimedia",
        "folder": "Industrial Technology - Multimedia",
        "mc_count": 10,
    },
    "vet-construction": {
        "name": "VET Construction",
        "folder": "VET - Construction",
        "mc_count": 15,
    },
}

# "17" then "B", each alone on its line. Multimedia/Construction papers up to
# 2023 interleave a whitespace-only line between the two (" \n \nC \n") where
# 2024-25 and every Maths paper do not (" \nC \n"). Both shapes must parse --
# without the blank-line tolerance, three of the eleven papers yield no answers
# at all.
ANSWER_ROW = re.compile(
    r"^[ \t]*(\d{1,2})[ \t]*\n(?:[ \t]*\n)*[ \t]*([A-D])[ \t]*$", re.MULTILINE
)


def extract_mc_key(pdf_path: str) -> dict[int, str]:
    """Return {question_number: letter} from the answer key on page 1."""
    page1 = fitz.open(pdf_path)[0].get_text()
    marker = re.search(r"Answer Key(.*?)(?:Section II|\Z)", page1, re.S)
    segment = marker.group(1) if marker else page1
    return {int(num): letter for num, letter in ANSWER_ROW.findall(segment)}


def find_papers(folder: str) -> dict[int, dict[str, str]]:
    """Map year -> {'mg': marking guidelines, 'paper': exam paper} by filename."""
    directory = os.path.join(NESA_ROOT, folder)
    if not os.path.isdir(directory):
        sys.exit(f"No such folder: {directory}")

    papers: dict[int, dict[str, str]] = {}
    for name in sorted(os.listdir(directory)):
        if not name.lower().endswith(".pdf"):
            continue
        year_match = re.match(r"(20\d{2})", name)
        if not year_match:
            continue
        year = int(year_match.group(1))
        entry = papers.setdefault(year, {})
        lowered = name.lower()
        if "feedback" in lowered:
            entry["feedback"] = name
        elif re.search(r"-mg\b|marking", lowered):
            entry["mg"] = name
        else:
            entry["paper"] = name
    return papers


def build(subject_id: str) -> dict:
    config = SUBJECTS[subject_id]
    papers = find_papers(config["folder"])

    entries, problems = [], []
    for year in sorted(papers, reverse=True):
        files = papers[year]
        if "mg" not in files:
            problems.append(f"{year}: no marking guidelines PDF found")
            continue

        mg_path = os.path.join(NESA_ROOT, config["folder"], files["mg"])
        key = extract_mc_key(mg_path)

        expected = config["mc_count"]
        missing = sorted(set(range(1, expected + 1)) - set(key))
        if missing:
            problems.append(f"{year}: missing answers for Q{missing} -- NOT WRITTEN")
            continue
        if len(key) != expected:
            problems.append(f"{year}: got {len(key)} answers, expected {expected}")

        entries.append(
            {
                "year": year,
                "markingGuidelines": files["mg"],
                "examPaper": files.get("paper"),
                "sectionI": {
                    "questionCount": expected,
                    "sourcePage": 1,
                    "answers": {str(n): key[n] for n in sorted(key)},
                },
            }
        )

    return {
        "schemaVersion": 1,
        "subjectId": subject_id,
        "subjectName": config["name"],
        "generatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generator": "scripts/build_answer_key.py",
        "source": {
            "publisher": "NSW Education Standards Authority",
            "folder": config["folder"],
            "extractedFrom": "Multiple-choice Answer Key table, page 1 of each "
                             "marking guidelines PDF",
            "note": "Official HSC answers are immutable. Do not hand-edit this "
                    "file -- regenerate it with the script above.",
        },
        "papers": entries,
        "extractionProblems": problems,
    }


def main() -> None:
    wanted = sys.argv[1:] or list(SUBJECTS)
    unknown = [s for s in wanted if s not in SUBJECTS]
    if unknown:
        sys.exit(f"Unknown subject(s): {unknown}. Known: {list(SUBJECTS)}")

    os.makedirs(OUT_DIR, exist_ok=True)
    for subject_id in wanted:
        data = build(subject_id)
        out_path = os.path.join(OUT_DIR, f"{subject_id}.json")
        with open(out_path, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(data, handle, indent=2, ensure_ascii=False)
            handle.write("\n")

        total = sum(len(p["sectionI"]["answers"]) for p in data["papers"])
        print(f"{subject_id}: {len(data['papers'])} papers, {total} answers "
              f"-> data/answer-key/{subject_id}.json")
        for problem in data["extractionProblems"]:
            print(f"    WARNING  {problem}")


if __name__ == "__main__":
    main()
