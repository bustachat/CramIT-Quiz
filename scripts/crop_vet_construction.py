#!/usr/bin/env python3
"""
CramIT -- VET Construction diagram cropper (written-completion port asset tool)
==============================================================================

Same mechanism as `scripts/crop_maths_advanced.py`: one crop registry per exam
year, cut straight from the NESA paper, coordinates in **PDF POINTS** (72 pt =
1 inch) so they are resolution independent and RENDER_DPI can change without
moving a crop.

Why this is a separate script and NOT an entry in `scripts/diagram_registry.json`:
that registry's coordinates are raw pixels verified at RENDER_DPI = 150 and its
`save_crop()` overwrites unconditionally, so a bare run re-cuts every
Mathematics Standard 2 crop. Same reason the Maths Advanced port got its own.

⚠️ This registry contains ONLY the crops added by the written-completion port.
VET's other 36 `/diagrams/vet-construction_*` images were cut by earlier tooling
and are deliberately absent, so running this can never disturb them.

⚠️ On these papers a diagram's dimension labels ("5 m", "1200") are outline
PATHS, not text -- `get_text()` returns nothing for them (the only strings the
text layer carries near these figures are broken caption fragments like
'Pic' / 'nic' / 'table'). So the box cannot be derived from the text layer, and
an ink profile alone is not enough either: the Maths port lost a graph's y-axis
labels exactly that way. Every box here is taken from `get_drawings()`, widened,
and then checked by `--verify`, which fails if any ink touches the boundary.

The question's own caption ("A concrete slab is to be laid ... as shown.") is
STEM text and is deliberately outside every box -- it belongs in the question's
`q` field, not baked into the image.

Usage:
    python scripts/crop_vet_construction.py --year 2021
    python scripts/crop_vet_construction.py --year 2021 --dry-run
    python scripts/crop_vet_construction.py --year 2021 --verify
"""

import argparse
import os
import sys

import fitz  # pymupdf

PDF_DIR = os.environ.get(
    "VET_PDF_DIR",
    r"C:/Claude Code Space/CRAMIT QUIZ Code Folder/NESA Exams Folder/VET - Construction",
)
OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "diagrams")
SUBJECT = "vet-construction"
RENDER_DPI = 300  # points are DPI-independent here, unlike diagram_registry.json

PAPERS = {
    2021: "2021-hsc-vet-construction.pdf",
    2022: "2022-hsc-vet-construction.pdf",
    2023: "2023-hsc-vet-construction.pdf",
    2024: "2024-hsc-vet-construction.pdf",
    2025: "2025-hsc-vet-construction.pdf",
}

# year -> [ (suffix, page_index, x0, y0, x1, y1) ] in PDF points, 0-indexed pages.
REGISTRY = {
    2021: [
        # Q18 stimulus: concrete slab for a picnic table -- a 6 m x 5 m rectangle with a
        # semicircular end. Serves parts (b) perimeter and (c) volume, so it is filed
        # under the question rather than a part. Vector ink runs x 158.6-436.1,
        # y 123.6-252.5; widened to clear the "5 m" and "6 m" path labels and the
        # dimension witness lines below them. Caption at y ~ 95-107 excluded.
        ("Q18_stimulus", 13, 150.0, 114.0, 450.0, 262.0),
    ],
    2022: [
        # Q19(b) stimulus: L-shaped bathroom plan dimensioned 1200/2400 across and
        # 1200/1500 down (mm). Vector ink runs x 206.0-389.0, y 123.6-270.2; widened to
        # clear the rotated "1200"/"1500" labels on the right and the lower dimension
        # string. Caption "A bathroom plan is shown." at y ~ 95-107 excluded.
        ("Q19b_stimulus", 15, 196.0, 114.0, 400.0, 280.0),
    ],
}


def paper_path(year: int) -> str:
    name = PAPERS.get(year)
    if not name:
        sys.exit(f"No paper registered for {year}. Known: {sorted(PAPERS)}")
    path = os.path.join(PDF_DIR, name)
    if not os.path.exists(path):
        sys.exit(f"Exam PDF not found: {path}")
    return path


def verify_year(year: int) -> int:
    """Fail if ink touches a crop boundary, i.e. the box is clipping the figure.

    Renders one pixel band inside each edge and looks for dark pixels. An empty
    band means the figure (and every path-drawn dimension label) sits clear of
    the boundary. This is the mechanical form of "open it and look" -- the Maths
    port shipped a crop whose y-axis labels were amputated because the box came
    from an ink profile that had already excluded them.
    """
    doc = fitz.open(paper_path(year))
    bad = 0
    for suffix, page_idx, x0, y0, x1, y1 in REGISTRY.get(year, []):
        page = doc[page_idx]
        pix = page.get_pixmap(dpi=RENDER_DPI, clip=fitz.Rect(x0, y0, x1, y1))
        w, h, n = pix.width, pix.height, pix.n
        buf = pix.samples

        def dark_in(xs, ys):
            hits = 0
            for yy in ys:
                for xx in xs:
                    off = (yy * w + xx) * n
                    if buf[off] < 200 or buf[off + 1] < 200 or buf[off + 2] < 200:
                        hits += 1
            return hits

        band = 6  # points-worth of pixels to inspect at each edge
        edges = {
            "top": dark_in(range(w), range(0, band)),
            "bottom": dark_in(range(w), range(h - band, h)),
            "left": dark_in(range(0, band), range(h)),
            "right": dark_in(range(w - band, w), range(h)),
        }
        touching = {k: v for k, v in edges.items() if v}
        status = "CLIPPED " + str(touching) if touching else "clear on all four edges"
        print(f"  {SUBJECT}_{year}_{suffix}.jpg  {w}x{h}px  {status}")
        if touching:
            bad += 1
    doc.close()
    return bad


def crop_year(year: int, dry_run: bool = False) -> int:
    entries = REGISTRY.get(year)
    if not entries:
        sys.exit(f"No crop registry for {year}. Known years: {sorted(REGISTRY)}")
    doc = fitz.open(paper_path(year))
    written = 0
    for suffix, page_idx, x0, y0, x1, y1 in entries:
        name = f"{SUBJECT}_{year}_{suffix}.jpg"
        out = os.path.join(OUT_DIR, name)
        rect = fitz.Rect(x0, y0, x1, y1)
        if dry_run:
            print(f"  would write {name}  page {page_idx + 1}  {rect}")
            continue
        pix = doc[page_idx].get_pixmap(dpi=RENDER_DPI, clip=rect)
        pix.save(out)
        print(f"  {name}  {pix.width}x{pix.height}px  ({pix.width / pix.height:.2f}:1)")
        written += 1
    doc.close()
    return written


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--year", type=int, required=True)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--verify", action="store_true",
                    help="check no ink touches a crop boundary, then exit")
    args = ap.parse_args()
    if args.verify:
        bad = verify_year(args.year)
        sys.exit(1 if bad else 0)
    n = crop_year(args.year, args.dry_run)
    print(f"\n{n} crop(s) written to {OUT_DIR}")


if __name__ == "__main__":
    main()
