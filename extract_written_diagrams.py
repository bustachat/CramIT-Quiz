#!/usr/bin/env python3
"""
CramIT -- Written Question Diagram Extractor
============================================
Extracts diagrams from HSC Section II (written-response) pages.

Unlike the MC extractor, Section II pages have one question per page:
  "Question N" heading → question text → DIAGRAM → dotted answer lines

This extractor always uses full-width crops (x0=30, x1=565 PDF pts) to
prevent y-axis labels and edge annotations from being clipped.

TWO MODES:

  CROP (default) — crops from written_diagram_registry.json:
    python extract_written_diagrams.py
    python extract_written_diagrams.py --year 2025

    On first run the registry is auto-bootstrapped from verified 2020-2025
    coordinates (derived from fix_diagram_crops_v2.py + fix_two_final.py).

  DETECT (requires ANTHROPIC_API_KEY) — Claude Vision detects diagrams:
    python extract_written_diagrams.py --detect
    python extract_written_diagrams.py --detect --year 2026

    Sends each Section II page to Claude Vision, which identifies the diagram
    region and returns pixel bounding box (y_start, y_end). Updates registry.
    Use for any new exam year — no manual coordinate work needed.

Workflow for a new exam year:
  1. Copy PDF to the NESA Exams folder (see PDF_DIR)
  2. Add filename to PAPERS dict below
  3. Run: python extract_written_diagrams.py --detect --year 2026
  4. Check output images in ./diagrams/
  5. Commit written_diagram_registry.json + new images to git

Requirements: pip install pymupdf pillow anthropic
Environment:  ANTHROPIC_API_KEY (detect mode only), PDF_DIR (optional)
"""

import os, sys, json, base64, io, argparse
import fitz
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')


# -- PATHS ---------------------------------------------------------------------

SCRIPT_DIR    = os.path.dirname(os.path.abspath(__file__))
OUT_DIR       = os.path.join(SCRIPT_DIR, 'diagrams')
REGISTRY_PATH = os.path.join(SCRIPT_DIR, 'written_diagram_registry.json')

_DEFAULT_PDF_DIR = os.path.normpath(
    os.path.join(SCRIPT_DIR, '..', '..', 'NESA Exams Folder', 'Maths Standard 2')
)
PDF_DIR = os.environ.get('PDF_DIR', _DEFAULT_PDF_DIR)
SUBJECT = 'mathematics-standard-2'


# -- RENDER SETTINGS -----------------------------------------------------------

ZOOM = 2.0
MAT  = fitz.Matrix(ZOOM, ZOOM)

# Full-width crop bounds in PDF points (A4 page = 595 x 842 pt).
# x0=30, x1=565 gives a 30pt margin on each side — wide enough to capture
# rotated y-axis labels and edge annotations ("NOT TO SCALE", etc.).
X0_FULL = 30
X1_FULL = 565

# Section II starts on page 9 (pages 1-8 = cover + MC Section I, per NESA format).
SECTION_II_FIRST_PAGE = 9


# -- PAPERS --------------------------------------------------------------------

PAPERS = {
    2020: '2020-hsc-mathematics-standard-2.pdf',
    2021: '2021-hsc-mathematics-standard-2.pdf',
    2022: '2022-hsc-mathematics-standard-2.pdf',
    2023: '2023-hsc-maths-std-2.pdf',
    2024: '2024-hsc-maths-std-2.pdf',
    2025: '2025-hsc-maths-standard-2.pdf',
    # 2026: '2026-hsc-maths-standard-2.pdf',
}


# -- BOOTSTRAP DATA ------------------------------------------------------------
# Verified crop coordinates (PDF points) for 2020-2025.
# Derived from manual inspection via fix_diagram_crops_v2.py + fix_two_final.py.
# page_idx is 0-indexed (page_idx = page_number - 1).
#
# These are the "known good" crops for existing papers.
# Run --detect to get Claude Vision precision on any year.

BOOTSTRAP = {
    2020: [
        {'q': 33, 'page_idx': 33, 'y0': 125, 'y1': 470,
         'desc': 'bacteria exponential growth graph'},
    ],
    2021: [
        {'q': 16, 'page_idx': 13, 'y0': 250, 'y1': 500,
         'desc': 'sphere/tank bowl diagram'},
        {'q': 32, 'page_idx': 26, 'y0': 145, 'y1': 420,
         'desc': 'semicircle shaded area'},
        {'q': 36, 'page_idx': 36, 'y0':  80, 'y1': 400,
         'desc': 'critical path network'},
        {'q': 37, 'page_idx': 37, 'y0': 150, 'y1': 440,
         'desc': 'obtuse triangle (sine rule)'},
        {'q': 38, 'page_idx': 38, 'y0':  75, 'y1': 445,
         'desc': 'z-table + normal distribution curve'},
        {'q': 39, 'page_idx': 39, 'y0': 100, 'y1': 520,
         'desc': 'compass radial survey'},
    ],
    2022: [
        {'q': 26, 'page_idx': 20, 'y0': 155, 'y1': 345,
         'desc': 'two right-angled triangles'},
        {'q': 28, 'page_idx': 22, 'y0':  80, 'y1': 240,
         'desc': '3D dam volume shape'},
    ],
    2023: [
        {'q': 16, 'page_idx': 10, 'y0': 140, 'y1': 460,
         'desc': 'heart rate sigmoid graph'},
        {'q': 24, 'page_idx': 19, 'y0': 100, 'y1': 330,
         'desc': 'trapezoidal concrete wall cross-section'},
    ],
    2024: [
        {'q': 28, 'page_idx': 21, 'y0':  80, 'y1': 240,
         'desc': 'parallel box-plots (Garden A / Garden B)'},
        {'q': 29, 'page_idx': 22, 'y0': 125, 'y1': 435,
         'desc': 'depreciation graph'},
    ],
    2025: [
        {'q': 17, 'page_idx': 10, 'y0': 150, 'y1': 470,
         'desc': 'TV/exercise scatterplot'},
        {'q': 28, 'page_idx': 24, 'y0': 130, 'y1': 445,
         'desc': 'cumulative frequency histogram + box-plot template'},
    ],
}


# -- DETECTION PROMPT ----------------------------------------------------------

DETECTION_PROMPT = """\
This is a rendered page from an HSC Mathematics Standard 2 exam, Section II (Written Response).

TASK: Find the VISUAL ELEMENT (graph, diagram, table, figure, or chart) on this page and return its exact pixel bounding box — diagram only, nothing else.

THE CROP MUST:
  - Start BELOW the last line of introductory/question text (paragraphs describing the scenario)
  - Start BELOW the "Question N (X marks)" heading
  - END ABOVE any "(a)", "(b)", "(c)" sub-question labels
  - END ABOVE any dotted answer lines where students write
  - Include ALL parts of the visual: axes, axis labels (including rotated y-axis text), tick marks,
    data points, measurement annotations, "NOT TO SCALE" text, border of diagrams/tables

COMMON MISTAKES TO AVOID:
  - Do NOT start the crop at the top of the page — skip past the question heading and all text paragraphs
  - Do NOT cut off the bottom of the diagram before the x-axis label or lowest measurement
  - Do NOT include "(a) Find..." style sub-questions at the bottom
  - Do NOT include dotted lines (answer lines) at the bottom

If a visual element IS present, add 20px padding on all sides beyond the outermost visible element.

Return ONLY this JSON (no markdown fences, no explanation):
{
  "question_number": 28,
  "has_diagram": true,
  "y_start": 580,
  "y_end": 1040,
  "description": "parallel box-plots comparing Garden A and Garden B flower heights"
}

If no visual element (the page is text only, or only has answer lines):
{
  "question_number": 19,
  "has_diagram": false
}

If question number is not readable, set question_number to null.
Return ONLY raw JSON."""


# -- REGISTRY ------------------------------------------------------------------

def load_registry():
    if os.path.exists(REGISTRY_PATH):
        with open(REGISTRY_PATH, 'r') as f:
            return json.load(f)
    return {'version': '1', 'subject': SUBJECT, 'papers': {}}


def save_registry(registry):
    with open(REGISTRY_PATH, 'w') as f:
        json.dump(registry, f, indent=2)
    print(f'Registry saved -> {os.path.basename(REGISTRY_PATH)}')


def bootstrap_registry():
    """Build registry from BOOTSTRAP hard-coded coordinates."""
    registry = {'version': '1', 'subject': SUBJECT, 'papers': {}}
    for year, entries in BOOTSTRAP.items():
        registry['papers'][str(year)] = [
            {
                'question':  e['q'],
                'page_idx':  e['page_idx'],
                'x0':        X0_FULL,
                'y0':        e['y0'],
                'x1':        X1_FULL,
                'y1':        e['y1'],
                'description': e['desc'],
                'source':    'hardcoded',
            }
            for e in entries
        ]
    save_registry(registry)
    total = sum(len(v) for v in registry['papers'].values())
    print(f'Bootstrapped: {total} written question diagrams (2020-2025).')
    print('Run --detect for Claude Vision precision on any year.\n')
    return registry


# -- PDF / IMAGE UTILITIES -----------------------------------------------------

def find_pdf(year):
    fname = PAPERS.get(year)
    if not fname:
        return None
    for d in [PDF_DIR, SCRIPT_DIR]:
        p = os.path.join(d, fname)
        if os.path.exists(p):
            return p
    return None


def render_page_pil(pdf_path, page_idx):
    """Render a PDF page at ZOOM resolution, return PIL Image."""
    doc  = fitz.open(pdf_path)
    page = doc[page_idx]
    pix  = page.get_pixmap(matrix=MAT, colorspace=fitz.csRGB)
    img  = Image.frombytes('RGB', [pix.width, pix.height], pix.samples)
    doc.close()
    return img


def pil_to_jpeg_b64(img):
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=85)
    return base64.b64encode(buf.getvalue()).decode('utf-8')


def crop_and_save(pdf_path, page_idx, x0, y0, x1, y1, out_name):
    """
    Crop a region (PDF points) using PyMuPDF clip and save as JPEG.
    Returns (width_px, height_px, size_kb).
    """
    doc  = fitz.open(pdf_path)
    page = doc[page_idx]
    clip = fitz.Rect(x0, y0, x1, y1)
    pix  = page.get_pixmap(matrix=MAT, clip=clip)
    out  = os.path.join(OUT_DIR, out_name)
    pix.save(out)
    doc.close()
    kb = os.path.getsize(out) // 1024
    return pix.width, pix.height, kb


# -- DETECT MODE ---------------------------------------------------------------

def detect_page(client, img, page_num):
    """
    Ask Claude Vision to detect a written-question diagram on one page.
    Returns the parsed JSON dict from Claude.
    """
    img_b64  = pil_to_jpeg_b64(img)
    response = client.messages.create(
        model='claude-opus-4-5',
        max_tokens=512,
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
                {'type': 'text', 'text': DETECTION_PROMPT},
            ],
        }]
    )
    raw = response.content[0].text.strip()
    if raw.startswith('```'):
        lines = raw.split('\n')
        raw   = '\n'.join(lines[1:-1] if lines[-1].strip() == '```' else lines[1:])
    return json.loads(raw)


def run_detect(years, registry):
    """
    For each year, scan every Section II page with Claude Vision.
    Updates registry['papers'][year] in place.
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
            print(f'    Expected: {fname}')
            print(f'    In:       {PDF_DIR}')
            continue

        doc          = fitz.open(pdf_path)
        total_pages  = len(doc)
        doc.close()

        print(f'\n  {year}  ({os.path.basename(pdf_path)}, {total_pages} pages)')
        print(f'  Scanning pages {SECTION_II_FIRST_PAGE}-{total_pages} ...')
        year_entries = []

        for page_idx in range(SECTION_II_FIRST_PAGE - 1, total_pages):
            page_num = page_idx + 1
            try:
                img    = render_page_pil(pdf_path, page_idx)
                result = detect_page(client, img, page_num)
            except json.JSONDecodeError as e:
                print(f'    [ERR] p{page_num}: invalid JSON from Claude — {e}')
                continue
            except Exception as e:
                print(f'    [ERR] p{page_num}: {e}')
                continue

            q_num = result.get('question_number')

            if not result.get('has_diagram'):
                print(f'    p{page_num}: Q{q_num} — no diagram')
                continue

            y_px_start = result.get('y_start')
            y_px_end   = result.get('y_end')
            desc       = result.get('description', '')

            if y_px_start is None or y_px_end is None:
                print(f'    [WARN] p{page_num}: Q{q_num} has_diagram=true but missing y coords')
                continue

            # Claude returns pixel coords; convert to PDF points for registry
            y0_pt = round(y_px_start / ZOOM)
            y1_pt = round(y_px_end   / ZOOM)

            print(f'    p{page_num}: Q{q_num} — y_pt={y0_pt}-{y1_pt}  "{desc}"')

            year_entries.append({
                'question':    q_num,
                'page_idx':    page_idx,
                'x0':          X0_FULL,
                'y0':          y0_pt,
                'x1':          X1_FULL,
                'y1':          y1_pt,
                'description': desc,
                'source':      'claude-vision',
            })

        # Sort by question number (None sorts to end)
        year_entries.sort(key=lambda e: e.get('question') or 9999)
        registry['papers'][str(year)] = year_entries
        print(f'  -> {len(year_entries)} diagram(s) recorded for {year}')


# -- CROP MODE -----------------------------------------------------------------

def run_crop(years, registry):
    """Crop and save all diagram images for each year using registry coordinates."""
    total_done = total_skip = 0

    for year in years:
        entries = registry.get('papers', {}).get(str(year), [])
        if not entries:
            print(f'  [WARN] {year}: no entries in registry.')
            print(f'    Fix:  python extract_written_diagrams.py --detect --year {year}')
            continue

        pdf_path = find_pdf(year)
        if not pdf_path:
            print(f'  [SKIP] {year}: PDF not found in {PDF_DIR}')
            total_skip += len(entries)
            continue

        print(f'\n  {year}')

        for entry in entries:
            q        = entry.get('question')
            page_idx = entry.get('page_idx')
            x0       = entry.get('x0', X0_FULL)
            y0       = entry.get('y0')
            x1       = entry.get('x1', X1_FULL)
            y1       = entry.get('y1')

            if None in (q, page_idx, y0, y1):
                print(f'  [SKIP] Q{q}: missing coordinates in registry')
                total_skip += 1
                continue

            fname = f'{SUBJECT}_{year}_Q{q}_stimulus.jpg'
            badge = '[AI]' if entry.get('source') == 'claude-vision' else '[--]'

            try:
                w, h, kb = crop_and_save(pdf_path, page_idx, x0, y0, x1, y1, fname)
                print(f'  {badge} Q{q:2d}  -> {fname}  ({w}x{h} px, {kb} KB)')
                total_done += 1
            except Exception as e:
                print(f'  [ERR] Q{q}: {e}')
                total_skip += 1

    return total_done, total_skip


# -- ENTRY POINT ---------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description='CramIT Written Question Diagram Extractor',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python extract_written_diagrams.py                       # crop all years
  python extract_written_diagrams.py --year 2025           # crop 2025 only
  python extract_written_diagrams.py --detect              # Vision-detect all years
  python extract_written_diagrams.py --detect --year 2026  # detect new paper
        """
    )
    parser.add_argument('--detect', action='store_true',
                        help='Use Claude Vision to detect diagrams (requires ANTHROPIC_API_KEY)')
    parser.add_argument('--year', type=int,
                        help='Process one year only (e.g. --year 2026)')
    args = parser.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)

    years = [args.year] if args.year else sorted(PAPERS.keys())
    mode  = 'DETECT (Claude Vision) + CROP' if args.detect else 'CROP (from registry)'

    print('=' * 55)
    print('  CramIT Written Diagram Extractor')
    print('=' * 55)
    print(f'  Mode    : {mode}')
    print(f'  Years   : {years}')
    print(f'  PDFs    : {PDF_DIR}')
    print(f'  Output  : {OUT_DIR}')
    print(f'  Registry: {REGISTRY_PATH}')
    print()

    # Load or bootstrap registry
    if os.path.exists(REGISTRY_PATH):
        registry = load_registry()
    else:
        print('No registry found — bootstrapping from hardcoded 2020-2025 coordinates...')
        registry = bootstrap_registry()

    # Optionally run detection (updates registry)
    if args.detect:
        run_detect(years, registry)
        save_registry(registry)
        print()

    # Always crop from registry (for the requested years)
    done, skipped = run_crop(years, registry)

    print()
    print(f'Done.  {done} files saved,  {skipped} skipped.')
    if skipped:
        print('Tip: run --detect to refresh coordinates for problem entries.')
    print(f'Files saved to: {OUT_DIR}')


if __name__ == '__main__':
    main()
