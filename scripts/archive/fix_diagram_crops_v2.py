"""
fix_diagram_crops_v2.py — Correct re-extraction for all 13 problematic written-question images.

Fixes two classes of problem:
  1. Wrong page number — image was taken from wrong page entirely
  2. Crop too loose   — captured full page including question text + answer lines
     (auto_bbox can't be used on Section II pages because the page border frame
      and answer-line dots are also vector drawings, expanding the bbox to full page)

All regions are hard-coded from visual inspection of the PDF pages.
Coordinates are in PDF points (1pt = 1/72 inch). Page is ~595×842pt (A4).

Run: python fix_diagram_crops_v2.py
"""
import fitz, os, sys
sys.stdout.reconfigure(encoding='utf-8')

BASE = r"C:\Claude Code Space\CRAMIT QUIZ Code Folder\NESA Exams Folder\Maths Standard 2"
OUT  = r"C:\Claude Code Space\CRAMIT QUIZ Code Folder\CODE\CramIT-Quiz\diagrams"
ZOOM = 2.0
MAT  = fitz.Matrix(ZOOM, ZOOM)

def crop(doc, page_idx, name, x0, y0, x1, y1):
    """Render a hard-coded region and save as JPG."""
    page = doc[page_idx]
    pix  = page.get_pixmap(matrix=MAT, clip=fitz.Rect(x0, y0, x1, y1))
    pix.save(os.path.join(OUT, name))
    print(f"  ✓ {name}  ({pix.width}×{pix.height} px)")

# ─────────────────────────────────────────────────────────────────────────────
print("\n=== 2020 ===")
doc = fitz.open(BASE + r"\2020-hsc-mathematics-standard-2.pdf")

# Q33 bacteria exponential graph  (page 34, page_idx=33)
# Previously used wrong page_idx=28 which was Booklet 2 cover page
# Region: skip question header+text (y<130), capture graph, stop before answer lines
crop(doc, 33, "mathematics-standard-2_2020_Q33_stimulus.jpg",
     30, 125, 545, 470)

doc.close()

# ─────────────────────────────────────────────────────────────────────────────
print("\n=== 2021 ===")
doc = fitz.open(BASE + r"\2021-hsc-mathematics-standard-2.pdf")

# Q16 sphere/tank  (page 14, page_idx=13)
# Previously used page_idx=11 (blank page)
# Region: skip "Question 16", formula block "V=4/3πr³", "where r...", "A tank consists..."
# Diagram (bowl) is below those 4 text elements
crop(doc, 13, "mathematics-standard-2_2021_Q16_stimulus.jpg",
     55, 270, 545, 500)

# Q32 semicircle shaded area  (page 27, page_idx=26) — correct page, wrong crop
# Previously auto_bbox captured full page (text + diagram + answer lines)
# Region: skip "Question 32 (5 marks)" + question text, stop before "(a) Find..."
crop(doc, 26, "mathematics-standard-2_2021_Q32_stimulus.jpg",
     55, 145, 545, 420)

# Q37 obtuse triangle  (page 38, page_idx=37)
# Previously used page_idx=36 (same as Q36 critical path) — completely wrong question
# Region: skip "Question 37" + 2-line text, capture triangle, stop before "Find the size..."
crop(doc, 37, "mathematics-standard-2_2021_Q37_stimulus.jpg",
     55, 150, 545, 440)

# Q38 z-table + normal distribution bell curve  (page 39, page_idx=38)
# Previously used page_idx=33 (wrong page — was a revenue quadratic graph)
# Region: capture z-value table (starts near top) through bell curve diagram
# Include both table and diagram — students need to read the table to answer
crop(doc, 38, "mathematics-standard-2_2021_Q38_stimulus.jpg",
     55, 75, 545, 445)

# Q39 compass radial survey  (page 40, page_idx=39)
# Previously used page_idx=35 (wrong page — was revenue graph/different question)
# Region: skip "Question 39" header + 1 line text, capture the radial survey diagram
crop(doc, 39, "mathematics-standard-2_2021_Q39_stimulus.jpg",
     55, 100, 545, 520)

doc.close()

# ─────────────────────────────────────────────────────────────────────────────
print("\n=== 2022 ===")
doc = fitz.open(BASE + r"\2022-hsc-mathematics-standard-2.pdf")

# Q26 two right-angled triangles  (page 21, page_idx=20)
# Previously used page_idx=21 (wrong — that's Q27 with no diagram)
# Region: skip question text (ends ~y=130), capture two-triangle diagram
crop(doc, 20, "mathematics-standard-2_2022_Q26_stimulus.jpg",
     55, 130, 545, 400)

doc.close()

# ─────────────────────────────────────────────────────────────────────────────
print("\n=== 2023 ===")
doc = fitz.open(BASE + r"\2023-hsc-maths-std-2.pdf")

# Q16 heart rate sigmoid graph  (page 11, page_idx=10) — correct page, full page captured
# Region: skip "Question 16" + 2-line text, capture graph with y-axis label "Heart rate"
# Must extend x0 left to capture the rotated "Heart rate (beats/minute)" y-axis label
crop(doc, 10, "mathematics-standard-2_2023_Q16_stimulus.jpg",
     40, 140, 545, 460)

# Q24 trapezoidal concrete wall cross-section  (page 20, page_idx=19) — full page captured
# Region: skip partial text at top, capture diagram with right-side "1.7 m" measurement
# Extend x1 to 565 to ensure right-side label is fully captured
crop(doc, 19, "mathematics-standard-2_2023_Q24_stimulus.jpg",
     30, 100, 565, 330)

doc.close()

# ─────────────────────────────────────────────────────────────────────────────
print("\n=== 2024 ===")
doc = fitz.open(BASE + r"\2024-hsc-maths-std-2.pdf")

# Q28 parallel box-plots  (page 22, page_idx=21) — re-check "Garden" labels
# Extend x0 to 30 to fully capture "Garden A" / "Garden B" left labels
crop(doc, 21, "mathematics-standard-2_2024_Q28_stimulus.jpg",
     30, 80, 545, 240)

# Q29 depreciation graph  (page 23, page_idx=22) — full page captured
# Region: skip "Question 29" + 1-line text, capture graph with y-axis "Value of asset ($)"
# x0=40 to capture the rotated y-axis label
crop(doc, 22, "mathematics-standard-2_2024_Q29_stimulus.jpg",
     40, 125, 545, 435)

doc.close()

# ─────────────────────────────────────────────────────────────────────────────
print("\n=== 2025 ===")
doc = fitz.open(BASE + r"\2025-hsc-maths-standard-2.pdf")

# Q17 TV/exercise scatterplot  (page 11, page_idx=10) — full page captured
# Region: skip "Question 17" + 2-line text, capture scatterplot with y-axis labels
# x0=40 to capture y-axis label "y ↑" and values 0-18
crop(doc, 10, "mathematics-standard-2_2025_Q17_stimulus.jpg",
     40, 150, 545, 470)

# Q28 cumulative frequency histogram + box-plot template  (page 25, page_idx=24)
# Full page captured — need just the cumulative freq graph (students read off it to draw)
# Region: skip "Question 28" header + 2-line text, capture histogram+polygon graph
crop(doc, 24, "mathematics-standard-2_2025_Q28_stimulus.jpg",
     40, 130, 545, 445)

doc.close()

print("\n✅ All done — verify images below then commit.")
print("\nVerify with: python -c \"")
print("  from PIL import Image; import os")
print("  for f in os.listdir('diagrams'): print(f)\"")
print("\nThen commit:")
print("  git add diagrams/")
print('  git commit -m "fix(stage-8b): correct page numbers + hard-coded crops for 13 written question images"')
print("  git push origin main")
