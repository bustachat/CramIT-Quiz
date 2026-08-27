# Handover — first live run of the porting playbook (Mathematics Advanced)

> ## ⛔ SUPERSEDED — do not start here
>
> **Go to [`docs/subject-plans/mathematics-advanced.md`](subject-plans/mathematics-advanced.md).**
> That is the runbook: one stage per session, with every established fact carried forward so a
> cold session never re-derives them.
>
> This file is kept only as the historical record of the brief that produced Stages 0 and 2
> (2026-08-27). Its "Start here: Stage 0" section is finished, and its sequencing notes have
> been folded into the runbook and the playbook.

**For:** the next fresh session. **Purpose:** run `docs/porting-playbook.md` for real,
starting at Stage 0, against Mathematics Advanced. This is simultaneously two things —
a candidate new subject, and the first test of whether the playbook actually works. Track
both. If the playbook turns out to be missing a step or wrong about something, that is a
useful, expected outcome — fix the playbook, don't just work around it silently.

Read `docs/porting-playbook.md` in full before starting. This file is the state handoff,
not a replacement for it.

---

## What's already in place

**Papers are downloaded.** `NESA Exams Folder\Maths Advanced\` has all six years
(2020–2025): `{year}_exam.pdf`, `{year}_marking_guidelines.pdf`, `{year}_marking_feedback.pdf`.
Confirmed by opening each `{year}_exam.pdf` — all six front pages read "Mathematics
Advanced", "3 hours working time" (this is the full 100-mark paper, not the ~10-mark
Extension slice discussed earlier in this project). `find_papers()` in
`scripts/build_answer_key.py` matches files by pattern (`(20\d{2})` prefix, then
`"feedback"` / `"-mg\b|marking"` / else-paper), not exact filename, so this naming
convention (`2020_exam.pdf` etc., different from the other subjects' NESA-original
filenames) will work as-is once the subject is registered — see below.

**Not yet present:**
- **No syllabus saved.** Stage 2 needs it; ask the owner before downloading (playbook
  Stage 2, step 2), same as every subject so far.
- **`mathematics-advanced` is registered nowhere in code.** Confirmed by grep: it exists
  only as a bare string in `agent.js`'s `ROADMAP_SUBJECTS` list (triage-only, never
  generation). No `subjects/mathematics-advanced.json`, no entry in
  `scripts/build_answer_key.py`'s or `scripts/build_written_key.py`'s `SUBJECTS` dicts,
  no `SUBJECT_ID_MAP`/`SUBJECT_CATALOGUE` entry in `index.html`. A prior file,
  `subjects/mathematics-advanced-2024.json`, was deleted in an earlier session (old agent
  schema, unloadable by the app) — there is no leftover data to reconcile against.
- Working tree has one pre-existing untracked file, `landing.html` — unrelated to this
  work, predates this session, leave it alone unless the owner raises it.

---

## ✅ Stage 0 is DONE (2026-08-27) — verdict **GO**

Read `docs/paper-reports/mathematics-advanced.md` and the `docs/HISTORY.md` entry
"Stage 0 run for real" before anything else. Headline numbers: 10 MC + 90 written marks per
paper, ~93% portable, notation `basic` (the predicted renderer blocker did not materialise),
Standard 2 is a near-exact structural precedent.

Two costs the fit tests do not price, both quantified in the report and both real:
**~100 image assets** (roughly five times VET Construction's load) and a **garbled text layer**
(NESA's MathType font mapping — `(x − 1)²` extracts as `^x - 1h2`), so Section II must be
transcribed from rendered pages rather than extracted.

Also already established, read-only, nothing written: `extract_mc_key()` returns 10/10 for all
six years and `parse_paper()` reconciles **exactly to 90 marks on every paper with zero
unresolved parts**. Stage 6 is de-risked before Stage 1 begins — with one caveat:
**`build_written_key.py`'s `-mg.pdf` glob will not match this folder's filenames** and exits
"no marking-guideline PDFs". Fix that when Stage 6 is actually reached, not before.

## ✅ Stage 2 is also DONE (2026-08-27) — same session

The owner supplied the syllabus location, so Stage 2 ran immediately rather than waiting for
Stage 1. Working document: **`docs/subject-plans/mathematics-advanced.md`** (Stages 1–3 live
there; Stage 0's Fit Report stays in `docs/paper-reports/`).

- **Primary source read in full** — `mathematics-advanced-stage-6-syllabus-2017.docx`, saved
  next to the papers. 14 subtopics, **358 content dot points**, both Year 11 and Year 12.
- **Two live syllabuses.** The 2017 one governs every paper we hold *and* the 2026 HSC; the
  **2024** one takes over from the **2027 HSC**. This topic list is dated — a deliberate product
  decision, not something to discover in 2027.
- **`category` is now derivable, not guessable.** New `scripts/build_mapping_grid.py` extracts
  NESA's official question → syllabus-code grid to `data/mapping-grid/mathematics-advanced.json`.
  All six papers reconcile to exactly 100 marks, zero uncoded rows, and it agrees with
  `build_written_key.py` on **every Section II part in all six papers**.
- **Scope and exam frequency diverge hard** — MA-C1 is 10.6% of the syllabus and 1.3% of six
  years' marks; MA-T3 is 1.7% of scope and 6.8% of marks. Use the grid for per-question
  `category`, the syllabus for any Study Mode weighting. Getting this backwards is the VET
  failure repeating.

**Next: Stage 1 (Survey)** — the only outstanding stage before Stage 3. Nothing is blocked.

---

## Original brief — Stage 0 (kept for reference)

Playbook §1. Work through the four fit tests and produce the Fit Report. Two things to
actually do, not just reason about:

1. **Format fit — compute the portable mark share from the papers' own front pages**,
   not from memory of what Maths Advanced "is like". Read Section I (MC) vs Section II
   (short/extended) mark totals from at least 2–3 years and average.
2. **Renderer fit — check this before anything else, it's the likely blocker.** Advanced
   covers calculus, exponentials/logs, trig identities, and (rarely) basic vectors.
   CLAUDE.md confirms: **no MathJax or KaTeX in this project** — question text is HTML,
   and every existing subject got by on `<sup>`, `<sub>`, `<em>` and Unicode. Sample a
   few actual MC questions from the papers and check honestly whether their notation
   survives that constraint, or whether this stalls at a renderer problem the way
   Extension 1/2 would. Standard 2's 318 questions did fine on the same constraint, which
   is *why* Advanced was picked as the test candidate — but verify it, don't assume it
   transfers.

Write the Fit Report to `docs/paper-reports/mathematics-advanced-{year}.md`. **That
directory does not exist yet** — this will be the first file in it, ever, on this
project. (The Content Agent has never run for real; it's still blocked on the
`ANTHROPIC_API_KEY` GitHub Secret.)

State the GO/NO-GO explicitly, with the reasoning, before doing anything else. If it's a
NO-GO (most likely reason: a renderer gap), that is a complete and successful outcome for
this session — stop there, document why, and report back rather than porting content the
app can't display.

---

## If Stage 0 is GO — sequencing notes for what follows

- **Register the subject in both key-builder scripts before running them.** Add
  `"mathematics-advanced": {"name": "Mathematics Advanced", "folder": "Maths Advanced",
  "mc_count": <n>}` to `SUBJECTS` in `scripts/build_answer_key.py`, and
  `"mathematics-advanced": "Maths Advanced"` to `SUBJECTS` in
  `scripts/build_written_key.py`. Determine `mc_count` from an actual paper, not a guess.
- **`qNum` from the first question authored** — playbook Stage 4/5. Retrofitting it later
  needs `backfill_qnum.py`, which refuses to guess and left 135 questions unverifiable
  for months across Multimedia and VET the last time this was skipped.
- **Canonical field names from Stage 3** — `marks` not `maxMark`, `category` not `topic`,
  `optionExplanations` (Maths Standard 2's `solution` is a deliberate step-by-step
  variant, not the default to copy). The four existing subjects disagree with each other
  on this; don't add a fifth variant.
- **Ground truth is two separate scripts, in order**: `build_answer_key.py` (MC answers)
  can run once the subject dict entry exists and papers are ported with `qNum`.
  `build_written_key.py` (written marks) is independent but has its own extraction traps
  documented in the playbook Stage 6 — read them before running it, not after it produces
  a wrong number.
- **Reconcile against the papers' own front-page section totals** — an independent check,
  not a self-consistent one. Every existing subject's key was verified this way (Maths
  85, Multimedia 30, VET 65 marks in Section II); get Advanced's equivalent numbers from
  its own papers.

---

## Standing reminders (apply regardless of how far Stage 0 goes)

- **Never re-derive answers by re-reading a marking guideline "to audit it"** — every
  attempt at that in this project's history produced a different wrong result each time.
  Extraction scripts + CI are the only trusted path.
- **Browser-verify anything rendered**, per this project's global and local CLAUDE.md
  rules — JSON being correct has shipped broken more than once here.
- **`docs/HISTORY.md` entry is mandatory** at the end of any non-trivial work, per
  CLAUDE.md §2 step 6 — including a Stage-0-only NO-GO outcome.
- **If the playbook itself needs a correction** (a stage that doesn't fit, a gate that's
  wrong, a step that's missing) — fix `docs/porting-playbook.md` in the same session and
  say so plainly. It has never been run before this; treat gaps found as expected, not as
  a mistake to route around quietly.

---

## Everything from this session is committed and pushed

`origin/main` is at `23d7728`. In order, most recent first:

- `23d7728` — playbook: NESA source-acquisition path (papers vs marking guidelines vs
  syllabus; the Content Agent fetches only papers), Compliance Agent note
- `3c899bd` — `docs/porting-playbook.md` created; CLAUDE.md pointers added in 3 places
- `9b4bc9e` — fix: HMS written questions rendered no marks badge (schema drift,
  `maxMark` vs `marks`)
- `c019273` — written-answer key built and enforced in CI (203 questions, 0 wrong)
- `fe695e3` — VET 2021 Q15 option images cropped; Multimedia 2022 Q2's wrong picture
  descriptions fixed

Nothing is pending review, nothing is half-committed. This session's own working tree
edits (the reconnaissance above) touched no files — read-only checks only.
