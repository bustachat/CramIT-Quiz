#!/usr/bin/env python3
"""
CramIT -- Mathematics Advanced diagram cropper (Stage 4 asset tool)
===================================================================

One crop registry per exam year, cut straight from the NESA paper.  Written
for the Mathematics Advanced port, which runs one paper per session
(docs/subject-plans/mathematics-advanced.md, Stage 4).

Why this is a separate script and not an entry in
`scripts/diagram_registry.json` / `extract_maths_diagrams.py`:

  * that registry's coordinates are raw pixels verified at RENDER_DPI = 150 and
    its `save_crop()` overwrites unconditionally, so a bare run re-cuts every
    Mathematics Standard 2 crop.  Nothing in this port needs to touch them.
  * on these papers the option letters (A. B. C. D.) and most axis labels are
    outline PATHS, not text, so the calibrate path in that script -- which
    finds option labels via `get_text()` -- has nothing to find.

Coordinates here are PDF POINTS (72 pt = 1 inch), which are resolution
independent: changing RENDER_DPI rescales the output without moving the crop.
They were derived from an ink profile of the rendered page (dark pixels outside
the text blocks), then every crop was opened and compared against the paper.

Option crops deliberately EXCLUDE the paper's own `A.` / `B.` glyph -- the app
renders its own `<span class="option-label">`, so a baked-in letter prints twice.
On these papers the letter cannot be excluded with an x-cut: it sits in the
cell's top-left corner and the graph's own axis and left arm run underneath it
(2020 Q5 option A: the letter spans x 100.8-111.3 and the x-axis line starts at
x 102.2).  Cropping to the right of the letter silently amputates the axis.  So
each option entry carries an `erase` rectangle instead -- the letter's own
bounding box, painted white after rendering.  Every erase box was checked
against an ink profile of that x-strip first: nothing but the letter lies
inside it.

Usage:
    python scripts/crop_maths_advanced.py --year 2020
    python scripts/crop_maths_advanced.py --year 2020 --dry-run
"""

import argparse
import os
import sys

import fitz  # pymupdf

PDF_DIR = os.environ.get(
    "MA_PDF_DIR",
    r"C:/Claude Code Space/CRAMIT QUIZ Code Folder/NESA Exams Folder/Maths Advanced",
)
OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "diagrams")
SUBJECT = "mathematics-advanced"
RENDER_DPI = 300  # points are DPI-independent here, unlike diagram_registry.json

# year -> [ (suffix, page_index, x0, y0, x1, y1, erase) ] in PDF points, 0-indexed
# pages.  `erase` is an optional list of rectangles (same coordinate space) painted
# white after rendering -- used only to drop the paper's own option letter.
REGISTRY = {
    2020: [
        # --- Section I ---
        # Q5/Q9 option cells: crop the whole cell, then white out the option letter.
        ("Q5_A",  3,  98, 303, 276, 462, [(98, 305, 113, 318)]),
        ("Q5_B",  3, 325, 303, 503, 462, [(325, 305, 340, 318)]),
        ("Q5_C",  3,  98, 481, 277, 640, [(98, 483, 113, 496)]),
        ("Q5_D",  3, 325, 481, 503, 640, [(325, 483, 340, 496)]),
        ("Q7_stimulus",  4, 164, 252, 424, 433),
        ("Q8_stimulus",  5, 188,  95, 400, 252),
        ("Q9_A",  5,  98, 525, 291, 634, [(98, 527, 113, 540)]),
        ("Q9_B",  5, 325, 525, 518, 634, [(325, 527, 340, 540)]),
        ("Q9_C",  5,  98, 656, 291, 766, [(98, 658, 113, 671)]),
        ("Q9_D",  5, 325, 656, 518, 766, [(325, 658, 340, 671)]),
        ("Q10_stimulus", 6, 160,  95, 433, 314),
        # --- Section II ---
        ("Q15_stimulus", 13, 185, 160, 410, 288),  # bearings, incl. NOT TO SCALE
        ("Q22_stimulus", 22, 235, 134, 360, 266),  # regular decagon, centre O
        ("Q25_stimulus", 25, 160, 146, 422, 240),  # rectangle + quarter circle
        ("Q27_stimulus", 29,  88, 230, 463, 341),  # box-plot, incl. axis caption
        ("Q29_stimulus", 32, 161, 122, 428, 286),  # y = c ln x
        ("Q30_stimulus", 33, 173, 133, 412, 326),  # two parabolas, shaded region
        ("Q31_stimulus", 35, 163, 222, 412, 382),  # mice population m(t)
    ],
}


def crop_year(year: int, dry_run: bool = False) -> int:
    entries = REGISTRY.get(year)
    if not entries:
        sys.exit(f"No crop registry for {year}. Known years: {sorted(REGISTRY)}")

    pdf_path = os.path.join(PDF_DIR, f"{year}_exam.pdf")
    if not os.path.exists(pdf_path):
        sys.exit(f"Exam PDF not found: {pdf_path}")

    doc = fitz.open(pdf_path)
    written = 0
    for entry in entries:
        suffix, page_idx, x0, y0, x1, y1 = entry[:6]
        erase = entry[6] if len(entry) > 6 else []
        name = f"{SUBJECT}_{year}_{suffix}.jpg"
        out = os.path.join(OUT_DIR, name)
        rect = fitz.Rect(x0, y0, x1, y1)
        if dry_run:
            print(f"  would write {name}  page {page_idx + 1}  {rect}")
            continue
        page = doc[page_idx]
        if erase:
            # Redactions with no replacement text simply blank the area.  Applied to
            # a copy of the page in memory; the PDF on disk is never modified.
            for ex0, ey0, ex1, ey1 in erase:
                page.add_redact_annot(fitz.Rect(ex0, ey0, ex1, ey1), fill=(1, 1, 1))
            page.apply_redactions()
        pix = page.get_pixmap(dpi=RENDER_DPI, clip=rect)
        pix.save(out)
        print(f"  {name}  {pix.width}x{pix.height}px  ({pix.width / pix.height:.2f}:1)")
        written += 1
    doc.close()
    return written


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--year", type=int, required=True, help="exam year to crop")
    ap.add_argument("--dry-run", action="store_true", help="print the crops without writing files")
    args = ap.parse_args()
    n = crop_year(args.year, args.dry_run)
    print(f"\n{n} crop(s) written to {OUT_DIR}")


if __name__ == "__main__":
    main()
