"""Crop the four cross-section OPTION diagrams for VET Construction 2021 Q15.

Background
----------
Only the site-plan *stimulus* for this question was ever cropped
(`/diagrams/vet-construction_2021_Q15_stimulus.jpg`); the four answer diagrams on
page 7 of `2021-hsc-vet-construction.pdf` were not, so the question ran on text
descriptions of the curves instead of the paper's own pictures. See CLAUDE.md §11.

Why this is not driven by `scripts/diagram_registry.json`
--------------------------------------------------------
That registry is scoped to Mathematics Standard 2 (`"subject": "mathematics-standard-2"`)
and carries no VET papers. Rather than widen a Maths-only registry for a single
question, the crop boxes here are *derived*, not hand-tuned: the page is rendered
to greyscale and the option bands are found from the ink profile.

Why the boxes are derived rather than measured by eye
----------------------------------------------------
On this page the option letters (`A.`) and the axis labels (`North`, `South`,
`Ground level`) are vector outlines, not text -- `page.get_text()` returns none of
them, and `page.get_drawings()` reports only the chart boxes. Ink segmentation is
the only reading that sees every mark actually printed.

Each option occupies two ink bands: the chart plus its `Ground level` label, then a
short band underneath holding `North` and `South`. Both are kept. The paper's own
`A.`/`B.`/... glyph is deliberately EXCLUDED -- index.html renders its own option
label beside the image (`<span class="option-label">`), so baking the letter into
the crop would print it twice.

Usage
-----
    python scripts/crop_vet_2021_q15_options.py [--dry-run]

Writes diagrams/vet-construction_2021_Q15_{A,B,C,D}.jpg. Idempotent.
"""

import argparse
import os
import sys

import fitz  # PyMuPDF
import numpy as np
from PIL import Image

PDF = (
    r"C:\Claude Code Space\CRAMIT QUIZ Code Folder\NESA Exams Folder"
    r"\VET - Construction\2021-hsc-vet-construction.pdf"
)
PAGE_INDEX = 6  # printed page 7
DPI = 300
OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "diagrams")
STEM = "vet-construction_2021_Q15"

INK_THRESHOLD = 200   # < this greyscale value counts as ink
PAD = 20              # px of white margin kept around the ink
MIN_BAND_H = 5        # px; ignore specks between bands
COL_GAP = 25          # px of white that separates the option letter from the chart

# Options region of the page, in PDF points: below the "Which of the following"
# line and above the page footer.
Y_TOP_PT, Y_BOTTOM_PT = 400, 780


def find_bands(ink, y0, y1):
    """Return [(row_start, row_end)] for each run of rows containing ink."""
    rows = ink[y0:y1].any(axis=1)
    bands, start = [], None
    for i, has_ink in enumerate(rows):
        if has_ink and start is None:
            start = i
        elif not has_ink and start is not None:
            if i - start > MIN_BAND_H:
                bands.append((start + y0, i + y0))
            start = None
    if start is not None:
        bands.append((start + y0, y1))
    return bands


def column_groups(ink, row_start, row_end):
    """Return [(x_start, x_end)] for ink clusters separated by >COL_GAP white px."""
    xs = np.where(ink[row_start:row_end].any(axis=0))[0]
    groups, gstart, prev = [], xs[0], xs[0]
    for x in xs[1:]:
        if x - prev > COL_GAP:
            groups.append((int(gstart), int(prev)))
            gstart = x
        prev = x
    groups.append((int(gstart), int(prev)))
    return groups


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="report the boxes, write nothing")
    args = ap.parse_args()

    if not os.path.exists(PDF):
        sys.exit(f"NESA paper not found (not in the repo, by copyright): {PDF}")

    scale = DPI / 72.0
    page = fitz.open(PDF)[PAGE_INDEX]
    pm = page.get_pixmap(dpi=DPI, colorspace=fitz.csGRAY)
    grey = np.frombuffer(pm.samples, dtype=np.uint8).reshape(pm.height, pm.width)
    ink = grey < INK_THRESHOLD

    bands = find_bands(ink, int(Y_TOP_PT * scale), int(Y_BOTTOM_PT * scale))
    if len(bands) != 8:
        sys.exit(f"expected 8 ink bands (4 charts + 4 North/South strips), found {len(bands)}")

    page_img = Image.frombytes("L", (pm.width, pm.height), pm.samples).convert("RGB")

    for i, letter in enumerate("ABCD"):
        chart, labels = bands[2 * i], bands[2 * i + 1]

        # Drop the leading group -- the paper's own "A." glyph -- and keep the chart.
        groups = column_groups(ink, *chart)
        if len(groups) < 2:
            sys.exit(f"option {letter}: expected an option letter plus a chart, got {groups}")
        x_start = min(groups[1][0], column_groups(ink, *labels)[0][0])
        x_end = max(groups[-1][1], column_groups(ink, *labels)[-1][1])

        box = (
            max(0, x_start - PAD),
            max(0, chart[0] - PAD),
            min(pm.width, x_end + PAD),
            min(pm.height, labels[1] + PAD),
        )
        out = os.path.join(OUT_DIR, f"{STEM}_{letter}.jpg")
        print(f"{letter}: box={box} size={box[2]-box[0]}x{box[3]-box[1]} -> {out}")
        if not args.dry_run:
            page_img.crop(box).save(out, "JPEG", quality=92, optimize=True)

    print("dry run - nothing written" if args.dry_run else "done")


if __name__ == "__main__":
    main()
