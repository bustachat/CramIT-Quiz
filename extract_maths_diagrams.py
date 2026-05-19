"""
CramIT — Maths Standard 2 Diagram Extractor
============================================
Extracts diagrams from HSC Maths Standard 2 MC section (Q1-15).
Crop coordinates calibrated for 1240x1755px renders (150 DPI from real PDFs).

Calibration v2 (April 2026): coordinates re-calibrated using pixel-gap analysis
on actual PDF renders. Each (y_start, y_end) lands cleanly between content
blocks — capturing diagrams + their A/B/C/D sub-options where applicable, and
excluding the question's leading text and text-only MC options.

Usage:
    python extract_maths_diagrams.py

Output:
    ./diagrams/mathematics-standard-2_YEAR_QNUM.jpg

Requirements:
    python -m pip install pillow pymupdf
"""

import os
import fitz  # pymupdf
from PIL import Image

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'diagrams')

PAPERS = {
    2020: '2020-hsc-mathematics-standard-2.pdf',
    2021: '2021-hsc-mathematics-standard-2.pdf',
    2022: '2022-hsc-mathematics-standard-2.pdf',
    2023: '2023-hsc-maths-std-2.pdf',
    2024: '2024-hsc-maths-std-2.pdf',
    2025: '2025-hsc-mathematics-standard-2.pdf',
}

# Crop coords calibrated for 1240x1755px (150 DPI render of real PDFs)
# Format: (year, question, page, y_start, y_end)
CROPS = [
    # ── 2020 ──────────────────────────────────────────────────────────────────
    (2020,  1,  2,   465,   980),  # 4 graphs as ABCD options
    (2020,  7,  4,   205,   805),  # 4 histograms as ABCD options
    (2020,  8,  4,   885,  1600),  # Question + score table + answer-options table
    (2020,  9,  5,   348,   880),  # 4 network diagrams as ABCD options
    (2020, 12,  6,   635,  1220),  # 4 scatter plots as ABCD options
    (2020, 15,  8,   200,   320),  # Rectangular table grid

    # ── 2021 ──────────────────────────────────────────────────────────────────
    (2021,  2,  3,   195,   380),  # Network diagram
    (2021,  3,  3,   800,   945),  # Stem-and-leaf plot
    (2021,  7,  5,   200,  1660),  # Histogram + 4 cumulative freq graphs
    (2021, 10,  6,   999,  1530),  # 4 exponential graphs as ABCD options
    (2021, 11,  7,   380,   660),  # Probability tree diagram

    # ── 2022 ──────────────────────────────────────────────────────────────────
    (2022,  1,  2,   463,   855),  # 4 frequency curves as ABCD options
    (2022,  2,  2,   996,  1565),  # 4 line graphs as ABCD options
    (2022,  3,  3,   175,   600),  # Network diagram with critical path
    (2022, 13,  7,   260,   745),  # Z-score table + normal distribution curve
    (2022, 15,  8,   235,  1222),  # Cumulative freq graph + 4 box plots

    # ── 2023 ──────────────────────────────────────────────────────────────────
    (2023,  5,  4,   260,   945),  # 4 petrol pump diagrams as ABCD options
    (2023,  8,  5,   540,  1185),  # Die + spinner + score table
    (2023, 12,  7,   290,   660),  # Cylindrical pipe cross-section
    (2023, 14,  8,   240,   555),  # Directed network diagram

    # ── 2024 ──────────────────────────────────────────────────────────────────
    (2024,  2,  2,   750,  1080),  # Linear function graph
    (2024,  4,  3,   535,  1130),  # Country map with regions
    (2024,  5,  4,   230,   490),  # Data table
    (2024,  6,  4,   855,  1015),  # Triangle diagram
    (2024, 15,  8,   780,  1494),  # Box plot + 4 histograms as ABCD

    # ── 2025 ──────────────────────────────────────────────────────────────────
    (2025,  1,  2,   465,   660),  # Network diagram
    (2025,  2,  2,  1050,  1565),  # 4 graphs as ABCD options
    (2025,  3,  3,   215,   510),  # Weighted network diagram
    (2025,  8,  5,   230,  1304),  # Histogram + 4 pie chart spinners as ABCD
]

RENDER_DPI = 150


def load_page(pdf_path, page_num):
    doc = fitz.open(pdf_path)
    page = doc[page_num - 1]
    mat = fitz.Matrix(RENDER_DPI / 72, RENDER_DPI / 72)
    pix = page.get_pixmap(matrix=mat, colorspace=fitz.csRGB)
    img = Image.frombytes('RGB', [pix.width, pix.height], pix.samples)
    doc.close()
    return img


def crop_diagram(img, y_start, y_end, margin=16):
    w = img.width
    # Clamp to image bounds
    y_end = min(y_end, img.height)
    return img.crop((margin, y_start, w - margin, y_end))


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(OUT_DIR, exist_ok=True)

    print('CramIT — Maths Standard 2 Diagram Extractor')
    print(f'Output: {OUT_DIR}')
    print()

    processed = 0
    skipped = 0

    for year, q_num, page, y1, y2 in CROPS:
        paper_path = os.path.join(script_dir, PAPERS[year])

        if not os.path.exists(paper_path):
            print(f'  ⚠ SKIP {year} Q{q_num}: file not found — {PAPERS[year]}')
            skipped += 1
            continue

        try:
            img = load_page(paper_path, page)
            cropped = crop_diagram(img, y1, y2)
            filename = f'mathematics-standard-2_{year}_Q{q_num}.jpg'
            out_path = os.path.join(OUT_DIR, filename)
            cropped.save(out_path, 'JPEG', quality=92)
            kb = os.path.getsize(out_path) // 1024
            print(f'  ✓ {year} Q{q_num:2d} → {filename} ({kb}KB)')
            processed += 1
        except Exception as e:
            print(f'  ✗ {year} Q{q_num}: {e}')
            skipped += 1

    print()
    print(f'Done. {processed} extracted, {skipped} skipped.')
    print(f'Files in: {OUT_DIR}')


if __name__ == '__main__':
    main()
