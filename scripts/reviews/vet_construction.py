# -*- coding: utf-8 -*-
"""Hand-typed verdicts from the VET Construction written-answer review, 2026-09-01.

Every one of the 23 questions was read against NESA's committed sample answer and
criteria rows in data/answer-key/written/vet-construction.json. Mechanical triage
(keyword absent from the answer, low term overlap, length vs marks) ordered the reading
queue and decided nothing -- see docs/porting-playbook.md section 6.

Consumed by scripts/build_review_ledger.py, which adds the sample-answer fingerprints.

Verdicts
--------
ok                  compared, bank agrees with NESA
corrected           a defect was found and fixed in this session
divergent-accepted  the bank legitimately reads unlike NESA's text (note required)
"""

REVIEWED_AT = "2026-09-01"

_ALL = ["modelAnswer", "keywords", "bandDescriptors"]

REVIEWED = {
    # --- 2021 -------------------------------------------------------------------------
    ("2021", "16(a)"): {
        "verdict": "corrected", "fields": _ALL,
        "note": ("Model answer and acceptableAnswers already matched NESA (chisel; firmer, "
                 "bevelled edge, mortice). Corrected only in that it had NO keywords at all "
                 "— the AI marker was being sent an empty concept list. keywords/minKeywords "
                 "added from NESA's own alternatives; the offline path is unchanged because "
                 "acceptableAnswers takes priority over keywords in buildKeywordFeedback(). "
                 "bandDescriptors: NESA prints ONE criteria row (all-or-nothing), so partial "
                 "and minimal state its non-attainment — authored text, not NESA's."),
    },
    ("2021", "16(b)"): {
        "verdict": "ok", "fields": _ALL,
        "note": None,
    },

    # --- 2022 -------------------------------------------------------------------------
    ("2022", "16(a)"): {
        "verdict": "ok", "fields": _ALL,
        "note": None,
    },
    ("2022", "17(c)"): {
        "verdict": "corrected", "fields": _ALL,
        "note": ("Two defects. (1) The stem read 'Identify the meaning of the symbols shown "
                 "(RWT and tree symbol)' — naming the tree GIVES AWAY one of the two marks. "
                 "Restored to the paper's own wording, 'Identify each of the architectural "
                 "symbols shown.' (2) The model answer attributed removal to '(the specific "
                 "marking on the plan)', which says nothing; the actual indicator, visible in "
                 "the committed crop, is the BROKEN (dashed) outline against the solid one "
                 "used for RWT. Both answers themselves were right and unchanged."),
    },
    ("2022", "19(a)"): {
        "verdict": "corrected", "fields": _ALL,
        "note": ("Model answer fabricated BOTH of the stimulus table's band labels: it said "
                 "3700 kg falls in a '3001-4000 kg' range and 54 km in a '51-60 km' range. "
                 "The table (crop verified) is in TONNES — 0-2.99 / 3.00-4.99 / 5.00-6.99 / "
                 "7.00-8.99 — with distance columns 1-30 / 31-50 / 51-70. Neither quoted band "
                 "exists, and the kg-to-tonne conversion that the question actually tests was "
                 "absent. NESA's sample reads '3700 kg 3.00-4.99 tonne weight range 51-70 km "
                 "distance = $450.00'. The $450 answer was right, so CI passed throughout — "
                 "the same failure class as Multimedia 2022 Q2. Also had no keywords; added."),
    },

    # --- 2023 -------------------------------------------------------------------------
    ("2023", "16(a)(i)"): {
        "verdict": "corrected", "fields": _ALL,
        "note": ("acceptableAnswers omitted 'sliding', which is the FIRST alternative NESA "
                 "lists ('Sliding saw, Compound saw, Mitre saw, Cut off saw'), so a student "
                 "writing NESA's own accepted answer was marked incorrect. Added, along with "
                 "the missing keywords/minKeywords. 'chop saw' is kept: not in NESA's list, "
                 "but a genuine synonym. bandDescriptors: one official row, as 2021 16(a)."),
    },
    ("2023", "18(b)"): {
        "verdict": "ok", "fields": _ALL,
        "note": ("All five symbol identifications match NESA (window, sink, stove top, "
                 "toilet, sliding door). The bank's parenthetical descriptions of each plan "
                 "symbol were checked against the committed crop and are accurate."),
    },
    ("2023", "19(b)(i)"): {
        "verdict": "corrected", "fields": _ALL,
        "note": ("The worst defect found. The model answer's headline result was 2.61 m3, "
                 "computed from the shed's OUTER PERIMETER only; NESA's answer is 2.99 m3 "
                 "and the drawing is captioned 'the hidden detail of the EDGE AND CENTRE "
                 "beams'. The bank omitted the centre beam entirely and then explained the "
                 "discrepancy away as 'corners (overlap) giving approximately 2.61-2.99 m3 "
                 "depending on method' — a fabricated reconciliation. The stem compounded it "
                 "by describing '300mm x 300mm PERIMETER beam footings'; restored to the "
                 "paper's own wording. Answer rewritten to NESA's method (2 x 8.5 = 17 m at "
                 "1.53 m3; three cross beams at 6.0 - 2 x 0.3 = 5.4 m, 16.2 m at 1.46 m3; "
                 "total 2.99 m3), keeping the 2.61 route named as the common error. keywords "
                 "'29' and '2.61' removed — they credited the wrong method."),
    },

    # --- 2024 -------------------------------------------------------------------------
    ("2024", "16(a)"): {
        "verdict": "ok", "fields": _ALL,
        "note": None,
    },
    ("2024", "16(b)"): {
        "verdict": "ok", "fields": _ALL,
        "note": ("Bank lists cord, test-and-tag, guards, belt condition/fitting and dust "
                 "extraction — a subset of NESA's list, which also offers casing inspection "
                 "and operator training. A subset is what a 3-mark answer needs; not a gap."),
    },
    ("2024", "19(a)"): {
        "verdict": "divergent-accepted", "fields": _ALL,
        "note": ("NESA's sample answer extracts as mangled equation layout — '!3! 4! + = 5 4 "
                 "+ 6 + 8 + 3 + 5 = 26 m' — so the bank's worked prose necessarily reads "
                 "nothing like it. Compared numerically instead: hypotenuse 5, perimeter 26 m, "
                 "both agree. Same standing exception as the Maths subjects."),
    },
    ("2024", "19(b)"): {
        "verdict": "divergent-accepted", "fields": _ALL,
        "note": ("NESA's sample extracts as mangled equation layout — 'pr2 12 ... 0.471 m3'. "
                 "Compared numerically: slab 7.2 m3, hole 0.471 m3, net 6.73 m3, all agree. "
                 "Keyword 'pi' is two characters, so keywordHit() can fire on any student "
                 "word beginning 'pi' (e.g. 'pipe'); left as authored, noted as loose."),
    },

    # --- 2025 -------------------------------------------------------------------------
    ("2025", "16(a)"): {"verdict": "ok", "fields": _ALL, "note": None},
    ("2025", "16(b)"): {"verdict": "ok", "fields": _ALL, "note": None},
    ("2025", "17(a)"): {"verdict": "ok", "fields": _ALL, "note": None},
    ("2025", "17(b)"): {"verdict": "ok", "fields": _ALL, "note": None},
    ("2025", "17(c)"): {
        "verdict": "ok", "fields": _ALL,
        "note": ("Covers NESA's secure storage, sign-in/out, fencing/lighting/cameras, racks "
                 "and covers, and adds asset engraving — a reasonable extension, not a "
                 "divergence."),
    },
    ("2025", "18(a)"): {"verdict": "ok", "fields": _ALL, "note": None},
    ("2025", "18(b)"): {
        "verdict": "corrected", "fields": _ALL,
        "note": ("The stem named 'the horizontal sliding window symbol shown', which IS the "
                 "answer to the third of three marks. Restored to the paper's own wording: "
                 "'Identify the meaning of the following symbols or abbreviations that are "
                 "found on construction drawings.' The three meanings themselves match NESA "
                 "(hot water, rainwater pipe, horizontal sliding window) and the model "
                 "answer's description of the arrow symbol matches the committed crop."),
    },
    ("2025", "18(c)"): {"verdict": "ok", "fields": _ALL, "note": None},
    ("2025", "20(a)"): {"verdict": "ok", "fields": _ALL, "note": None},
    ("2025", "20(b)"): {
        "verdict": "ok", "fields": _ALL,
        "note": ("Follows NESA point for point (assess and plan, mechanical aids, lifting "
                 "technique, team lifting, ergonomic design, breaks and rotation, PPE) and "
                 "carries the workplace examples the top band requires."),
    },
    ("2025", "21"): {
        "verdict": "ok", "fields": _ALL,
        "note": ("Matches NESA's substance across design for standard sizes, just-in-time "
                 "delivery, trade sequencing and Gantt charts, quantity calculation, "
                 "training and instruction, and tool maintenance. NOTE an extractor artefact, "
                 "pre-existing and not introduced by this review: because this is the LAST "
                 "question header in the document, parse_paper() runs its sample block to the "
                 "end of the PDF, so the committed sampleAnswer for the final question of "
                 "every paper also swallows the Mapping Grid. Harmless to the mark check; it "
                 "does mean this fingerprint covers more text than the sample alone."),
    },
}
