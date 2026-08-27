# Mathematics Advanced — port runbook

**One stage per session.** This file is the single entry point: a fresh session should be able
to open it cold, run one stage, tick its gate, and write its result back here. Stage 0's Fit
Report is separate: `docs/paper-reports/mathematics-advanced.md` (verdict **GO**).

| Stage | Status | Session |
|---|---|---|
| 0 Feasibility | ✅ GO — 2026-08-27 | done |
| **1 Survey** | ⬜ **next** | 1 session |
| 2 Syllabus grounding | ✅ complete — 2026-08-27 | done |
| 3 Schema | ⬜ | 1 short session, must follow Stage 1 |
| 4 Port | ⬜ | **~6 sessions, one per paper year** |
| 5 Assets | ⬜ | 2–3 sessions (~100 crops) |
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
| Section I assets | 24 stimulus images, 11 option-image sets (=44 crops), 9 tables → HTML, 24 plain text |
| Section II assets | 39 questions reference a stimulus or table (crops vs HTML not yet split — Stage 1) |
| Unportable | ~14 drawing parts, ~42 of 540 marks (~7.8%) → `omittedParts` |
| Notation | `basic` — no ∑, matrices, vectors, complex numbers or radical sign |
| **Text layer** | **garbled on every paper** — `(x − 1)²` extracts as `^x - 1h2`, `#` is ×, `ƒ` is *f* |
| Ground truth, pre-verified | `extract_mc_key()` 10/10 every year; `parse_paper()` 37–42 parts/paper, **0 unresolved, exact 90/90 on all six** |
| Official topic + marks | `data/mapping-grid/mathematics-advanced.json` — every part, all six papers, reconciled |

---

## Stage 1 — Survey ⬜ NEXT

**Goal:** every one of the 294 parts classified, so Stage 4 has no open questions.

Start from the mapping grid — it already gives each part's `category`, marks and outcome. What
it does not give is *presentation*, which is what this stage adds.

Per question, record: type (MC / short written / **unportable**), stimulus (none / raster /
table), options (text / images / bare-letters-in-stimulus), option aspect ratio (wide > ~3:1 →
`optionImagesWide`), and text-layer quality.

**Three traps the playbook requires you to actively test for:**

1. **Run the stem sweep** for prose standing in for a picture — not an option sweep:
   `which (of the following )?(best )?(represents|shows|depicts|illustrates|could be|could represent)`
   and `which (diagram|graph|drawing|image|picture|sketch|plan|symbol|section)`.
   ⚠️ The Stage 0 pass used a regex missing `could represent` and undercounted; use the above.
2. **Bare-letter options are not automatically a gap** — they are complete when all four
   alternatives live inside one stimulus, and a gap when the paper prints four separate diagrams.
3. **Array position is not the question number.** Join on `qNum` or not at all.

**Do not trust vector-drawing counts to find diagram questions.** Tried at Stage 0 and it failed
both ways — straight-line graphs have no curves and scored 0 (2024 Q1), while text underlines
scored false positives. Read the stems, or render the page and look.

**GATE 1** — [ ] all 294 parts classified · [ ] crop list, table list and omission list produced ·
[ ] stem sweep run and every hit resolved · [ ] text-layer quality recorded per paper

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

## Stage 3 — Schema ⬜ (short session, after Stage 1)

Canonical names, per playbook Stage 3 — a new port uses these, existing deviations are debt:
`year`, `qNum`, `category`, `optionExplanations`, `marks`, `answer`, `omittedParts`,
`omittedQuestions`.

Two decisions to take and record here:

1. **Braced piecewise function** (2–3 across six papers, e.g. 2020 Q23) — borderless two-row
   table with a CSS brace, or a crop?
2. **Integrals and stacked fractions** in MC stems/options (~6 of 60 MC) — `∫` U+222B with
   `<sub>`/`<sup>` limits, and inline `1/3`. Confirm against how Standard 2 already writes rates.

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

The dominant cost — roughly five times VET Construction's load, the heaviest so far.

- Text layer has the option labels → `extract_maths_diagrams.py --calibrate` (registry, 150 dpi)
- Text layer empty / labels are outline paths → **ink-profile segmentation at 300 dpi**
  (`crop_vet_2021_q15_options.py` is the worked example)
- ⚠️ **`RENDER_DPI` is load-bearing** — registry coordinates are raw pixels verified at 150 dpi.
  Changing it without rescaling silently crops the wrong region: files still written, non-empty,
  plausible, wrong. `save_crop()` overwrites unconditionally, and a bare run with no `--year`
  re-cuts every registry entry.
- **Exclude the paper's own `A.`/`B.` glyph** — `index.html` renders its own option label.
- Wide option images (> ~3:1) need `optionImagesWide: true`.

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
