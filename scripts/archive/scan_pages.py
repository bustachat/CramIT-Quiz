"""
scan_pages.py — Render candidate pages to find correct page numbers for missing diagrams.
"""
import fitz, os, sys
sys.stdout.reconfigure(encoding='utf-8')

BASE = r"C:\Claude Code Space\CRAMIT QUIZ Code Folder\NESA Exams Folder\Maths Standard 2"
OUT  = r"C:\Claude Code Space\CRAMIT QUIZ Code Folder\CODE\CramIT-Quiz\scan_preview"
MAT  = fitz.Matrix(1.5, 1.5)   # 1.5x for quick preview
os.makedirs(OUT, exist_ok=True)

def scan(pdf_name, year, pages):
    doc = fitz.open(BASE + "\\" + pdf_name)
    print(f"\n{year} ({len(doc)} pages total)")
    for i in pages:
        if i >= len(doc):
            print(f"  p{i+1}: OUT OF RANGE")
            continue
        txt = doc[i].get_text()[:80].replace('\n', ' ').strip()
        draws = len(doc[i].get_drawings())
        pix = doc[i].get_pixmap(matrix=MAT)
        fname = f"{year}_p{i+1:02d}.jpg"
        pix.save(os.path.join(OUT, fname))
        print(f"  p{i+1:2d} ({draws:2d} drawings): {txt[:70]}")
    doc.close()

# 2020: Q33 bacteria graph — cover was at page_idx=28, so Q33 content is on page_idx=29-32
scan("2020-hsc-mathematics-standard-2.pdf", 2020, range(28, 36))

# 2021: Q16 sphere — Section II Booklet 1 starts around page 13-14
scan("2021-hsc-mathematics-standard-2.pdf", 2021, range(11, 20))

# 2021: Q38 (obtuse triangle) and Q39 (radial survey) — Q36 is page_idx=36, so Q38/39 are after
scan("2021-hsc-mathematics-standard-2.pdf", 2021, range(36, 45))

# 2022: Q26 two triangles — Q28 is page_idx=22, Q26 should be 2 pages before
scan("2022-hsc-mathematics-standard-2.pdf", 2022, range(18, 24))

print("\nDone — check scan_preview/ folder")
