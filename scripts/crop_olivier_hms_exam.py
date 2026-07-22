#!/usr/bin/env python3
"""
crop_olivier_hms_exam.py — one-off diagram cropper for olivier-hms-exam-prep.html

Source: "ATAR Notes Year 12 HSC Health and Movement Science — Summary Sheets"
(local NESA Exams Folder, NOT committed). Every page is a full-page photographic
scan, so the diagrams cannot be pulled out as separate image objects — they must be
clip-cropped by coordinate. Crop rectangles are expressed as fractions of the page
(DPI-independent) and rendered at high DPI for a crisp result.

This is a side-project asset only (Olivier's standalone study tool). Not part of the
CramIT app, its /diagrams/ folder, or its schema. Run once to (re)generate the images.

Usage:  python scripts/crop_olivier_hms_exam.py
"""
import os
import fitz  # PyMuPDF

PDF = r"C:\Claude Code Space\CRAMIT QUIZ Code Folder\NESA Exams Folder\Health and Movement Science\ATAR Notes year 12 HSC healthand Movement Science.pdf"
OUT = os.path.join(os.path.dirname(__file__), "..", "olivier-hms-exam-diagrams")
DPI = 160          # render resolution for the crop (crisp on mobile, small files)
JPG_QUALITY = 82   # JPEG quality — these land in a public repo, keep them lean

# (output_name, 0-based page index, x0, y0, x1, y1) — bounds as fractions of the page.
CROPS = [
    ("determinants-rainbow", 5,  0.055, 0.110, 0.505, 0.360),
    ("tech-hexagon",         11, 0.555, 0.345, 0.965, 0.625),
    ("sdg-flower",           14, 0.510, 0.075, 0.965, 0.355),
    ("macrocycle",           21, 0.515, 0.315, 0.915, 0.470),
    ("peaking-tapering",     21, 0.440, 0.475, 0.955, 0.680),
    ("biomechanics-stride",  24, 0.125, 0.415, 0.875, 0.680),
    ("injury-direct-indirect", 26, 0.275, 0.150, 0.615, 0.290),
    ("injury-hard-soft",     26, 0.155, 0.355, 0.755, 0.460),
    ("injury-overuse",       26, 0.595, 0.465, 0.940, 0.695),
    ("ricer",                27, 0.095, 0.405, 0.955, 0.680),
    ("hard-tissue",          28, 0.635, 0.080, 0.960, 0.365),
]


def main():
    os.makedirs(OUT, exist_ok=True)
    doc = fitz.open(PDF)
    mat = fitz.Matrix(DPI / 72, DPI / 72)
    for name, idx, fx0, fy0, fx1, fy1 in CROPS:
        page = doc[idx]
        r = page.rect
        clip = fitz.Rect(fx0 * r.width, fy0 * r.height, fx1 * r.width, fy1 * r.height)
        pix = page.get_pixmap(matrix=mat, clip=clip, colorspace=fitz.csRGB)
        path = os.path.join(OUT, name + ".jpg")
        pix.save(path, jpg_quality=JPG_QUALITY)
        print(f"{name}.jpg  {pix.width}x{pix.height}  ({round(pix.size/1024)} KB)")
    doc.close()


if __name__ == "__main__":
    main()
