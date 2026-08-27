# Mathematics Advanced — port runbook

**One stage per session.** This file is the single entry point: a fresh session should be able
to open it cold, run one stage, tick its gate, and write its result back here. Stage 0's Fit
Report is separate: `docs/paper-reports/mathematics-advanced.md` (verdict **GO**).

| Stage | Status | Session |
|---|---|---|
| 0 Feasibility | ✅ GO — 2026-08-27 | done |
| 1 Survey | ✅ complete — 2026-08-27 | done |
| 2 Syllabus grounding | ✅ complete — 2026-08-27 | done |
| **3 Schema** | ⬜ **next** | 1 short session |
| 4 Port | ⬜ | **~6 sessions, one per paper year** |
| 5 Assets | ⬜ | 3 sessions — **121 crops + 28 tables**, measured at Stage 1 |
| 6 Ground truth | ⬜ | 1 session |
| 7 Release | ⬜ | 1 session |

### How to start each session

Paste this, changing the stage number:

> Read `docs/subject-plans/mathematics-advanced.md` and `docs/porting-playbook.md`.
> Run **Stage N** for Mathematics Advanced. Do not re-derive anything the runbook already
> records. Write the result back into the runbook and tick its gate before finishing.

### Rules that apply in every session

- **Do not re-derive what is already recorded here.** Every number below was measured, not
  estimated, and several took more than one attempt to get right.
- **Never re-read a marking guideline "to audit the answers."** Every attempt in this project's
  history produced a different wrong result. Extraction scripts + CI are the only trusted path.
- **Papers are local, never committed** — `NESA Exams Folder/Maths Advanced/`, copyright.
- **`docs/HISTORY.md` entry is mandatory** at the end of any non-trivial session, plus CLAUDE.md
  if a file-structure, schema or instruction fact changed.
- **If the playbook is wrong, fix `docs/porting-playbook.md` in the same session and say so.**
  It has been corrected twice already from live runs; gaps found are expected, not failures.

### Established facts — carry these forward, do not re-measure

| | |
|---|---|
| Papers | 2020–2025, `{year}_exam.pdf` + `{year}_marking_guidelines.pdf` + `{year}_marking_feedback.pdf` |
| Structure, every year | 100 marks = Section I 10 MC (Q1–10) + Section II 90 (Q11–31/32/34) |
| Total workload | **294 question parts** — 60 MC + 234 Section II parts across 131 questions |
| Section I assets | **25** stimulus images, **12** option-image sets (=48 crops), **10** tables → HTML, 22 plain-text stems (Stage 1 corrected Stage 0 — see Stage 1) |
| Section II assets | **48 crops + 18 tables** across 46 questions/parts |
| **Total assets** | **121 crops · 28 tables → HTML** (Stage 0's "~100" was low) |
| Unportable | **17 drawing parts, 41 of 540 Section II marks (7.6%)** → `omittedParts` / `omittedQuestions`; portable share **93.2%** |
| Notation | `basic` — no ∑, matrices, vectors or complex numbers. ⚠️ **Radicals DO occur** (2020 Q1, 2025 Q3/Q5): Stage 0 read "no radical sign" off the text layer, and √ is drawn as paths, so it is invisible there. Same for ∞ |
| **Text layer** | **garbled on every paper, but not the same way each year** — 2024 alone uses the MathType `^…h` / `]…g` bracket mapping; every year loses ∞ and √ entirely, prints π as `p`, and re-orders stacked fractions. **124 of 294 parts (42%) carry a detectable corruption** |
| Ground truth, pre-verified | `extract_mc_key()` 10/10 every year; `parse_paper()` 37–42 parts/paper, **0 unresolved, exact 90/90 on all six** |
| Official topic + marks | `data/mapping-grid/mathematics-advanced.json` — every part, all six papers, reconciled |

---

## Stage 1 — Survey ✅ COMPLETE

**All 294 parts classified. Nothing unresolved.** Every part in
`data/mapping-grid/mathematics-advanced.json` was located in its exam paper by *(page, y)* and
classified for presentation. The numbers below are measured, not estimated — do not re-derive them.

### Method (and where it under-detects)

Three independent detectors, unioned, then **every candidate rendered and looked at** across 23
contact sheets:

1. **Text-gap bands** — a vertical band carrying ink but no body text.
2. **`page.find_tables()`** — noisy in both directions: it reads graph axes as 2×2 tables, so
   every hit was filtered to ≥6 cells and then confirmed by eye.
3. **Ink profile** — dark pixels lying outside every text-block bbox, at 72 dpi.

⚠️ **No single detector was complete.** Detector 1 misses a chart whose axis labels are wide text
blocks (it lost 2022 Q11(b)'s Pareto chart); detector 3 misses a diagram whose labels sit inside
one large text block. Four Section II diagrams — 2022 Q28, 2024 Q20, 2025 Q28, 2025 Q29 — were
found **only** by the union plus the visual pass. If Stage 5 ever re-derives this list, union all
three and look at the pages; a single-detector sweep silently drops assets.

Vector-path counting was not used: Stage 0 already showed it fails both ways.

### Section I — 60 questions

| Year | Stimulus image | Option images (×4) | Table stimulus | Options as table rows | Plain text |
|---|---|---|---|---|---|
| 2020 | Q7, Q8, Q10 | Q5, Q9 | Q3 | Q2, Q3 | Q1, Q4, Q6 |
| 2021 | Q4, Q6, Q7, Q8, Q10 | Q4, Q5 | Q2 | — | Q1, Q3, Q9 |
| 2022 | Q3, Q7, Q8, Q10 | Q1, Q10 | — | Q2 | Q4, Q5, Q6, Q9 |
| 2023 | Q1, Q2, Q4, Q5, Q10 | Q6 | Q2, Q6 | Q4 | Q3, Q7, Q8, Q9 |
| 2024 | Q1, Q7, Q8, Q9, Q10 | Q7, Q8 | Q3 | — | Q2, Q4, Q5, Q6 |
| 2025 | Q6, Q9, Q10 | Q2, Q4, Q6 | Q1 | — | Q3, Q5, Q7, Q8 |

**Two corrections to Stage 0's table**, both found by rendering the page rather than reading the
stem: **2020 Q9** has four option images (normal curves with different regions shaded) and was
counted as plain text; **2021 Q6** has a probability-tree stimulus and was counted as plain text.
Totals move to **25 stimulus images and 12 option sets (48 option crops)**.

**A question can sit in two columns at once** — 2023 Q2 has a die/spinner picture *and* a
partially completed table; 2023 Q6 has a table stimulus *and* four option graphs.

**`optionImagesWide` is not needed anywhere.** All 12 option sets measure between 0.8:1 and
2.6:1. The one worth re-checking at crop time is **2024 Q8** (four histograms): its C/D row's ink
extent measures 3.7:1, an artefact of where the bars stop rather than the crop's real shape.

**Trap 2 (bare-letter options) does not occur in this subject.** Every MC question whose options
*look* like bare letters (2020 Q10, 2023 Q5, 2024 Q10, 2025 Q10) has numeric options — 0/1/2/3,
not labels pointing into a shared stimulus. There is nothing here like VET 2021 Q15.

**One presentation case Stage 0 did not record: options printed as rows of a table** — 2020 Q2,
2020 Q3, 2022 Q2, 2023 Q4. The four alternatives are table rows with A./B./C./D. down a
left-hand column. Portable as ordinary text options (join each row's cells), but *how* is a
Stage 3 decision.

### Section II — 234 parts across 131 questions

| Year | Crops | Tables → HTML |
|---|---|---|
| 2020 | Q15, Q22, Q25, Q27, Q29, Q30, Q31 | Q20 |
| 2021 | Q12, Q17, Q17(b), Q18, Q22, Q24, Q28, Q32, Q33 | Q22, Q25, Q32 (×2), Q34 |
| 2022 | Q11(b), Q14, Q16, Q17, Q24, Q28, Q29(a), Q31 | Q11, Q21 |
| 2023 | Q22, Q23, Q24, Q26, Q27, Q28, Q32 | Q12, Q15, Q23 |
| 2024 | Q11, Q13, Q14, Q16, Q20, Q21, Q22, Q23, Q28, Q31 | Q11, Q13, Q22(b), Q23, Q24(b), Q26 |
| 2025 | Q11, Q14, Q24, Q25(c), Q27, Q28, Q28(b) | Q20 |

48 crops, 18 tables. Almost every crop is line art the paper drew itself — graphs, geometry
diagrams, box plots, scatterplots, probability trees. **Two are illustrations rather than maths**:
2022 Q17 (a pyramid of playing cards) and 2024 Q28 (a Ferris wheel).

Six of the 18 tables are **future-value / z-score lookup tables** (2021 Q25, 2022 Q21, 2023 Q15,
2024 Q24(b), 2024 Q26, 2025 Q20) — wide, and exactly what `.study-dtable`'s stacked-card collapse
exists for. Three more are **blank tables the student fills in** (2022 Q12(b), 2024 Q11, Q13):
reproduce the table as HTML and mark the answer as text — see Stage 3.

### Unportable — 17 parts, 41 marks (7.6% of Section II, 6.8% of the paper)

| Year | Parts (marks) | Total |
|---|---|---|
| 2020 | Q11(a) 1 · **Q16 4** · **Q24 3** | 8 |
| 2021 | **Q19 3** · **Q21 2** · Q27(a) 2 · Q28(b) 2 | 9 |
| 2022 | Q12(b) 2 · Q27(c) 3 | 5 |
| 2023 | Q18(a) 3 · Q19(a) 2 · Q30(b) 2 | 7 |
| 2024 | Q17(a) 2 · **Q19 5** · Q25(b) 2 | 9 |
| 2025 | Q15(b) 2 · Q16(b) 1 | 3 |

All 17 require the student to *produce* a drawing — sketch a curve, plot a point on a printed
grid, complete a printed graph. **Bold entries are whole single-part questions** and belong in
subject-level `omittedQuestions` (2020 Q16, Q24; 2021 Q19, Q21; 2024 Q19 — 17 marks); the other
12 are `omittedParts` on their question. Portable share of the paper: **93.2%**, confirming
Stage 0's estimate.

**"Shaded region" is not a drawing task.** A verb sweep flags roughly 40 parts; most say *the*
shaded region — the paper drew it and the student computes an area. Only the imperative
("sketch", "plot", "complete the graph") is unportable. 2020 Q27 was a false positive twice over:
"box-**plot**" matched the verb, and the box plot is a *given* stimulus.

**Seven portable parts lean on a part we omit** — 2020 Q11(b), Q11(c); 2021 Q27(d), Q28(c);
2023 Q18(b), Q19(b); 2025 Q15(c) (11 marks). Six say "or otherwise" or restate the function, so
they stand alone. **2021 Q27(d) is the exception**: it says *"Explain your answer by referring to
the graph drawn in part (a)"*, and (a) is omitted. Decide at Stage 4 — supply the graph as a
stimulus, or omit (d) as well. Do not quietly reword NESA.

### Stem sweep — run, every hit resolved

The playbook's regex plus the two patterns it was missing (below) returns **13 hits**: 2020 Q5 ·
2021 Q3, Q5, Q7, Q8 · 2022 Q1, Q10 · 2023 Q6 · 2024 Q1, Q7, Q8 · 2025 Q2, Q4.

**Twelve are complete** — the paper prints four separate diagrams, already in the option-image
list above. **One is genuinely text**: 2021 Q3 ("Which of the following represents the domain of
ƒ(x) = ln(1 − x)?") has interval-notation options and no picture. **No question was found where
prose stands in for a missing picture** — the Multimedia 2022 Q2 failure has no analogue here.

⚠️ **The playbook's regex was incomplete, and is now fixed there.** It misses `which of these …`
(2024 Q8) and `a possible sketch` (2023 Q6). Both are picture-option questions; both would have
been missed by the sweep as written.

### Text-layer quality — per paper, measured

| Year | Corruption style | Parts needing manual transcription |
|---|---|---|
| 2020 | *f* → `â`/`ƒ`; integrals as `⌠⎮⌡`; π → `p` | 18 / 49 (37%) |
| 2021 | same | 24 / 48 (50%) |
| 2022 | same, **plus scrambled reading order** (`( ed.` then `a)  Jane borrows…`) | 19 / 52 (37%) |
| 2023 | same | 24 / 48 (50%) |
| 2024 | **MathType brackets** — `^x - 1h2` is `(x − 1)²`, `]xg` is `(x)`, `#` is × | 18 / 47 (38%) |
| 2025 | *f* → `ƒ`; π → `p` | 21 / 50 (42%) |

**Stage 0 said "garbled on every paper" and gave a 2024 example. It is garbled on every paper,
but only 2024 uses the bracket mapping** — searching a 2021 paper for `^x - 1h2` finds nothing.
Four defects are common to all six years:

- **∞ and √ never appear in the text layer of any paper** — zero occurrences of either character
  across 2020–2025, although both are printed. They are drawn as paths. 2022 Q4's options extract
  as `( − , 1` for `(−∞, 1]`; 2025 Q3/Q5's surd options extract as bare digits.
- **π extracts as the letter `p`** — `0 ≤ x ≤ 2p` means `0 ≤ x ≤ 2π`. Only 2020 contains a single
  genuine `π` character in the whole paper.
- **Stacked fractions are split and re-ordered.** "Show that P = 2x + 72/x" extracts as
  `72 (a)  Show that P = 2x + . x`. **91 of 294 parts contain at least one stacked fraction**
  (599 fraction bars across the six papers).
- 42% of parts (124/294) carry a *detectable* corruption marker — and that is a **lower bound**,
  since a re-ordered fraction with no other marker is invisible to the check. Treat the whole of
  Section II as transcription work, exactly as Stage 4 already says.

**GATE 1** — [x] all 294 parts classified · [x] crop list, table list and omission list produced ·
[x] stem sweep run and every hit resolved · [x] text-layer quality recorded per paper

---

## Stage 2 — Syllabus grounding ✅ COMPLETE

### Provenance (Gate 2 requires this stated explicitly)

**Primary source, read in full.** `NESA Exams Folder/Maths Advanced/mathematics-advanced-stage-6-syllabus-2017.docx`
— the official *Mathematics Advanced Stage 6 Syllabus (2017)*, 1.63 MB, downloaded from
nsw.gov.au at the owner's direction and saved alongside the papers under the same copyright
treatment (not committed to GitHub). Read with `python-docx`, both `document.paragraphs` and
`document.tables`: 1122 paragraphs, 10 tables. `mathematics-standard-and-advanced-common-content.pdf`
saved alongside.

**This topic list comes from the primary syllabus, not a mapping-grid proxy.**

### Which syllabus applies — and this port's shelf life

| Syllabus | Governs | Status |
|---|---|---|
| **Mathematics Advanced Stage 6 (2017)** | **The 2020–2025 papers, and the 2026 HSC** | Year 12 continues on it through Term 3, 2026 |
| Mathematics Advanced 11–12 (2024) | 2027 HSC onwards | Year 11 from Term 1 2026; Year 12 from Term 4 2026 |

The 2017 syllabus is correct for this bank. **But the topic list is dated: the 2027 cohort sits
a different syllabus.** A product decision to take deliberately, not discover in 2027. The 2024
syllabus is web-only on curriculum.nsw.edu.au — no PDF or DOCX download found.

### The topic list — 14 subtopics, both years

The HSC examines the Year 12 course with Year 11 as assumed knowledge, and the grids confirm
Year 11 subtopics are examined directly every year. **Both years are in scope.** `category`
values are the syllabus codes with `MA-` stripped, matching Standard 2's convention.

| `category` | Title | Yr | Scope | Examined | Yield |
|---|---|---|---:|---:|---:|
| `C3` | Applications of Differentiation | 12 | 5.3% | **15.7%** | ×2.96 |
| `M1` | Modelling Financial Situations | 12 | 8.4% | 13.0% | ×1.55 |
| `C4` | Integral Calculus | 12 | 10.3% | 11.7% | ×1.13 |
| `S3` | Random Variables | 12 | 8.7% | 10.2% | ×1.18 |
| `F1` | Working with Functions | 11 | **15.6%** | 6.8% | ×0.44 |
| `T1` | Trigonometry and Measure of Angles | 11 | 5.9% | 6.8% | ×1.16 |
| `T3` | Trigonometric Functions and Graphs | 12 | **1.7%** | 6.8% | **×4.03** |
| `S2` | Descriptive Statistics and Bivariate Data Analysis | 12 | 8.1% | 6.3% | ×0.78 |
| `S1` | Probability and Discrete Probability Distributions | 11 | 7.3% | 6.1% | ×0.84 |
| `F2` | Graphing Techniques | 12 | 2.8% | 5.6% | ×2.01 |
| `C2` | Differential Calculus | 12 | 4.2% | 4.7% | ×1.11 |
| `E1` | Logarithms and Exponentials | 11 | 8.7% | 3.6% | ×0.42 |
| `T2` | Trigonometric Functions and Identities | 11 | 2.5% | 1.3% | ×0.53 |
| `C1` | Introduction to Differentiation | 11 | **10.6%** | **1.3%** | **×0.12** |

358 content dot points total. Six top-level topics group these: Functions (F1, F2),
Trigonometric Functions (T1–T3), Calculus (C1–C4), Exponential and Logarithmic (E1), Financial
Mathematics (M1), Statistical Analysis (S1–S3).

⚠️ **`F1`, `M1`, `S1` and `S2` are also Standard 2 codes and mean different things** — Standard
2's `F1` is financial "Money Matters". Separate files, separate filters, nothing breaks; but
never key a shared lookup on the bare code.

**Scope and examination diverge hard.** C1 is the second-largest subtopic by scope and
near-invisible in six years — Year 11 foundation that Year 12 calculus silently assumes. Use the
**grid for per-question `category`**, the **syllabus for any Study Mode weighting**. Backwards
is the VET failure repeating. Full data: `data/exam-trends/mathematics-advanced.json`.

**GATE 2** — [x] primary syllabus read · [x] weighting from scope, not exam frequency ·
[x] provenance stated · [x] second live syllabus identified · [x] grid reconciled

---

## Stage 3 — Schema ⬜ NEXT (short session)

Canonical names, per playbook Stage 3 — a new port uses these, existing deviations are debt:
`year`, `qNum`, `category`, `optionExplanations`, `marks`, `answer`, `omittedParts`,
`omittedQuestions`.

Six decisions to take and record here. The first two came from Stage 0; the last four are
Stage 1 findings, each with the exact questions they affect.

1. **Braced piecewise function** (2–3 across six papers, e.g. 2020 Q23) — borderless two-row
   table with a CSS brace, or a crop?
2. **Integrals and stacked fractions** in MC stems/options (~6 of 60 MC) — `∫` U+222B with
   `<sub>`/`<sup>` limits, and inline `1/3`. Confirm against how Standard 2 already writes rates.
3. **Options printed as rows of a table** — 2020 Q2, 2020 Q3, 2022 Q2, 2023 Q4. Either render the
   table in the stem and make the options bare row references, or flatten each row into a text
   option (`Median: Changes · Mean: Stays the same`). Flattening keeps the options meaningful on
   the results screen and inside `optionExplanations`; the table-in-stem form is closer to the
   paper. Pick one and apply it to all four.
4. **Blank tables the student fills in** — 2022 Q12(b), 2024 Q11, 2024 Q13. The table is
   reproduced as HTML in the stem and the answer is a short text list of the cell values, marked
   on keywords. Fix the model-answer format before Stage 4 authors the first one, so all three
   match. (2022 Q12(b) is omitted anyway — it also asks for a graph.)
5. **The 12 `omittedParts` and 5 `omittedQuestions`** are enumerated in Stage 1. Confirm the
   canonical shape of both keys against `subjects/multimedia.json`, the only existing file that
   carries `omittedQuestions`.
6. **π, ∞ and √** appear throughout and never survive extraction. Fix the characters now —
   `π` U+03C0, `∞` U+221E, `√` U+221A — so Stage 4 is not re-deciding this per question.

**GATE 3** — [ ] field mapping written down before any question is authored · [ ] every
deviation deliberate and recorded

---

## Stage 4 — Port ⬜ (~6 sessions, one paper per session)

**Suggested order: 2024 → 2025 → 2023 → 2022 → 2021 → 2020.** 2024 is the lightest asset load
(2 graphic-bearing MC) and the cleanest text, so it establishes the pattern; 2020 is heaviest.

Per session: one year, Section I then Section II, ~49 parts.

- **Carry `qNum` from the first question authored.** Retrofitting needs `backfill_qnum.py`,
  which refuses to guess; skipping it left 135 questions unverifiable for months across
  Multimedia and VET.
- **Take `category` and `marks` from `data/mapping-grid/mathematics-advanced.json`** — do not
  read them off the paper.
- **Transcribe Section II from rendered pages, not the text layer.** This is not optional:
  `^x - 1h2` is `(x − 1)²`. Render at ~140 dpi and read the image.
- Tables become reconstructed `<table>` HTML, never a crop — mobile needs `.study-dtable`'s
  stacked-card collapse.
- Drawing parts get an `omittedParts` entry; a whole unportable question gets
  subject-level `omittedQuestions`. Silent omission is how 2020 Standard 2 sat at 84/85 marks
  for over a year.
- Run `node scripts/validate_subjects.cjs` before finishing each session.

**GATE 4** — [ ] validator green, `missingImages: 0` · [ ] every part has `qNum` · [ ] omissions
declared, and each paper's marks total 100

---

## Stage 5 — Assets ⬜ (2–3 sessions, ~100 crops)

The dominant cost — roughly six times VET Construction's load, the heaviest so far.
**Stage 1 measured it: 121 crops (25 Section I stimulus + 48 Section I option + 48 Section II)
and 28 tables to reconstruct as HTML.** The per-question crop and table lists are in Stage 1;
work from those, not from a fresh sweep.

- Text layer has the option labels → `extract_maths_diagrams.py --calibrate` (registry, 150 dpi)
- Text layer empty / labels are outline paths → **ink-profile segmentation at 300 dpi**
  (`crop_vet_2021_q15_options.py` is the worked example)
- ⚠️ **`RENDER_DPI` is load-bearing** — registry coordinates are raw pixels verified at 150 dpi.
  Changing it without rescaling silently crops the wrong region: files still written, non-empty,
  plausible, wrong. `save_crop()` overwrites unconditionally, and a bare run with no `--year`
  re-cuts every registry entry.
- **Exclude the paper's own `A.`/`B.` glyph** — `index.html` renders its own option label.
- Wide option images (> ~3:1) need `optionImagesWide: true`. **Stage 1 measured all 12 option
  sets at 0.8:1 to 2.6:1, so none needs it** — re-check only 2024 Q8's histograms, whose ink
  extent measures 3.7:1 on the C/D row.

**GATE 5** — [ ] every crop opened and compared against the paper, option by option · [ ] every
table renders as HTML, not an image

---

## Stage 6 — Ground truth ⬜

Pre-verified at Stage 0: both extractors already reconcile exactly on all six papers. Two things
must happen first:

1. **Register the subject in both key builders.** `build_answer_key.py` `SUBJECTS`:
   `"mathematics-advanced": {"name": "Mathematics Advanced", "folder": "Maths Advanced", "mc_count": 10}`.
   `build_written_key.py` `SUBJECTS`: `"mathematics-advanced": "Maths Advanced"`.
2. ⚠️ **Fix `build_written_key.py`'s file glob first.** It selects guidelines with
   `re.search(r"-mg\.pdf$", …)`, which never matches `2020_marking_guidelines.pdf` — it exits
   `"no marking-guideline PDFs (*-mg.pdf) in …"`. Widen it to `find_papers()`'s logic (as
   `build_answer_key.py` and `build_mapping_grid.py` already use), and **keep `feedback`
   excluded** or the marking-centre notes get parsed as guidelines.

```bash
python scripts/build_answer_key.py  mathematics-advanced
python scripts/build_written_key.py mathematics-advanced
node   scripts/check_answer_key.cjs
node   scripts/check_written_key.cjs
```

**The residual human gate CI cannot cover:** a passing check compares only the official *letter*,
so it is blind to reordered options, wrong option text, and a description standing in for a
missing picture. For every question with an `image` or `optionImages`, compare the paper and the
committed crop option by option. Prefer the paper's own wording.

**GATE 6** — [ ] 0 wrong, 0 unverifiable · [ ] every paper reconciles to 100 · [ ] image
questions compared by a human

---

## Stage 7 — Release ⬜

1. `subjects/index.json` — add the filename
2. `index.html` — `SUBJECT_ID_MAP` (JSON fetch URL) **and** `SUBJECT_CATALOGUE` (billing id,
   written to Supabase `subject_selections.subject_id` — chosen once, expensive to change)
3. Subject card + artwork
4. **Browser-verify at mobile width**: load the subject, render questions carrying images,
   answer one correctly and one incorrectly, confirm explanations render, no console errors.
   Images use `loading="lazy"` — force `loading='eager'` before asserting anything loaded.
5. `docs/HISTORY.md` entry; CLAUDE.md §7 row + §11 roadmap

**GATE 7** — [ ] full local CI green · [ ] exercised in a browser at mobile width · [ ] docs updated

---

## Deferred, not part of this port

- **Study Mode** (`studyNotes`) — a separate project of comparable size (Multimedia 47 blocks,
  VET 71), built **one topic at a time** by the owner's explicit preference.
- **Exam Trends panel** — data already built (`data/exam-trends/mathematics-advanced.json`);
  UI placement is an open design decision.
- **Extended variant questions**, as Standard 2 has — not decided.
