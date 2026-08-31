# Mathematics Advanced — port runbook

**One stage per session.** This file is the single entry point: a fresh session should be able
to open it cold, run one stage, tick its gate, and write its result back here. Stage 0's Fit
Report is separate: `docs/paper-reports/mathematics-advanced.md` (verdict **GO**).

| Stage | Status | Session |
|---|---|---|
| 0 Feasibility | ✅ GO — 2026-08-27 | done |
| 1 Survey | ✅ complete — 2026-08-27 | done |
| 2 Syllabus grounding | ✅ complete — 2026-08-27 | done |
| 3 Schema | ✅ complete — 2026-08-27 | done |
| **4 Port + assets** | ✅ **complete — all 6 papers** (2020, 2023, 2022, 2025, 2021, 2024 ✅ 2026-08-31) | 6 sessions, one per paper year |
| 5 Assets | ➡️ folded into Stage 4 | method reference only — **124 crops + 28 tables**, split per year |
| **6 Ground truth** | ✅ **complete — 2026-08-31** | done |
| 7 Release | ⬜ | 1 session |

### How to start each session

Paste this, changing the stage number:

> Read `docs/subject-plans/mathematics-advanced.md` and `docs/porting-playbook.md`.
> Run **Stage N** for Mathematics Advanced. Do not re-derive anything the runbook already
> records. Write the result back into the runbook and tick its gate before finishing.

**For a Stage 4 session, name the paper** — the stage runs six times, once per year:

> Read `docs/subject-plans/mathematics-advanced.md` and `docs/porting-playbook.md`.
> Run **Stage 4 for the {YEAR} paper** — port it and crop its assets, on the
> `port/maths-advanced` branch. Do not re-derive anything the runbook already records.
> Tick that year's row in the Stage 4 tracker before finishing.

Stage 4's tracker table says which year is next.

### Rules that apply in every session

- **Do not re-derive what is already recorded here.** Every number below was measured, not
  estimated, and several took more than one attempt to get right.
- **Never re-read a marking guideline "to audit the answers."** Every attempt in this project's
  history produced a different wrong result. Extraction scripts + CI are the only trusted path.
- **Papers are local, never committed** — `NESA Exams Folder/Maths Advanced/`, copyright.
- **`docs/HISTORY.md` entry is mandatory** at the end of any non-trivial session, plus CLAUDE.md
  if a file-structure, schema or instruction fact changed.
- **If the playbook is wrong, fix `docs/porting-playbook.md` in the same session and say so.**
  It has been corrected in three sessions already (Stages 1, 2 and 3); gaps found are expected,
  not failures.

### Established facts — carry these forward, do not re-measure

| | |
|---|---|
| Papers | 2020–2025, `{year}_exam.pdf` + `{year}_marking_guidelines.pdf` + `{year}_marking_feedback.pdf` |
| Structure, every year | 100 marks = Section I 10 MC (Q1–10) + Section II 90 (Q11–31/32/34) |
| Total workload | **294 question parts** — 60 MC + 234 Section II parts across 131 questions |
| Section I assets | **25** stimulus images, **12** option-image sets (=48 crops), **10** tables → HTML, 22 plain-text stems (Stage 1 corrected Stage 0 — see Stage 1) |
| Section II assets | **49 crops + 18 tables** across 46 questions/parts |
| **Total assets** | **124 crops · 28 tables → HTML** (Stage 0's "~100" was low). ⚠️ Stage 1's Section II crop list is a **lower bound, three times over** — 2023 Q16 is missing from it, 2025 Q29 is missing from it (although Stage 1's own method paragraph names it), and a question listed once can carry **two** diagrams (2022 Q28). Read each question's own page as you write it |
| Unportable | **17 drawing parts, 41 of 540 Section II marks (7.6%)** → `omittedParts` / `omittedQuestions`; portable share **93.2%** |
| Notation | `basic` — no ∑, matrices, vectors or complex numbers. ⚠️ **Radicals DO occur** (2020 Q1, 2025 Q3/Q5): Stage 0 read "no radical sign" off the text layer, and √ is drawn as paths, so it is invisible there. Same for ∞ |
| **Text layer** | **garbled on every paper, but not the same way each year** — 2024 alone uses the MathType `^…h` / `]…g` bracket mapping; every year loses ∞ and √ entirely, prints π as `p`, and re-orders stacked fractions. **124 of 294 parts (42%) carry a detectable corruption** |
| Ground truth, pre-verified | `extract_mc_key()` 10/10 every year; `parse_paper()` 37–42 parts/paper, **0 unresolved, exact 90/90 on all six** |
| Official topic + marks | `data/mapping-grid/mathematics-advanced.json` — every part, all six papers, reconciled. ⚠️ **Regenerated 2026-08-28** after `build_mapping_grid.py` was found to bleed a multi-line Content cell into the rows above and below it; 20 rows across the two maths subjects carried a code NESA never gave them (see the 2025 session note) |
| Schema | Fixed at Stage 3 — canonical field names, no deviations. **Two engine fixes are blocking for Stage 7**: the shared `NESA_CAT_LABELS` map collides on 5 of 14 codes, and the written-question badge reads `q.topic` not `category` |
| Bank shape | **One entry per NESA question**, not per part (Stage 4, 2020) — matches Standard 2 and the `check_written_key.cjs` prefix-sum join |
| Stem images | ⚠️ **An inline `<img>` inside `q` needs its own `max-width:100%` style** — there is no `.q-text img` rule, so an unstyled one renders at natural crop width and `body{overflow-x:hidden}` silently cuts it off. Stage 4 decision 6 (found 2026-08-29) |
| Crop tool | `scripts/crop_maths_advanced.py --year {YEAR}` — points, not pixels; one registry block per year. **Never** add this subject to `diagram_registry.json` |
| File format | `subjects/mathematics-advanced.json` round-trips **byte-for-byte** through `json.dumps(indent=2, ensure_ascii=False)` plus a trailing newline — safe to load, extend with a year, and dump |

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

⚠️ **This paragraph said "`optionImagesWide` is not needed anywhere" and was wrong.** The
measurement behind it — all 12 option sets between 0.8:1 and 2.6:1 — did not survive cropping:
**2021 Q4 cuts at 2.94:1** and renders **160 × 54 px** in the 2×2 grid at 430 px, so it is set
there (see the 2021 session note). **The ratio is not the test; the rendered height is.** The
other candidate named here, **2024 Q8** (four histograms, C/D row ink extent 3.7:1), was
measured at crop time and does **not** need it: that 3.7:1 banded the C/D *row*, and a single
cell cuts at 1.75:1 and renders 160 × 96 px. **2021 Q4 is the subject's only one.**

**Trap 2 (bare-letter options) does not occur in this subject.** Every MC question whose options
*look* like bare letters (2020 Q10, 2023 Q5, 2024 Q10, 2025 Q10) has numeric options — 0/1/2/3,
not labels pointing into a shared stimulus. There is nothing here like VET 2021 Q15.

**One presentation case Stage 0 did not record: options printed as rows of a table** — 2020 Q2,
2020 Q3, 2022 Q2, 2023 Q4. The four alternatives are table rows with A./B./C./D. down a
left-hand column. Portable as ordinary text options (join each row's cells). **Stage 3
decision 3 took this: flatten each row into a text option**, header row into the stem.

### Section II — 234 parts across 131 questions

| Year | Crops | Tables → HTML |
|---|---|---|
| 2020 | Q15, Q22, Q25, Q27, Q29, Q30, Q31 | Q20 |
| 2021 | Q12, Q17, Q17(b), Q18, Q22, Q24, Q28, Q32, Q33 | Q22, Q25, Q32 (×2), Q34 |
| 2022 | Q11(b), Q14, Q16, Q17, Q24, Q28, Q29(a), Q31 | Q11, Q21 |
| 2023 | Q16, Q22, Q23, Q24, Q26, Q27, Q28, Q32 | Q12, Q15, Q23 |
| 2024 | Q11, Q13, Q14, Q16, Q20, Q21, Q22, Q23, Q28, Q31 | Q11, Q13, Q22(b), Q23, Q24(b), Q26 |
| 2025 | Q11, Q14, Q24, Q25(c), Q27, Q28, Q28(b), **Q29** | Q20 |

49 crops, 18 tables. Almost every crop is line art the paper drew itself — graphs, geometry
diagrams, box plots, scatterplots, probability trees. **Two are illustrations rather than maths**:
2022 Q17 (a pyramid of playing cards) and 2024 Q28 (a Ferris wheel).

Six of the 18 tables are **future-value / z-score lookup tables** (2021 Q25, 2022 Q21, 2023 Q15,
2024 Q24(b), 2024 Q26, 2025 Q20) — candidates for Stage 3 decision 9's scroll wrapper.
⚠️ **"Lookup table" is not the test; the column count is.** 2023 Q15's future-value table
has only **5 columns** and fits at 390 px unwrapped, while the table that actually needed the
wrapper that year was **Q23's 11-column z-table**, which is not on this list at all. Count the
columns of every table you build. *(This line originally said they were "exactly what
`.study-dtable`'s stacked-card collapse exists for" — that class is Study Mode only and the
question renderer never applies it.)* Three more are **blank tables the student fills in**
(2022 Q12(b), 2024 Q11, Q13): reproduce the table as HTML and mark the answer as text — see
Stage 3 decision 4.

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

## Stage 3 — Schema ✅ COMPLETE

**Every field, character and markup form Stage 4 needs is fixed here.** Nothing below is a
preference to revisit per question. The six decisions the runbook carried are taken; **four more
surfaced from reading the engine** and are taken too. Every rendering claim was measured in a
browser at a 430 px viewport against `index.html`'s own CSS — not inferred from the markup.

### The engine, as it actually is

Read this before doubting any decision below. Line numbers are `index.html`.

| Fact | Where | Consequence |
|---|---|---|
| `q.q` renders through `formatQuestionText()`, which passes HTML through untouched | 1630, 1706 | Raw `<table>`, `<img>`, `<em>`, `<sup>` all work in a stem |
| `formatQuestionText()` also parses **pipe-delimited markdown tables** into `.q-table` | 1637–1652 | Unused by Maths — Standard 2 writes `<table>` HTML in all 34 of its tables |
| Options are injected raw: `<span class="option-label">A.</span>${opt}` | 1744 | Option strings may contain HTML |
| With `optionImages`, option text is **also** used as `alt="${opt}"` | 1739 | An option string carrying `"` breaks the tag. Never combine HTML options with `optionImages` |
| The results breakdown injects `q.q` and `q.options[i]` **raw** into a 12 px div, bypassing `formatQuestionText()` | 2208–2210 | A `<table>` option renders a whole table into the results card |
| `s.categories` is the sorted union of MC + written `category`, built at load | 730–734 | Filter chips are data-driven; nothing to register |
| Category chip labels come from **one global flat map** `NESA_CAT_LABELS`, keyed on the bare code | 705–716, 991 | **Collides — see decision 8** |
| The written-question badge reads `q.topic` only; the MC badge reads `q.category \|\| q.topic` | 1764 vs 1696 | **Canonical `category` renders no badge on written questions — decision 10** |
| Marks badge reads `q.marks \|\| q.maxMark \|\| q.totalMarks` | 1760 | Canonical `marks` is correct |
| `body { overflow-x: hidden }`; `.question-area { padding: 22px 20px }` | 60, 213 | Stem width is **390 px** at a 430 px viewport, and anything wider is **clipped, not scrolled** |
| `validate_subjects.cjs` **fails** a written question with neither `keywords` nor `acceptableAnswers` | validator 74 | A scoring mechanism is mandatory, not optional |
| `check_written_key.cjs` parses `qNum` with `^(\d+)(\([a-z]+\))*$` | checker 69 | `16`, `23(a)`, `19(b)(i)` parse; nothing else does |

### Field mapping — the Gate 3 artifact

Canonical throughout (playbook §4). **No deviations.** Maths Advanced has past papers, an
official syllabus code per question and an official mark, so every canonical field is available.

**MC question** — `subjects/mathematics-advanced.json` → `mcQuestions[]`

| Field | Type | Rule |
|---|---|---|
| `year` | number | 2020–2025 |
| `qNum` | number 1–10 | From the paper. **Carried from the first question authored** |
| `category` | string | Bare syllabus code, `MA-` stripped — `C3`, `T1`. From the mapping grid (decision 7) |
| `q` | string | Stem. HTML allowed |
| `image` | string | `/diagrams/mathematics-advanced_{year}_Q{n}_stimulus.jpg`, omitted if none |
| `optionImages` | array of 4 | `…_A.jpg` … `…_D.jpg`. Omitted if text options |
| `optionImagesWide` | bool | ⚠️ **Set where the 2×2 grid renders the option unreadably short — measure it, do not trust the ratio.** This row said "**Never set**, Stage 1 measured all 12 option sets at 0.8:1–2.6:1" until 2026-08-29. **2021 Q4 crops at 2.94:1 and renders 160 × 54 px in the grid against 360 × 122 px one-per-row**, so it is set there. The other candidate, 2024 Q8, was measured (160 × 96 px) and does not need it &mdash; **2021 Q4 is the only one in the subject** |
| `options` | array of exactly 4 strings | Required even with `optionImages` |
| `answer` | int 0–3 | Indexes `options[]` in the paper's printed order |
| `optionExplanations` | array of 4 strings | Canonical per-option rationale |
| `solution` | string | `<div class="step"><span class="step-number">1.</span> …</div>`, matching Standard 2. Legitimately alongside `optionExplanations`, not instead of it |

**Written question** → `writtenQuestions[]`

| Field | Type | Rule |
|---|---|---|
| `year` | number | |
| `qNum` | string | `"17"`, `"23(a)"`, `"19(b)(i)"` — **only** these shapes parse |
| `section` | `"II"` | Standard 2 carries it on all 151; nothing reads it. Kept for symmetry |
| `category` | string | Bare code |
| `marks` | number | **From the mapping grid, never read off the paper.** Not `maxMark` |
| `q` | string | Stem. HTML allowed; diagrams go inline as `<img>` |
| `image` | `null` | Written diagrams are inline in `q`; Standard 2 has 71 inline `<img>` and **zero** populated `image` fields |
| `answer` | string | Model answer. Not `modelAnswer`/`sampleAnswer` |
| `keywords` + `minKeywords` | array + number | Non-numeric answers |
| `acceptableAnswers` | array | Single-value numeric answers |
| `bandDescriptors` | `{full, partial, minimal}` | Feeds the AI marking prompt. Standard 2 has it on 151/151 — match that |
| `omittedParts` | array | Only where a part is dropped (decision 5) |

⚠️ **At least one of `keywords` or `acceptableAnswers` is mandatory** — the validator fails the
build without it, and `buildKeywordFeedback()` (1992) is the entire offline marking path.

**Subject level:** `id` `mathematics-advanced` · `name` `Mathematics Advanced` · `icon` 📈 ·
`accentColor` `#5B7FA6` (`--accent3`, distinguishing it from Standard 2's amber) ·
`omittedQuestions` · `mcQuestions` · `writtenQuestions`. No `tips`, no `studyNotes` (deferred).

---

### The ten decisions

**1 · Braced piecewise functions — HTML, never a crop.** An inline borderless table with the
brace in a `rowspan` cell. Measured at 430 px: the brace cell and the two-row block are both
**48.3 px**, so the glyph spans the rows exactly, and the stem does not overflow.

```html
<table style="display:inline-table;vertical-align:middle;border-collapse:collapse;margin:0 0 0 4px">
  <tr><td rowspan="2" style="border:0;padding:0 4px 0 0;font-size:2.6em;font-weight:300;line-height:0.86;vertical-align:middle">{</td>
      <td style="border:0;padding:1px 0;text-align:left;font-size:0.85em"><em>x</em>&sup2; &minus; 1,&nbsp; <em>x</em> &lt; 2</td></tr>
  <tr><td style="border:0;padding:1px 0;text-align:left;font-size:0.85em">3<em>x</em> &minus; 5,&nbsp; <em>x</em> &ge; 2</td></tr>
</table>
```

Inline styles, not a class, so no `index.html` change is needed — matching the 29 inline-styled
tables Standard 2 already ships.

⚠️ **The `2.6em` is sized for two rows.** A three-row brace (2022 Q30) needs `rowspan="3"`
and `font-size:3.9em` — measured, brace cell 72.5 px against a 72.5 px three-row block.
Scale the em value with the row count and re-measure at 430 px.

**2 · Integrals and fractions — inline Unicode, following Standard 2.** `∫` U+222B with
`<sub>`/`<sup>` limits; `d<em>x</em>`; fractions written inline with `/`, parenthesised when the
numerator or denominator is compound. Standard 2 has **no** stacked-fraction markup anywhere —
it writes `1/48`, `(4/3)π`, `130/60 = 13/6` — so this matches an established bank rather than
inventing a form. A stem carrying `∫₀^(π/4) sec²x dx`, `P = 2x + 72/x`, `0 ≤ x ≤ 2π` and
`√3 ≠ ∞` measured 59.4 px over two lines, no overflow. Note `∫` renders narrow (4.9 px at 18 px
display weight) — thin, but a real glyph, not a fallback box.

**3 · Options printed as table rows → flatten to text options.** Affects **2020 Q2, 2020 Q3,
2022 Q2, 2023 Q4**. Render the table's *header* row as the closing line of the stem so the
columns are named once, then flatten each option: `Median: Changes · Mean: Stays the same`.

Why flatten rather than keep a one-row table per option, which Standard 2 2020 Q8 does: the
results breakdown injects `q.options[i]` raw into a 12 px card (2209), so a table option renders
a whole table there, and `optionExplanations` then has to refer to a row the student cannot read
back. A flattened option measured **52 px** — one option button, no wrap problem. Apply to all
four; do not mix forms.

**4 · Blank tables the student fills in.** Affects **2024 Q11** and **2024 Q13** (2022 Q12(b) is
omitted anyway — it also asks for a graph). Reproduce the table as HTML with the blank cells
present and empty (`<td>&nbsp;</td>`); the model answer is the cell values in row order, labelled
by their column header:

```jsonc
"answer": "x = 1: y = 3\nx = 2: y = 9",
"keywords": ["3", "9"], "minKeywords": 2
```

A 5-column blank table measured 390 px — fits. The stem HTML is what gets posted to
`/mark-written` as `question` (2060), so the AI marker sees the table too.

**5 · Omissions — shapes confirmed against `check_written_key.cjs`.** Stage 1 enumerated
**12 `omittedParts` and 5 `omittedQuestions` (17 marks)**.

```jsonc
// subject level — 2020 Q16, 2020 Q24, 2021 Q19, 2021 Q21, 2024 Q19
"omittedQuestions": [ { "year": 2020, "qNum": 16, "marks": 4, "reason": "…" } ]
// on the question — the other 12 parts
"omittedParts":    [ { "part": "a", "marks": 1, "reason": "…" } ]
```

The checker validates each `omittedQuestions` entry three ways (the question exists in the
official key, the marks match, and it is *not* also present in the bank) and adds `omittedParts`
marks back before comparing — so both keys are enforced, not decorative. `reason` is prose for a
human and must say what the student is asked to *produce*.

**6 · Mathematical characters — Unicode, fixed now.** Standard 2's live bank already uses
`−` U+2212 (883×), `×` (1024×), `π` (61×), `√` (16×), `≤`/`≥`, `θ`, `σ`, `Δ` and the Unicode
superscripts `⁰¹²³⁴⁵⁶ⁿ⁻` (over 300×, against 5 uses of `<sup>`). Match it exactly, and add
`∫` U+222B, `∞` U+221E, `≠` U+2260, `→` U+2192.

- **Unicode superscripts for single-character exponents** (`x²`, `e⁻ˣ`); `<sup>` only where the
  exponent is a compound expression (`2<sup>x+1</sup>`).
- `<em>` for variables — Standard 2 uses it 334×.
- Every character above was width-measured in the app's own fonts: all render real glyphs, none
  falls back to a notdef box.
- ⚠️ These characters **do not exist in the text layer** (∞ and √ never; π extracts as `p`).
  They are typed in from the rendered page, per Stage 4.

**7 · A part with two syllabus codes — 7 of 294.** The mapping grid stores `codes` as a
*sorted set*, so "take the first" means "take the alphabetically first", which is arbitrary:
2025 Q28(b) would file a trig-graphs question under `T1` rather than `T3`.

**Rule: the 287 single-code parts take their code mechanically. For these 7, Stage 4 picks the
code naming the skill the marks are actually awarded for, at transcription time, and records the
full official list on the question as `gridCodes: ["T1","T3"]`** — so the pick is auditable and
NESA's tagging is not lost. `gridCodes` is inert data; the validator ignores unknown keys.

| Year | Parts (codes) | n |
|---|---|---|
| 2023 | Q28 C1/C4 | 1 |
| 2024 | Q22(a) C2/C3 · Q30 F2/M1 | 2 |
| 2025 | Q17(c) E1/M1 · Q21(b) E1/S3 · Q27(c) C3/C4/E1 · Q28(b) T1/T3 | 4 |

2020, 2021 and 2022 have none, and **none is in Section I**.

⚠️ **This table said 21 until 2026-08-28, and 14 of those 21 were an extraction artefact.**
`build_mapping_grid.py` gave each row "the lines from just after the PREVIOUS label to just
before the NEXT one" — a comment that names the very problem it causes. A Content cell holding
two or three codes is **vertically centred**, so its first line sits above its own label line and
its last line below: the codes leaked into the neighbouring rows in *both* directions. 2025
Q17(c) (`E1`/`M1`) pushed `E1` up into Q17(b) and `M1` down into Q18; Q27(c) (`C3`/`C4`/`E1`)
pushed `C3` up into Q27(b) and `E1` down into Q28(a). Marks were never affected, so every paper
still reconciled to 100 and nothing flagged it. **The fix reads the grid's own drawn horizontal
rules and assigns each line to the ruled band it falls in** (`row_rules()` / `band_of()`);
the label-bracketing path survives only as a fallback for a page with no usable rules. Six
Mathematics Standard 2 rows were wrong the same way (2021 39(b), 2021 41, 2023 32(b), 2023 34(a),
2024 28, 2024 30) — all in Section II, so §10's claim that all 90 Standard 2 MC questions agree
with NESA's tagging is untouched. Both subjects were regenerated and `data/exam-trends/` rebuilt
on top of them. Four already-ported questions carried a `gridCodes` list that was spurious once
corrected (2020 MC Q2, 2020 Q13, 2020 Q26, 2023 Q27); the key is now absent on all four, and no
`category` changed.

**8 · The category-label collision is real, and it is in the engine.** Stage 2 warned "never key
a shared lookup on the bare code." `NESA_CAT_LABELS` (705) **is** that lookup — one flat global
map, consulted for whichever subject is on screen. **Five of Advanced's 14 codes collide**, each
meaning something different:

| Code | Would render as (Standard 2's wording) | Should read |
|---|---|---|
| `F1` | F1 — Money Matters | Working with Functions |
| `F2` | F2 — Investment | Graphing Techniques |
| `M1` | M1 — Measurement | Modelling Financial Situations |
| `S1` | S1 — Data Analysis | Probability & Discrete Probability Distributions |
| `S2` | S2 — Probability | Descriptive Statistics & Bivariate Data |

**Decision: the data keeps bare syllabus codes** — they match Standard 2's convention, the
mapping grid and the syllabus, and prefixing them (`MA-C3`) would put a prefix in front of the
student on every filter chip. **The map becomes subject-aware instead**, at Stage 7:
`NESA_CAT_LABELS[subjectKey]?.[c] || c`, with today's entries moved under `maths`. Two chip call
sites (991, 1170). Do **not** ship Advanced before this — five of fourteen filters would carry
another subject's topic names. *(Noticed in passing: `M6` is live in the Standard 2 bank but
absent from the map, so it already renders bare. Pre-existing; not this port's to fix.)*

**9 · Wide lookup tables need a scroll wrapper — measured, not assumed.** Six of the 28 tables
are future-value / z-score grids (2021 Q25, 2022 Q21, 2023 Q15, 2024 Q24(b), 2024 Q26, 2025 Q20).
At a 430 px viewport the stem is **390 px** wide.

| Case | Measured | Verdict |
|---|---|---|
| 6-column `.q-table` | 390 px | Fits — `width:100%` compresses it |
| 8-column `.q-table`, bare | **513 px**, and `body.scrollWidth` 533 against a 430 px client | Overflows the page; with `body{overflow-x:hidden}` the far columns are **silently clipped** |
| Same inside `<div style="overflow-x:auto">` | wrapper 390 px, scrolls to 520 px internally; `body.scrollWidth` back to 430 | **Correct** |

**Rule: any table with 7 or more columns is wrapped.** Use `class="q-table"` (251) rather than
inline-styled borders — it is the app's own question-table style, uses the design tokens, shades
the header row and left-aligns the first column. Standard 2's 29 inline-styled `#ccc` tables are
debt, not precedent.

```html
<div style="overflow-x:auto;-webkit-overflow-scrolling:touch;margin:14px 0">
  <table class="q-table" style="min-width:520px;margin:0">…</table>
</div>
```

⚠️ **The runbook and the playbook were both wrong about why this matters** — both said mobile
tables need "`.study-dtable`'s stacked-card collapse." `.study-dtable` is applied in exactly one
place (1343, `renderStudyBlock()`) and **the question renderer never uses it**. Question tables
get `.q-table` or `.nesa-table`, and neither collapses *or* scrolls. Both documents are corrected
in this session.

**10 · Written questions render no topic badge.** The written path reads `q.topic` (1764); the MC
path reads `q.category || q.topic` (1696). Canonical `category` therefore shows a year badge and
no topic on every written question — the same class of defect as HMS's missing marks badge:
nothing throws, nothing scores wrong, no validator sees it. **Decision: keep `category` (it is
canonical, and it already drives the written filter at 779) and fix the engine at Stage 7** —
one line, mirroring the MC path. That also lights up Standard 2's 151 written questions, which
have carried `category` and shown no badge since their port.

### Deliberate deviations from canonical

**None.** The two additions — `gridCodes` (decision 7) and `section` (Standard 2 parity) — are
extra provenance, not renames of a canonical field.

### Carried into later stages

| Stage | Item |
|---|---|
| 4 | Pick the code for the 7 multi-code parts; record `gridCodes` |
| 4 | Wrap the 6 wide lookup tables; `class="q-table"`, no inline borders |
| 7 | **Blocking:** make `NESA_CAT_LABELS` subject-aware (decision 8) |
| 7 | One-line written-badge fix, `q.category \|\| q.topic` (decision 10) |

**GATE 3** — [x] field mapping written down before any question is authored · [x] every
deviation deliberate and recorded (there are none)

---


## Stage 4 — Port + assets ✅ COMPLETE (6 sessions, one paper per session)

**Stage 5 is folded into this stage.** Each session ports **one year and crops that year's own
assets**, finishing green. The asset *method* — crop tooling, the DPI trap, the option-label
rule — is still written out below as Stage 5, as a reference these sessions consult; it is no
longer a separate scheduling stage.

⚠️ **Why they were merged** (decided 2026-08-28): `validate_subjects.cjs` **exits 1** on a
question whose `image` path has no file yet — verified, not assumed. Porting all six papers
first and cropping afterwards would leave the validator, and CI on every push, red for six
sessions, and Gate 4's own wording ("validator green, `missingImages: 0`") is unsatisfiable
under that order. Interleaving makes the gate honest and keeps every question answerable the
moment it is authored.

### Branch — do not commit these sessions to `main`

**The branch already exists, locally and on `origin`** (created 2026-08-28, first push after
the 2020 paper). Do not create it again:

```bash
git checkout port/maths-advanced     # add `origin/` after a fresh clone
git pull
```

Merge to `main` only when the whole subject is ported, cropped, ground-truthed and green.
`main` stays a clean signal throughout, and Cloudflare gives the branch its own preview URL —
use it for the mobile-width browser check rather than shipping a half-ported subject to
`cramit-quiz.pages.dev`.

### Per-year load and progress

Derived from the Stage 1 lists; reconciles to the 124 crops and 28 tables recorded
above. Crop counts are a **lower bound** — 2023 and 2022 each came in one over their estimate. "Corrupt" is that paper's share of parts carrying a detectable text-layer defect.

| Session | Year | Parts | Crops | Tables | Corrupt | Status |
|---|---|---:|---:|---:|---:|---|
| 1 | **2020** | 49 | 18 | 4 | 37% | ✅ 2026-08-28 |
| 2 | **2023** | 48 | 17 | 6 | 50% | ✅ 2026-08-28 |
| 3 | **2022** | 52 | 21 | 3 | 37% | ✅ 2026-08-28 |
| 4 | **2025** | 50 | 23 | 2 | 42% | ✅ 2026-08-28 |
| 5 | **2021** | 48 | 22 | 6 | 50% | ✅ 2026-08-29 |
| 6 | **2024** | 47 | 23 | 7 | 38% | ✅ 2026-08-31 |

**Tick the Status cell at the end of each session** — that is how the next cold session knows
which paper is next.

⚠️ **The old suggested order (2024 first, "lightest asset load — 2 graphic-bearing MC") was
wrong, and is corrected here.** 2024 Section I has **seven** graphic-bearing MC (five stimulus,
two option sets), and 2024 is the **heaviest** paper of the six at 30 assets. That sentence came
from Stage 0 and survived Stage 1's corrections uncaught. **2020 leads instead**: joint-lightest
at 22 assets, the lowest corruption rate, and it exercises three Stage 3 decisions early where
they are cheap to correct — options printed as table rows (Q2, Q3, decision 3), two whole
`omittedQuestions` (Q16, Q24, decision 5) and an `omittedParts` entry (Q11(a)). 2024 goes last:
heaviest, and the only paper using the MathType bracket mapping.

### Per session

**Stage 3 fixed every field name, character and markup form — follow it, do not re-decide.**
The field tables are the contract; decisions 1–6 cover piecewise braces, integrals and
fractions, table-row options, blank tables, the two omission keys, and the Unicode set.

Section I, then Section II, then that year's crops, then validate.

- **Carry `qNum` from the first question authored.** Retrofitting needs `backfill_qnum.py`,
  which refuses to guess; skipping it left 135 questions unverifiable for months across
  Multimedia and VET.
- **Take `category` and `marks` from `data/mapping-grid/mathematics-advanced.json`** — do not
  read them off the paper. For the **21 parts carrying two or three codes** (enumerated in
  Stage 3 decision 7 — 2020 ×3, 2023 ×2, 2024 ×6, 2025 ×10), pick the code naming the skill the
  marks are awarded for and record the full official list as `gridCodes`.
- **Transcribe Section II from rendered pages, not the text layer.** This is not optional:
  `^x - 1h2` is `(x − 1)²`. Render at ~140 dpi and read the image.
- Tables become reconstructed `<table class="q-table">` HTML, never a crop. **7 columns or more
  goes inside an `overflow-x:auto` wrapper** — the stem is 390 px on a phone and `body` hides
  its overflow, so a wide table is clipped rather than scrollable. Stage 3 decision 9 has the
  markup and the measurements.
- Drawing parts get an `omittedParts` entry; a whole unportable question gets
  subject-level `omittedQuestions`. Silent omission is how 2020 Standard 2 sat at 84/85 marks
  for over a year.
- **Crop this year's assets in this session**, using the method reference below, and open every
  crop against the paper before finishing.
- `node scripts/validate_subjects.cjs` must be **green with `missingImages: 0`** before the
  session ends. That is now achievable, and it is the point of the merge.

### Decisions the 2020 session took that every later year inherits

The first porting session settled five things Stage 3 left open because they only surface
once questions are actually being written. **Follow them; they are not per-year choices.**

**1 · One bank entry per NESA question, not per part.** `subjects/mathematics-advanced.json`
stores 2020's Section II as **19 written entries**, one per question, with the parts laid out
in the stem and the model answer covering all of them. That matches Mathematics Standard 2
(140 of its 151 written entries are merged this way) and it reconciles trivially with
`check_written_key.cjs`, which sums every official leaf part under a bank entry's `qNum`
prefix. Per-part entries are legal but were not used.

**2 · A merged entry spanning parts with different codes takes one `category` and records
the union in `gridCodes`.** Stage 3 decision 7 covers a *part* carrying two codes; merging
creates the same problem one level up. Same rule: pick the code naming the skill the marks are
awarded for, keep NESA's full list in `gridCodes`. 2020 used it on Q18 (`C2` of `C2/C4`),
Q21 (`E1` of `C3/E1`), Q25 (`C3` of `C3/F1`), Q30 (`C4` of `C4/F1`) and Q31 (`T3` of `C3/T3`),
alongside the three single-part multi-code cases Stage 3 already enumerated.

**3 · An omitted part inside a question the bank still carries forces the merged form.**
2020 Q11 loses part (a) — draw the model on a printed grid. If (b) and (c) were separate
entries, each would match only its own leaf and the dropped mark would vanish silently, which
is exactly what `omittedParts` exists to prevent. Stored as one entry `"11"` with
`"marks": 3` and `omittedParts: [{part: "a", marks: 1}]`, the checker adds the mark back and
reconciles against the official 4.

**4 · NESA's part letters are kept even when a part is dropped.** Q11 presents "(b)" and "(c)"
with no "(a)", followed by a visibly separate italic note saying part (a) asked for a graph on
a printed grid and is not included. Re-lettering (b)→(a) would be rewording NESA; leaving the
paper's "the grid on the previous page" dangling with no explanation would be worse for the
student. The note is clearly ours, outside the quoted text.

**5 · Options carrying `optionImages` must be plain text — no HTML.** The engine reuses the
option string as `alt="${opt}"` (1739). 2020 Q5 and Q9 therefore describe their graphs in bare
text with literal `μ`/`σ`, while every other option string in the paper uses `<em>`/`<sup>`.

**6 · Every inline stem `<img>` carries `style="max-width:100%;height:auto;display:block;margin:14px auto"` —
and the session verifies it in the browser.** *(Added by the 2021 session, which shipped nine
without it.)* There is **no `.q-text img` rule in `index.html`**; the only `max-width` on a
question image is `.device-phone .q-image-wrap img` (306), which governs the separate `image`
field, not an `<img>` written inside `q`. An unstyled stem image therefore renders at its natural
crop width — 1767 px inside a 390 px stem, in the worst 2021 case — and `body { overflow-x: hidden }`
swallows the overflow instead of scrolling it. Nothing reports this: `body.scrollWidth` still
reads 430, `validate_subjects.cjs` only existence-checks the path, and no console error fires.
The diagram is simply cut off. Mathematics Standard 2 has used this inline style on all 71 of its
stem images since its port, so it is an established convention, not a new one.

**The check that catches it** is comparing each question's own box against its content, which no
page-level measurement does:

```js
[...document.querySelectorAll('.question-area')]
  .filter(a => a.scrollWidth > a.clientWidth + 1)   // must be empty
```

It is now a Gate 4 item.

### 2020 — done (2026-08-28)

10 MC + 19 written entries + 2 `omittedQuestions` (Q16, Q24) + 1 `omittedParts` (Q11(a)).
**Marks reconcile to exactly 100/100** against the mapping grid, per question as well as per
paper, and every `category` was asserted to be one of NESA's own codes for that question.

**All ten MC answers were checked against the official key** before authoring, by calling
`extract_mc_key()` from `build_answer_key.py` read-only on `2020_marking_guidelines.pdf` —
`D B A B C B A A C D`. Ten independent derivations from the paper agreed with all ten. That
does not replace Stage 6 (which commits the key and puts it under CI); it just means the port
did not start from guesses.

**Assets: 18 crops, via a new `scripts/crop_maths_advanced.py`.** Deliberately *not* an entry
in `scripts/diagram_registry.json` — that registry's coordinates are raw pixels verified at
`RENDER_DPI = 150`, `save_crop()` overwrites unconditionally, and a bare run re-cuts every
Standard 2 crop. The new script stores **PDF points**, so its `RENDER_DPI` can change without
moving a crop, and takes `--year`, so each remaining session adds one registry block.

⚠️ **The option letter cannot be excluded with an x-cut on these papers.** It sits in the
cell's top-left corner and the graph runs underneath it: on 2020 Q5 option A the letter spans
x 100.8–111.3 pt and the graph's own x-axis starts at x 102.2 pt. A first pass cropped from
x = 114 and silently amputated the left arm of the parabola and the end of the axis — plausible,
non-empty, wrong, exactly the failure mode the DPI trap has. The script instead crops the whole
cell and **paints a white `erase` rectangle over the letter's own bounding box**, each one
checked against an ink profile of that x-strip first (nothing but the letter lies inside it).

Coordinates came from an ink profile (dark pixels at 150 dpi, banded with a configurable gap)
rather than the text layer, since the option letters and most axis labels are outline paths.
All 18 crops were then rendered into contact sheets and compared against the paper option by
option.

**Measured in the browser at a 430 px viewport** (stem 390 px), not inferred:

| Case | Measured | Verdict |
|---|---|---|
| Q3's 4-column table, bare `.q-table` | 390 px, `body.scrollWidth` 430 | fits |
| Q20's **7-column** table in the `overflow-x:auto` wrapper | wrapper 390 px, scrolls to 520 px, `body.scrollWidth` **430** | decision 9 works |
| Q23's piecewise brace (decision 1) | brace cell 38.0 px, two-row block 38.0 px, table 183 px | glyph spans the rows exactly |
| Q5 option images in `.options-grid-2x2` | 160 × 143 px each | legible |
| Q9 option images in `.options-grid-2x2` | 160 × 90 px each | legible |
| Unicode set (`∫ ∞ √ ≠ → π σ μ − ≤ ² ³`) | 4.9–18.0 px, all distinct from `�` at 17.5 px | real glyphs, no notdef |

**`optionImagesWide` confirmed unnecessary**, as Stage 1 predicted: at 160 px wide these render
143 px and 90 px tall, nothing like the VET 160 × 35 px case that created the flag.

**The file round-trips byte-for-byte** through `json.dumps(indent=2, ensure_ascii=False)` plus a
trailing newline — verified. Unlike `multimedia.json`, which has hand-authored compact inline
arrays and must never be round-tripped, this file is safe to load, extend with a year, and dump.
That is how sessions 2–6 should append.

**Not done here, and correct that it is not:** the subject is still registered nowhere —
no `subjects/index.json` entry, no `SUBJECT_ID_MAP`, no `SUBJECT_CATALOGUE`, no subject card.
That is Stage 7. `validate_subjects.cjs` picks the file up anyway (it globs `subjects/*.json`),
so CI covers it from now on; the two key checkers skip it until Stage 6 commits its keys.

### 2023 — done (2026-08-28)

10 MC + 22 written entries + 3 `omittedParts` (Q18(a) 3, Q19(a) 2, Q30(b) 2) and **no new
`omittedQuestions`** — 2023 has no whole unportable question, exactly as Stage 1 predicted.
**Marks reconcile to exactly 100** against the mapping grid: 10 MC + 83 written + 7 omitted.
The build script refuses to write unless the prefix-sum join, the paper total, every `category`
being one of NESA's own codes for that question, and every `gridCodes` list matching NESA's own
union all hold.

**All ten MC answers were confirmed against the official key before authoring**, by calling
`extract_mc_key()` read-only on `2023_marking_guidelines.pdf` — `D D A B A C A B D C`. Ten
independent derivations from the paper agreed with all ten.

**Assets: 17 crops** via `scripts/crop_maths_advanced.py --year 2023` (a new registry block).
Section I: Q1, Q2, Q4, Q5, Q10 stimulus + Q6's four option cells. Section II: Q16, Q22, Q23,
Q24, Q26, Q27, Q28, Q32. Coordinates came from an ink profile at 150 dpi, then every crop was
built into a contact sheet and compared against the paper.

⚠️ **Stage 1's Section II crop list was one short: 2023 Q16** (the shape *APQBCD*, a labelled
geometry diagram) is not on it and was found only by reading the question's own page while
porting. The list is a **lower bound** — the three unioned detectors under-count. Corrected
above; the subject total moves 121 → 122.

⚠️ **The "six wide lookup tables" list is not the test for decision 9 — the column count is.**
2023 Q15's future-value table is on that list but has only **5 columns** and measures 390 px
unwrapped, so it needs nothing. The table that actually needed the wrapper is **Q23's
11-column z-table**, which is not on the list at all. Count columns on every table you build.

**Two option-letter facts, both different from 2020.** On page 6 the `A.`/`B.`/`C.`/`D.` glyphs
are real **text**, not outline paths, so `get_text("words")` returns their exact boxes; and
`get_drawings()` reports **zero** vector paths intersecting any of the four boxes, so the white
`erase` rectangle removes the letter and nothing else. The 2020 amputation trap does not arise
here — but it was checked rather than assumed, and every remaining year should be checked the
same way.

**Measured in the browser at a 430 px viewport** (stem 390 px), all 32 questions rendered:

| Case | Measured | Verdict |
|---|---|---|
| `body.scrollWidth`, every one of the 32 questions | **430**, never more | nothing clipped |
| Q23's **11-column** z-table in the `overflow-x:auto` wrapper | wrapper 390 px, scrolls to 694 px internally | decision 9 works |
| Q15's 5-column future-value table, bare `.q-table` | 390 px | fits — no wrapper needed |
| Q12 (6 col), MC Q2 (6 col), MC Q6 (4 col), bare | 390 px each | fit |
| Q29's piecewise brace (decision 1) | brace cell **48.3 px**, two-row block **48.3 px**, table 222 px | glyph spans the rows exactly |
| MC Q6 option images in `.options-grid-2x2` | 160 × 131 px each | legible |
| MC Q4's flattened table-row options (decision 3) | 52 px per button, no wrap | one line each |
| Every stimulus image | loads, `naturalWidth` non-zero, 388–390 px wide | none broken |
| 40 distinct non-ASCII characters used | 3.4–15.7 px, all distinct from `�` at 17.5 px | real glyphs, no notdef |

Zero console errors. `optionImagesWide` again unnecessary (1.22:1 option crops).

**Two multi-code merges beyond Stage 3's list**, both settled by the same rule and recorded in
`gridCodes`: Q26 (`C4` of `C4/T3`) and Q32 (`C4` of `C4/F1`) split their marks **evenly**
between two codes, which the "take the code the marks are awarded for" rule does not decide.
**Tie-break, inherited by the remaining papers: take the part carrying the heavier mathematical
demand** — in both cases the calculus part — and keep NESA's full list in `gridCodes`. That
also matches 2020's Q30, which took `C4` of `C4/F1`. Q24 (`C3` of `C3/F1`, 4 marks against 1),
Q27 (`F2` of `C1/C4/F2`, 3 against 2) and Q28 (`C4` of `C1/C4`, single part) were decided by
mark weight and by which skill the work sits in.

**Q19 is the "leans on an omitted part" case for 2023, and it stands alone.** Its (b) says
"Hence, **or otherwise**, solve the inequality", so dropping the sketch in (a) costs the student
nothing — unlike 2021 Q27(d), which is still open for that session.

### 2022 — done (2026-08-28)

10 MC + 22 written entries + **2 `omittedParts`** (Q12(b) 2, Q27(c) 3) and **no new
`omittedQuestions`** — like 2023, no whole 2022 question is a drawing task, exactly as Stage 1
predicted. **Marks reconcile to exactly 100**: 10 MC + 85 written + 5 omitted. The build script
refuses to write unless the prefix-sum join, the paper total, every `category` being one of
NESA's own codes for that question, every `gridCodes` list matching NESA's own union, and every
grid part having a bank entry all hold — and unless the existing file round-trips byte-for-byte
first.

**All ten MC answers were confirmed against the official key before authoring**, by calling
`extract_mc_key()` read-only on `2022_marking_guidelines.pdf` — `A D B A D B C C A B`. Ten
independent derivations from the paper agreed with all ten.

**Assets: 21 crops** via `scripts/crop_maths_advanced.py --year 2022` (a new registry block).
Section I: Q3, Q7, Q8, Q10 stimulus + Q1's and Q10's four option cells each. Section II: Q11,
Q14, Q16, Q17, Q24, Q28 (×2), Q29, Q31. Coordinates came from an ink profile at 150 dpi, then
every crop was built into a contact sheet and compared against the paper.

⚠️ **Stage 1's crop list under-counts a second way: one list entry can be two diagrams.**
2022 **Q28** is a single entry on that list but the paper draws the circle twice — once for
part (a) with the sector shaded, and again on the next page with the hyperbola added for
part (c). Both are needed; the stem carries both. **Naming convention set here, inherited by
later years: a second diagram inside one question takes the part letter as a suffix on the
question number** — `mathematics-advanced_2022_Q28b_stimulus.jpg` beside
`…_Q28_stimulus.jpg`. 2025's list has `Q25(c)` and `Q28(b)` entries and will need it. Subject
total moves 122 → **123**.

⚠️ **Q21 is the year's 7-column table, and it did need the wrapper.** Unlike 2023 — where the
listed "wide lookup table" fitted and an unlisted one overflowed — 2022's future-value table
*is* on Stage 1's list of six and *is* 7 columns wide. That does not rehabilitate the list:
the rule remains **count the columns of every table you build**. Q11's 4-column complaints
table needs nothing.

**Option letters: the 2020 amputation trap did not recur, but was checked.** On page 2
(Q1's options) the text layer is garbled — the `A.` glyph extracts as the word `Mul` — so the
letter boxes were derived from the *geometry* instead: `C.`/`D.` extract cleanly, and the two
option rows are a fixed 156.7 pt apart, which places `A.`/`B.` exactly where the garbled span
sits. On page 7 (Q10's options) all four letters are real text. **`get_drawings()` reports zero
vector paths intersecting any of the eight letter boxes**, so the white `erase` rectangle
removes the letter and nothing else. ⚠️ But an x-cut would still have been wrong on Q10: option
A's lower-left branch starts at x = 103.6 pt, *left* of the letter's right edge at 114.9 pt —
they miss each other only in <em>y</em>. Crop the whole cell and erase.

**Three multi-code merges, all settled by the rules already in the runbook**, with NESA's full
list kept in `gridCodes`: Q18 (`C2` of `C2`/`C4`, 2 marks against 1), Q27 (`C3` of `C2`/`C3` —
`C3` carries 5 of the 7 marks, counting the omitted part) and Q31 (`C3` of `C3`/`F1`, 4 against
2). Q28 (`C4` of `C4`/`F1`/`T1`) and Q29 (`C4` of `C4`/`M1`) went the same way on mark weight.
**Q20 is the year's even split** — `E1` 2 marks, `C3` 2 marks — so the 2023 tie-break applies:
take the part carrying the heavier mathematical demand, here differentiating the exponential
model in (c), giving `C3`.

**Measured in the browser at a 430 px viewport** (stem 390 px), all 32 questions rendered
through `index.html`'s own CSS in a throwaway harness:

| Case | Measured | Verdict |
|---|---|---|
| `body.scrollWidth`, all 32 questions | **430**, never more; no `.question-area` overflows | nothing clipped |
| Q21's **7-column** future-value table in the wrapper | wrapper 390 px, scrolls to 560 px internally | decision 9 works |
| Q11's 4-column complaints table, bare `.q-table` | 390 px | fits — no wrapper needed |
| Q30's **three-row** piecewise brace (decision 1) | brace cell **72.5 px**, three-row block **72.5 px**, table 171 px | glyph spans the rows exactly at `font-size:3.9em` |
| MC Q1 option images in `.options-grid-2x2` | 160 × 163 px (0.98:1) | legible |
| MC Q10 option images in `.options-grid-2x2` | 160 × 174 px (0.92:1) | legible |
| All 21 images | load, `naturalWidth` non-zero, stimulus 388–390 px wide | none broken |
| 31 distinct non-ASCII characters used | 3.4–18.0 px; `→` and `…` also rasterised and compared to `�` (74 and 30 ink pixels against notdef's 380) | real glyphs, no notdef |
| `<sup>` exponents (Q27, Q29, Q32, MC Q6) | 15 px against an 18 px base, `vertical-align: super` | real superscripts |

Zero console errors. `optionImagesWide` again unnecessary.

⚠️ **Decision 1's brace needs `font-size:3.9em` for three rows**, not the 2.6em the two-row
template uses. 2023's two-row brace measured 48.3 px; three rows measure 72.5 px, and 3.9em
matches it exactly. Scale the em value with the row count and re-measure.

**One note on the harness**: it badges written questions with `q.category || q.topic`, i.e.
the *post-fix* engine. The live engine still reads `q.topic` alone (Stage 3 decision 10), so
these questions show no topic badge until the Stage 7 one-liner lands. That is a known blocking
item, not a new finding.

### 2025 — done (2026-08-28)

10 MC + 21 written entries + **2 `omittedParts` worth 3 marks** (Q15(b) 2, Q16(b) 1) and **no new
`omittedQuestions`** — as in 2023 and 2022, no whole 2025 question is a drawing task, exactly as
Stage 1 predicted. **Marks reconcile to exactly 100**: 10 MC + 87 written + 3 omitted. The build
script refuses to write unless the prefix-sum join, the paper total, every `category` being one of
NESA's own codes for that question, every `gridCodes` list matching NESA's union, every grid part
having a bank entry and every referenced image file existing all hold — and unless the existing
file round-trips byte-for-byte first.

**All ten MC answers were confirmed against the official key before authoring**, by calling
`extract_mc_key()` read-only on `2025_marking_guidelines.pdf` — `B A D C B C A D B C`. Ten
independent derivations from the paper agreed with all ten. Q9 is the one worth re-reading: the
straight-line estimate lands exactly on 6.2, and the answer is `[6.0, 6.2)` **because `f′` is
falling across the interval**, so the true rise is strictly under 0.2. The half-open intervals are
deliberate.

⚠️ **`data/mapping-grid/` was wrong, and this session fixed the extractor rather than working
around it.** Porting Q18 (composite functions) turned up `codes: ["MA-F1","MA-M1"]` — Modelling
Financial Situations on a function question. NESA's printed grid says `MA-F1` alone.
`build_mapping_grid.py` was giving each row "the lines from just after the PREVIOUS label to just
before the NEXT one", and a Content cell holding two or three codes is **vertically centred**, so
its lines leak into the rows above *and* below. **20 rows across the two maths subjects carried a
code NESA never assigned**, and because marks were untouched every paper still reconciled to 100
and nothing flagged it. The fix reads the grid's **own drawn horizontal rules** and assigns each
text line to the ruled band containing it. Full detail, and the corrected multi-code table
(21 → **7 of 294**), are in Stage 3 decision 7. Both mapping grids were regenerated,
`data/exam-trends/` rebuilt on top of them, and four stale `gridCodes` keys removed from
already-ported questions. **No `category` changed anywhere, and no answer or mark moved.**

**Assets: 23 crops** via `scripts/crop_maths_advanced.py --year 2025` (a new registry block).
Section I: Q6, Q9, Q10 stimulus + Q2's, Q4's and Q6's four option cells each. Section II: Q11,
Q14, Q24, Q25, Q27, Q28 (×2), Q29. Coordinates came from an ink profile at 150 dpi, then every
crop was built into a contact sheet and compared against the paper.

⚠️ **Stage 1's Section II crop list under-counts a third way: 2025 Q29.** The mountain-peak
diagram (T above O, with Y and F on level ground) is not in Stage 1's 2025 row, even though
Stage 1's own *method* paragraph names "2025 Q29" among the four diagrams found only by the union
of its three detectors. The table and the prose disagreed and the table was believed. Subject
total moves 123 → **124**. **Q25 needed no part-letter suffix** after all — its only diagram is in
part (c), so it is `…_2025_Q25_stimulus.jpg`; the suffix convention is for a *second* diagram in
one question, which here is only Q28.

⚠️ **A crop can be clipped by trusting the ink profile alone.** Q28(b)'s first cut used the ink
band's left edge, x = 85 pt, and silently removed the graph's y-axis labels 1, 2 and 3 — they
start at x = 78.4 pt, which the text layer gives exactly and the banded profile had merged away.
Cross-check any left or bottom edge that runs close to axis labels against `get_text("words")`
before accepting it. Caught by looking at the contact sheet, not by any assertion.

**Option letters: the 2020 amputation trap did not recur, and was checked.** On pages 3, 4 and 5
all twelve `A.`/`B.`/`C.`/`D.` glyphs are real text with exact boxes, and `get_drawings()` reports
**zero** vector paths intersecting any of the twelve, so the white `erase` rectangle removes the
letter and nothing else. On Q2 an x-cut would also have been safe (a blank column separates the
letter at x ≤ 109.4 from the graph at x ≥ 127.7) but on Q4 and Q6 the graph runs straight through
the letter's x-range — so erase stays the uniform method.

**Four multi-code parts, all genuine after the extractor fix**, with NESA's full list kept in
`gridCodes`: Q17 (`M1` of `E1`/`M1` — M1 carries 5 of the 7 marks, E1 only the logarithmic solve
in (c)), Q21 (`S3` of `E1`/`S3` — S3 owns (a) outright), Q27 (`C4` of `C3`/`C4`/`E1` — C4 carries
4 of 6) and Q28 (`T1` of `T1`/`T3` — T1 owns (a) outright). **Q25 is the year's even split** and
the hardest call: `C2` 2 marks, `C4` 2, `M1` 2, one per part. The 2023 tie-break (heavier
mathematical demand) does not settle it cleanly either, since the sting is in (c)'s arithmetic
series. It is filed under **`C4`**, because (a) exists only to supply the primitive that (b) and
(c) integrate with, and the series is a step inside an area calculation rather than the subject of
the question — the same reading that put 2022 Q28 under `C4`.

**Q15 is the "leans on an omitted part" case for 2025, and it is kept.** Part (b) asks for
P₂ to be sketched on the printed diagram and is dropped; part (c) says "Hence, find the values of
t … for which P₁ and P₂ are BOTH decreasing." Unlike 2021 Q27(d) — which points at "the graph
drawn in part (a)" and nothing else — part (c) names two functions whose **equations are both
given**, so it is fully answerable analytically. P₂'s definition is repeated inline in (c), and
the omission note says so explicitly rather than letting the substitution pass as NESA's wording.
Stage 1's other 2025 flag, Q16(b), is a plain "complete the printed graph" and is simply dropped.
**Q15's diagram was deliberately not cropped**: it exists to be drawn on, and supplying a grid
carrying only P₁ would invite the student to read P₂ off a curve that is not there.

**Measured in the browser at a 430 px viewport** (stem 390 px), all 31 questions rendered through
`index.html`'s own CSS in a throwaway harness:

| Case | Measured | Verdict |
|---|---|---|
| `body.scrollWidth`, all 31 questions | **430**, never more; no `.question-area` overflows | nothing clipped |
| Q20's **7-column** future-value table in the wrapper | wrapper 390 px, scrolls to 564 px internally | decision 9 works |
| MC Q1's 2-column distribution table, bare `.q-table` | 390 px | fits — no wrapper needed |
| Q21's **three-row** piecewise brace (decision 1) | brace cell **72.5 px**, three-row block **72.5 px**, table 121 px | glyph spans the rows exactly at `font-size:3.9em` |
| MC Q2 / Q4 / Q6 option images in `.options-grid-2x2` | 160 × 128, 160 × 154, 160 × 166 px | legible |
| Plain-text option buttons | 52 px, single line | no wrap |
| All 23 images | load, `naturalWidth` non-zero | none broken |
| 38 distinct non-ASCII characters used | none matches the notdef glyph's ink count (50 px²); only `&nbsp;` is blank | real glyphs, no notdef |
| `<sup>` exponents (MC Q2, Q10, Q16, Q27) | 15 px against an 18 px base, `vertical-align: super` | real superscripts |

Zero console errors. `optionImagesWide` again unnecessary (0.97:1 to 1.25:1). As in the 2022
session, **screenshots were unavailable** — the Browser pane was not displayed, so these are DOM
measurements rather than pictures. The harness badges written questions with
`q.category || q.topic`, the *post-fix* engine; the live engine still reads `q.topic` alone
(Stage 3 decision 10), so these show no topic badge until the Stage 7 one-liner lands.

Local CI green: `MC=686 Written=327 imageRefs=266 missingImages=0`; both key checkers still pass
203 written and 225 MC questions on the other subjects, which this session did not touch.

### 2021 — done (2026-08-29)

10 MC + 22 written entries + **2 `omittedParts`** (Q27(a) 2, Q28(b) 2) and **2 new
`omittedQuestions`** (Q19 3, Q21 2) — 2021 is the second paper after 2020 to carry a whole
unportable question, and it carries two, exactly as Stage 1 predicted. **Marks reconcile to
exactly 100**: 10 MC + 81 written + 4 omitted parts + 5 omitted questions. The build script
refuses to write unless the file first round-trips byte-for-byte and then all six content gates
hold — the prefix-sum join, the paper total, every `category` being one of NESA's own codes,
every `gridCodes` union, **every official part being covered by a bank entry or a declared
omission**, and every referenced image file existing.

**All ten MC answers were confirmed against the official key before authoring**, by calling
`extract_mc_key()` read-only on `2021_marking_guidelines.pdf` — `B C D C A D A C B B`. Ten
independent derivations from the paper agreed with all ten. Q7 is the one worth re-reading: the
answer turns on `f`(0) being **negative**, which is not stated and is only visible by zooming
into the origin — the curve crosses the *x*-axis just to the right of the *y*-axis.

**Assets: 22 crops** via `scripts/crop_maths_advanced.py --year 2021` (a new registry block).
Section I: Q4, Q6, Q7, Q8, Q10 stimulus + Q4's and Q5's four option cells each. Section II: Q12,
Q17 (×2), Q18, Q22, Q24, Q28, Q32, Q33. Stage 1's counts were **exactly right for this paper**,
the first year they have been — 22 crops, 6 tables, no surprises in either direction.

⚠️ **`optionImagesWide` IS needed for this subject after all, on 2021 Q4 — Stage 1 and Stage 3
were both wrong.** Stage 1 measured all 12 option sets at 0.8:1 to 2.6:1 and concluded it was
"not needed anywhere"; Stage 3's field table hardened that into "**Never set.**" 2021 Q4's four
cumulative-download charts crop at **2.94:1** (1446 × 492 px), outside the range Stage 1 quoted,
and the browser settles it:

| Layout | Measured, 430 px viewport | Verdict |
|---|---|---|
| `.options-grid-2x2` (the default) | **160 × 54 px** each | a 20-bar chart with a *y*-axis to 800 and days 1–20 labelled, in 54 px |
| `.options-list-wide` (`optionImagesWide: true`) | **360 × 122 px** each | legible |

160 × 54 px is the VET 160 × 35 px case that created the flag, not the 160 × 143 px case that
retired it. Both documents are corrected above. **The rule is not an aspect-ratio threshold and
never was — render the option set and look at the height.** 2024 Q8's histograms, whose ink
extent Stage 1 measured at 3.7:1, are the remaining candidate and must be measured the same way.

⚠️ **An inline stem `<img>` needs an explicit `max-width:100%`, and nothing enforces it.**
`index.html` has **no** `.q-text img` rule — the only `max-width` on a question image is
`.device-phone .q-image-wrap img` (306), which applies to the separate `image` field, not to an
`<img>` written inside `q`. Every 2020/2022/2023/2025 entry carries
`style="max-width:100%;height:auto;display:block;margin:14px auto"` inline; the 2021 entries were
authored without it, and all nine rendered at natural size — up to **1767 px inside a 390 px
stem** — with `body { overflow-x: hidden }` swallowing the overflow. `body.scrollWidth` still
read 430, the validator was green, and no console error fired: the diagrams were simply cut off
on the right. Caught only by measuring `.question-area` scrollWidth against clientWidth, which is
now a standing check (below). Recorded as decision 6.

**Two multi-code merges, and one three-way tie.** Q27 (`T3` of `C4`/`T3`) — T3 carries 5 of the
8 marks counting the omitted (a), the 2022 Q27 precedent. Q28 (`C4` of `C4`/`F2`) — C4 carries 4
of 6. **Q33 is the year's even split**: (a) and (b) are `S3`, (c) and (d) are `S1`, 4 marks each,
and the 2023 tie-break on "heavier mathematical demand" does not separate them cleanly either.
Filed under **`S3`**, because three of the four parts operate directly on the continuous
probability density function and the pdf is the question's subject — (d) is one conditional-
probability application of the result (c) produces. That is the same reading that put 2025 Q25
under `C4` and 2022 Q28 under `C4`.

**Q27(d) is the "leans on an omitted part" case Stage 1 left open for this session, and it is
kept.** Stage 1 singled it out as *the* exception across all six papers: it says *"Explain your
answer by referring to the graph drawn in part (a)"*, and (a) — sketch *P* for 0 ≤ *t* ≤ 12 — is
omitted. Neither of Stage 1's two suggested outs was taken. **Supplying the graph was rejected**:
NESA does not print it, so it would have to be drawn by us, and a fabricated diagram presented
inside a NESA question is not a crop. **Dropping (d) was rejected too**: the graph in question is
just the curve *P*(*t*) = 400 sin(π*t*/12), whose equation the stem already gives, so (d) is
fully answerable — the reasoning is that *P* peaks at *t* = 6, which reads straight off the
function. NESA's wording of (d) is kept **verbatim**, including the reference to part (a), and
the visibly separate italic note says what (a) asked for and describes the curve it produces.
Nothing is reworded; the note is clearly ours. Contrast 2025 Q15, where the omitted part's
*definition* had to be repeated inline because it was not in the stem — here nothing needs
repeating.

**Measured in the browser at a 430 px viewport** (stem 390 px), all 32 questions rendered through
`index.html`'s own CSS in a throwaway harness:

| Case | Measured | Verdict |
|---|---|---|
| `body.scrollWidth`, all 32 questions | **430**, never more | nothing clipped |
| `.question-area` scrollWidth vs clientWidth, all 32 | equal on all 32 **after** the `max-width` fix; **8 of them overflowed to 975–1767 px before it** | the check that found the image defect |
| Q22's **7-column** *z*-table in the wrapper | wrapper 390 px, scrolls to 520 px internally | decision 9 works |
| Q34's **8-column** distribution table in the wrapper | wrapper 390 px, scrolls to 520 px internally | decision 9 works |
| Q25's **6-column** future-value table, bare `.q-table` | **399.1 px**, spanning x 20 → 419.1 in a 430 px viewport | fits — spills 9 px into the 20 px right padding, **nothing clipped** |
| MC Q2 (2 col), Q32's two 3-col tables, bare | 390 px each | fit |
| Q30 and Q33 piecewise braces (decision 1, two rows) | brace cell **51.0 / 48.4 px** against two-row blocks of **51.0 / 48.4 px** | glyph spans the rows exactly at `font-size:2.6em` |
| MC Q4 option images, `optionImagesWide: true` | 360 × 122 px | see the correction above |
| MC Q5 option images in `.options-grid-2x2` | 160 × 123 px (1.30:1) | legible |
| All 17 images (9 stem, 8 option) | load, `naturalWidth` non-zero, stem images 390 px wide | none broken |
| Plain-text option buttons, all 32 | 52 px, single line | no wrap |
| 27 distinct non-ASCII characters used | rasterised; **none** matches the notdef glyph's ink count of 50 px², only `&nbsp;` is blank | real glyphs, no notdef |
| `<sup>` exponents | 15 px against an 18 px base, `vertical-align: super` | real superscripts |
| Q17 (two diagrams), Q27 and Q28 (omission notes) | 2 images render; (a)/(b) absent with the italic note present | omissions read correctly |

Zero console errors. As in the 2022 and 2025 sessions, **screenshots were unavailable** — the
Browser pane was not displayed — so these are DOM measurements rather than pictures. The harness
badges written questions with `q.category || q.topic`, the *post-fix* engine; the live engine
still reads `q.topic` alone (Stage 3 decision 10), so these show no topic badge until the Stage 7
one-liner lands.

Local CI green: `MC=696 Written=349 imageRefs=288 missingImages=0`; both key checkers still pass
225 MC and 203 written questions on the other subjects, which this session did not touch.

### 2024 — done (2026-08-31), the last paper

10 MC + 20 written entries + **2 `omittedParts`** (Q17(a) 2, Q25(b) 2) and **1 new
`omittedQuestion`** (Q19 5 — sketch a quartic from its stationary points and inflections).
**Marks reconcile to exactly 100**: 10 MC + 81 written + 4 omitted parts + 5 omitted question.
The build script refuses to write unless the file first round-trips byte-for-byte and then all
six content gates hold — the prefix-sum join, the paper total, every `category` being one of
NESA's own codes, every `gridCodes` union (and no *spurious* `gridCodes` on a single-code
question), every official grid part being covered by a bank entry or a declared omission, and
every referenced image file existing.

**All ten MC answers were confirmed against the official key before authoring**, by calling
`extract_mc_key()` read-only on `2024_marking_guidelines.pdf` — `C B A C A D C D B B`. Ten
independent derivations from the paper agreed with all ten. Q8 is the one worth re-reading: the
box plot carries **no printed scale**, so the quartiles have to be read off the seven histogram
columns — measured from the drawn rectangles, the box spans columns 2 to 6 with the median line
on column 4, and option D is the only histogram whose 4th and 5th values fall in column 3.

**The written model answers were cross-checked against NESA's own sample answers**, obtained by
calling `build_written_key.py`'s `parse_paper()` read-only: 37 leaf parts reconciling to 90/90.
Every derivation agreed. This is not the same thing as re-deriving MC answers by reading, which
§10 forbids — it is the extractor Stage 6 will commit, run in dry-run.

**Assets: 23 crops** via `scripts/crop_maths_advanced.py --year 2024` (a new registry block).
Section I: Q1, Q7, Q8, Q9, Q10 stimulus + Q7's and Q8's four option cells each. Section II: Q11,
Q13, Q14, Q16, Q20, Q21, Q22, Q23, Q28, Q31. **Stage 1's counts were exactly right for this
paper — 23 crops and 7 tables (Section I Q3 plus six in Section II), the second year running
after 2021 and the only two of the six.** Section II's list needed no additions: unlike 2023,
2025 and 2022, no question turned up an unlisted diagram or a second diagram of its own.

⚠️ **`optionImagesWide` is NOT needed here, and that closes the question for the subject.**
Stage 1 flagged **2024 Q8**'s four histograms as the last candidate, having measured their ink
extent at 3.7:1. That measurement did not survive cropping: it banded the C/D *row* rather than a
single cell. Each Q8 crop is **1.75:1** (184 × 105 pt) and renders **160 × 96 px** in the
`.options-grid-2x2` — squarely in 2020's 160 × 90 px territory, not 2021 Q4's 160 × 54 px. Q7's
four graphs render **160 × 161 px**. Both sets were re-rendered offline at exactly those boxes
and read: every bar height, the 0–4 axis and the −1/1/2/3 tick labels are legible. **2021 Q4
remains the subject's only `optionImagesWide`.**

**The 2020 option-letter amputation trap did not recur, and was checked rather than assumed.**
All eight letters (Q7 A–D on page 5, Q8 A–D on page 6) are real text — `get_text("words")`
returns their exact boxes — and `get_drawings()` reports **zero** vector paths intersecting any
of the eight, so the white `erase` rectangle removes the letter and nothing else. Confirmed by
eye on the contact sheets: every axis and curve is intact.

**Stage 3 decision 4 (blank tables) is used here for the first and only time.** 2024 Q11 and
Q13 are the subject's only two blank-table questions — 2022 Q12(b), the third on Stage 1's list,
is omitted anyway. Both are reproduced as `.q-table` HTML with `<td>&nbsp;</td>` in the blanks
(measured: every empty cell renders 34 px tall, so the grid reads as a table to fill in), and the
model answer lists the cell values labelled by their column. Q13's table is *partially*
completed — NESA prints *A* = 34 and the 61 — and those printed values are kept in place.

**Three multi-code calls, two of them even splits.** Q22 (`C3` of `C2`/`C3`/`C4`) splits 3 marks
of concavity against 3 of trapezoidal rule; filed under **`C3`** because part (c) is answered
*from* part (a)'s concavity result, so the concavity is the question's spine — the mirror of the
2025 Q25 reading, where (a) existed only to serve (b) and (c). Q31 (`C3` of `C3`/`T1`) splits 3–3
between sector geometry and minimisation; filed under **`C3`**, the 2023 tie-break on heavier
mathematical demand — (b) needs the derivative, the second-derivative test and a substitution
back. **Q30 is the harder call**: a single 3-mark part carrying `F2`/`M1`, where most of the
working is a reciprocal-graph transformation but the question's subject is the limiting sum of a
geometric series. Filed under **`M1`**, because the stem offers the graph as *"or otherwise"* —
an optional scaffold — while the mark-bearing insight is that a limiting sum exists only for
−1 < *x* < 1. That is the 2021 Q33 reading (file under the question's subject), applied to a
single part rather than to a merge. Four merged entries also span codes: Q14 (`C4` of `C4`/`F1`,
3 of 4 marks), Q17 (`C3` of `C3`/`F2`, both surviving parts), Q18 (`E1` of `E1`/`S1`, 2 of 3) and
Q27 (`C4` of `C2`/`C4`, 3 of 5).

**Both omissions sit inside a question the bank still carries, so both force the merged form**
(decision 3). Q17 keeps NESA's part letters (b) and (c) with a visibly separate italic note
saying (a) asked for a sketch of *V*(*t*); parts (b) and (c) work from the equation alone, so
nothing needed repeating. Q25 keeps (a) and (c) with a note about the omitted (b); (c) asks for
the median of *f*(*x*) itself and needs only *h* from (a), so again nothing was substituted —
contrast 2025 Q15, where the omitted part's definition had to be repeated inline.

**Measured in the browser at a 430 px viewport** (stem 390 px), all 30 questions rendered through
`index.html`'s own CSS in a throwaway harness:

| Case | Measured | Verdict |
|---|---|---|
| `body.scrollWidth`, all 30 questions | **430**, never more | nothing clipped |
| `.question-area` scrollWidth vs clientWidth, all 30 | equal on all 30 | decision 6's check is clean |
| Q23's **10-column** *z*-table in the wrapper | wrapper 390 px, scrolls to 630 px internally | decision 9 works |
| MC Q3 (4 col), Q11 and Q13 (3 col), Q22 (6 col), Q24 (4 col), Q26 (5 col), bare | 390 px each | fit |
| Q25's piecewise brace (decision 1, **three rows**) | brace cell **72.5 px** against a 72.5 px block at `font-size:3.9em` | confirms 2022's scaling rule a second time |
| MC Q7 option images in `.options-grid-2x2` | 160 × 161 px | legible — see above |
| MC Q8 option images in `.options-grid-2x2` | 160 × 96 px | legible — `optionImagesWide` not set |
| All 23 images (10 stem, 5 MC stimulus, 8 option) | load, `naturalWidth` non-zero, stem images 390 px wide | none broken |
| Plain-text option buttons, all 32 | **52 px**, single line | no wrap |
| 31 distinct non-ASCII characters used | rasterised; **none** matches the notdef glyph's ink count of 84 | real glyphs, no notdef |
| `<sup>` exponents | 15 px against an 18 px base | real superscripts |
| Q17 and Q25 omission notes | present; the dropped part letter appears only inside the note | omissions read correctly |
| Blank table cells (Q11 ×6, Q24 ×13) | 34 px tall each | render as fillable cells |

Zero console errors. As in the 2021, 2022 and 2025 sessions, **screenshots were unavailable** —
the Browser pane was not displayed — so these are DOM measurements. Option-image legibility was
therefore judged by re-rendering each crop offline at its measured display box and reading it,
which is the honest substitute.

Local CI green: `MC=706 Written=369 imageRefs=311 missingImages=0`; both key checkers still pass
225 MC and 203 written questions on the other subjects, which this session did not touch.

**Stage 4 is complete.** All six papers are ported and cropped: **60 MC + 126 written entries +
5 `omittedQuestions` + 12 `omittedParts`**, 124 crops in `/diagrams/`, every paper reconciling to
exactly 100 marks. **Stage 1 predicted exactly 12 `omittedParts` and 5 `omittedQuestions`
(17 marks), and the port landed on both.** The subject is still **registered nowhere in code** — that is Stage 7 — and
its answer keys are not yet committed, which is Stage 6, **next**.

**GATE 4** (ticked per year) — [x] validator green, `missingImages: 0` · [x] every part has
`qNum` · [x] omissions declared, and each paper's marks total 100 · [x] every crop opened and
compared against the paper, option by option · [x] every table renders as HTML, not an image ·
[x] any 7+ column table wrapped and checked at 430 px · [x] **no `.question-area` overflows its
own client width** (added 2021 — see decision 6) · [x] the year's Status cell ticked above
— **all ticked for all six papers. Stage 4 is closed; Stage 6 is next.**

---

## Stage 5 — Asset method 📖 (reference, not a scheduled stage)

**Folded into Stage 4** — each porting session crops its own year. This section stays as the
method the sessions consult; there is no separate Stage 5 session and no separate gate.

The dominant cost — roughly six times VET Construction's load, the heaviest so far.
**Stage 1 measured it: 124 crops (25 Section I stimulus + 48 Section I option + 51 Section II)
and 28 tables to reconstruct as HTML**, split per year in Stage 4's tracker. ⚠️ Treat the
Section II crop list as a **lower bound** — 2023 Q16 and 2025 Q29 were both missing from it,
and 2022 Q28 is one list entry carrying **two** diagrams (see those session notes). The
per-question crop and table lists are in Stage 1; work from those, not from a fresh sweep.

**Use `scripts/crop_maths_advanced.py --year {YEAR}`** — written in the 2020 session, one
registry block per year, coordinates in **PDF points** rather than pixels. Add this year's block
and run it; the 2020 block is the worked example.

- ⚠️ **Do not put this subject in `scripts/diagram_registry.json`.** That registry's coordinates
  are raw pixels verified at `RENDER_DPI = 150`, `save_crop()` overwrites unconditionally, and a
  bare run with no `--year` re-cuts every Mathematics Standard 2 crop. Changing its DPI without
  rescaling silently crops the wrong region — files still written, non-empty, plausible, wrong.
  Points sidestep the whole trap: `crop_maths_advanced.py`'s DPI can change freely.
- `extract_maths_diagrams.py --calibrate` finds option labels through `get_text()`, and on these
  papers **the option letters and most axis labels are outline paths**, so it finds nothing.
  Derive boxes from an **ink profile** instead (dark pixels at 150 dpi, banded with a small gap);
  `crop_vet_2021_q15_options.py` is the other worked example.
- **A question listed once in Stage 1 can carry two diagrams** (2022 Q28 draws its circle on
  two pages). The second takes the part letter as a suffix on the question number:
  `…_2022_Q28b_stimulus.jpg` beside `…_2022_Q28_stimulus.jpg`. 2025's `Q25(c)` and `Q28(b)`
  list entries will need the same.
- **Exclude the paper's own `A.`/`B.` glyph** — `index.html` renders its own option label — but
  ⚠️ **not with an x-cut.** The letter sits in the cell's top-left corner with the graph running
  underneath it (2020 Q5 option A: letter x 100.8–111.3 pt, x-axis starts x 102.2 pt), so
  cropping to its right amputates the axis. Use the script's `erase` rectangle, and ink-profile
  that x-strip first to confirm nothing but the letter is inside it.
- ⚠️ **Wide option images need `optionImagesWide: true`, and the test is the rendered height,
  not the aspect ratio.** This bullet used to say Stage 1's 0.8:1–2.6:1 range meant "none needs
  it"; **2021 Q4 cropped at 2.94:1 and rendered 160 × 54 px in the 2×2 grid**, against 360 × 122 px
  one-per-row, so it is set there. 2020's sets are genuinely fine (160 × 143 px, 160 × 90 px) and
  so are 2022's, 2023's, 2025's and 2024's (160 × 96 px and 160 × 161 px). **Render each option
  set at 430 px and read the height off the DOM** — all twelve sets have now been measured, and
  2021 Q4 is the only one that needed the flag.

**No Gate 5** — its three checks moved into Gate 4, where they are applied per year: every crop
compared against the paper option by option, every table rendered as HTML rather than an image,
and any 7+ column table wrapped and checked at 430 px (Stage 3 decision 9). The six wide lookup
tables land in the 2021, 2022, 2023, 2024 (×2) and 2025 sessions.

---

## Stage 6 — Ground truth ✅ COMPLETE (2026-08-31)

Both keys are built, committed and enforced. **Nothing needed correcting** — the bank was
right on its first check, which is what Stage 0's dry runs predicted.

| | |
|---|---|
| `data/answer-key/mathematics-advanced.json` | 6 papers, **60 MC answers** |
| `data/answer-key/written/mathematics-advanced.json` | 6 papers, **234 parts, 90 marks each** |
| `check_answer_key.cjs` | **60 checked, 0 wrong, 0 unverifiable** (subject total now 285) |
| `check_written_key.cjs` | **126 checked, 0 wrong, 0 unverifiable, 5 declared omissions** (total 329) |

**No workflow edit was needed.** Both checkers enumerate their key directory, so committing
the two files is what wires them into `validate.yml`.

### What was changed in the tooling

1. `build_answer_key.py` `SUBJECTS` — added the subject (`Maths Advanced`, `mc_count: 10`).
2. `build_written_key.py` `SUBJECTS` — added `"mathematics-advanced": "Maths Advanced"`.
3. ⚠️ **The `-mg.pdf$` glob is fixed**, as this runbook predicted. It is now
   `is_guidelines()`, mirroring `build_answer_key.find_papers()`: `feedback` is tested
   **first** and excluded, then `-mg|marking` matches. Verified inert for the other three
   subjects — all three regenerate byte-identical written keys, and Multimedia's
   `{year} ... HSC Marking Feedback.pdf` files stay excluded.
4. Regenerating the other three **MC** keys changes only their `generatedAt` timestamp, so
   those three files were reverted — the committed diff is the two new files alone.

### New: reverse coverage, reported not enforced

`check_written_key.cjs` could only see a question whose mark was *wrong*, never one that was
simply **absent** — the failure that left 2020 Standard 2 at 84/85 for over a year. It now
also reports, per subject, how many official leaf parts are claimed by a bank entry or a
declared omission:

| Subject | Coverage |
|---|---|
| **mathematics-advanced** | **234 / 234** |
| mathematics-standard-2 | 235 / 235 |
| multimedia | 30 / 42 — Section III (Q16, 15 marks/paper) never ported |
| vet-construction | 23 / 76 — written bank covers 23 of 65 marks/paper |

It is **reported, not enforced**: those last two gaps are deliberate, documented decisions,
and failing on them would turn CI red on work already scoped out. If either is ever closed,
promote this to a hard assertion.

### Reconciliation — all six papers, both directions

| Year | MC | written | omittedParts | omittedQuestions | total |
|---|---|---|---|---|---|
| 2020 | 10 | 82 | 1 | 7 | **100** |
| 2021 | 10 | 81 | 4 | 5 | **100** |
| 2022 | 10 | 85 | 5 | 0 | **100** |
| 2023 | 10 | 83 | 7 | 0 | **100** |
| 2024 | 10 | 81 | 4 | 5 | **100** |
| 2025 | 10 | 87 | 3 | 0 | **100** |

Every official leaf part is claimed **exactly once** — 0 unclaimed, 0 double-claimed.

### The residual human gate — how it was actually discharged

Eyeballing 124 crops is not a method. Three checks, each covering what the others miss:

1. **12 option-set contact sheets, read one by one.** Each puts the NESA page's own option
   area above the four committed crops **in bank array order**, with the key marked. All 12
   match the paper's A/B/C/D ordering; no reordering, no wrong-picture pairing. The two
   closest calls are **2024 Q7** (C and D differ only by a horizontal shift) and **2024 Q8**
   (four similar histograms) — both correct.
2. **All 124 crops re-rendered from the PDF at their registry rectangle and pixel-compared
   to the committed file. 0 mismatches**, so every file on disk is a faithful cut of the
   paper at the place it claims.
3. **All 124 position-checked against the paper's own question labels. 0 mismatches**, so no
   crop is attached to the wrong question. ⚠️ Two traps in writing that check: a bare number
   in the left margin is only a question label on a **Section I** page — on Section II pages
   body text starts at x = 70.7 and `x = 4` posed as "Q4" (2021 Q24 was flagged spuriously);
   and tightening the x threshold instead breaks Section I, whose numbers sit in the *same*
   band. The separator is the **`Question N` header**: use headers where a page has them,
   bare margin numbers where it does not.

Crop reconciliation: **124 referenced, 124 on disk, 0 orphans, 0 missing.** Note MC stems
carry inline `<img>` too (2023 Q2), not only the `image` field — a scan that reads
`image`/`optionImages` plus written stems alone reports a phantom orphan.

**GATE 6** — [x] 0 wrong, 0 unverifiable · [x] every paper reconciles to 100 ·
[x] image questions compared by a human

---

## Stage 7 — Release ⬜

1. `subjects/index.json` — add the filename
2. `index.html` — `SUBJECT_ID_MAP` (JSON fetch URL) **and** `SUBJECT_CATALOGUE` (billing id,
   written to Supabase `subject_selections.subject_id` — chosen once, expensive to change)
3. Subject card + artwork
4. **Two engine fixes Stage 3 found — both blocking, both one-liners** (`index.html`):
   - `NESA_CAT_LABELS` (705) is one flat global map keyed on the bare code, and **5 of
     Advanced's 14 codes collide with Standard 2's** (`F1 F2 M1 S1 S2`). Make it subject-aware,
     `NESA_CAT_LABELS[subjectKey]?.[c] || c`, moving today's entries under `maths`; two chip
     call sites, 991 and 1170. Without it five filters carry another subject's topic names.
   - The written-question badge (1764) reads `q.topic`, so canonical `category` renders no
     topic badge at all. Mirror the MC path (1696): `q.category || q.topic`. This also fixes
     Standard 2's 151 written questions.
5. **Browser-verify at mobile width**: load the subject, render questions carrying images,
   answer one correctly and one incorrectly, confirm explanations render, no console errors.
   Images use `loading="lazy"` — force `loading='eager'` before asserting anything loaded.
   Include one wide lookup table and one category filter chip in what you actually look at.
6. `docs/HISTORY.md` entry; CLAUDE.md §7 row + §11 roadmap

**GATE 7** — [ ] full local CI green · [ ] both engine fixes landed and seen working ·
[ ] exercised in a browser at mobile width · [ ] docs updated

---

## Deferred, not part of this port

- **Study Mode** (`studyNotes`) — a separate project of comparable size (Multimedia 47 blocks,
  VET 71), built **one topic at a time** by the owner's explicit preference.
- **Exam Trends panel** — data already built (`data/exam-trends/mathematics-advanced.json`);
  UI placement is an open design decision.
- **Extended variant questions**, as Standard 2 has — not decided.
