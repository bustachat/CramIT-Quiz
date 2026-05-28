#!/usr/bin/env python3
"""
CramIT — Intelligent Diagram Extractor v2
==========================================
Extracts diagrams from HSC exam PDFs.

Two modes:

  CROP (default — no API key needed):
      python extract_maths_diagrams.py
      python extract_maths_diagrams.py --year 2024

      Crops diagram images from diagram_registry.json.
      On first run, the registry is auto-bootstrapped from verified hardcoded
      coordinates (2020–2025), so existing images are reproducible immediately.

  DETECT (requires ANTHROPIC_API_KEY):
      python extract_maths_diagrams.py --detect
      python extract_maths_diagrams.py --detect --year 2026

      Sends each PDF page to Claude Vision, which returns bounding boxes for
      every diagram. Updates diagram_registry.json. Use for any new exam year
      — no manual coordinate calibration needed.

Workflow for a new exam paper:
  1. Copy PDF to the NESA Exams folder (see PDF_DIR below)
  2. Add the filename to the PAPERS dict in this script
  3. Run:  python extract_maths_diagrams.py --detect --year 2026
  4. Check the output images in ./diagrams/
  5. Commit diagram_registry.json + new images to git

Output:
    ./diagrams/mathematics-standard-2_YEAR_QNUM.jpg

Requirements:
    pip install pymupdf pillow anthropic

Environment variables:
    ANTHROPIC_API_KEY   Required for --detect mode only
    PDF_DIR             Optional: override the default PDF folder path
"""

import os
import sys
import json
import base64
import io
import argparse

import fitz          # pymupdf
from PIL import Image


# ── PATHS ──────────────────────────────────────────────────────────────────────

SCRIPT_DIR    = os.path.dirname(os.path.abspath(__file__))
OUT_DIR       = os.path.join(SCRIPT_DIR, 'diagrams')
REGISTRY_PATH = os.path.join(SCRIPT_DIR, 'diagram_registry.json')

# PDFs live in the NESA Exams folder (two levels up from the repo root).
# Override with the PDF_DIR environment variable if your layout differs.
_DEFAULT_PDF_DIR = os.path.normpath(
    os.path.join(SCRIPT_DIR, '..', '..', 'NESA Exams Folder', 'Maths Standard 2')
)
PDF_DIR = os.environ.get('PDF_DIR', _DEFAULT_PDF_DIR)

SUBJECT    = 'mathematics-standard-2'
RENDER_DPI = 150   # renders at ~1240 × 1755 px per A4 page


# ── PAPERS ─────────────────────────────────────────────────────────────────────
# Add new years here when NESA releases new papers.

PAPERS = {
    2020: '2020-hsc-mathematics-standard-2.pdf',
    2021: '2021-hsc-mathematics-standard-2.pdf',
    2022: '2022-hsc-mathematics-standard-2.pdf',
    2023: '2023-hsc-maths-std-2.pdf',
    2024: '2024-hsc-maths-std-2.pdf',
    2025: '2025-hsc-maths-standard-2.pdf',
    # 2026: '2026-hsc-mathematics-standard-2.pdf',  # <- add here when available
}

# Pages to scan in --detect mode.
# The MC section of Maths Standard 2 spans pages 2–8 across all years.
MC_PAGES = list(range(2, 9))


# ── HARDCODED BOOTSTRAP ────────────────────────────────────────────────────────
# Verified pixel coordinates for 2020–2025, calibrated at 150 DPI (1240 × 1755 px).
# Used ONLY to bootstrap diagram_registry.json on first run — no API key needed.
# Format: (year, question_number, page, y_start, y_end, description)

BOOTSTRAP_CROPS = [
    # 2020
    (2020,  1,  2,  465,   980, '4 graphs as ABCD options'),
    (2020,  7,  4,  205,   805, '4 histograms as ABCD options'),
    (2020,  8,  4,  885,  1600, 'Score table + answer-options table'),
    (2020,  9,  5,  348,   880, '4 network diagrams as ABCD options'),
    (2020, 12,  6,  635,  1220, '4 scatter plots as ABCD options'),
    (2020, 15,  8,  200,   320, 'Rectangular table grid'),
    # 2021
    (2021,  2,  3,  195,   380, 'Network diagram'),
    (2021,  3,  3,  800,   945, 'Stem-and-leaf plot'),
    (2021,  7,  5,  200,  1660, 'Histogram + 4 cumulative freq graphs'),
    (2021, 10,  6,  999,  1530, '4 exponential graphs as ABCD options'),
    (2021, 11,  7,  380,   660, 'Probability tree diagram'),
    # 2022
    (2022,  1,  2,  463,   855, '4 frequency curves as ABCD options'),
    (2022,  2,  2,  996,  1565, '4 line graphs as ABCD options'),
    (2022,  3,  3,  175,   600, 'Network diagram with critical path'),
    (2022, 13,  7,  260,   745, 'Z-score table + normal distribution curve'),
    (2022, 15,  8,  235,  1222, 'Cumulative freq graph + 4 box plots'),
    # 2023
    (2023,  5,  4,  260,   945, '4 petrol pump diagrams as ABCD options'),
    (2023,  8,  5,  540,  1185, 'Die + spinner + score table'),
    (2023, 12,  7,  290,   660, 'Cylindrical pipe cross-section'),
    (2023, 14,  8,  240,   555, 'Directed network diagram'),
    # 2024
    (2024,  2,  2,  750,  1080, 'Linear function graph'),
    (2024,  4,  3,  535,  1130, 'Country map with regions'),
    (2024,  5,  4,  230,   490, 'Data table'),
    (2024,  6,  4,  855,  1015, 'Triangle diagram'),
    (2024, 15,  8,  780,  1494, 'Box plot + 4 histograms as ABCD'),
    # 2025
    (2025,  1,  2,  465,   660, 'Network diagram'),
    (2025,  2,  2, 1050,  1565, '4 graphs as ABCD options'),
    (2025,  3,  3,  215,   510, 'Weighted network diagram'),
    (2025,  8,  5,  230,  1304, 'Histogram + 4 pie chart spinners as ABCD'),
]


# ── CLAUDE VISION DETECTION PROMPT ─────────────────────────────────────────────

DETECTION_PROMPT = """\
This is a rendered page from an HSC Mathematics Standard 2 exam paper \
(Multiple Choice section, Questions 1–15).

Identify every VISUAL element that a student needs to see to answer a question. Include:
- Graphs: bar, line, cumulative frequency, histogram, scatter plot, pie chart, exponential
- Network or graph diagrams (vertices and edges, critical path diagrams)
- Tables containing numerical data, scores, or frequency distributions
- Geometric figures, shapes, cross-sections, or scale drawings
- Statistical displays: stem-and-leaf plots, box plots, normal distribution curves
- Probability diagrams: tree diagrams, spinners, sample space grids
- Images used as answer options A B C D — capture ALL of them together as ONE entry

Return a JSON object with this exact structure (no other text, no markdown):
{"diagrams": [{"question_number": 5, "description": "brief description", "y_start": 340, "y_end": 920}]}

Coordinate rules:
- y_start and y_end are pixel distances from the TOP of this image (0 = top edge)
- Add 20 pixels of extra padding above y_start and below y_end
- x coordinates are not needed — we always crop the full page width
- When answer options are all images (e.g. 4 graphs labelled A B C D), wrap them in ONE entry
- DO NOT include: question text, the letters A B C D, page numbers, NESA headers or footers
- If no diagrams appear on this page, return: {"diagrams": []}
- Return ONLY the raw JSON object"""


# ── REGISTRY HELPERS ───────────────────────────────────────────────────────────

def load_registry():
    """Load registry from disk, or return an empty structure."""
    if os.path.exists(REGISTRY_PATH):
        with open(REGISTRY_PATH, 'r') as f:
            return json.load(f)
    return {'version': '2', 'subject': SUBJECT, 'papers': {}}


def save_registry(registry):
    with open(REGISTRY_PATH, 'w') as f:
        json.dump(registry, f, indent=2)
    print(f'Registry saved -> {os.path.basename(REGISTRY_PATH)}')


def bootstrap_registry():
    """
    Create diagram_registry.json from the hardcoded BOOTSTRAP_CROPS.
    Called automatically on the first crop run so no API key is needed.
    """
    registry = {'version': '2', 'subject': SUBJECT, 'papers': {}}
    for year, q, page, y1, y2, desc in BOOTSTRAP_CROPS:
        key = str(year)
        registry['papers'].setdefault(key, []).append({
            'question':    q,
            'page':        page,
            'y_start':     y1,
            'y_end':       y2,
            'description': desc,
            'source':      'hardcoded-bootstrap',
        })
    save_registry(registry)
    total = sum(len(v) for v in registry['papers'].values())
    print(f'Bootstrapped {total} entries from hardcoded coordinates (2020–2025).\n')
    return registry


# ── PDF / IMAGE UTILITIES ──────────────────────────────────────────────────────

def find_pdf(year):
    """
    Return the full path to the PDF for a given year.
    Checks PDF_DIR first, then the script's own directory as fallback.
    """
    filename = PAPERS.get(year)
    if not filename:
        return None
    for search_dir in [PDF_DIR, SCRIPT_DIR]:
        candidate = os.path.join(search_dir, filename)
        if os.path.exists(candidate):
            return candidate
    return None


def render_page(pdf_path, page_num):
    """Render one PDF page to a PIL Image at RENDER_DPI."""
    doc  = fitz.open(pdf_path)
    page = doc[page_num - 1]
    mat  = fitz.Matrix(RENDER_DPI / 72, RENDER_DPI / 72)
    pix  = page.get_pixmap(matrix=mat, colorspace=fitz.csRGB)
    img  = Image.frombytes('RGB', [pix.width, pix.height], pix.samples)
    doc.close()
    return img


def crop_region(img, y_start, y_end, h_margin=16):
    """Crop a horizontal strip from a full-width page image."""
    y_end = min(y_end, img.height)
    return img.crop((h_margin, y_start, img.width - h_margin, y_end))


def pil_to_jpeg_b64(img):
    """Encode a PIL Image as a base64 JPEG string for the Claude API."""
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=85)
    return base64.b64encode(buf.getvalue()).decode('utf-8')


# ── CLAUDE VISION DETECTION ─────────────────────────────────────────────────────

def detect_page(client, page_img, page_num):
    """
    Ask Claude Vision to identify all diagrams on one rendered page image.
    Returns a list of dicts: [{'question_number', 'description', 'y_start', 'y_end'}, ...]
    """
    img_b64 = pil_to_jpeg_b64(page_img)

    response = client.messages.create(
        model='claude-opus-4-5',
        max_tokens=1024,
        messages=[{
            'role': 'user',
            'content': [
                {
                    'type': 'image',
                    'source': {
                        'type':       'base64',
                        'media_type': 'image/jpeg',
                        'data':       img_b64,
                    },
                },
                {
                    'type': 'text',
                    'text': DETECTION_PROMPT,
                },
            ],
        }]
    )

    raw = response.content[0].text.strip()

    # Strip accidental markdown code fences
    if raw.startswith('```'):
        lines = raw.split('\n')
        raw = '\n'.join(lines[1:-1] if lines[-1] == '```' else lines[1:])

    parsed   = json.loads(raw)
    diagrams = parsed.get('diagrams', [])

    if diagrams:
        print(f'    p{page_num}: {len(diagrams)} diagram(s)')
        for d in diagrams:
            q = d.get('question_number', '?')
            print(f'      Q{q}  y:{d.get("y_start")}–{d.get("y_end")}  {d.get("description","")[:55]}')
    else:
        print(f'    p{page_num}: no diagrams')

    return diagrams


def run_detect(years, registry):
    """
    Run Claude Vision detection across all MC pages for each requested year.
    Updates `registry` in place.
    """
    try:
        import anthropic
    except ImportError:
        print('\nERROR: anthropic package not installed.')
        print('Fix:   pip install anthropic\n')
        sys.exit(1)

    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print('\nERROR: ANTHROPIC_API_KEY environment variable is not set.')
        print('Fix:   set ANTHROPIC_API_KEY=sk-ant-...\n')
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    for year in years:
        pdf_path = find_pdf(year)
        if not pdf_path:
            fname = PAPERS.get(year, '(not in PAPERS dict)')
            print(f'\n  [SKIP] {year}: PDF not found')
            print(f'    Looked in: {PDF_DIR}')
            print(f'    Expected:  {fname}')
            continue

        print(f'\n  {year}  ({os.path.basename(pdf_path)})')
        year_entries = []

        for page_num in MC_PAGES:
            try:
                img      = render_page(pdf_path, page_num)
                diagrams = detect_page(client, img, page_num)
            except json.JSONDecodeError as e:
                print(f'    [ERR] p{page_num}: Claude returned invalid JSON - {e}')
                continue
            except Exception as e:
                print(f'    [ERR] p{page_num}: {e}')
                continue

            for d in diagrams:
                year_entries.append({
                    'question':    d.get('question_number'),
                    'page':        page_num,
                    'y_start':     d.get('y_start'),
                    'y_end':       d.get('y_end'),
                    'description': d.get('description', ''),
                    'source':      'claude-vision',
                })

        registry['papers'][str(year)] = year_entries
        print(f'  -> {len(year_entries)} diagram(s) recorded for {year}')


# ── CROP FROM REGISTRY ─────────────────────────────────────────────────────────

def run_crop(years, registry):
    """Crop and save all diagrams for each year using coordinates from the registry."""
    total_done = total_skip = 0

    for year in years:
        if year not in PAPERS:
            print(f'  [WARN] {year}: not in PAPERS dict - add the filename first')
            continue

        entries = registry.get('papers', {}).get(str(year), [])
        if not entries:
            print(f'  [WARN] {year}: no entries in registry')
            print(f'    Fix: python extract_maths_diagrams.py --detect --year {year}')
            continue

        pdf_path = find_pdf(year)
        if not pdf_path:
            print(f'  [SKIP] {year}: PDF not found in {PDF_DIR}')
            total_skip += len(entries)
            continue

        page_cache = {}

        for entry in entries:
            q    = entry.get('question')
            page = entry.get('page')
            y1   = entry.get('y_start')
            y2   = entry.get('y_end')
            src  = entry.get('source', '')

            if None in (q, page, y1, y2):
                print(f'  [ERR] {year} Q{q}: incomplete entry in registry, skipping')
                total_skip += 1
                continue

            try:
                if page not in page_cache:
                    page_cache[page] = render_page(pdf_path, page)
                img     = page_cache[page]
                cropped = crop_region(img, y1, y2)

                filename = f'{SUBJECT}_{year}_Q{q}.jpg'
                out_path = os.path.join(OUT_DIR, filename)
                cropped.save(out_path, 'JPEG', quality=92)

                kb    = os.path.getsize(out_path) // 1024
                badge = '[AI]' if src == 'claude-vision' else '[--]'
                print(f'  {badge} OK {year} Q{q:2d}  p{page}  -> {filename} ({kb} KB)')
                total_done += 1

            except Exception as e:
                print(f'  [ERR] {year} Q{q}: {e}')
                total_skip += 1

    return total_done, total_skip


# ── ENTRY POINT ────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='CramIT Intelligent Diagram Extractor v2',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python extract_maths_diagrams.py                    # crop all years
  python extract_maths_diagrams.py --year 2024        # crop 2024 only
  python extract_maths_diagrams.py --detect           # Vision-detect all years
  python extract_maths_diagrams.py --detect --year 2026  # detect new paper
        """
    )
    parser.add_argument('--detect', action='store_true',
                        help='Run Claude Vision to detect diagrams and update registry')
    parser.add_argument('--year',   type=int,
                        help='Process one year only (e.g. --year 2026)')
    args = parser.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)

    years = [args.year] if args.year else sorted(PAPERS.keys())
    mode  = 'DETECT (Claude Vision)' if args.detect else 'CROP (from registry)'

    print('=' * 55)
    print('  CramIT — Intelligent Diagram Extractor v2')
    print('=' * 55)
    print(f'  Mode    : {mode}')
    print(f'  Years   : {years}')
    print(f'  PDFs    : {PDF_DIR}')
    print(f'  Output  : {OUT_DIR}')
    print(f'  Registry: {REGISTRY_PATH}')
    print()

    # ── DETECT MODE ──────────────────────────────────────────────────────────
    if args.detect:
        registry = load_registry()
        run_detect(years, registry)
        save_registry(registry)
        print()
        print('Detection complete.')
        print('Run without --detect to crop the diagrams:')
        print('  python extract_maths_diagrams.py')
        return

    # ── CROP MODE ─────────────────────────────────────────────────────────────
    # Auto-bootstrap the registry on first run (no API key needed)
    if not os.path.exists(REGISTRY_PATH):
        print('No registry found — bootstrapping from hardcoded coordinates...')
        registry = bootstrap_registry()
    else:
        registry = load_registry()

    done, skipped = run_crop(years, registry)

    print()
    print(f'Done.  {done} extracted,  {skipped} skipped.')
    if skipped:
        print('Tip: to auto-detect missing diagrams, run:')
        print('  python extract_maths_diagrams.py --detect --year YYYY')
    print(f'Files saved to: {OUT_DIR}')


if __name__ == '__main__':
    main()
