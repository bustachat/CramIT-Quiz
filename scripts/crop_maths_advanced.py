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
    2023: [
        # --- Section I ---
        ("Q1_stimulus",  1, 148, 227, 441, 430),  # bee scatterplot, incl. "Time" caption
        ("Q2_stimulus",  2, 190,  89, 405, 175),  # die and 4-sector spinner (score table is HTML)
        ("Q4_stimulus",  3, 185, 230, 371, 430),  # cubic with a double root
        ("Q5_stimulus",  4, 102, 164, 495, 419),  # odd function, shaded region, incl. NOT TO SCALE
        # Q6 option cells: crop the whole cell, then white out the option letter.
        ("Q6_A",  5,  99, 212, 284, 364, [(99, 213, 114, 229)]),
        ("Q6_B",  5, 314, 212, 500, 364, [(315, 213, 330, 229)]),
        ("Q6_C",  5,  99, 388, 284, 540, [(99, 389, 114, 405)]),
        ("Q6_D",  5, 314, 388, 500, 540, [(315, 389, 330, 405)]),
        ("Q10_stimulus", 7, 177, 104, 412, 292),  # y = x^2 meeting y = k at P and Q
        # --- Section II ---
        ("Q16_stimulus", 13, 145, 161, 451, 284),  # shape APQBCD, incl. NOT TO SCALE
        ("Q22_stimulus", 20, 194, 136, 402, 313),  # rectangular prism, incl. NOT TO SCALE
        ("Q23_stimulus", 21, 182, 251, 413, 352),  # normal curve shaded below z
        ("Q24_stimulus", 23, 122, 150, 462, 288),  # garden bed and concrete path
        ("Q26_stimulus", 27, 116, 180, 437, 317),  # camera filming a swing, incl. NOT TO SCALE
        ("Q27_stimulus", 28, 167, 138, 423, 349),  # y = a|x - b| + c through three points
        ("Q28_stimulus", 29, 110, 152, 478, 370),  # curve with two parallel tangents
        ("Q32_stimulus", 35,  99, 160, 484, 395),  # y = e^-2x and y = e^-x - 1/4
    ],
    2022: [
        # --- Section I ---
        # Q1 option cells: crop the whole cell, then white out the option letter.
        # The letter's own box carries no vector path (checked: 0 drawings intersect
        # any of the eight letter boxes on pages 2 and 7), so the erase is safe here --
        # unlike 2020, where the graph ran underneath it.
        ("Q1_A",  1,  97, 219, 233, 357, [(99.9, 221.4, 112.4, 235.4)]),
        ("Q1_B",  1, 313, 219, 449, 357, [(315.9, 221.4, 329.0, 235.4)]),
        ("Q1_C",  1,  97, 376, 233, 513, [(99.9, 378.1, 112.4, 392.1)]),
        ("Q1_D",  1, 313, 376, 449, 513, [(315.9, 378.1, 329.0, 392.1)]),
        ("Q3_stimulus",  2, 176, 366, 417, 543),   # tower BT, incl. NOT TO SCALE
        ("Q7_stimulus",  4, 134,  96, 461, 267),   # probability density function
        ("Q8_stimulus",  5, 113, 131, 483, 270),   # even function, regions A and B
        ("Q10_stimulus", 6, 101,  98, 498, 294),   # y = f(x) and y = g(x), side by side
        ("Q10_A", 6, 100, 337, 283, 536, [(102.2, 338.6, 115.9, 352.6)]),
        ("Q10_B", 6, 316, 337, 499, 536, [(318.2, 338.6, 331.2, 352.6)]),
        ("Q10_C", 6, 100, 564, 283, 763, [(102.2, 565.3, 115.2, 579.3)]),
        ("Q10_D", 6, 316, 564, 499, 763, [(318.2, 565.3, 331.9, 579.3)]),
        # --- Section II ---
        ("Q11_stimulus",  9, 100, 431, 497, 675),  # Pareto chart, incl. both axis captions
        ("Q14_stimulus", 11,  69, 431, 522, 579),  # y = k sin(ax)
        ("Q16_stimulus", 13, 188, 140, 402, 387),  # parabola meeting a line, shaded
        ("Q17_stimulus", 14, 206, 163, 390, 340),  # house of cards, 3 rows
        ("Q24_stimulus", 20, 114, 208, 448, 427),  # scatterplot + line of best fit
        ("Q28_stimulus", 25, 156, 168, 439, 376),  # circle, interval to (1, 1), shaded
        ("Q28b_stimulus", 26, 156, 158, 439, 366), # same circle with the hyperbola added
        ("Q29_stimulus", 27, 169, 187, 427, 379),  # y = 2^-x with 5 rectangular strips
        ("Q31_stimulus", 29, 164, 139, 433, 322),  # line through P(1, 2), triangle XOY
    ],
    2025: [
        # --- Section I ---
        # Option letters are real TEXT on pages 3, 4 and 5, and `get_drawings()` reports
        # ZERO vector paths intersecting any of the twelve letter boxes -- checked, not
        # assumed, so the 2020 amputation trap does not arise here and the white `erase`
        # rectangle removes the letter and nothing else.
        ("Q2_A", 2,  96,  92, 255, 219, [(99.3, 95.1, 110.9, 110.9)]),
        ("Q2_B", 2, 312,  92, 471, 219, [(315.9, 95.1, 326.9, 110.9)]),
        ("Q2_C", 2,  96, 228, 255, 356, [(99.9, 231.5, 110.9, 247.3)]),
        ("Q2_D", 2, 312, 228, 471, 356, [(315.3, 231.5, 326.9, 247.3)]),
        ("Q4_A", 3,  96,  99, 290, 286, [(99.3, 102.0, 110.9, 117.8)]),
        ("Q4_B", 3, 312,  99, 506, 286, [(315.3, 102.0, 326.3, 117.8)]),
        ("Q4_C", 3,  96, 311, 290, 499, [(99.3, 314.6, 110.3, 330.4)]),
        ("Q4_D", 3, 312, 311, 506, 499, [(315.3, 314.6, 326.9, 330.4)]),
        ("Q6_stimulus", 4, 196,  93, 397, 293),   # y = f(x), asymptotes x = -2 and y = 1
        ("Q6_A", 4,  97, 331, 295, 536, [(100.7, 334.7, 112.3, 350.5)]),
        ("Q6_B", 4, 313, 331, 511, 536, [(316.7, 334.7, 327.7, 350.5)]),
        ("Q6_C", 4,  97, 543, 295, 749, [(100.7, 547.3, 111.7, 563.1)]),
        ("Q6_D", 4, 313, 543, 511, 749, [(316.7, 547.3, 328.3, 563.1)]),
        ("Q9_stimulus",  6, 126,  91, 455, 325),  # y = f'(x) on a printed grid
        ("Q10_stimulus", 7, 176, 100, 406, 330),  # y = f(x) with all stationary points
        # --- Section II ---
        ("Q11_stimulus",  9, 205, 142, 388, 308),  # h = t^2 - 8t + 12
        ("Q14_stimulus", 11,  95, 147, 488, 392),  # scatterplot, incl. both axis captions
        ("Q24_stimulus", 24, 163, 130, 437, 319),  # y = e ln x, y = ax^2 + c, y = x
        ("Q25_stimulus", 26, 159, 129, 423, 279),  # regions under y = x sin x, shaded
        ("Q27_stimulus", 29, 160, 133, 420, 279),  # shaded region under y = (1/2)^x
        ("Q28_stimulus", 31, 202, 176, 438, 328),  # circular paddock, shaded segment
        # x0 = 74, not 85: the y-axis labels 1/2/3 start at x = 78.4 and a first pass at
        # 85 clipped every one of them -- the ink band understated it, the text layer did not.
        ("Q28b_stimulus", 32, 74, 134, 527, 362),  # y = sin(theta) + pi/2 on a grid
        # Q29 is NOT on Stage 1's crop list for 2025 -- found by reading the page.
        ("Q29_stimulus", 33, 154, 169, 432, 385),  # mountain peak T, points O, Y, F
    ],
    2021: [
        # --- Section I ---
        # Option letters extract as GARBLED words on both option pages (`A.` comes out
        # as `Mu` on page 3, `ap` on page 4), so the letter boxes come from the ink
        # profile of the x-strip they sit in, not from the text layer.  `get_drawings()`
        # reports ZERO vector paths intersecting any of the eight boxes -- checked, so
        # the 2020 amputation trap does not arise and the white `erase` removes the
        # letter and nothing else.
        ("Q4_stimulus", 2, 126, 103, 429, 213),   # downloads per day, incl. both axis captions
        ("Q4_A", 2, 97, 260, 444, 378, [(99, 262.0, 117, 274.5)]),
        ("Q4_B", 2, 97, 389, 444, 507, [(99, 391.1, 117, 403.6)]),
        ("Q4_C", 2, 97, 518, 444, 636, [(99, 519.8, 117, 532.3)]),
        ("Q4_D", 2, 97, 646, 444, 764, [(99, 648.4, 117, 660.9)]),
        # Q5's two columns are NOT symmetric about the page centre: the left cell's
        # content runs x 100.6-249.4, the right cell's x 345.1-493.9.
        ("Q5_A", 3,  97,  96, 253, 216, [(98, 97.5, 115, 110.5)]),
        ("Q5_B", 3, 341,  96, 497, 216, [(343, 97.5, 360, 110.5)]),
        ("Q5_C", 3,  97, 247, 253, 367, [(98, 248.8, 115, 261.8)]),
        ("Q5_D", 3, 341, 247, 497, 367, [(343, 248.8, 360, 261.8)]),
        ("Q6_stimulus",  4, 219, 178, 371, 297),  # partially completed probability tree
        ("Q7_stimulus",  5, 172, 108, 421, 284),  # y = f(x), local min x = -2, local max x = 3
        ("Q8_stimulus",  6, 168,  96, 426, 267),  # quartic, simple root left, triple root right
        ("Q10_stimulus", 7, 105, 110, 484, 266),  # y = mx tangent to y = cos x at x = a
        # --- Section II ---
        ("Q12_stimulus", 10, 145, 133, 451, 284),  # semicircle, triangle XYZ, incl. NOT TO SCALE
        ("Q17_stimulus", 13,  68, 164, 487, 414),  # height vs temperature scatterplot + regression
        ("Q17b_stimulus", 14, 96, 150, 510, 400),  # latitude vs temperature, the SECOND graph
        ("Q18_stimulus", 15, 166, 136, 427, 268),  # triangle ABC, incl. NOT TO SCALE
        ("Q22_stimulus", 18, 183, 252, 412, 343),  # normal curve, strip between 0 and z shaded
        ("Q24_stimulus", 20, 160, 198, 429, 384),  # y = 3/(x-1) meeting y = 3x/2, shaded
        ("Q28_stimulus", 25, 137, 138, 458, 284),  # f(x) = 8 - 2^x, region against the axes
        ("Q32_stimulus", 33, 162, 405, 433, 487),  # unlabelled normal curve with 7 tick marks
        ("Q33_stimulus", 34, 163, 269, 430, 406),  # pdf f(x) = Ax/(x^2 + 4) on 0 <= x <= 6
    ],
    2024: [
        # --- Section I ---
        ("Q1_stimulus",  1, 194, 216, 418, 372),  # decreasing line, incl. NOT TO SCALE
        ("Q7_stimulus",  4, 165,  94, 429, 299),  # y = f(x), zeros at 0, 2 and 4
        # Q7/Q8 option cells: crop the whole cell, then white out the option letter.
        ("Q7_A",  4, 100, 336, 303, 540, [(99, 337, 114, 353)]),
        ("Q7_B",  4, 325, 336, 529, 540, [(324, 337, 339, 353)]),
        ("Q7_C",  4, 100, 557, 303, 761, [(99, 558, 114, 574)]),
        ("Q7_D",  4, 325, 557, 529, 761, [(324, 558, 339, 574)]),
        ("Q8_stimulus",  5, 203,  91, 392, 125),  # single box plot, no scale printed
        ("Q8_A",  5, 100, 197, 289, 310, [(99, 199, 114, 215)]),
        ("Q8_B",  5, 316, 197, 505, 310, [(315, 199, 330, 215)]),
        ("Q8_C",  5, 100, 330, 289, 444, [(99, 332, 114, 348)]),
        ("Q8_D",  5, 316, 330, 505, 444, [(315, 332, 330, 348)]),
        ("Q9_stimulus",  6, 186, 120, 408, 303),  # two-stage probability tree
        ("Q10_stimulus", 7, 110,  94, 472, 318),  # quartic with horizontal inflection Q
        # --- Section II ---
        ("Q11_stimulus", 10, 167, 122, 429, 347),  # y = g(x), incl. the y = g(x) label
        ("Q13_stimulus", 12,  86, 207, 474, 502),  # populations W and K, incl. both axis captions
        ("Q14_stimulus", 13, 137, 133, 458, 316),  # two parabolas, shaded region, incl. NOT TO SCALE
        ("Q16_stimulus", 15, 106, 197, 450, 290),  # parallel box plots, incl. the 140-185 scale
        ("Q20_stimulus", 19, 156, 162, 443, 334),  # tower TC with A and B, incl. NOT TO SCALE
        ("Q21_stimulus", 20,  98, 194, 499, 521),  # anaconda scatterplot, incl. KEY and axis captions
        ("Q22_stimulus", 21,  73, 121, 483, 330),  # f(x) = ln(1 + x^2), two shaded strips
        ("Q23_stimulus", 23, 181, 237, 414, 343),  # standard normal curve shaded up to z
        ("Q28_stimulus", 29, 208, 210, 463, 398),  # Ferris wheel illustration, incl. NOT TO SCALE
        ("Q31_stimulus", 33, 216, 175, 380, 338),  # concentric circles, region QRST shaded
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
