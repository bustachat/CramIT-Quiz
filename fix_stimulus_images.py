"""
fix_stimulus_images.py — Re-crop written question stimulus images using
proper y-bound detection: diagram ends at the first instruction text
(left-margin text >20 chars appearing after the question header).

Run: python fix_stimulus_images.py
"""
import fitz
import os
import sys
import re

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

DIAG_DIR = "diagrams"
PDF = {
    2022: "C:/Claude Code Space/CRAMIT QUIZ Code Folder/NESA Exams Folder/Maths Standard 2/2022-hsc-mathematics-standard-2.pdf",
    2023: "C:/Claude Code Space/CRAMIT QUIZ Code Folder/NESA Exams Folder/Maths Standard 2/2023-hsc-maths-std-2.pdf",
    2024: "C:/Claude Code Space/CRAMIT QUIZ Code Folder/NESA Exams Folder/Maths Standard 2/2024-hsc-maths-std-2.pdf",
    2025: "C:/Claude Code Space/CRAMIT QUIZ Code Folder/NESA Exams Folder/Maths Standard 2/2025-hsc-maths-standard-2.pdf",
}

# (year, qNum, page_idx_0based, suffix)
# page_idx verified from PDF page text
CROPS = [
    (2022, 23, 17, "stimulus"),
    (2022, 32, 27, "stimulus"),
    (2022, 35, 30, "stimulus"),
    (2023, 18, 12, "stimulus"),
    (2023, 34, 29, "stimulus"),   # special: diagram is blank grid to plot on
    (2023, 38, 34, "stimulus"),
    (2024, 19, 12, "stimulus"),
    (2024, 26, 19, "stimulus"),
    (2024, 30, 23, "stimulus"),
    (2024, 34, 27, "stimulus"),
    (2024, 35, 28, "stimulus"),
    (2024, 38, 31, "stimulus"),
    (2025, 26, 21, "stimulus"),
    (2025, 36, 31, "stimulus"),
    (2025, 39, 34, "stimulus"),
]

# Hardcoded y-crop bounds (y0, y1) in PDF points, derived from text analysis.
# x always full content width: 50–575.
# These were calculated by reading the page text blocks and finding:
#   y0 = a few pts above the topmost drawing / first axis label
#   y1 = a few pts above the first instruction text (verb or "(a)")
HARDCODED = {
    # 2022
    (2022, 23): (150, 460),   # scatterplot; "(a)" at y=472
    (2022, 32): (180, 425),   # trapezoidal cross-section; "(a)" at y=435
    (2022, 35): (165, 435),   # scatterplot + best-fit line; "Describe" at y=444
    # 2023
    (2023, 18): (100, 345),   # histogram; "Provide TWO" at y=358
    (2023, 34): (435, 740),   # blank regression grid (below answer lines); axis labels y=452–726
    (2023, 38): (140, 360),   # z-table + normal dist diagram; "The weights" at y=369
    # 2024
    (2024, 19): (155, 388),   # scatter/graph; "(a)" at y=398
    (2024, 26): (125, 525),   # toy cross-section; "Find the width" at y=536
    (2024, 30): (155, 527),   # anacondas scatter plot; "Write THREE" at y=537
    (2024, 34): (128, 292),   # 3D container; "What is the total" at y=302
    (2024, 35): (128, 395),   # graph/diagram; "(a)" at y=407
    (2024, 38): (105, 308),   # cylinder+cone cake; "The ratio" at y=319
    # 2025
    (2025, 26): (128, 298),   # toy cross-section; "(a)" at y=310
    (2025, 36): (115, 355),   # salvage value graph; "The salvage values" at y=367
    (2025, 39): (182, 507),   # exponential decay graph; "Using the information" at y=518
}


def crop_page(year, qnum, page_idx, suffix):
    out_name = f"mathematics-standard-2_{year}_Q{qnum}_{suffix}.jpg"
    out_path = os.path.join(DIAG_DIR, out_name)

    key = (year, qnum)
    if key not in HARDCODED:
        print(f"  SKIP {year} Q{qnum}: no hardcoded bounds")
        return False

    y0, y1 = HARDCODED[key]
    x0, x1 = 50, 575

    doc = fitz.open(PDF[year])
    page = doc[page_idx]

    clip = fitz.Rect(x0, y0, x1, y1)
    mat = fitz.Matrix(2, 2)   # 2x = 144 dpi effective
    pix = page.get_pixmap(matrix=mat, clip=clip, colorspace=fitz.csRGB)
    pix.save(out_path)
    doc.close()

    print(f"  OK  {year} Q{qnum}: {pix.width}x{pix.height}px  clip=({x0},{y0},{x1},{y1}) -> {out_name}")
    return True


def main():
    print("=== Re-cropping written question stimulus images ===\n")
    ok = fail = 0
    for year, qnum, page_idx, suffix in CROPS:
        try:
            if crop_page(year, qnum, page_idx, suffix):
                ok += 1
            else:
                fail += 1
        except Exception as e:
            print(f"  ERROR {year} Q{qnum}: {e}")
            fail += 1
    print(f"\nDone: {ok} cropped, {fail} failed/skipped")


if __name__ == "__main__":
    main()
