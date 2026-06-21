"""Crop 2024 written question stimulus images at 3x resolution."""
import fitz
import os

PDF = r"C:\Claude Code Space\CRAMIT QUIZ Code Folder\NESA Exams Folder\Maths Standard 2\2024-hsc-maths-std-2.pdf"
OUT = r"C:\Claude Code Space\CRAMIT QUIZ Code Folder\CODE\CramIT-Quiz\diagrams"
PREFIX = "mathematics-standard-2"
SCALE = 3

crops = [
    # (suffix, page_idx, y0, y1, x0, x1)
    ("Q16_stimulus",   9, 112, 345, 30, 565),   # network of towns
    ("Q18_stimulus",  11, 112, 340, 30, 565),   # weighted network (original)
    ("Q19_stimulus",  12, 145, 395, 30, 565),   # assignment vs test scatterplot
    ("Q26_stimulus",  19, 112, 265, 30, 565),   # gutter cross-section sketch
    ("Q26b_stimulus", 19, 350, 535, 30, 565),   # parabola graph of A vs w
    ("Q28_stimulus",  21, 192, 315, 30, 565),   # parallel box-plots
    ("Q29_stimulus",  22, 112, 345, 30, 565),   # depreciation graph
    ("Q30_stimulus",  23, 180, 535, 30, 565),   # anaconda scatterplot
    ("Q32_stimulus",  25, 140, 345, 30, 565),   # pentagon in circle
    ("Q34_stimulus",  27, 112, 245, 30, 565),   # soccer ball container
    ("Q35_stimulus",  28, 200, 355, 30, 565),   # normal curve diagram
    ("Q36_stimulus",  29, 112, 330, 30, 565),   # two flagpoles on slope
    ("Q38_stimulus",  31, 112, 320, 30, 565),   # cone+cylinder cake
    ("Q40_stimulus",  33, 112, 353, 30, 565),   # compass radial survey
]

doc = fitz.open(PDF)

for suffix, page_idx, y0, y1, x0, x1 in crops:
    page = doc[page_idx]
    pw = page.rect.width
    ph = page.rect.height
    clip = fitz.Rect(x0, y0, min(x1, pw), min(y1, ph))
    mat = fitz.Matrix(SCALE, SCALE)
    pix = page.get_pixmap(matrix=mat, clip=clip)
    fname = f"{PREFIX}_2024_{suffix}.jpg"
    out_path = os.path.join(OUT, fname)
    pix.save(out_path)
    print(f"Saved {fname}")

doc.close()
print("Done.")
