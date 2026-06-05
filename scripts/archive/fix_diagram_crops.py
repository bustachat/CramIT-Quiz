"""
fix_diagram_crops.py — Re-extract 13 written-question diagram images with corrected crop bounds.
Issues fixed:
  - Text bleeding at top (y0 too low captured PDF question text)
  - Answer lines at bottom (y1 too high captured dotted answer lines)
  - Left edge clipped (x0 too large clipped y-axis labels and "Start" node text)
  - Right edge clipped (x1 too small clipped measurement labels)

Run: python fix_diagram_crops.py
"""
import fitz, os, sys
sys.stdout.reconfigure(encoding='utf-8')

BASE = r"C:\Claude Code Space\CRAMIT QUIZ Code Folder\NESA Exams Folder\Maths Standard 2"
OUT  = r"C:\Claude Code Space\CRAMIT QUIZ Code Folder\CODE\CramIT-Quiz\diagrams"
ZOOM = 2.0
MAT  = fitz.Matrix(ZOOM, ZOOM)
PAD  = 12

def save_region(doc, page_idx, out_name, x0, y0, x1, y1):
    page = doc[page_idx]
    clip = fitz.Rect(x0, y0, x1, y1)
    pix  = page.get_pixmap(matrix=MAT, clip=clip)
    pix.save(os.path.join(OUT, out_name))
    print(f"  ✓ {out_name}  ({pix.width}×{pix.height} px)")

def auto_bbox(page, x0=20, y0=80, x1=None, y1=None):
    pw = page.rect.width
    if x1 is None: x1 = pw - 20
    if y1 is None: y1 = page.rect.height * 0.85
    xs, ys = [], []
    for d in page.get_drawings():
        r  = d["rect"]
        cx = (r.x0 + r.x1) / 2
        cy = (r.y0 + r.y1) / 2
        if x0 < cx < x1 and y0 < cy < y1:
            xs += [r.x0, r.x1]; ys += [r.y0, r.y1]
    if not xs:
        return None
    return (min(xs) - PAD, min(ys) - PAD, max(xs) + PAD, max(ys) + PAD)

def auto_save(doc, page_idx, name, x0=20, y0=80, x1=None, y1=None, fallback=None):
    page = doc[page_idx]
    bbox = auto_bbox(page, x0, y0, x1, y1)
    if bbox:
        save_region(doc, page_idx, name, *bbox)
    elif fallback:
        save_region(doc, page_idx, name, *fallback)
    else:
        print(f"  WARN: no drawings on p{page_idx+1} for {name}")

# ─────────────────────────────────────────────────────────────────────────────
# 2020
# ─────────────────────────────────────────────────────────────────────────────
print("\n=== 2020 ===")
doc = fitz.open(BASE + r"\2020-hsc-mathematics-standard-2.pdf")

# Q33 bacteria exponential graph — y-axis labels were clipped (x0 was 50, too far right)
# Fix: widen left margin to x0=20 so "100","200","300","400" labels are captured
auto_save(doc, 28, "mathematics-standard-2_2020_Q33_stimulus.jpg",
          x0=20, y0=80, fallback=(20, 80, 560, 500))

doc.close()

# ─────────────────────────────────────────────────────────────────────────────
# 2021
# ─────────────────────────────────────────────────────────────────────────────
print("\n=== 2021 ===")
doc = fitz.open(BASE + r"\2021-hsc-mathematics-standard-2.pdf")

# Q16 sphere half-volume — formula "V=4/3πr³" and question text bled into top
# Fix: raise y0 to 220 to skip past the text block; diagram (bowl) is below it
auto_save(doc, 11, "mathematics-standard-2_2021_Q16_stimulus.jpg",
          x0=30, y0=220, fallback=(30, 220, 560, 540))

# Q32 semicircle shaded area — massive overcrop: text above + answer lines below
# Fix: tight y0=120 (skip question text), y1=430 (stop before dotted answer lines)
auto_save(doc, 26, "mathematics-standard-2_2021_Q32_stimulus.jpg",
          x0=20, y0=120, y1=430, fallback=(20, 120, 560, 430))

# Q36 critical path network — "Start" node label clipped to "rt" on left edge
# Fix: widen x0 from 50 to 20
auto_save(doc, 36, "mathematics-standard-2_2021_Q36_stimulus.jpg",
          x0=20, y0=80, y1=400, fallback=(20, 80, 560, 400))

# Q37 uses same critical path network as Q36 (multi-part question)
# Same fix: widen x0 so "Start" is captured
auto_save(doc, 36, "mathematics-standard-2_2021_Q37_stimulus.jpg",
          x0=20, y0=80, y1=400, fallback=(20, 80, 560, 400))

# Q38 obtuse triangle (sine rule) — question text "a triangle ABC where..." bled into top
# Fix: raise y0 to ~160 to skip past the question text line
auto_save(doc, 33, "mathematics-standard-2_2021_Q38_stimulus.jpg",
          x0=20, y0=160, fallback=(20, 160, 560, 500))

# Q39 compass radial survey — bearing angle labels (D(0°), A(0°), B(150°)) clipped
# Fix: widen x0 to 20, extend x1 to 570
auto_save(doc, 35, "mathematics-standard-2_2021_Q39_stimulus.jpg",
          x0=20, y0=80, x1=570, fallback=(20, 80, 570, 540))

doc.close()

# ─────────────────────────────────────────────────────────────────────────────
# 2022
# ─────────────────────────────────────────────────────────────────────────────
print("\n=== 2022 ===")
doc = fitz.open(BASE + r"\2022-hsc-mathematics-standard-2.pdf")

# Q26 two right-angled triangles — question text ", BD = 93 cm, ∠ACB = 41°..." bled in at top
# Fix: raise y0 to 120 so the diagram (below the text) is captured cleanly
auto_save(doc, 21, "mathematics-standard-2_2022_Q26_stimulus.jpg",
          x0=20, y0=120, fallback=(20, 120, 560, 500))

# Q28 dam volume — answer dotted lines captured below the 3D dam diagram
# Fix: tighten y1 to 280 to cut off before the answer lines start
auto_save(doc, 22, "mathematics-standard-2_2022_Q28_stimulus.jpg",
          x0=20, y0=80, y1=280, fallback=(20, 80, 560, 280))

doc.close()

# ─────────────────────────────────────────────────────────────────────────────
# 2023
# ─────────────────────────────────────────────────────────────────────────────
print("\n=== 2023 ===")
doc = fitz.open(BASE + r"\2023-hsc-maths-std-2.pdf")

# Q16 heart rate sigmoid graph — y-axis labels clipped (x0 was 50, clip "1" from "160","180")
# Fix: widen x0 to 20
auto_save(doc, 10, "mathematics-standard-2_2023_Q16_stimulus.jpg",
          x0=20, y0=80, fallback=(20, 80, 560, 520))

# Q24 trapezoidal concrete wall cross-section — right measurement "1.2 m" clipped to "1."
# Fix: extend x1 to 575 so the right side label is captured
auto_save(doc, 19, "mathematics-standard-2_2023_Q24_stimulus.jpg",
          x0=20, y0=80, x1=575, fallback=(20, 80, 575, 380))

doc.close()

# ─────────────────────────────────────────────────────────────────────────────
# 2024
# ─────────────────────────────────────────────────────────────────────────────
print("\n=== 2024 ===")
doc = fitz.open(BASE + r"\2024-hsc-maths-std-2.pdf")

# Q28 parallel box-plots — "Garden A" / "Garden B" labels clipped to "arden A" / "arden B"
# Fix: widen x0 to 20
auto_save(doc, 21, "mathematics-standard-2_2024_Q28_stimulus.jpg",
          x0=20, y0=80, y1=360, fallback=(20, 80, 560, 360))

# Q29 depreciation graph — y-axis labels and left edge clipped
# Fix: widen x0 to 20
auto_save(doc, 22, "mathematics-standard-2_2024_Q29_stimulus.jpg",
          x0=20, y0=80, fallback=(20, 80, 560, 520))

doc.close()

# ─────────────────────────────────────────────────────────────────────────────
# 2025
# ─────────────────────────────────────────────────────────────────────────────
print("\n=== 2025 ===")
doc = fitz.open(BASE + r"\2025-hsc-maths-standard-2.pdf")

# Q17 TV/exercise scatterplot — y-axis labels clipped (leading digit cut off)
# Fix: widen x0 to 20
auto_save(doc, 10, "mathematics-standard-2_2025_Q17_stimulus.jpg",
          x0=20, y0=80, fallback=(20, 80, 560, 520))

# Q28 cumulative frequency histogram — y-axis entirely missing from crop
# Fix: widen x0 to 20, use fallback with wide margin
auto_save(doc, 24, "mathematics-standard-2_2025_Q28_stimulus.jpg",
          x0=20, y0=80, y1=500, fallback=(20, 80, 560, 500))

doc.close()

print("\n✅ Done — verify images in diagrams/ then commit.")
print("\nGit commands:")
print("  git add diagrams/")
print('  git commit -m "fix(stage-8b): re-crop 13 written question diagrams — fix text bleeding and edge clipping"')
print("  git push origin main")
