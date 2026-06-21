"""Crop 2023 written question stimulus images at 3x resolution."""
import fitz
import os

PDF = r"C:\Claude Code Space\CRAMIT QUIZ Code Folder\NESA Exams Folder\Maths Standard 2\2023-hsc-maths-std-2.pdf"
OUT = r"C:\Claude Code Space\CRAMIT QUIZ Code Folder\CODE\CramIT-Quiz\diagrams"
PREFIX = "mathematics-standard-2"
SCALE = 3

crops = [
    # (qnum_suffix, page_idx, y0, y1, x0, x1)
    ("Q16_stimulus",  10,  96, 384, 30, 565),
    ("Q18_stimulus",  12,  96, 358, 30, 565),
    ("Q19_stimulus",  13,  96, 333, 30, 565),   # running tracks network
    ("Q19b_stimulus", 13, 437, 632, 30, 565),   # spanning tree
    ("Q20_stimulus",  14, 152, 413, 30, 565),
    ("Q24_stimulus",  19,  96, 267, 30, 565),
    ("Q26_stimulus",  21, 112, 300, 30, 565),
    ("Q27_stimulus",  22, 180, 383, 30, 565),
    ("Q31_stimulus",  26, 152, 402, 30, 565),
    ("Q33_stimulus",  28, 152, 303, 30, 565),
    ("Q34_stimulus",  29, 328, 750, 30, 565),
    ("Q35_stimulus",  31, 112, 249, 30, 565),
    ("Q38_stimulus",  34, 215, 369, 30, 565),
]

doc = fitz.open(PDF)

for suffix, page_idx, y0, y1, x0, x1 in crops:
    page = doc[page_idx]
    pw = page.rect.width
    ph = page.rect.height
    clip = fitz.Rect(x0, y0, min(x1, pw), min(y1, ph))
    mat = fitz.Matrix(SCALE, SCALE)
    pix = page.get_pixmap(matrix=mat, clip=clip)
    fname = f"{PREFIX}_2023_{suffix}.jpg"
    out_path = os.path.join(OUT, fname)
    pix.save(out_path)
    print(f"Saved {fname}")

doc.close()
print("Done.")
