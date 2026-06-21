"""Crop 2025 written question stimulus images at 3x resolution."""
import fitz
import os

PDF = r"C:\Claude Code Space\CRAMIT QUIZ Code Folder\NESA Exams Folder\Maths Standard 2\2025-hsc-maths-standard-2.pdf"
OUT = r"C:\Claude Code Space\CRAMIT QUIZ Code Folder\CODE\CramIT-Quiz\diagrams"
PREFIX = "mathematics-standard-2"
SCALE = 3

# Q22 already has its crops from a previous session (Q22_stimulus.jpg + Q22b_stimulus.jpg)
crops = [
    # (suffix, page_idx, y0, y1, x0, x1)
    ("Q17_stimulus", 10, 128, 462, 30, 565),   # scatterplot (with blank plot area)
    ("Q19_stimulus", 12, 128, 265, 30, 565),   # project network diagram
    ("Q20_stimulus", 13, 128, 336, 30, 565),   # parabola graph
    ("Q25_stimulus", 19, 128, 420, 30, 565),   # exercise vs TV scatterplot
    ("Q26_stimulus", 21, 128, 308, 30, 565),   # toy curved surface diagram
    ("Q28_stimulus", 24, 145, 387, 30, 565),   # cumulative frequency graph
    ("Q32_stimulus", 27, 128, 323, 30, 565),   # pyramid with spheres
    ("Q35_stimulus", 30, 140, 267, 30, 565),   # triangle PTA
    ("Q36_stimulus", 31, 128, 363, 30, 565),   # car depreciation graph
    ("Q37_stimulus", 32, 140, 338, 30, 565),   # equilateral triangles park
    ("Q39_stimulus", 34, 175, 515, 30, 565),   # medication exponential decay graph
]

doc = fitz.open(PDF)

for suffix, page_idx, y0, y1, x0, x1 in crops:
    page = doc[page_idx]
    pw = page.rect.width
    ph = page.rect.height
    clip = fitz.Rect(x0, y0, min(x1, pw), min(y1, ph))
    mat = fitz.Matrix(SCALE, SCALE)
    pix = page.get_pixmap(matrix=mat, clip=clip)
    fname = f"{PREFIX}_2025_{suffix}.jpg"
    out_path = os.path.join(OUT, fname)
    pix.save(out_path)
    print(f"Saved {fname}")

doc.close()
print("Done.")
