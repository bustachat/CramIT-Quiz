# CramIT — Subject Porting Playbook

**Read this before starting any new subject.** It is the missing procedure behind
CLAUDE.md §10's five-step "Adding a new subject", which begins *after* the hard part
(step 1 is "Create `subjects/{id}.json`" — the entire port compressed into one line).

Scope: taking a NSW HSC subject from "we should add this" to live, verified content on
`cramit-quiz.pages.dev`, and keeping it correct for years afterwards.

**Companion documents**

| Document | What it holds | Read when |
|---|---|---|
| `CLAUDE.md` §7, §10 | Subject registry, question schema, the hard content rules | Always — auto-loaded |
| `docs/HISTORY.md` | Why each rule exists; every port's actual failures | Investigating a rule |
| `docs/agents-plan.md` | Stage 9 agent roster, autonomy levels, release pipeline | Stage 7 and §10 below |
| `CramIT_Autonomous_Operations_Blueprint_V4.docx` | Authoritative agent spec (not in repo) | Stage 7 and §10 below |

> **Why this exists.** Four subjects have been ported. Every one of them shipped a class
> of defect the next one repeated, and CLAUDE.md's rules were each written *after* the
> failure: wrong answers (5 in Maths, 6 in VET), invented option labels describing the
> wrong picture (4 questions), a topic list built from mapping grids instead of the
> syllabus (2 subjects), a fabricated exam citation, 135 questions that were unverifiable
> for months, a paper silently totalling 84/85 marks, and — found while writing this
> playbook — HMS written questions rendering no marks badge at all because that port
> invented its own field name. **None of these were caught by CI.** All of them were
> preventable at a stage earlier than the one that caught them.

---

## 0. The pipeline at a glance

Each stage produces an artifact and passes a gate. **Do not start a stage before its
predecessor's gate passes** — most historical defects are a stage skipped, not a stage
done badly.

| # | Stage | Artifact | Gate | Owner today | Agent owner at scale |
|---|---|---|---|---|---|
| 0 | Feasibility | Fit Report | GO / NO-GO | Human + Claude Code | Content Agent (triage) |
| 1 | Survey | Work Plan | Every question classified | Claude Code | Content Agent |
| 2 | Syllabus grounding | Topic list | Primary syllabus read | Human + Claude Code | Syllabus & Standards Agent |
| 3 | Schema | Field mapping | Canonical fields chosen | Claude Code | — (validator-enforced) |
| 4 | Port | `subjects/{id}.json` | Validator green | Claude Code | Content Agent (Level 1) |
| 5 | Assets | Crops / tables | Every asset resolves | Claude Code | Human (crop tooling) |
| 6 | Ground truth | Answer keys | 100% verifiable, 0 wrong | Claude Code | — (CI-enforced) |
| 7 | Release | Deployed subject | Browser-verified | Human | QA Agent + human PR |
| 8 | Operate | — | Annual paper intake | Human | Content + Syllabus Agents |

Study Mode (`studyNotes`) is a **separate follow-on project**, not part of a port. See §9.

---

## 1. Stage 0 — Feasibility (GO / NO-GO)

**Purpose: earn the right to say no.** Not every HSC subject fits this engine, and
discovering that after porting 200 questions is the expensive way to find out.

### Inputs required before you can assess

| Input | Where | If missing |
|---|---|---|
| Past papers, 5–6 years | `NESA Exams Folder/{subject}/` | **Stop.** No papers = no port (see HMS) |
| Marking guidelines (`-mg` suffix) | same folder | **Stop.** No ground truth possible |
| Official NESA syllabus | Usually *not* pre-saved — ask before downloading | Stage 2 cannot proceed |

### The four fit tests

**1. Format fit — does the paper's mark distribution survive the engine?**

The engine presents 4-option MC and short written answers marked by AI against keywords
plus a model answer. It **cannot** present extended essays, multi-page working, or
anything the student must draw.

Compute, from the papers' own front pages: MC marks, short-answer marks, and
extended-response marks as a share of the total.

| Portable share | Verdict |
|---|---|
| > 70% | Good fit — proceed |
| 40–70% | Proceed, but declare the gap in `omittedQuestions` up front |
| < 40% | `written-only` or **NO-GO** — say so plainly rather than porting a fragment |

**2. Renderer fit — can the app display this subject's notation?**

There is **no MathJax or KaTeX in this project.** Question text is HTML, and every
existing subject got by on `<sup>`, `<sub>`, `<em>` and Unicode. A subject needing
integrals, summations, matrices, vectors or complex numbers is a **renderer project
first and a porting project second** — do not start the port until that is resolved.

**3. Content-shape fit — how much of the paper is pictures?**

Count questions carrying a stimulus image, and questions whose *options* are images.
This drives Stage 5's cost, which is the most manual part of a port.

**4. Precedent fit — does a structurally similar subject already exist?**

Porting alongside a similar subject is far cheaper. Mathematics Advanced shares
Standard 2's structure, notation and much of its topic space; Extension 1/2 shares
almost none of it.

### Output: the Fit Report

Write to `docs/paper-reports/{subject}-{year}.md` — the directory the Content Agent
already targets. **It does not exist yet; the agent has never run.** One report per
paper, plus a subject-level verdict:

```
sections[]          name, questionCount, type
mcCount, shortAnswerCount, extendedResponseCount
diagramDependentCount
notationComplexity  none | basic | needs-renderer-work
themes[]
fitSummary
recommendation      generate-mc | generate-mc-and-written | written-only | poor-fit
```

`agent.js`'s `triagePaper()` already returns most of this shape. Its resolution is too
coarse for Stage 1 (`diagramDependentCount` is a single integer), but it is the right
Stage 0 instrument.

### Worked example — Mathematics Extension 1 (illustrative; not yet formally assessed)

Extension 1 is roughly 10 MC marks out of 70; the remainder is extended working. Format
fit lands well under 40%, and its notation fails test 2 outright. Expected verdict:
**NO-GO** until a maths renderer exists. That is the playbook working correctly — a
fast, cheap no.

**Mathematics Advanced is the honest first candidate** for exercising this playbook,
precisely because it passes all four tests, so it tests the *process* rather than the
engine's limits.

### GATE 0

- [ ] Papers **and** marking guidelines present for every year in scope
- [ ] Portable mark share computed from the papers' front pages, not estimated
- [ ] Notation verdict recorded
- [ ] Explicit GO / NO-GO written down, with the reason

---

## 2. Stage 1 — Survey (the per-question work plan)

**Purpose: replace judgement calls with measurements.** Stage 0 says whether to port;
Stage 1 says exactly what porting will cost, question by question.

Most of this is mechanical and should be *measured from the PDF*, never estimated by
reading it — this project's repeated failure mode is a confident impression of a paper
that turned out wrong. Where the survey cannot decide, it must **report the question as
unresolved rather than guess** (the standard `backfill_qnum.py` already holds).

### Per-question classification

| Dimension | Values | Consumes |
|---|---|---|
| Question type | MC / short written / extended / **unportable** | `omittedQuestions` |
| Stimulus | none / raster / vector / table | Stage 5 |
| Options | text / images / bare letters-in-stimulus | `optionImages` |
| Option aspect ratio | normal / wide (> ~3:1) | `optionImagesWide` |
| Text-layer quality | clean / garbled / absent | Stage 5 method choice |
| Marks | integer, from the guidelines' Marks column | Stage 6 |

### Three traps this stage must actively test for

**Bare-letter options are not automatically a gap.** VET 2022 Q7/Q13 and 2025 Q6 use
`W/X/Y/Z` and `A/B/C/D` where all four alternatives live *inside one stimulus* — those
are complete. VET 2021 Q15 used text descriptions where the paper had four *separate*
diagrams — that was a gap. Distinguish by asking whether the stimulus contains all four
labelled alternatives.

**A question with no image at all can still be an image question.** Where a stimulus was
never cropped, a port has sometimes substituted prose — and the prose can be wrong while
the answer stays right, so CI passes and the question is unanswerable. Multimedia 2022 Q2
described three stars as `outline star / filled circle / filled star` when the paper
prints a filled star with no outline, an unfilled star with one, and a filled star with
one; a student reasoning correctly picks A and is marked wrong against the correct answer
D. **Catch these with a stem sweep**, not an option sweep — the giveaway is prose standing
in for a picture:

```
which (of the following )?(best )?(represents|shows|depicts|illustrates)
which (diagram|graph|drawing|image|picture|sketch|plan|symbol|section)
```

**Array position is not the question number.** Multimedia 2022 stores its ten questions
in the order 1, 3, 4, 5, 6, 8, 9, 10, 7, 2. Every *other* year in every subject happens
to be in paper order, which is exactly what makes position such a tempting shortcut.

### GATE 1

- [ ] Every question in every year classified — none left unclassified
- [ ] Crop list, table list and omission list produced
- [ ] Stem sweep run; every hit resolved as *complete* or *needs a crop*
- [ ] Text-layer quality recorded per paper

---

## 3. Stage 2 — Syllabus grounding

**This is a hard rule and it has been broken twice** (Multimedia, then VET), both times
by presenting a mapping-grid-derived topic list as syllabus-grounded.

1. Locate the **official NESA syllabus** (`site:educationstandards.nsw.edu.au` or
   `site:nsw.gov.au` — syllabus hosting has moved for some subjects; old links 301).
2. **Ask the owner before downloading**, then save into `NESA Exams Folder/{subject}/`
   (same copyright treatment as the papers — not committed to GitHub).
3. Read the actual content. For DOCX, `pandoc` is unavailable in this environment;
   `python-docx` works — extract **both** `document.paragraphs` **and**
   `document.tables`, because NESA's VET template puts the substantive
   scope-of-learning content in tables, not paragraphs.
4. Marking-guideline mapping grids are a *secondary cross-check only*. They reflect exam
   history, not syllabus scope: VET's "Working in the industry" carries 80 rows of
   scope-of-learning against Safety's 48, and includes content (cultural diversity,
   anti-discrimination) that has **never appeared in any exam paper checked**.
5. State plainly whether the topic list came from the primary source or a proxy.

### GATE 2

- [ ] Primary syllabus document located, saved, and read
- [ ] Topic list proportional to scope-of-learning size, not exam frequency
- [ ] Provenance stated explicitly

---

## 4. Stage 3 — Schema (canonical fields)

**The four existing ports do not share a schema.** Measured 2026-08-27:

| | Maths | Multimedia / VET | HMS |
|---|---|---|---|
| Topic field | `category` | *(none)* | `topic` |
| MC explanation | `solution` | `optionExplanations` | `explanation` |
| Written marks | `marks` | `marks` | **`maxMark`** |
| Paper identity | `year` + `qNum` | `year` + `qNum` | *(none)* |
| `bandDescriptors` | yes | Multimedia yes, VET no | yes |
| `acceptableAnswers` / `minKeywords` | yes | yes | no |

The engine absorbed this drift through fallback chains rather than the data being fixed —
CLAUDE.md §10 documents `q.answer || q.modelAnswer || q.sampleAnswer` as the normal way
to read a model answer. That is a symptom, not a design. It has cost something real
exactly once so far: HMS written questions rendered **no marks badge at all**, from the
port until 2026-08-27, because one display path read `q.marks || q.totalMarks` and HMS
alone uses `maxMark`. Nothing threw, nothing scored wrong, and no validator could see it.

**A new port uses the canonical field names.** Where an existing subject differs, that is
technical debt to be migrated — not a precedent to copy.

| Purpose | Canonical | Notes |
|---|---|---|
| Paper year | `year` | Omit only if no papers exist |
| Paper question number | `qNum` | **Required** for CI verification |
| Topic / category | `category` | |
| MC per-option rationale | `optionExplanations` | Maths' `solution` is a step-by-step variant, legitimately different |
| Written maximum marks | `marks` | Not `maxMark` |
| Model answer | `answer` | |
| Whole question the engine can't present | `omittedQuestions` (subject-level) | |
| Part the engine can't present | `omittedParts` (per question) | |

**Legitimate deviations** (record them; do not "fix" them):

- **No `year`/`qNum`** when the subject has no past papers. HMS is the only such case —
  2026 is its first HSC year. This is correct, not drift.
- **No `category`** where the source bank has no topic field and topics were defined from
  the syllabus instead (Multimedia, VET).

⚠️ `scripts/validate_subjects.cjs` is **permissive of unknown top-level keys**, so it
cannot currently catch a new port inventing its own field names. Extending it to enforce
canonical names is the remediation for the drift above, and should land before the next
port rather than after it.

### GATE 3

- [ ] Field mapping written down before any question is authored
- [ ] Every deviation from canonical is deliberate and recorded

---

## 5. Stages 4 & 5 — Port and assets

### The ordering constraint (non-obvious, and it has bitten)

```
port questions (with qNum from the start)
  └─> build_answer_key.py          (needs marking-guideline PDFs)
        └─> check_answer_key.cjs   (needs qNum on every question)
              └─> build_written_key.py / check_written_key.cjs
```

`backfill_qnum.py` exists to rescue a port that skipped `qNum` — it matches on **exact
option-set equality only** and refuses `--write` unless every question resolves. Needing
it means questions sit unverifiable in the meantime; 135 did, across Multimedia and VET.
**Carry `qNum` from the first question you author.**

### Content decision rule (crop vs markup vs text)

Already in CLAUDE.md, filed under written questions; it applies to the whole port:

| Source content | Becomes |
|---|---|
| Plain text | `q` field |
| Diagram / photo | Cropped JPG, `<img>`; never an SVG redraw |
| Table | Reconstructed `<table>` HTML — **not** a crop |
| Whole question the engine can't present | `omittedQuestions` entry |

Tables as HTML matter for mobile: the app's `.study-dtable` pattern collapses to stacked
cards, which a screenshot of a table cannot do.

### Cropping method

| Situation | Method |
|---|---|
| Text layer has the option labels | `extract_maths_diagrams.py --calibrate` (registry, 150 dpi) |
| Text layer empty / labels are outline paths | **Ink-profile segmentation** at 300 dpi |

The second case is real: on VET 2021 p7 the option letters and axis labels are outline
paths, so `get_text()` **and** `get_drawings()` both return nothing. See
`scripts/crop_vet_2021_q15_options.py` and `scripts/crop_multimedia_2022_q2_stimulus.py`.

⚠️ `RENDER_DPI` in `extract_maths_diagrams.py` is load-bearing: the registry's
coordinates are raw pixels **verified at 150 dpi**. Changing it without rescaling every
coordinate silently crops the wrong region — files still written, non-empty, plausible,
and wrong. `save_crop()` also overwrites unconditionally, and a bare run with no
`--year` re-cuts every registry entry.

Two further asset rules:

- **Exclude the paper's own `A.`/`B.` glyph** from option crops. `index.html` renders its
  own `<span class="option-label">`, so a baked-in letter prints twice.
- **Wide option images** (> ~3:1) need `optionImagesWide: true`. In the 2×2 grid at a
  430px viewport they render ~160×35px; the existing 380px single-column fallback does
  not catch this.

### GATE 4/5

- [ ] `node scripts/validate_subjects.cjs` green, `missingImages: 0`
- [ ] Every crop opened and compared against the paper, option by option
- [ ] Every table renders as HTML, not as an image

---

## 6. Stage 6 — Ground truth

Official HSC answers and marks never change, so they are derived **once**, committed, and
enforced by CI. **Do not "audit the answers" by reading a marking guideline again** — that
has been attempted repeatedly and produced a different result every time, including a
clean bill of health for a bank that had five wrong answers.

```bash
python scripts/build_answer_key.py  <subject-id>   # MC answers, page 1 of the guidelines
python scripts/build_written_key.py <subject-id>   # written marks + sample answers
node   scripts/check_answer_key.cjs
node   scripts/check_written_key.cjs
```

Both builders need the local PDFs, which are **not in the repo** (copyright) — which is
precisely why the generated keys are committed. CI can never regenerate them.

**Reconcile every paper against the section totals printed on the exam's own front page**
(Maths 85, Multimedia 30, VET 65). That is an independent check; a self-consistent one is
worth nothing.

### What CI cannot catch — the residual human gate

`check_answer_key.cjs` compares the official *letter*. It therefore cannot see:

- **Reordered options** — the letter indexes the *paper's* order
- **Wrong option text** — option text is invisible to it
- **A description standing in for a missing picture** (Multimedia 2022 Q2)

A passing check does **not** mean the options are right. For any question with an `image`
or `optionImages`, a human compares the paper and the committed crop, option by option.
Prefer the paper's own wording: if it prints bare `W / X / Y / Z`, the options are
`W / X / Y / Z`, not invented descriptions.

### GATE 6

- [ ] 100% of MC questions verifiable (`0 unverifiable`), `0 wrong`
- [ ] Written marks check `0 wrong`; every omission declared
- [ ] Every paper reconciles to its front-page totals
- [ ] Image questions manually compared against the paper

---

## 7. Stage 7 — Release

**Today:** commit to `main`; Cloudflare Pages deploys in ~60 seconds.

**Blueprint target** (`docs/agents-plan.md` §7) — *none of this exists yet*:

```
agent/*  → auto-preview URLs        (agents commit freely)
staging  → staging.cramit-quiz.pages.dev
main     → cramit-quiz.pages.dev    (PR + owner approval, no direct pushes)
```

Blockers: the `staging` branch, branch protection, and the staging Supabase project.

**Browser verification is mandatory for content and is not optional.** JSON being correct
is not the same as the rendered output being correct — that has shipped broken more than
once here. Load the subject, render questions carrying images, answer one correctly and
one incorrectly, and confirm explanations render. Note that images use `loading="lazy"`,
so `naturalWidth` reads 0 while the Browser pane is hidden — force `loading='eager'`
before asserting anything loaded.

### GATE 7

- [ ] Full local CI green
- [ ] Subject exercised in a browser at mobile width, no console errors
- [ ] `docs/HISTORY.md` entry added; CLAUDE.md §7 updated

---

## 8. Stage 8 — Operate

A port is not finished when it ships.

| Trigger | Action | Owner at scale |
|---|---|---|
| New HSC paper (annually) | Extend the keys, port questions, re-verify | Content Agent → PR |
| Syllabus revision | Re-ground topics (Stage 2) | Syllabus & Standards Agent |
| Student-reported error | Triage against ground truth | Service Desk → `content_issues` |
| Band descriptor change | Update marking data | Syllabus & Standards Agent |

The coordination tables this depends on — `content_issues`, `known_issues`,
`band_descriptors`, `marking_criteria`, `written_submissions` — are **specified in the
Blueprint but not deployed**. Until they exist, this stage is manual and undertracked.

---

## 9. Study Mode is a separate project

`studyNotes` is **not** part of a port. It is a distinct content project of comparable
size — Multimedia's was 47 blocks and 42 revision questions; VET's was 71 and 54.

Two things make it different: it requires Stage 2's syllabus grounding to be *complete*
(it is topic-shaped, not question-shaped), and by the owner's explicit preference it is
built **one topic at a time, not batched**.

⚠️ `validate_subjects.cjs` **does not existence-check `studyNotes` images**, so a broken
study-image path passes validation silently and `imageRefs` will not move. Study images
must be browser-verified.

---

## 10. Scaling to the Blueprint

The pipeline above is deliberately written so each stage can be handed to an agent
without restructuring it. Mapping to the Blueprint's roster:

| Stage | Agent | Blueprint phase | Max autonomy |
|---|---|---|---|
| 0–1 Feasibility, Survey | Content Agent (1) | 1 | Level 1 — PR only |
| 2 Syllabus grounding | Syllabus & Standards (21) | 3 | Level 1 |
| 4 Port | Content Agent (1) | 1 | **Level 1 always** |
| 6 Ground truth | — | — | CI-enforced, no agent |
| 7 Release QA | QA / Testing (10) | 1 | Level 2 |
| 8 Operate | Content + Service Desk | 1–2 | Level 1–2 |

**The Content Agent is capped at Level 1 permanently.** The Blueprint's own risk table
gives the reason — *"commits wrong questions to repo"* — and this playbook's history is
the evidence: five wrong Maths answers, six wrong VET answers, and four questions whose
option text described the wrong picture all passed every automated check that existed at
the time. **Stage 6's human gate is not a transitional measure.** It is the control that
catches the defect class machines have demonstrably missed here.

Practical consequences for building the agent side:

- **Ground truth must precede autonomy.** An agent may only port a subject whose answer
  and written keys already exist and pass; otherwise it is generating unverifiable
  content and the human gate has nothing to check against.
- **Each stage emits a reviewable artifact**, so a human approves a *stage* rather than a
  diff. That is what makes Level 1 tolerable at volume — reviewing a Fit Report and a
  Work Plan is bounded work; reviewing 200 generated questions is not.
- **Cost.** The Blueprint budgets the Content Agent at **$15–60/month** running nightly.
  A porting burst is materially more expensive than steady-state monitoring; use
  `logUsage()` and check against that envelope before scaling out.
- **Caching.** `agent.js` deliberately uses no `cache_control` — its prompts sit under the
  minimum cacheable prefix. If Stage 0/1 prompts grow past it, caching becomes worthwhile;
  confirm with a non-zero `cache_read_input_tokens` on a second call rather than assuming.

**Prerequisites before any of this runs autonomously**, none of which exist today: the
`ANTHROPIC_API_KEY` GitHub Secret (the Content Agent has still never run for real), the
`staging` branch and branch protection, the staging Supabase project, and the agent
coordination tables.

---

## 11. Definition of Done

- [ ] GO decision recorded with its reasoning (Stage 0)
- [ ] Every question classified; no unresolved items (Stage 1)
- [ ] Topic list from the primary syllabus (Stage 2)
- [ ] Canonical field names; deviations deliberate and recorded (Stage 3)
- [ ] `validate_subjects.cjs` green, `missingImages: 0` (Stage 4/5)
- [ ] Answer key **and** written key: 0 wrong, 0 unverifiable (Stage 6)
- [ ] Papers reconcile to front-page totals (Stage 6)
- [ ] Image questions compared against the paper by a human (Stage 6)
- [ ] Browser-verified at mobile width, no console errors (Stage 7)
- [ ] `subjects/index.json`, `SUBJECT_ID_MAP`, `SUBJECT_CATALOGUE`, subject card (CLAUDE.md §10)
- [ ] `docs/HISTORY.md` entry; CLAUDE.md §7 row added

---

## Appendix — what the existing ports actually cost

| Subject | MC | Written | Papers | Notes |
|---|---|---|---|---|
| Mathematics Standard 2 | 318 (90 HSC + 228 variants) | 151 | 2020–25 | Only subject with variants and `tips` |
| Health & Movement Science | 193 | 40 | **none** | New 2026 subject; no papers can exist yet |
| VET Construction | 75 | 23 | 2021–25 | 19 image questions — heaviest asset load |
| Industrial Technology — Multimedia | 60 | 29 | 2020–25 | Section III (15 marks/paper) never ported |

Totals: **646 MC, 243 written, 188 image references, 225 MC answers and 203 written
marks under CI enforcement.**

Two deliberate, recorded gaps: Multimedia **Section III** (rotating business/industry
themes, no existing bank content to build from) and HMS's **four non-photo diagrams**
(they need bespoke CSS ported, not an image copy).
