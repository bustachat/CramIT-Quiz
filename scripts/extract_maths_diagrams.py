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

  CALIBRATE (no API key needed -- recommended after bootstrap):
      python extract_maths_diagrams.py --calibrate
      python extract_maths_diagrams.py --calibrate --year 2023

      Uses PyMuPDF text extraction to find the exact pixel y-position of every
      A./B./C./D. option label in the PDF.  Sets y_start to label_y - 10px and
      y_end to the next label's y (or the section bottom for the last option).
      Automatically crops after calibrating.  No API calls needed.
      Run this once after bootstrap -- it fixes the "question text bleeding into
      option images" problem without touching x_start/x_end column splits.

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
  3. Run:  python extract_maths_diagrams.py --calibrate --year 2026
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
# Verified pixel coords for 2020-2025 at RENDER_DPI=150 (~1240x1755 px per page).
#
# Each entry directly specifies 'stimulus' and/or 'options' matching the registry
# format. No equal-split guessing -- every option has explicit coordinates.
#
# 2x2 GRID options include x_start/x_end to split left vs right column.
# VERTICAL STACK options omit x coords (full page width used automatically).
# Column split for 2x2 grids: left x=16-618, right x=622-1224.
#
# Row-split y values for 2x2 questions were derived from PDF label positions
# and confirmed against rendered debug images.
#
# NOTE: 2020 Q1/Q9/Q12 row splits are estimated from PDF H-separator lines.
#       Run --detect to replace all bootstrap coords with Claude Vision precision.

_L = {'x_start':  16, 'x_end': 618}   # left  column for 2x2 grids
_R = {'x_start': 622, 'x_end': 1224}  # right column for 2x2 grids

BOOTSTRAP_CROPS = [

    # ---- 2020 ----------------------------------------------------------------

    # Q1  p2  options_only  2x2 GRID  (row split from PDF H-separator at y=582)
    {'year': 2020, 'q':  1, 'page': 2, 'type': 'options_only',
     'stimulus': None,
     'options': [
         {**_L, 'label': 'A', 'y_start':  465, 'y_end':  579},
         {**_R, 'label': 'B', 'y_start':  465, 'y_end':  579},
         {**_L, 'label': 'C', 'y_start':  582, 'y_end':  883},
         {**_R, 'label': 'D', 'y_start':  582, 'y_end':  883},
     ]},

    # Q7  p4  options_only  2x2 GRID  (row split at ~505, confirmed debug image)
    {'year': 2020, 'q':  7, 'page': 4, 'type': 'options_only',
     'stimulus': None,
     'options': [
         {**_L, 'label': 'A', 'y_start':  205, 'y_end':  502},
         {**_R, 'label': 'B', 'y_start':  205, 'y_end':  502},
         {**_L, 'label': 'C', 'y_start':  506, 'y_end':  805},
         {**_R, 'label': 'D', 'y_start':  506, 'y_end':  805},
     ]},

    # Q8  p4  stimulus_and_options  VERTICAL options
    # (stimulus = score table; options = 4 table rows, labels at y=1421/1468/1515/1562)
    {'year': 2020, 'q':  8, 'page': 4, 'type': 'stimulus_and_options',
     'stimulus': {'y_start': 885, 'y_end': 1418,
                  'description': 'Score table'},
     'options': [
         {'label': 'A', 'y_start': 1421, 'y_end': 1465},
         {'label': 'B', 'y_start': 1468, 'y_end': 1512},
         {'label': 'C', 'y_start': 1515, 'y_end': 1559},
         {'label': 'D', 'y_start': 1562, 'y_end': 1600},
     ]},

    # Q9  p5  options_only  2x2 GRID  (options y=465-777 from H-separator; midpoint row split)
    {'year': 2020, 'q':  9, 'page': 5, 'type': 'options_only',
     'stimulus': None,
     'options': [
         {**_L, 'label': 'A', 'y_start':  465, 'y_end':  618},
         {**_R, 'label': 'B', 'y_start':  465, 'y_end':  618},
         {**_L, 'label': 'C', 'y_start':  622, 'y_end':  777},
         {**_R, 'label': 'D', 'y_start':  622, 'y_end':  777},
     ]},

    # Q12 p6  options_only  2x2 GRID  (options y=858-1195 from H-separator; midpoint row split)
    {'year': 2020, 'q': 12, 'page': 6, 'type': 'options_only',
     'stimulus': None,
     'options': [
         {**_L, 'label': 'A', 'y_start':  858, 'y_end': 1023},
         {**_R, 'label': 'B', 'y_start':  858, 'y_end': 1023},
         {**_L, 'label': 'C', 'y_start': 1027, 'y_end': 1195},
         {**_R, 'label': 'D', 'y_start': 1027, 'y_end': 1195},
     ]},

    # Q15 p8  stimulus_only
    {'year': 2020, 'q': 15, 'page': 8, 'type': 'stimulus_only',
     'stimulus': {'y_start': 200, 'y_end': 320,
                  'description': 'Rectangular table grid'},
     'options': None},

    # ---- 2021 ----------------------------------------------------------------

    # Q2  p3  stimulus_only
    {'year': 2021, 'q':  2, 'page': 3, 'type': 'stimulus_only',
     'stimulus': {'y_start': 195, 'y_end': 380,
                  'description': 'Network diagram'},
     'options': None},

    # Q3  p3  stimulus_only
    {'year': 2021, 'q':  3, 'page': 3, 'type': 'stimulus_only',
     'stimulus': {'y_start': 800, 'y_end': 945,
                  'description': 'Stem-and-leaf plot'},
     'options': None},

    # Q7  p5  stimulus_and_options  VERTICAL options
    # (confirmed VERTICAL from debug image -- green line cut through each graph)
    {'year': 2021, 'q':  7, 'page': 5, 'type': 'stimulus_and_options',
     'stimulus': {'y_start': 200, 'y_end': 540,
                  'description': 'Histogram of downloads per day'},
     'options': [
         {'label': 'A', 'y_start':  560, 'y_end':  835},
         {'label': 'B', 'y_start':  838, 'y_end': 1113},
         {'label': 'C', 'y_start': 1116, 'y_end': 1391},
         {'label': 'D', 'y_start': 1394, 'y_end': 1660},
     ]},

    # Q10 p6  options_only  2x2 GRID  (confirmed debug image; row split at midpoint ~1264)
    {'year': 2021, 'q': 10, 'page': 6, 'type': 'options_only',
     'stimulus': None,
     'options': [
         {**_L, 'label': 'A', 'y_start':  999, 'y_end': 1261},
         {**_R, 'label': 'B', 'y_start':  999, 'y_end': 1261},
         {**_L, 'label': 'C', 'y_start': 1265, 'y_end': 1530},
         {**_R, 'label': 'D', 'y_start': 1265, 'y_end': 1530},
     ]},

    # Q11 p7  stimulus_only
    {'year': 2021, 'q': 11, 'page': 7, 'type': 'stimulus_only',
     'stimulus': {'y_start': 380, 'y_end': 660,
                  'description': 'Probability tree diagram'},
     'options': None},

    # ---- 2022 ----------------------------------------------------------------

    # Q1  p2  options_only  2x2 GRID  (labels A/B at y=460, C/D at y=686; row split=684)
    {'year': 2022, 'q':  1, 'page': 2, 'type': 'options_only',
     'stimulus': None,
     'options': [
         {**_L, 'label': 'A', 'y_start':  440, 'y_end':  681},
         {**_R, 'label': 'B', 'y_start':  440, 'y_end':  681},
         {**_L, 'label': 'C', 'y_start':  684, 'y_end':  875},
         {**_R, 'label': 'D', 'y_start':  684, 'y_end':  875},
     ]},

    # Q2  p2  options_only  2x2 GRID  (labels C/D at y=1320; row split=1318)
    {'year': 2022, 'q':  2, 'page': 2, 'type': 'options_only',
     'stimulus': None,
     'options': [
         {**_L, 'label': 'A', 'y_start':  976, 'y_end': 1315},
         {**_R, 'label': 'B', 'y_start':  976, 'y_end': 1315},
         {**_L, 'label': 'C', 'y_start': 1318, 'y_end': 1585},
         {**_R, 'label': 'D', 'y_start': 1318, 'y_end': 1585},
     ]},

    # Q3  p3  stimulus_only
    {'year': 2022, 'q':  3, 'page': 3, 'type': 'stimulus_only',
     'stimulus': {'y_start': 175, 'y_end': 600,
                  'description': 'Network diagram with critical path'},
     'options': None},

    # Q13 p7  stimulus_only
    {'year': 2022, 'q': 13, 'page': 7, 'type': 'stimulus_only',
     'stimulus': {'y_start': 260, 'y_end': 745,
                  'description': 'Z-score table and normal distribution curve'},
     'options': None},

    # Q15 p8  stimulus_and_options  2x2 GRID options
    # (labels A/B at y=827, C/D at y=1044; row split=1042)
    {'year': 2022, 'q': 15, 'page': 8, 'type': 'stimulus_and_options',
     'stimulus': {'y_start': 235, 'y_end': 620,
                  'description': 'Cumulative frequency graph'},
     'options': [
         {**_L, 'label': 'A', 'y_start':  620, 'y_end': 1039},
         {**_R, 'label': 'B', 'y_start':  620, 'y_end': 1039},
         {**_L, 'label': 'C', 'y_start': 1042, 'y_end': 1242},
         {**_R, 'label': 'D', 'y_start': 1042, 'y_end': 1242},
     ]},

    # ---- 2023 ----------------------------------------------------------------

    # Q5  p4  options_only  2x2 GRID  (labels A/B at y=260, C/D at y=628; row split=626)
    {'year': 2023, 'q':  5, 'page': 4, 'type': 'options_only',
     'stimulus': None,
     'options': [
         {**_L, 'label': 'A', 'y_start':  240, 'y_end':  623},
         {**_R, 'label': 'B', 'y_start':  240, 'y_end':  623},
         {**_L, 'label': 'C', 'y_start':  626, 'y_end':  965},
         {**_R, 'label': 'D', 'y_start':  626, 'y_end':  965},
     ]},

    # Q8  p5  stimulus_only
    {'year': 2023, 'q':  8, 'page': 5, 'type': 'stimulus_only',
     'stimulus': {'y_start': 540, 'y_end': 1185,
                  'description': 'Die, spinner and score table'},
     'options': None},

    # Q12 p7  stimulus_only
    {'year': 2023, 'q': 12, 'page': 7, 'type': 'stimulus_only',
     'stimulus': {'y_start': 290, 'y_end': 660,
                  'description': 'Cylindrical pipe cross-section'},
     'options': None},

    # Q14 p8  stimulus_only
    {'year': 2023, 'q': 14, 'page': 8, 'type': 'stimulus_only',
     'stimulus': {'y_start': 240, 'y_end': 555,
                  'description': 'Directed network diagram'},
     'options': None},

    # ---- 2024 ----------------------------------------------------------------

    # Q2  p2  stimulus_only
    {'year': 2024, 'q':  2, 'page': 2, 'type': 'stimulus_only',
     'stimulus': {'y_start': 750, 'y_end': 1080,
                  'description': 'Linear function graph'},
     'options': None},

    # Q4  p3  stimulus_only
    {'year': 2024, 'q':  4, 'page': 3, 'type': 'stimulus_only',
     'stimulus': {'y_start': 535, 'y_end': 1130,
                  'description': 'Country map with regions'},
     'options': None},

    # Q5  p4  stimulus_only
    {'year': 2024, 'q':  5, 'page': 4, 'type': 'stimulus_only',
     'stimulus': {'y_start': 230, 'y_end': 490,
                  'description': 'Data table'},
     'options': None},

    # Q6  p4  stimulus_only
    {'year': 2024, 'q':  6, 'page': 4, 'type': 'stimulus_only',
     'stimulus': {'y_start': 855, 'y_end': 1015,
                  'description': 'Triangle diagram'},
     'options': None},

    # Q15 p8  stimulus_and_options  2x2 GRID options
    # (labels A/B at y=997, C/D at y=1275; row split=1273)
    {'year': 2024, 'q': 15, 'page': 8, 'type': 'stimulus_and_options',
     'stimulus': {'y_start': 780, 'y_end': 980,
                  'description': 'Box plot question data'},
     'options': [
         {**_L, 'label': 'A', 'y_start': 1000, 'y_end': 1270},
         {**_R, 'label': 'B', 'y_start': 1000, 'y_end': 1270},
         {**_L, 'label': 'C', 'y_start': 1273, 'y_end': 1514},
         {**_R, 'label': 'D', 'y_start': 1273, 'y_end': 1514},
     ]},

    # ---- 2025 ----------------------------------------------------------------

    # Q1  p2  stimulus_only
    {'year': 2025, 'q':  1, 'page': 2, 'type': 'stimulus_only',
     'stimulus': {'y_start': 465, 'y_end': 660,
                  'description': 'Network diagram'},
     'options': None},

    # Q2  p2  options_only  2x2 GRID  (labels A/B at y=1045, C/D at y=1329; row split=1327)
    {'year': 2025, 'q':  2, 'page': 2, 'type': 'options_only',
     'stimulus': None,
     'options': [
         {**_L, 'label': 'A', 'y_start': 1025, 'y_end': 1324},
         {**_R, 'label': 'B', 'y_start': 1025, 'y_end': 1324},
         {**_L, 'label': 'C', 'y_start': 1327, 'y_end': 1585},
         {**_R, 'label': 'D', 'y_start': 1327, 'y_end': 1585},
     ]},

    # Q3  p3  stimulus_only
    {'year': 2025, 'q':  3, 'page': 3, 'type': 'stimulus_only',
     'stimulus': {'y_start': 215, 'y_end': 510,
                  'description': 'Weighted network diagram'},
     'options': None},

    # Q8  p5  stimulus_and_options  2x2 GRID options
    # (labels A/B at y=651, C/D at y=1001; row split=999)
    {'year': 2025, 'q':  8, 'page': 5, 'type': 'stimulus_and_options',
     'stimulus': {'y_start': 230, 'y_end': 600,
                  'description': 'Histogram of data'},
     'options': [
         {**_L, 'label': 'A', 'y_start':  630, 'y_end':  996},
         {**_R, 'label': 'B', 'y_start':  630, 'y_end':  996},
         {**_L, 'label': 'C', 'y_start':  999, 'y_end': 1324},
         {**_R, 'label': 'D', 'y_start':  999, 'y_end': 1324},
     ]},
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

IMPORTANT LAYOUT NOTE:
Option images can be arranged in two ways:
  - VERTICAL STACK: all 4 options are full-width and stacked top-to-bottom.
    In this case x_start and x_end span the full page width.
  - 2x2 GRID: options A+B are side-by-side on one row, C+D on the row below.
    In this case A and B share the same y range but have different x ranges
    (A on the left half, B on the right half), and similarly for C and D.
Always check which layout applies and give correct x_start/x_end per option.

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
        {"label": "A", "x_start": 16, "x_end": 1224, "y_start": 530, "y_end": 780},
        {"label": "B", "x_start": 16, "x_end": 1224, "y_start": 800, "y_end": 1050},
        {"label": "C", "x_start": 16, "x_end": 1224, "y_start": 1070, "y_end": 1330},
        {"label": "D", "x_start": 16, "x_end": 1224, "y_start": 1350, "y_end": 1650}
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
      "question_number": 9,
      "type": "options_only",
      "stimulus": null,
      "options": [
        {"label": "A", "x_start":  16, "x_end": 612, "y_start": 463, "y_end": 660},
        {"label": "B", "x_start": 628, "x_end": 1224, "y_start": 463, "y_end": 660},
        {"label": "C", "x_start":  16, "x_end": 612, "y_start": 676, "y_end": 880},
        {"label": "D", "x_start": 628, "x_end": 1224, "y_start": 676, "y_end": 880}
      ]
    }
  ]
}

Coordinate rules:
- y_start and y_end are pixel distances from the TOP of this image (0 = top edge)
- x_start and x_end are pixel distances from the LEFT edge (image width is ~1240px)
- Add 20px padding around each element
- For VERTICAL STACK options: x_start=16, x_end=1224 (full width) for each option
- For 2x2 GRID options: use ~16 to ~612 for left column, ~628 to ~1224 for right column
- Stimulus always uses full page width (no x coordinates needed for stimulus)
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

    Each entry in BOOTSTRAP_CROPS already has explicit 'stimulus' and 'options'
    sub-dicts with precise pixel coordinates (no equal-split guessing).

    2x2 grid options include x_start/x_end for left/right column splitting.
    Vertical-stack options omit x coords (crop_region defaults to full width).

    Run --detect to replace hardcoded coords with Claude Vision precision.
    """
    registry = {'version': '3', 'subject': SUBJECT, 'papers': {}}

    for c in BOOTSTRAP_CROPS:
        entry = {
            'question': c['q'],
            'page':     c['page'],
            'type':     c['type'],
            'stimulus': c.get('stimulus'),
            'options':  c.get('options'),
            'source':   'hardcoded-bootstrap',
        }
        registry['papers'].setdefault(str(c['year']), []).append(entry)

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
    print('Run --detect for Claude Vision precision on any questions.\n')
    return registry


# -- LABEL-BASED CALIBRATION --------------------------------------------------

def find_label_positions(pdf_path, page_num, y_approx_min_px, y_approx_max_px):
    """
    Find the exact pixel y-position of option labels A./B./C./D. on one PDF page.

    Uses PyMuPDF text extraction -- no API calls or ML models needed.
    Searches within the approximate pixel y range (+ 100px slack each side).

    NESA format is "A." "B." "C." "D." with a trailing period.
    Falls back to bare "A" "B" "C" "D" near the left margin if the primary
    search fails (some older PDFs encode labels without the period).

    Returns {'A': int, 'B': int, 'C': int, 'D': int}  pixel y of label top,
    or None if all four labels could not be located.
    """
    scale   = RENDER_DPI / 72          # PDF points -> render pixels
    y_slack = 100 / scale              # 100px slack in PDF-point space

    y_lo = (y_approx_min_px / scale) - y_slack
    y_hi = (y_approx_max_px / scale) + y_slack

    doc   = fitz.open(pdf_path)
    page  = doc[page_num - 1]
    words = page.get_text('words')     # (x0, y0, x1, y1, word, blk, ln, wrd)
    doc.close()

    # Primary: NESA standard "A." "B." "C." "D."
    primary = {'A.': 'A', 'B.': 'B', 'C.': 'C', 'D.': 'D'}
    found   = {}

    for w in words:
        x0, y0, x1, y1, text = w[0], w[1], w[2], w[3], w[4]
        if y0 < y_lo or y0 > y_hi:
            continue
        clean = text.strip()
        if clean in primary and primary[clean] not in found:
            found[primary[clean]] = int(y0 * scale)

    if len(found) == 4:
        return found

    # Fallback: bare letter near left margin (x0 < 200 PDF points)
    for w in words:
        x0, y0, x1, y1, text = w[0], w[1], w[2], w[3], w[4]
        if y0 < y_lo or y0 > y_hi:
            continue
        clean = text.strip()
        if clean in ('A', 'B', 'C', 'D') and clean not in found and x0 < 200:
            found[clean] = int(y0 * scale)

    return found if len(found) == 4 else None


def run_calibrate(years, registry):
    """
    For every registry entry that has image options, use PDF text extraction to
    find the exact pixel y of each A./B./C./D. label, then rewrite y_start and
    y_end for every option.  Column splits (x_start/x_end) are preserved.

    Layout auto-detection:
      2x2 GRID   -- A and B labels share the same y row (within 30px)
      VERT STACK -- A, B, C, D each appear at their own y position

    Coordinate rules:
      y_start  = label_y - 10px     (10px breathing room above the letter)
      y_end    = next-row label_y - 10px   (last row keeps existing bottom)

    Updates each entry in-place and sets source = 'calibrated'.
    Call save_registry() after this function returns.
    """
    PADDING = 10
    updated = skipped = 0

    for year in years:
        pdf_path = find_pdf(year)
        if not pdf_path:
            print(f'  [SKIP] {year}: PDF not found')
            continue

        entries = registry.get('papers', {}).get(str(year), [])
        if not entries:
            print(f'  [SKIP] {year}: no registry entries')
            continue

        print(f'\n  {year}')

        for entry in entries:
            if entry.get('type') == 'stimulus_only':
                continue

            q    = entry['question']
            pg   = entry['page']
            opts = entry.get('options') or []
            if not opts:
                continue

            # Approximate y window from current registry coordinates
            all_y  = [o['y_start'] for o in opts] + [o['y_end'] for o in opts]
            bottom = max(o['y_end'] for o in opts)   # preserve existing bottom

            labels = find_label_positions(pdf_path, pg,
                                          min(all_y) - 100, max(all_y) + 100)

            if not labels or len(labels) < 4:
                print(f'  [WARN] Q{q:2d}: could not locate all 4 labels'
                      f' -- keeping existing coords')
                skipped += 1
                continue

            a_y = labels['A']
            b_y = labels['B']
            c_y = labels['C']
            d_y = labels['D']

            is_2x2 = abs(a_y - b_y) < 30   # same y row = 2x2 grid

            # --- Sanity-check label order ----------------------------------
            # For 2x2:  row-1 (A,B) must be ABOVE row-2 (C,D)
            # For vert: A < B < C < D (each label below the previous)
            if is_2x2:
                if min(c_y, d_y) <= max(a_y, b_y):
                    print(f'  [WARN] Q{q:2d}: C/D labels above A/B'
                          f' (A@{a_y} B@{b_y} C@{c_y} D@{d_y})'
                          f' -- likely picking up wrong labels, keeping bootstrap')
                    skipped += 1
                    continue
            else:
                if not (a_y < b_y < c_y < d_y):
                    print(f'  [WARN] Q{q:2d}: vertical labels out of order'
                          f' (A@{a_y} B@{b_y} C@{c_y} D@{d_y})'
                          f' -- keeping bootstrap')
                    skipped += 1
                    continue

            print(f'  [CAL] Q{q:2d}  {"2x2 " if is_2x2 else "vert"}'
                  f'  A@{a_y}  B@{b_y}  C@{c_y}  D@{d_y}')

            new_opts = []
            for opt in opts:
                lbl     = opt['label']
                lbl_y   = labels[lbl]
                new_opt = dict(opt)          # copy -- preserves x_start/x_end

                new_opt['y_start'] = lbl_y - PADDING

                if is_2x2:
                    # AB row ends just before CD row; CD row ends at bottom
                    if lbl in ('A', 'B'):
                        new_opt['y_end'] = min(c_y, d_y) - PADDING
                    else:
                        new_opt['y_end'] = bottom
                else:
                    # Vertical stack: each option ends where the next begins
                    next_y = {'A': b_y, 'B': c_y, 'C': d_y, 'D': None}[lbl]
                    new_opt['y_end'] = (next_y - PADDING) if next_y else bottom

                new_opts.append(new_opt)

            entry['options'] = new_opts
            entry['source']  = 'calibrated'
            updated += 1

    print(f'\n  Calibrated: {updated}   Skipped: {skipped}')
    return updated


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


def crop_region(img, y_start, y_end, x_start=None, x_end=None, h_margin=16):
    """
    Crop a region from a full page image.
    x_start/x_end default to full width (used for stimulus and vertical-stack options).
    Pass explicit x_start/x_end for 2x2 grid option images.
    """
    if x_start is None:
        x_start = h_margin
    if x_end is None:
        x_end = img.width - h_margin
    y_end = min(y_end, img.height)
    x_end = min(x_end, img.width)
    return img.crop((x_start, y_start, x_end, y_end))


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

    # claude-sonnet-4-6: 3x cheaper than Opus, sufficient for bounding-box detection.
    # Switch to claude-opus-4-5 only if detection accuracy becomes a problem.
    response = client.messages.create(
        model='claude-sonnet-4-6',
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
                # Use explicit x coords if present (2x2 grid layout),
                # otherwise fall back to full page width
                x1 = opt.get('x_start')
                x2 = opt.get('x_end')
                cropped = crop_region(page_img, y1, y2, x_start=x1, x_end=x2)
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
    parser.add_argument('--calibrate', action='store_true',
                        help='Auto-set option y coords from PDF label positions, then crop')
    parser.add_argument('--year', type=int,
                        help='Process one year only (e.g. --year 2026)')
    args = parser.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)

    years = [args.year] if args.year else sorted(PAPERS.keys())
    if args.detect:
        mode = 'DETECT (Claude Vision)'
    elif args.calibrate:
        mode = 'CALIBRATE (PDF text) + CROP'
    else:
        mode = 'CROP (from registry)'

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

    # -- Load / bootstrap registry (shared by --calibrate and plain crop) ------
    if not os.path.exists(REGISTRY_PATH):
        print('No registry found - bootstrapping from hardcoded coordinates...')
        registry = bootstrap_registry()
    else:
        registry = load_registry()
        # Upgrade old v2 registry (flat entries, no type field) to v3
        if registry.get('version', '2') != '3':
            print(f'Registry version {registry.get("version","?")} detected - upgrading to v3...')
            registry = bootstrap_registry()

    # -- CALIBRATE MODE --------------------------------------------------------
    if args.calibrate:
        print('Calibrating option label positions from PDF text...\n')
        run_calibrate(years, registry)
        save_registry(registry)
        print()
        print('Calibration saved. Cropping now...')
        print()

    # -- CROP (runs after calibrate, or standalone) ----------------------------
    done, skipped = run_crop(years, registry)

    print()
    print(f'Done.  {done} files saved,  {skipped} skipped.')
    if skipped:
        print('Tip: run --calibrate or --detect to fix missing coordinates.')
    print(f'Files saved to: {OUT_DIR}')


if __name__ == '__main__':
    main()
