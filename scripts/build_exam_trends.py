"""Build per-topic exam-trend data: how big a topic is, against how heavily it is examined.

The two axes, and why both are needed
-------------------------------------
**Scope** -- how many content dot points the official NESA syllabus devotes to a subtopic.
**Examination** -- how many marks that subtopic actually earned across every past paper,
read from NESA's own Mapping Grid (`data/mapping-grid/`, via `build_mapping_grid.py`).

Neither alone is honest. Scope alone tells a student to spend 13.5% of their time on
Mathematics Standard 2's Data Analysis, which has earned 3.9% of the marks. Examination alone
tells them to skip Mathematics Advanced's Introduction to Differentiation (1.3% of marks) --
the Year 11 foundation that every Year 12 calculus question silently assumes. The interesting
number is the ratio between them, and the honest presentation shows both.

This replaces guessing. A prior hand-written analysis of this exact question (a 2025 Word
document on Mathematics Standard 1) estimated topic weights from *word-frequency counts* --
"Area & Measurement (Highest in 2024 with 33 mentions)", "Financial Mathematics (20-25% of
Marks)". Word counts are not marks, and a mention in a stem is not a mark in the guidelines.
Every figure here is mark-weighted from the official grid.

What it emits, per subtopic
---------------------------
    scopeDotPoints / scopeShare      syllabus size
    examMarks / examShare            marks earned across all papers
    marksPerPaper                    average, the number a student actually feels
    yearsPresent / yearsTotal        frequency -- "appears in 6 of 6 papers"
    mcMarks / writtenMarks           where those marks live
    perYear                          the series, for a sparkline
    yieldRatio                       examShare / scopeShare; >1 punches above its size

A row's marks are split evenly when the grid cites two content codes for one question part.

Usage
-----
    python scripts/build_exam_trends.py <subject-id>
    python scripts/build_exam_trends.py all

Needs the local syllabus DOCX and the committed mapping grid. The syllabus is not in the repo
(copyright), so CI can never regenerate this -- hence the generated file is committed.
"""

import argparse
import collections
import json
import os
import re
import sys

import docx

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NESA = r"C:\Claude Code Space\CRAMIT QUIZ Code Folder\NESA Exams Folder"
GRID_DIR = os.path.join(REPO, "data", "mapping-grid")
OUT_DIR = os.path.join(REPO, "data", "exam-trends")

SUBJECTS = {
    "mathematics-standard-2": {
        "folder": "Maths Standard 2",
        "syllabus": "mathematics-standard-stage-6-syllabus-2017.docx",
        "prefix": "MS",
        # Section I is Questions 1-15 in Standard 2, 1-10 in Advanced.
        "mc_last_q": 15,
        # The Standard syllabus is shared between Standard 1 and Standard 2; only the
        # subtopics the grid actually cites belong to this course.
        "note": "2017 syllabus (shared Standard 1 / Standard 2 document)",
    },
    "mathematics-advanced": {
        "folder": "Maths Advanced",
        "syllabus": "mathematics-advanced-stage-6-syllabus-2017.docx",
        "prefix": "MA",
        "mc_last_q": 10,
        "note": "2017 syllabus; superseded by the 2024 syllabus from the 2027 HSC",
    },
}


def syllabus_scope(path, prefix):
    """Return {code: (title, content-dot-point count)} from the syllabus DOCX.

    NESA's Stage 6 maths template puts each subtopic under a `Heading 3` of the form
    "MS-F4 Investments and Loans", with its dot points under a `Content` heading of the same
    level. Both paragraphs and tables are read elsewhere in this project because VET syllabuses
    hide content in tables; the maths ones do not, but the heading walk below is unaffected
    either way.
    """
    head = re.compile(r"^(%s-[A-Z]\d)\s*(.*)$" % prefix)
    doc = docx.Document(path)
    out, code, in_content = {}, None, False
    for para in doc.paragraphs:
        style, text = para.style.name, para.text.strip()
        if not text:
            continue
        if style == "Heading 3":
            match = head.match(text)
            if match:
                code = match.group(1)
                out.setdefault(code, [match.group(2), 0])
                in_content = False
            elif code:
                in_content = text.lower() == "content"
            continue
        if style.startswith("Heading"):
            in_content = False
            continue
        if code and in_content and len(text) > 3:
            out[code][1] += 1
    return {k: tuple(v) for k, v in out.items()}


def build(subject_id, dry_run=False):
    config = SUBJECTS[subject_id]
    grid_path = os.path.join(GRID_DIR, subject_id + ".json")
    if not os.path.isfile(grid_path):
        sys.exit("no mapping grid: run scripts/build_mapping_grid.py %s first" % subject_id)
    syl_path = os.path.join(NESA, config["folder"], config["syllabus"])
    if not os.path.isfile(syl_path):
        sys.exit("syllabus not found (not in the repo, by copyright): " + syl_path)

    scope = syllabus_scope(syl_path, config["prefix"])
    papers = json.load(open(grid_path, encoding="utf-8"))["papers"]
    years = sorted(papers)

    marks = collections.Counter()
    mc_marks, written_marks = collections.Counter(), collections.Counter()
    per_year = collections.defaultdict(collections.Counter)
    present = collections.defaultdict(set)
    parts = collections.Counter()
    unknown = set()

    for year in years:
        for label, row in papers[year].items():
            if not row["codes"] or not row["marks"]:
                continue
            qnum = int(re.match(r"\d+", label).group())
            share = row["marks"] / len(row["codes"])
            for code in row["codes"]:
                if code not in scope:
                    unknown.add(code)
                marks[code] += share
                per_year[code][year] += share
                present[code].add(year)
                parts[code] += 1
                bucket = mc_marks if qnum <= config["mc_last_q"] else written_marks
                bucket[code] += share

    if unknown:
        sys.exit("grid cites codes absent from the syllabus: %s" % ", ".join(sorted(unknown)))

    examined = sorted(marks)
    total_marks = sum(marks.values())
    total_scope = sum(scope[c][1] for c in examined)

    topics = []
    for code in examined:
        dot_points = scope[code][1]
        scope_share = dot_points / total_scope
        exam_share = marks[code] / total_marks
        topics.append({
            "code": code,
            "category": code.split("-")[1],
            "title": scope[code][0],
            "scopeDotPoints": dot_points,
            "scopeShare": round(scope_share, 4),
            "examMarks": round(marks[code], 1),
            "examShare": round(exam_share, 4),
            "marksPerPaper": round(marks[code] / len(years), 1),
            "yearsPresent": len(present[code]),
            "yearsTotal": len(years),
            "questionParts": parts[code],
            "mcMarks": round(mc_marks[code], 1),
            "writtenMarks": round(written_marks[code], 1),
            "perYear": {y: round(per_year[code][y], 1) for y in years},
            "yieldRatio": round(exam_share / scope_share, 2) if scope_share else None,
        })
    topics.sort(key=lambda t: -t["examShare"])

    print("  %s: %d topics, %s papers, %.0f marks, %d syllabus dot points"
          % (subject_id, len(topics), len(years), total_marks, total_scope))
    for t in topics:
        print("    %-4s %-40s scope %5.1f%%  exam %5.1f%%  x%-5s %d/%d yrs"
              % (t["category"], t["title"][:40], 100 * t["scopeShare"],
                 100 * t["examShare"], t["yieldRatio"], t["yearsPresent"], t["yearsTotal"]))

    data = {
        "subject": subject_id,
        "source": ("Syllabus scope from the official NESA syllabus DOCX; examined marks from "
                   "the marking guidelines' Mapping Grid. Neither is in the repo (copyright)."),
        "syllabus": config["note"],
        "papers": years,
        "totalMarks": round(total_marks, 1),
        "totalScopeDotPoints": total_scope,
        "note": ("Two axes. scopeShare = how much of the syllabus a topic is. examShare = how "
                 "much of the marks it has earned. yieldRatio = examShare / scopeShare; above "
                 "1 means it punches above its size. Show BOTH -- weighting study time by "
                 "examShare alone starves foundation topics that are assumed rather than "
                 "examined. Regenerate with scripts/build_exam_trends.py; never hand-edit."),
        "topics": topics,
    }
    out_path = os.path.join(OUT_DIR, subject_id + ".json")
    print("  => %s" % out_path)
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
        build(sid, args.dry_run)


if __name__ == "__main__":
    main()
