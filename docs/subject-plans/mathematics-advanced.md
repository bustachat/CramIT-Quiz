# Mathematics Advanced — port working document

Stages 1–3 of `docs/porting-playbook.md` for the `mathematics-advanced` port.
Stage 0's Fit Report is separate: `docs/paper-reports/mathematics-advanced.md` (verdict **GO**).

| Stage | Status |
|---|---|
| 0 Feasibility | ✅ GO — 2026-08-27 |
| 1 Survey | ⬜ not started |
| **2 Syllabus grounding** | ✅ **complete — 2026-08-27** |
| 3 Schema | ⬜ not started |

---

## Stage 2 — Syllabus grounding

### Provenance (stated explicitly, per playbook Gate 2)

**Primary source, read in full.** `NESA Exams Folder/Maths Advanced/mathematics-advanced-stage-6-syllabus-2017.docx`
— the official *Mathematics Advanced Stage 6 Syllabus (2017)*, 1.63 MB, downloaded from
nsw.gov.au at the owner's direction and saved alongside the papers under the same copyright
treatment (not committed to GitHub). Read with `python-docx`, both `document.paragraphs` and
`document.tables`: 1122 paragraphs, 10 tables.

Also saved: `mathematics-standard-and-advanced-common-content.pdf` (the content Standard and
Advanced share — relevant because Standard 2 is already ported).

**This topic list comes from the primary syllabus, not a mapping-grid proxy.** The grids were
extracted too, but as a *secondary* axis (see "Scope vs examination" below), which is the whole
point of the rule.

### Which syllabus applies — and the shelf life this port has

NESA has two live Mathematics Advanced syllabuses:

| Syllabus | Governs | Status |
|---|---|---|
| **Mathematics Advanced Stage 6 (2017)** | **The 2020–2025 papers we are porting, and the 2026 HSC** | Year 12 continues on it through Term 3, 2026 |
| Mathematics Advanced 11–12 (2024) | 2027 HSC onwards | Year 11 from Term 1 2026; Year 12 from Term 4 2026 |

The 2017 syllabus is the correct grounding for this bank — every question in it was written
against that document. **But this port's topic list has a defined shelf life: the 2027 HSC
cohort sits a different syllabus.** That is a product decision to take deliberately, not to
discover in 2027. The 2024 syllabus is web-only on curriculum.nsw.edu.au (a JS app, no PDF or
DOCX download found), so mapping the two is a manual job when it is worth doing.

### The topic list — 14 subtopics, both years

The HSC examines the Year 12 course with Year 11 as assumed knowledge, and the mapping grids
confirm Year 11 subtopics are examined directly every year. **Both years are in scope.**

`category` values are the syllabus codes with the `MA-` prefix stripped, matching how
Standard 2 stores its own (`A1`, `F1`, `M1`…).

| `category` | Syllabus code | Title | Year | Scope (content dot points) | Examined (marks, 6 papers) |
|---|---|---|---|---:|---:|
| `F1` | MA-F1 | Working with Functions | 11 | **56** (15.6%) | 41.0 (6.8%) |
| `C1` | MA-C1 | Introduction to Differentiation | 11 | **38** (10.6%) | 7.7 (**1.3%**) |
| `C4` | MA-C4 | Integral Calculus | 12 | 37 (10.3%) | 70.3 (11.7%) |
| `E1` | MA-E1 | Logarithms and Exponentials | 11 | 31 (8.7%) | 21.7 (3.6%) |
| `S3` | MA-S3 | Random Variables | 12 | 31 (8.7%) | 61.5 (10.2%) |
| `M1` | MA-M1 | Modelling Financial Situations | 12 | 30 (8.4%) | 78.0 (13.0%) |
| `S2` | MA-S2 | Descriptive Statistics and Bivariate Data Analysis | 12 | 29 (8.1%) | 38.0 (6.3%) |
| `S1` | MA-S1 | Probability and Discrete Probability Distributions | 11 | 26 (7.3%) | 36.5 (6.1%) |
| `T1` | MA-T1 | Trigonometry and Measure of Angles | 11 | 21 (5.9%) | 41.0 (6.8%) |
| `C3` | MA-C3 | Applications of Differentiation | 12 | 19 (5.3%) | **94.2 (15.7%)** |
| `C2` | MA-C2 | Differential Calculus | 12 | 15 (4.2%) | 28.0 (4.7%) |
| `F2` | MA-F2 | Graphing Techniques | 12 | 10 (2.8%) | 33.7 (5.6%) |
| `T2` | MA-T2 | Trigonometric Functions and Identities | 11 | 9 (2.5%) | 8.0 (1.3%) |
| `T3` | MA-T3 | Trigonometric Functions and Graphs | 12 | **6** (1.7%) | **40.5 (6.8%)** |
| | | **Total** | | **358** | **600.0 / 600** |

Six top-level topics group these: Functions (F1, F2), Trigonometric Functions (T1, T2, T3),
Calculus (C1, C2, C3, C4), Exponential and Logarithmic Functions (E1), Financial Mathematics
(M1), Statistical Analysis (S1, S2, S3).

⚠️ **`F1`, `M1`, `S1` and `S2` are also Standard 2 category codes and mean different things.**
Standard 2's `F1` is financial "Money Matters"; Advanced's `F1` is "Working with Functions".
Nothing breaks — the subjects are separate JSON files with separate filter controls — but never
compare `category` across the two subjects, and never write a shared lookup keyed on the bare
code.

### Scope vs examination — the divergence, measured on both axes

This is the check the VET Construction incident produced the rule for, and it is the first time
this project has had *both* numbers for the same subject:

- **MA-C1 (Introduction to Differentiation): 10.6% of the syllabus, 1.3% of examined marks.**
  Second-largest subtopic by scope, near-invisible in six years of papers — it is Year 11
  foundation content the Year 12 calculus questions silently assume. A mapping-grid-derived
  topic list would have all but deleted it.
- **MA-T3 (Trigonometric Functions and Graphs): 1.7% of scope, 6.8% of marks** — smallest
  subtopic in the syllabus, examined four times its weight.
- **MA-C3 (Applications of Differentiation): 5.3% of scope, 15.7% of marks** — the single
  most-examined subtopic, from a modest slice of the syllabus.
- MA-F1 and MA-E1 both carry substantially more scope than exam presence.

**Consequence for the port:** question `category` is assigned from the mapping grid (below) —
that is what each question *is*. Any later **Study Mode topic weighting** must use the scope
column, not the marks column, or C1, F1 and E1 get starved and T3 and C3 get bloated.

### Bonus: `category` is derivable, not guessable

Every NESA marking guideline ends with a **Mapping Grid** giving each question part's marks,
syllabus content code and outcome code. New tooling extracts it:

```bash
python scripts/build_mapping_grid.py mathematics-advanced
```

→ `data/mapping-grid/mathematics-advanced.json` (committed; CI can never regenerate it, same as
the answer keys). **All six papers reconcile to exactly 100 marks with zero uncoded rows.**

Independently cross-checked against `build_written_key.py`'s positional Marks-column reader:
**the two agree on every Section II part in all six papers**, with one benign structural
difference (2023 Q31 — the grid splits it as `31(b)`, the guidelines head it as `31`; totals
match).

Two extraction traps are recorded in the script's docstring, each of which produced a wrong
number first: the code can be split across words in the text layer (`MA- M1`), and a row's cell
text is vertically centred so it can begin *above* its own label line.

### GATE 2

- [x] Primary syllabus document located, saved, and read — 2017 DOCX, paragraphs **and** tables
- [x] Topic list proportional to scope-of-learning size, not exam frequency — scope column is
      the syllabus's own dot-point count; the divergence from exam frequency is quantified above
- [x] Provenance stated explicitly — primary source, not a proxy

**Stage 2 passes.**

---

## Stage 1 — Survey (outstanding)

Not started. Inputs that already exist and should not be re-derived:

- Section I is classified in the Fit Report: 24 stimulus images, 11 option-image sets, 9 tables,
  24 plain-text, across 60 MC.
- 39 Section II questions reference a stimulus or table (needs splitting into crops vs HTML tables).
- ~14 drawing parts, ~42 marks, already located per year → `omittedParts`.
- `data/mapping-grid/mathematics-advanced.json` gives every question's `category` and marks.
- Text-layer quality is **garbled on every paper** — Section II must be transcribed from
  rendered pages, not extracted. This is the dominant Stage 1/4 cost.

## Stage 3 — Schema (outstanding)

Canonical names per playbook Stage 3: `year`, `qNum`, `category`, `optionExplanations`, `marks`,
`answer`. One open decision carried from Stage 0: how to render a **braced piecewise function**
(2–3 instances across six papers) — borderless two-row table with a CSS brace, or a crop.
