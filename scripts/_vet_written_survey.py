# -*- coding: utf-8 -*-
"""Survey VET Construction Section II-IV question stems from the EXAM PAPERS.

Stage 1 for the completion port. Reads the papers only -- never the marking guidelines
(the marks, sample answers and criteria are already committed ground truth in
data/answer-key/written/, and CLAUDE.md section 10 forbids re-deriving them by reading).

Prints, per paper: each part's stem text as the page lays it out, and whether the page
carries a graphic the stem may depend on.

    python scripts/_vet_written_survey.py [year] [--graphics]
"""
import os
import re
import sys

import fitz

NESA = r"C:\Claude Code Space\CRAMIT QUIZ Code Folder\NESA Exams Folder\VET - Construction"
PAPERS = {
    "2021": "2021-hsc-vet-construction.pdf",
    "2022": "2022-hsc-vet-construction.pdf",
    "2023": "2023-hsc-vet-construction.pdf",
    "2024": "2024-hsc-vet-construction.pdf",
    "2025": "2025-hsc-vet-construction.pdf",
}

# Answer-lines, the "Office Use Only" barcode furniture and page numbers are layout, not
# question text. Filtered so a stem reads as prose.
NOISE = re.compile(
    r"^\s*(\.{5,}|\u2013 \d+ \u2013|Office Use Only|Do NOT write|Centre Number|Student Number|"
    r"\d{10}|\d{4}\s*$|HIGHER SCHOOL|Construction\s*$|Section [IV]+|Question \d+ (continues|continued)|"
    r"BLANK PAGE|End of paper|\u00a9 |Please turn over)", re.I)


def graphics(page):
    """Rough graphic detector: embedded rasters, plus dense vector drawing."""
    rasters = len(page.get_images(full=True))
    strokes = sum(len(d["items"]) for d in page.get_drawings())
    return rasters, strokes


def main():
    years = [sys.argv[1]] if len(sys.argv) > 1 and sys.argv[1] in PAPERS else sorted(PAPERS)
    want_graphics = "--graphics" in sys.argv
    for year in years:
        path = os.path.join(NESA, PAPERS[year])
        doc = fitz.open(path)
        print("=" * 90)
        print("%s  %s  (%d pages)" % (year, PAPERS[year], doc.page_count))
        started = False
        for pi in range(doc.page_count):
            text = doc[pi].get_text()
            if re.search(r"Question\s+16\s*\(", text):
                started = True
            if not started:
                continue
            lines = [l.rstrip() for l in text.split("\n")
                     if l.strip() and not NOISE.match(l)]
            if not lines:
                continue
            rasters, strokes = graphics(doc[pi])
            flag = ""
            if want_graphics and (rasters or strokes > 40):
                flag = "   [GRAPHIC: %d raster, %d strokes]" % (rasters, strokes)
            print("\n--- page %d ---%s" % (pi + 1, flag))
            print("\n".join(lines))


if __name__ == "__main__":
    main()
