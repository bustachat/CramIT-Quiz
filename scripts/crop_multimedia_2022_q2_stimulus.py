"""Crop the three-image stimulus for Industrial Technology - Multimedia 2022 Q2.

Background
----------
The paper asks "Which of the following images uses stroke colour?" above three
star shapes labelled 1, 2, 3. The stimulus was never cropped when the subject was
ported; instead the port appended descriptions to the stem --
"(Image 1: outline star, Image 2: filled circle, Image 3: filled star)" -- and all
three descriptions are wrong about the paper:

    paper image 1  filled star, NO outline        port said "outline star"
    paper image 2  unfilled star WITH outline     port said "filled circle"
    paper image 3  filled star WITH outline       port said "filled star"

The keyed answer D ("2 and 3") is correct for the real pictures, but a student
reasoning from the port's text would answer A ("Only 1") and be marked wrong. The
answer-key check cannot see this: it compares the official letter only, never the
option or stem text (CLAUDE.md S10, rule 6).

The crop box is derived, not eyeballed: the stimulus is the ink between the end of
the stem and the first option, and the "1 2 3" labels are kept with it.

Usage
-----
    python scripts/crop_multimedia_2022_q2_stimulus.py [--dry-run]

Writes diagrams/multimedia_2022_Q2_stimulus.jpg. Idempotent.
"""

import argparse
import os
import sys

import fitz  # PyMuPDF
import numpy as np
from PIL import Image

PDF = (
    r"C:\Claude Code Space\CRAMIT QUIZ Code Folder\NESA Exams Folder"
    r"\Industrial Technology - Multimedia\2022-hsc-indus-tech-multimedia.pdf"
)
PAGE_INDEX = 1  # printed page 2
DPI = 300
OUT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "diagrams", "multimedia_2022_Q2_stimulus.jpg",
)

# The stimulus band in PDF points: below the stem (ends y=337.9) and above
# option A (starts y=419.5). The 1/2/3 labels sit at y=400-412 and are kept.
Y_TOP_PT, Y_BOTTOM_PT = 342.0, 416.0
INK_THRESHOLD = 200
PAD = 18


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="report the box, write nothing")
    args = ap.parse_args()

    if not os.path.exists(PDF):
        sys.exit(f"NESA paper not found (not in the repo, by copyright): {PDF}")

    scale = DPI / 72.0
    page = fitz.open(PDF)[PAGE_INDEX]
    pm = page.get_pixmap(dpi=DPI, colorspace=fitz.csGRAY)
    grey = np.frombuffer(pm.samples, dtype=np.uint8).reshape(pm.height, pm.width)
    ink = grey < INK_THRESHOLD

    y0, y1 = int(Y_TOP_PT * scale), int(Y_BOTTOM_PT * scale)
    band = ink[y0:y1]
    rows = np.where(band.any(axis=1))[0]
    cols = np.where(band.any(axis=0))[0]
    if not len(rows) or not len(cols):
        sys.exit("no ink found in the stimulus band - check Y_TOP_PT / Y_BOTTOM_PT")

    box = (
        max(0, int(cols[0]) - PAD),
        max(0, y0 + int(rows[0]) - PAD),
        min(pm.width, int(cols[-1]) + PAD),
        min(pm.height, y0 + int(rows[-1]) + PAD),
    )
    print(f"box={box} size={box[2]-box[0]}x{box[3]-box[1]} -> {OUT}")
    if args.dry_run:
        print("dry run - nothing written")
        return
    img = Image.frombytes("L", (pm.width, pm.height), pm.samples).convert("RGB")
    img.crop(box).save(OUT, "JPEG", quality=92, optimize=True)
    print("done")


if __name__ == "__main__":
    main()
