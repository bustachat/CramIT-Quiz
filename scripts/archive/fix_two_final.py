"""fix_two_final.py — Two remaining crop adjustments."""
import fitz, os, sys
sys.stdout.reconfigure(encoding='utf-8')
BASE = r"C:\Claude Code Space\CRAMIT QUIZ Code Folder\NESA Exams Folder\Maths Standard 2"
OUT  = r"C:\Claude Code Space\CRAMIT QUIZ Code Folder\CODE\CramIT-Quiz\diagrams"
MAT  = fitz.Matrix(2.0, 2.0)

def crop(doc, page_idx, name, x0, y0, x1, y1):
    pix = doc[page_idx].get_pixmap(matrix=MAT, clip=fitz.Rect(x0, y0, x1, y1))
    pix.save(os.path.join(OUT, name))
    print(f"  ✓ {name}  ({pix.width}×{pix.height} px)")

# 2021 Q16 sphere — bowl top (2m measurement) was clipped; lower y0 from 270→250
doc = fitz.open(BASE + r"\2021-hsc-mathematics-standard-2.pdf")
crop(doc, 13, "mathematics-standard-2_2021_Q16_stimulus.jpg", 55, 250, 545, 500)
doc.close()

# 2022 Q26 two triangles — "where AC = 35cm..." text still showed; raise y0 130→155
# Also clip answer lines by lowering y1 from 400→345
doc = fitz.open(BASE + r"\2022-hsc-mathematics-standard-2.pdf")
crop(doc, 20, "mathematics-standard-2_2022_Q26_stimulus.jpg", 55, 155, 545, 345)
doc.close()

print("Done.")
