#!/usr/bin/env python3
"""
CramIT -- Intelligent Diagram Extractor v3
==========================================
Extracts diagrams from HSC exam PDFs, correctly separating the question
stimulus from the answer-option images so the quiz can render them differently.

THREE diagram types:
  stimulus_only        -- question has a diagram; A/B/C/D options are text.
                          Output: _Q{n}_stimulus.jpg
  options_only         -- A/B/C/D options are each an image; no question diagram.
                          Output: _Q{n}_A.jpg  _Q{n}_B.jpg  _Q{n}_C.jpg  _Q{n}_D.jpg
  stimulus_and_options -- question diagram + image options.
                          Output: _Q{n}_stimulus.jpg + _Q{n}_A/B/C/D.jpg

Two modes:

  CROP (default -- no API key needed):
      python extract_maths_diagrams.py
      python extract_maths_diagrams.py --year 2024

      Crops diagrams from diagram_registry.json.
      On first run the registry is auto-bootstrapped from hardcoded coordinates.
      stimulus_only crops are precise; option splits are approximate equal strips.
      Run --detect to replace with Claude Vision precise coordinates.

  DETECT (requires ANTHROPIC_API_KEY):
      python extract_maths_diagrams.py --detect
      python extract_maths_diagrams.py --detect --year 2026

      Sends each MC page to Claude Vision, which identifies each diagram type and
      returns separate bounding boxes for the stimulus and every option A/B/C/D.
      Updates diagram_registry.json with precise coordinates.
      Use for any new exam year -- no manual calibration needed.

Workflow for a new exam paper:
  1. Copy PDF to the NESA Exams folder (see PDF_DIR)
  2. Add the filename to the PAPERS dict below
  3. Run:  python extract_maths_diagrams.py --detect --year 2026
  4. Check output images in ./diagrams/
  5. Commit diagram_registry.json + new images to git

Quiz question data structure (Stage 3):
  {
    image: '/diagrams/mathematics-standard-2_2021_Q7_stimulus.jpg',  // or null
    optionImages: [                                                    // or null
      '/diagrams/mathematics-standard-2_2021_Q7_A.jpg',
      '/diagrams/mathematics-standard-2_2021_Q7_B.jpg',
      '/diagrams/mathematics-standard-2_2021_Q7_C.jpg',
      '/diagrams/mathematics-standard-2_2021_Q7_D.jpg',
    ]
  }

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


# -- PATHS ---------------------------------------------------------------------

SCRIPT_DIR    = os.path.dirname(os.path.abspath(__file__))
OUT_DIR       = os.path.join(SCRIPT_DIR, 'diagrams')
REGISTRY_PATH = os.path.join(SCRIPT_DIR, 'diagram_registry.json')

_DEFAULT_PDF_DIR = os.path.normpath(
    os.path.join(SCRIPT_DIR, '..', '..', 'NESA Exams Folder', 'Maths Standard 2')
)
PDF_DIR = os.environ.get('PDF_DIR', _DEFAULT_PDF_DIR)

SUBJECT    = 'mathematics-standard-2'
RENDER_DPI = 150   # ~1240 x 1755 px per A4 page


# -- PAPERS --------------------------------------------------------------------
# Add new years here when NESA releases new papers.

PAPERS = {
    2020: '2020-hsc-mathematics-standard-2.pdf',
    2021: '2021-hsc-mathematics-standard-2.pdf',
    2022: '2022-hsc-mathematics-standard-2.pdf',
    2023: '2023-hsc-maths-std-2.pdf',
    2024: '2024-hsc-maths-std-2.pdf',
    2025: '2025-hsc-maths-standard-2.pdf',
    # 2026: '2026-hsc-maths-standard-2.pdf',  # <- add here when available
}

# Pages to scan in --detect mode (MC section spans pages 2-8 across all years).
MC_PAGES = list(range(2, 9))


# -- BOOTSTRAP DATA ------------------------------------------------------------
# Verified pixel coords for 2020-2025 at RENDER_DPI=150 (1240x1755 px per page).
#
# Types:
#   'stimulus_only'
#       y_start/y_end = the single question diagram.
#       Output: _Q{n}_stimulus.jpg
#
#   'options_only'
#       y_start/y_end = total bbox covering all 4 option images.
#       Bootstrap splits into 4 equal strips (approximate -- run --detect to fix).
#       Output: _Q{n}_A.jpg  _Q{n}_B.jpg  _Q{n}_C.jpg  _Q{n}_D.jpg
#
#   'stimulus_and_options'
#       y_start/stimulus_y_end = question stimulus.
#       stimulus_y_end/y_end = the 4 option images (equal-split for bootstrap).
#       Output: _Q{n}_stimulus.jpg + _Q{n}_A/B/C/D.jpg

BOOTSTRAP_CROPS = [
    # -- 2020 --
    {'year': 2020, 'q':  1, 'page': 2, 'y_start':  465, 'y_end':  980,
     'type': 'options_only',
     'desc': '4 graphs as ABCD options'},

    {'year': 2020, 'q':  7, 'page': 4, 'y_start':  205, 'y_end':  805,
     'type': 'options_only',
     'desc': '4 histograms as ABCD options'},

    {'year': 2020, 'q':  8, 'page': 4, 'y_start':  885, 'y_end': 1600,
     'type': 'stimulus_and_options', 'stimulus_y_end': 1150,
     'desc': 'Score table'},

    {'year': 2020, 'q':  9, 'page': 5, 'y_start':  348, 'y_end':  880,
     'type': 'options_only',
     'desc': '4 network diagrams as ABCD options'},

    {'year': 2020, 'q': 12, 'page': 6, 'y_start':  635, 'y_end': 1220,
     'type': 'options_only',
     'desc': '4 scatter plots as ABCD options'},

    {'year': 2020, 'q': 15, 'page': 8, 'y_start':  200, 'y_end':  320,
     'type': 'stimulus_only',
     'desc': 'Rectangular table grid'},

    # -- 2021 --
    {'year': 2021, 'q':  2, 'page': 3, 'y_start':  195, 'y_end':  380,
     'type': 'stimulus_only',
     'desc': 'Network diagram'},

    {'year': 2021, 'q':  3, 'page': 3, 'y_start':  800, 'y_end':  945,
     'type': 'stimulus_only',
     'desc': 'Stem-and-leaf plot'},

    {'year': 2021, 'q':  7, 'page': 5, 'y_start':  200, 'y_end': 1660,
     'type': 'stimulus_and_options', 'stimulus_y_end': 540,
     'desc': 'Histogram of downloads per day'},

    {'year': 2021, 'q': 10, 'page': 6, 'y_start':  999, 'y_end': 1530,
     'type': 'options_only',
     'desc': '4 exponential graphs as ABCD options'},

    {'year': 2021, 'q': 11, 'page': 7, 'y_start':  380, 'y_end':  660,
     'type': 'stimulus_only',
     'desc': 'Probability tree diagram'},

    # -- 2022 --
    {'year': 2022, 'q':  1, 'page': 2, 'y_start':  463, 'y_end':  855,
     'type': 'options_only',
     'desc': '4 frequency curves as ABCD options'},

    {'year': 2022, 'q':  2, 'page': 2, 'y_start':  996, 'y_end': 1565,
     'type': 'options_only',
     'desc': '4 line graphs as ABCD options'},

    {'year': 2022, 'q':  3, 'page': 3, 'y_start':  175, 'y_end':  600,
     'type': 'stimulus_only',
     'desc': 'Network diagram with critical path'},

    {'year': 2022, 'q': 13, 'page': 7, 'y_start':  260, 'y_end':  745,
     'type': 'stimulus_only',
     'desc': 'Z-score table and normal distribution curve'},

    {'year': 2022, 'q': 15, 'page': 8, 'y_start':  235, 'y_end': 1222,
     'type': 'stimulus_and_options', 'stimulus_y_end': 620,
     'desc': 'Cumulative frequency graph'},

    # -- 2023 --
    {'year': 2023, 'q':  5, 'page': 4, 'y_start':  260, 'y_end':  945,
     'type': 'options_only',
     'desc': '4 petrol pump diagrams as ABCD options'},

    {'year': 2023, 'q':  8, 'page': 5, 'y_start':  540, 'y_end': 1185,
     'type': 'stimulus_only',
     'desc': 'Die, spinner and score table'},

    {'year': 2023, 'q': 12, 'page': 7, 'y_start':  290, 'y_end':  660,
     'type': 'stimulus_only',
     'desc': 'Cylindrical pipe cross-section'},

    {'year': 2023, 'q': 14, 'page': 8, 'y_start':  240, 'y_end':  555,
     'type': 'stimulus_only',
     'desc': 'Directed network diagram'},

    # -- 2024 --
    {'year': 2024, 'q':  2, 'page': 2, 'y_start':  750, 'y_end': 1080,
     'type': 'stimulus_only',
     'desc': 'Linear function graph'},

    {'year': 2024, 'q':  4, 'page': 3, 'y_start':  535, 'y_end': 1130,
     'type': 'stimulus_only',
     'desc': 'Country map with regions'},

    {'year': 2024, 'q':  5, 'page': 4, 'y_start':  230, 'y_end':  490,
     'type': 'stimulus_only',
     'desc': 'Data table'},

    {'year': 2024, 'q':  6, 'page': 4, 'y_start':  855, 'y_end': 1015,
     'type': 'stimulus_only',
     'desc': 'Triangle diagram'},

    {'year': 2024, 'q': 15, 'page': 8, 'y_start':  780, 'y_end': 1494,
     'type': 'stimulus_and_options', 'stimulus_y_end': 1000,
     'desc': 'Box plot question data'},

    # -- 2025 --
    {'year': 2025, 'q':  1, 'page': 2, 'y_start':  465, 'y_end':  660,
     'type': 'stimulus_only',
     'desc': 'Network diagram'},

    {'year': 2025, 'q':  2, 'page': 2, 'y_start': 1050, 'y_end': 1565,
     'type': 'options_only',
     'desc': '4 graphs as ABCD options'},

    {'year': 2025, 'q':  3, 'page': 3, 'y_start':  215, 'y_end':  510,
     'type': 'stimulus_only',
     'desc': 'Weighted network diagram'},

    {'year': 2025, 'q':  8, 'page': 5, 'y_start':  230, 'y_end': 1304,
     'type': 'stimulus_and_options', 'stimulus_y_end': 600,
     'desc': 'Histogram of data'},
]


# -- DETECTION PROMPT ----------------------------------------------------------

DETECTION_PROMPT = """\
This is a rendered page from an HSC Mathematics Standard 2 exam paper \
(Multiple Choice section, Questions 1-15).

For each question on this page that uses visual elements, identify the DIAGRAM TYPE \
and return SEPARATE bounding boxes for the question stimulus and each answer option image.

THREE diagram types:

1. stimulus_only
   The question has a diagram/graph/table as question data.
   The answer options A B C D are TEXT only (numbers, fractions, words).

2. options_only
   The answer options A B C D are each a distinct image (graph, chart, diagram).
   There is no separate question diagram above them.

3. stimulus_and_options
   BOTH: a question diagram exists (the stimulus) AND A B C D are each distinct images.
   Example: a histogram at the top showing data, then 4 cumulative frequency graphs
   labelled A B C D below it.

Return ONLY this JSON (no markdown fences, no explanation):
{
  "diagrams": [
    {
      "question_number": 7,
      "type": "stimulus_and_options",
      "stimulus": {
        "y_start": 200,
        "y_end": 480,
        "description": "histogram showing number of downloads per day"
      },
      "options": [
        {"label": "A", "y_start": 530, "y_end": 780},
        {"label": "B", "y_start": 800, "y_end": 1050},
        {"label": "C", "y_start": 1070, "y_end": 1330},
        {"label": "D", "y_start": 1350, "y_end": 1650}
      ]
    },
    {
      "question_number": 3,
      "type": "stimulus_only",
      "stimulus": {
        "y_start": 175,
        "y_end": 600,
        "description": "network diagram with critical path"
      },
      "options": null
    },
    {
      "question_number": 1,
      "type": "options_only",
      "stimulus": null,
      "options": [
        {"label": "A", "y_start": 463, "y_end": 614},
        {"label": "B", "y_start": 630, "y_end": 781},
        {"label": "C", "y_start": 797, "y_end": 948},
        {"label": "D", "y_start": 964, "y_end": 1115}
      ]
    }
  ]
}

Coordinate rules:
- y_start and y_end are pixel distances from the TOP of this image (0 = top edge)
- Add 20px padding above y_start and below y_end for each element
- x coordinates are not needed -- we always crop the full page width
- For options: give EACH of A, B, C, D its OWN separate y_start and y_end
- DO NOT include: question text, the letters A/B/C/D themselves, \
page numbers, NESA headers or footers
- If no diagrams on this page, return: {"diagrams": []}
- Return ONLY raw JSON"""


# -- REGISTRY HELPERS ----------------------------------------------------------

def load_registry():
    if os.path.exists(REGISTRY_PATH):
        with open(REGISTRY_PATH, 'r') as f:
            return json.load(f)
    return {'version': '3', 'subject': SUBJECT, 'papers': {}}


def save_registry(registry):
    with open(REGISTRY_PATH, 'w') as f:
        json.dump(registry, f, indent=2)
    print(f'Registry saved -> {os.path.basename(REGISTRY_PATH)}')


def bootstrap_registry():
    """
    Build diagram_registry.json v3 from BOOTSTRAP_CROPS.

    stimulus_only:         precise single bbox.
    options_only:          total bbox split into 4 equal horizontal strips.
    stimulus_and_options:  stimulus up to stimulus_y_end; remaining height split x4.

    NOTE: The option splits for options_only and stimulus_and_options are approximate.
          Run --detect afterwards to replace with precise Claude Vision coordinates.
    """
    registry = {'version': '3', 'subject': SUBJECT, 'papers': {}}
    labels   = ['A', 'B', 'C', 'D']

    for c in BOOTSTRAP_CROPS:
        year, q, page   = c['year'], c['q'], c['page']
        y_start, y_end  = c['y_start'], c['y_end']
        diag_type, desc = c['type'], c['desc']

        entry = {
            'question': q,
            'page':     page,
            'type':     diag_type,
            'source':   'hardcoded-bootstrap',
        }

        if diag_type == 'stimulus_only':
            entry['stimulus'] = {'y_start': y_start, 'y_end': y_end, 'description': desc}
            entry['options']  = None

        elif diag_type == 'options_only':
            height = y_end - y_start
            each   = height // 4
            entry['stimulus'] = None
            entry['options']  = [
                {'label': l,
                 'y_start': y_start + i * each,
                 'y_end':   y_start + (i + 1) * each if i < 3 else y_end}
                for i, l in enumerate(labels)
            ]

        elif diag_type == 'stimulus_and_options':
            stim_end   = c['stimulus_y_end']
            opts_start = stim_end + 20   # 20px gap below stimulus
            height     = y_end - opts_start
            each       = height // 4
            entry['stimulus'] = {'y_start': y_start, 'y_end': stim_end, 'description': desc}
            entry['options']  = [
                {'label': l,
                 'y_start': opts_start + i * each,
                 'y_end':   opts_start + (i + 1) * each if i < 3 else y_end}
                for i, l in enumerate(labels)
            ]

        registry['papers'].setdefault(str(year), []).append(entry)

    save_registry(registry)
    stim_count = sum(
        1 for yr in registry['papers'].values()
        for e in yr if e['type'] == 'stimulus_only'
    )
    opts_count = sum(
        1 for yr in registry['papers'].values()
        for e in yr if e['type'] in ('options_only', 'stimulus_and_options')
    )
    print(f'Bootstrapped: {stim_count} stimulus-only, {opts_count} with option images.')
    print('NOTE: option splits are approximate. Run --detect for precise coordinates.\n')
    return registry


# -- PDF / IMAGE UTILITIES -----------------------------------------------------

def find_pdf(year):
    filename = PAPERS.get(year)
    if not filename:
        return None
    for search_dir in [PDF_DIR, SCRIPT_DIR]:
        candidate = os.path.join(search_dir, filename)
        if os.path.exists(candidate):
            return candidate
    return None


def render_page(pdf_path, page_num):
    doc  = fitz.open(pdf_path)
    page = doc[page_num - 1]
    mat  = fitz.Matrix(RENDER_DPI / 72, RENDER_DPI / 72)
    pix  = page.get_pixmap(matrix=mat, colorspace=fitz.csRGB)
    img  = Image.frombytes('RGB', [pix.width, pix.height], pix.samples)
    doc.close()
    return img


def crop_region(img, y_start, y_end, h_margin=16):
    y_end = min(y_end, img.height)
    return img.crop((h_margin, y_start, img.width - h_margin, y_end))


def pil_to_jpeg_b64(img):
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=85)
    return base64.b64encode(buf.getvalue()).decode('utf-8')


def save_crop(img, year, q, suffix):
    """
    Crop and save one image element.
    suffix is 'stimulus', 'A', 'B', 'C', or 'D'.
    Returns (filename, size_kb).
    """
    filename = f'{SUBJECT}_{year}_Q{q}_{suffix}.jpg'
    out_path = os.path.join(OUT_DIR, filename)
    img.save(out_path, 'JPEG', quality=92)
    kb = os.path.getsize(out_path) // 1024
    return filename, kb


# -- CLAUDE VISION DETECTION ---------------------------------------------------

def detect_page(client, page_img, page_num):
    """
    Ask Claude Vision to identify all diagrams on one rendered page image.
    Returns a list of diagram dicts matching the detection prompt structure.
    """
    img_b64 = pil_to_jpeg_b64(page_img)

    response = client.messages.create(
        model='claude-opus-4-5',
        max_tokens=1536,
        messages=[{
            'role': 'user',
            'content': [
                {
                    'type':   'image',
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

    # Strip accidental markdown fences
    if raw.startswith('```'):
        lines = raw.split('\n')
        raw   = '\n'.join(lines[1:-1] if lines[-1].strip() == '```' else lines[1:])

    parsed   = json.loads(raw)
    diagrams = parsed.get('diagrams', [])

    if diagrams:
        print(f'    p{page_num}: {len(diagrams)} diagram(s)')
        for d in diagrams:
            q     = d.get('question_number', '?')
            dtype = d.get('type', '?')
            stim  = d.get('stimulus') or {}
            opts  = d.get('options') or []
            s_range = (f"{stim.get('y_start','')}-{stim.get('y_end','')}"
                       if stim else 'none')
            print(f'      Q{q} [{dtype}]  stimulus:{s_range}  options:{len(opts)}')
    else:
        print(f'    p{page_num}: no diagrams')

    return diagrams


def run_detect(years, registry):
    """
    Run Claude Vision detection for each year's MC pages.
    Updates registry in place.
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
                    'question': d.get('question_number'),
                    'page':     page_num,
                    'type':     d.get('type', 'stimulus_only'),
                    'stimulus': d.get('stimulus'),
                    'options':  d.get('options'),
                    'source':   'claude-vision',
                })

        registry['papers'][str(year)] = year_entries
        print(f'  -> {len(year_entries)} diagram(s) recorded for {year}')


# -- CROP FROM REGISTRY --------------------------------------------------------

def crop_entry(page_img, entry, year, badge):
    """
    Crop and save all image files for one registry entry.
    Returns (files_saved, files_skipped).
    """
    q         = entry.get('question')
    diag_type = entry.get('type', 'stimulus_only')
    done = skip = 0

    try:
        # -- stimulus --
        if diag_type in ('stimulus_only', 'stimulus_and_options'):
            stim = entry.get('stimulus') or {}
            y1, y2 = stim.get('y_start'), stim.get('y_end')
            if y1 is not None and y2 is not None:
                cropped = crop_region(page_img, y1, y2)
                fname, kb = save_crop(cropped, year, q, 'stimulus')
                print(f'  {badge} Q{q:2d}  [stimulus]  -> {fname} ({kb} KB)')
                done += 1
            else:
                print(f'  [WARN] {year} Q{q}: stimulus entry missing y_start/y_end')
                skip += 1

        # -- options A/B/C/D --
        if diag_type in ('options_only', 'stimulus_and_options'):
            opts = entry.get('options') or []
            if not opts:
                print(f'  [WARN] {year} Q{q}: no options in registry entry')
                skip += 1
            for opt in opts:
                label = opt.get('label', '?')
                y1, y2 = opt.get('y_start'), opt.get('y_end')
                if y1 is None or y2 is None:
                    print(f'  [WARN] {year} Q{q} option {label}: missing coordinates')
                    skip += 1
                    continue
                cropped = crop_region(page_img, y1, y2)
                fname, kb = save_crop(cropped, year, q, label)
                print(f'  {badge} Q{q:2d}  [option {label}]  -> {fname} ({kb} KB)')
                done += 1

    except Exception as e:
        print(f'  [ERR] {year} Q{q}: {e}')
        skip += 1

    return done, skip


def run_crop(years, registry):
    """Crop and save all diagrams for each year using registry coordinates."""
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

        print(f'\n  {year}')
        page_cache = {}

        for entry in entries:
            page = entry.get('page')
            if page is None:
                total_skip += 1
                continue

            if page not in page_cache:
                page_cache[page] = render_page(pdf_path, page)

            src   = entry.get('source', '')
            badge = '[AI]' if src == 'claude-vision' else '[--]'
            done, skip = crop_entry(page_cache[page], entry, year, badge)
            total_done += done
            total_skip += skip

    return total_done, total_skip


# -- ENTRY POINT ---------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description='CramIT Intelligent Diagram Extractor v3',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python extract_maths_diagrams.py                       # crop all years
  python extract_maths_diagrams.py --year 2024           # crop 2024 only
  python extract_maths_diagrams.py --detect              # Vision-detect all years
  python extract_maths_diagrams.py --detect --year 2026  # detect new paper
        """
    )
    parser.add_argument('--detect', action='store_true',
                        help='Run Claude Vision to detect diagrams and update registry')
    parser.add_argument('--year', type=int,
                        help='Process one year only (e.g. --year 2026)')
    args = parser.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)

    years = [args.year] if args.year else sorted(PAPERS.keys())
    mode  = 'DETECT (Claude Vision)' if args.detect else 'CROP (from registry)'

    print('=' * 55)
    print('  CramIT Diagram Extractor v3')
    print('=' * 55)
    print(f'  Mode    : {mode}')
    print(f'  Years   : {years}')
    print(f'  PDFs    : {PDF_DIR}')
    print(f'  Output  : {OUT_DIR}')
    print(f'  Registry: {REGISTRY_PATH}')
    print()

    # -- DETECT MODE -----------------------------------------------------------
    if args.detect:
        registry = load_registry()
        run_detect(years, registry)
        save_registry(registry)
        print()
        print('Detection complete. Now crop the diagrams:')
        print('  python extract_maths_diagrams.py')
        return

    # -- CROP MODE -------------------------------------------------------------
    if not os.path.exists(REGISTRY_PATH):
        print('No registry found - bootstrapping from hardcoded coordinates...')
        registry = bootstrap_registry()
    else:
        registry = load_registry()
        # Upgrade old v2 registry (flat entries, no type field) to v3
        if registry.get('version', '2') != '3':
            print(f'Registry version {registry.get("version","?")} detected - upgrading to v3...')
            registry = bootstrap_registry()

    done, skipped = run_crop(years, registry)

    print()
    print(f'Done.  {done} files saved,  {skipped} skipped.')
    if skipped:
        print('Tip: run --detect to auto-fix missing or approximate coordinates.')
    print(f'Files saved to: {OUT_DIR}')


if __name__ == '__main__':
    main()
