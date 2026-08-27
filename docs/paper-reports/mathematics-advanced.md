# Fit Report — Mathematics Advanced (Stage 0)

**Subject id (proposed):** `mathematics-advanced` · **Papers:** 2020–2025 (6 years)
**Assessed:** 2026-08-27 · **Playbook:** `docs/porting-playbook.md` §1
**Verdict: GO** — with one large, quantified caveat (asset load). Reasoning below.

This is also the first live run of the porting playbook. Findings about the *playbook and
tooling* are recorded in the last section, not silently worked around.

---

## Inputs (Gate 0, item 1)

| Input | Status |
|---|---|
| Past papers, 6 years | ✅ `NESA Exams Folder/Maths Advanced/{year}_exam.pdf`, 2020–2025 |
| Marking guidelines | ✅ `{year}_marking_guidelines.pdf`, 2020–2025 |
| Marking feedback (extra, not in other subjects) | ✅ `{year}_marking_feedback.pdf` — NESA's notes from the marking centre. Not required by any stage; see tooling note 2 |
| Official NESA syllabus | ❌ **not saved.** Stage 2 is blocked until the owner is asked and it is downloaded |

All six front pages read "Mathematics Advanced", "Working time – 3 hours", "Total marks: 100" —
this is the full HSC paper, not an Extension slice.

Acquisition path: **A (human, local)**. Path B is not applicable — the Content Agent cannot
fetch marking guidelines at all (playbook §1, Source acquisition).

---

## Test 1 — Format fit: **PASS** (~93% portable)

Measured from the papers' own front pages, identical across all six years:

| | Marks | Questions |
|---|---|---|
| Section I (multiple choice) | **10** | Q1–10 |
| Section II (short/extended written) | **90** | Q11–31 / 32 / 34 |
| **Total** | **100** | |

Section II is *not* essay-shaped. Parsed from the marking guidelines, it decomposes into
**37–42 separately-marked parts per paper**, almost all 1–5 marks — the same shape Mathematics
Standard 2 already ports as 151 written questions against its own 85-mark Section II.

Unportable content is **drawing/sketching/plotting tasks**, which the engine cannot present:

| Year | Drawing parts | Marks |
|---|---|---|
| 2020 | Q11(a), Q11(b), Q16, Q24 | 10 |
| 2021 | Q19, Q21, Q27(a), Q28(b) | 9 |
| 2022 | Q12 (graph from table), Q27(c) | ~5 |
| 2023 | Q18(a), Q19(a), Q30(b) | 7 |
| 2024 | Q17(a), Q19, Q25(b) | 9 |
| 2025 | Q15(b) | 2 |

≈ **42 of 540 Section II marks ≈ 7.8%**, i.e. ~7 marks per 100-mark paper. Two independent
sweeps (paper-side instruction verbs; marking-guideline criteria verbs) agree within ±5 marks
across the six papers; the paper-side sweep is the higher figure and is used here.

**Portable mark share ≈ 92–93%** — comfortably above the playbook's >70% "good fit" band.

Those ~14 parts become `omittedParts` entries. Two paper-level anchors exist for reconciling
them later: the front-page section totals, and the mid-paper banners the papers print
themselves (e.g. 2020 p24: "Questions 11–23 are worth 46 marks in total").

---

## Test 2 — Renderer fit: **PASS** (the predicted blocker did not materialise)

There is no MathJax or KaTeX in this project. Full non-ASCII inventory across all six papers:

```
– − • â ° ƒ ≤ ’ © ′ ″ ¯ ⌠⎮⌡ — · ≥ ⎧⎨⎩ ∠ π ‘
```

What is **absent** is the decisive part: **no ∑, no matrices, no vectors, no complex numbers.**

⚠️ **Corrected at Stage 1: "no radical sign" was wrong.** This inventory is of the *text layer*,
and √ — like ∞ — is drawn as vector paths, so neither character appears in it while both are
printed on the page (2020 Q1 `y = √(2x − 3)`; 2022 Q4's interval options; 2025 Q3/Q5's surds).
Both are ordinary Unicode and neither threatens the no-MathJax constraint, so the GO stands
unchanged — but do not carry the "no radical sign" line forward. Mathematics Advanced's notation is `<sup>` / `<sub>` / `<em>` / Unicode
territory, which is exactly the constraint Standard 2's 318 questions already live inside
(its bank uses ² ³ ⁻ ⁴ ¹ ⁿ ₁ ₂ π σ μ √ ∠ and only 14 `<sup>` tags in total).

Three constructs need a decision but none is a blocker:

| Construct | Frequency | Resolution |
|---|---|---|
| Definite/indefinite integral in a **stem or MC option** | ~6 of 60 MC (2020 Q4/Q7, 2022 Q6, 2024 Q5/Q10, 2025 Q5), plus scattered Section II | `∫` (U+222B) with `<sub>`/`<sup>` limits; already legible inline |
| Stacked fraction in an MC option (e.g. `⅓e³ˣ + c`) | same ~6 questions | Inline `1/3`, matching how Standard 2 writes rates. Degrades visually, does not lose meaning |
| Piecewise function with a brace | 2–3 across 6 papers (e.g. 2020 Q23) | Borderless 2-row table with a CSS brace, **or** a crop. Decide at Stage 3 |

Leibniz notation (`dV/dt`) appears regularly and renders fine inline.

**Notation complexity: `basic`.** This is the finding that separates Advanced from Extension 1/2,
and it is why the GO stands.

---

## Test 3 — Content-shape fit: **the real cost, and the main caveat on this GO**

Section I, classified by reading all 60 stems (see Stage 1 note below):

| Year | Stimulus image | Option-image sets | Table (→ HTML) | Plain text |
|---|---|---|---|---|
| 2020 | 3 (Q7, 8, 10) | 1 (Q5) | 2 (Q2, Q3) | 4 |
| 2021 | 4 (Q4, 7, 8, 10) | 2 (Q4, Q5) | 1 (Q2) | 4 |
| 2022 | 4 (Q3, 7, 8, 10) | 2 (Q1, Q10) | 1 (Q2) | 4 |
| 2023 | 5 (Q1, 2, 4, 5, 10) | 1 (Q6) | 3 (Q2, Q4, Q6) | 4 |
| 2024 | 5 (Q1, 7, 8, 9, 10) | 2 (Q7, Q8) | 1 (Q3) | 4 |
| 2025 | 3 (Q6, 9, 10) | 3 (Q2, Q4, Q6) | 1 (Q1) | 4 |
| **Total** | **24** | **11** | **9** | **24** |

Section II: **39 questions across the six papers reference a stimulus, diagram or table.**

Rough asset budget: **~24 + ~39 ≈ 60 stimulus crops, plus 11 × 4 = 44 option crops ≈ 100 image
assets**, before Stage 1 separates the tables (which become HTML, not crops).

For scale, the playbook's appendix calls **VET Construction's 19 image questions** the heaviest
asset load of the four existing subjects. Mathematics Advanced is several times that. Stage 5
is the dominant cost of this port, and that should be priced in before Stage 4 starts, not
discovered during it.

Mitigating: this is precisely the shape `scripts/extract_maths_diagrams.py` +
`scripts/diagram_registry.json` were built for, and the `{subject}_{year}_Q{n}_{A..D}` naming
already carries 56 Standard 2 option crops. The tooling exists; the volume is the issue.

**Text-layer quality: `garbled` on every paper.** NESA typesets maths via a MathType-style font
mapping — `^…h` and `]…g` are bracket glyphs, `#` is ×, superscripts flatten inline, and `ƒ`
stands in for *f*. `y = ^x - 1h2` is `y = (x − 1)²`. Section II questions must therefore be
**transcribed from rendered pages**, not extracted from the text layer. This is a Stage 4 cost
multiplier and the single most under-appreciated number in this report.

---

## Test 4 — Precedent fit: **PASS, strongest of any port so far**

Mathematics Standard 2 is live with 318 MC and 151 written questions, from the **same NESA paper
format and the same marking-guideline format**. Shared: notation constraint, diagram tooling,
registry naming, `category` field, `solution` step-by-step convention, and much of the topic
space (functions, trigonometry, statistics). Advanced adds calculus and drops financial
modelling depth.

Content areas, from the marking guidelines' mapping grids — **a secondary proxy, explicitly NOT
the syllabus** (playbook §3 / CLAUDE.md §10; presenting a mapping-grid list as syllabus-grounded
is the rule that has been broken twice):

```
MA-F1 29   MA-F2 17   MA-T1 18   MA-T2  4   MA-T3 19
MA-C1  4   MA-C2 13   MA-C3 37   MA-C4 38   MA-E1 13
MA-M1 33   MA-S1 24   MA-S2 20   MA-S3 31
```

Calculus (C1–C4, 92 grid rows) and statistics (S1–S3, 75) dominate. **This list must be
re-grounded in the official syllabus at Stage 2 before any topic list is fixed.**

---

## Stage 6 dry run (not required by Gate 0 — run anyway, and it is the best signal in this report)

Both ground-truth extractors were run **read-only** against the Maths Advanced PDFs, with no
change to any script and nothing written:

| Check | Result |
|---|---|
| `build_answer_key.find_papers("Maths Advanced")` | ✅ all 6 years classified correctly — `paper` / `mg` / `feedback` |
| `build_answer_key.extract_mc_key()` | ✅ **10/10 answers parsed for all 6 years**, 60 total |
| `build_written_key.parse_paper()` | ✅ 37–42 parts per paper, **0 unresolved** |
| Reconciliation vs front-page Section II total | ✅ **90 / 90 / 90 / 90 / 90 / 90** — exact, all six years |

Zero unresolved parts and an exact reconciliation on the first attempt is better than any
existing subject managed. Stage 6 is de-risked for this subject before Stage 1 begins.

---

## Triage record (playbook §1 output schema)

```
sections[]              Section I  — 10 questions, MC,      10 marks
                        Section II — 21–24 questions, written, 90 marks
mcCount                 60   (10 × 6 papers)
shortAnswerCount        232  separately-marked Section II parts across 6 papers
extendedResponseCount   0    (no essay-format question in any paper)
diagramDependentCount   63   (24 MC stimulus + 39 Section II) + 11 MC option-image sets
notationComplexity      basic
themes[]                MA-F1 F2 · T1 T2 T3 · C1 C2 C3 C4 · E1 · M1 · S1 S2 S3
                        (mapping-grid proxy — NOT syllabus-grounded, see Test 4)
fitSummary              100-mark paper, 10 MC + 90 written. ~93% portable; ~42/540 marks are
                        drawing tasks → omittedParts. Notation fits the no-MathJax constraint.
                        Ground-truth extractors already reconcile exactly. Dominant cost is
                        ~100 image assets and a garbled text layer forcing manual transcription.
recommendation          generate-mc-and-written
```

---

## GATE 0

- [x] Papers **and** marking guidelines present for every year in scope — 2020–2025, both
- [x] Portable mark share computed from the papers' front pages — 10 / 90 / 100, all six years
- [x] Notation verdict recorded — `basic`; no ∑, matrices, vectors or complex numbers
- [x] Explicit GO / NO-GO written down with the reason — **GO**, above

**GO.** Mathematics Advanced clears all four fit tests. The decision is not close on tests 1, 2
or 4. The caveat is entirely test 3: this is the most asset-heavy port attempted here, roughly
five times VET Construction's, compounded by a text layer that cannot be trusted for
transcription. That is a scheduling fact, not a reason to say no — but Stage 1 should size it
per-question before Stage 4 is committed to.

**Next: ~~Stage 1 (Survey)~~ — Stage 1 completed 2026-08-27; see the runbook. Stage 3 is next.** ~~Stage 2 is blocked~~ — **Stage 2 was completed the same day**
(2026-08-27): the owner supplied the syllabus location, the official 2017 DOCX was downloaded
and read, and the topic list now lives in `docs/subject-plans/mathematics-advanced.md`. The
14 `MA-*` codes below are superseded by that document, which has the syllabus's own scope
weighting alongside them.

---

## Findings for the playbook and tooling (first live run)

1. **`build_written_key.py` will silently skip this subject.** It selects guidelines with
   `re.search(r"-mg\.pdf$", basename)`, so `2020_marking_guidelines.pdf` never matches and the
   script exits `"no marking-guideline PDFs (*-mg.pdf) in …"`. Its sibling
   `build_answer_key.py` uses the tolerant `find_papers()` and handles this folder fine. The
   two scripts disagree about how a marking guideline is recognised. Everything above was
   obtained by calling `parse_paper()` directly, bypassing the glob. **This must be fixed
   before Stage 6** — as a Stage 6 prerequisite, not a Stage 0 edit, since no gate has been
   passed that licenses touching shared tooling.
2. **A third PDF per year exists here that no other subject has** — `{year}_marking_feedback.pdf`
   (NESA's notes from the marking centre). `find_papers()` already classifies it correctly
   because it tests `"feedback"` *before* `"marking"`; had the order been reversed it would have
   been mistaken for the guidelines. Worth stating in the playbook's input table, since the
   ordering is load-bearing and invisible.
3. **A Stage 6 dry run belongs in Stage 0.** Running both extractors read-only cost minutes and
   produced the single strongest feasibility signal in this report (exact 90-mark reconciliation,
   zero unresolved parts). It also surfaced finding 1. Proposed as a new Gate 0 checklist item.
4. **"One report per paper" is redundant when the paper format is stable.** Six near-identical
   files would carry the same information as the per-paper tables above. This report is
   subject-level with per-year rows. The per-paper convention comes from `agent.js`'s
   `triagePaper()`, which genuinely runs once per paper; a human Stage 0 does not.
5. **A naive digit regex over a marking-guideline block over-counts — confirmed again.** A first
   pass here read Section II as 106 / 113 / 117 marks against a true 90, reproducing exactly the
   failure CLAUDE.md §10 rule 8 documents for 2020 Standard 2. The positional Marks-column reader
   in `build_written_key.py` got 90 on every paper. The rule holds; do not re-derive it.
