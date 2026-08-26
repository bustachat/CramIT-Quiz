# Handover — extend the HSC answer-key check to Multimedia and VET Construction

**Written:** 2026-08-26, at the end of the session that built the answer-key database.
**Status:** not started. Maths is done and enforced; these two are blocked on one thing.
**Read first:** `CLAUDE.md` §10 ("HSC answers are ground truth in `data/answer-key/`") and
the `docs/HISTORY.md` entry for 2026-08-26.

---

## The one-line version

`data/answer-key/` + `scripts/check_answer_key.cjs` are built, working, and green for
Mathematics Standard 2 (90 answers). Extending them to Multimedia and VET Construction is
blocked because **those subjects' questions carry no `qNum`**, so there is no reliable way
to join a stored question to its official answer. 135 questions are currently unauditable.

Backfilling `qNum` is the whole job. Everything else already works.

---

## Why this is not a five-minute task

The obvious shortcut — "the questions are stored in paper order, so array position is the
question number" — **is false, and it has already produced wrong answers twice today.**

`multimedia.json` 2025 *is* in paper order. `multimedia.json` 2022 is **not** — all ten
questions are present but in a different order. Assuming position produced six phantom
"errors" for Multimedia and six more for VET, all of which were retracted. Three further
attempts using fuzzy text-matching each produced a *different* count (8, then 11, then 7)
while reporting high confidence; one matched 2024 Maths' "Pia's marks" question, which is
paper Q5, to Q9.

**A wrong `qNum` is worse than no `qNum`.** It makes the check compare a question against
some other question's official answer, producing a confident false pass or false fail. The
check currently reports these questions as `unverifiable`, which is honest. Do not trade
that for a guess.

---

## Current state of the two subjects

| | Multimedia | VET Construction |
|---|---|---|
| Subject file | `subjects/multimedia.json` | `subjects/vet-construction.json` |
| Original MC questions | 60 | 75 |
| Years | 2020–2025, 10/year | 2021–2025, 15/year |
| `qNum` field | **absent** | **absent** |
| `variant` questions | none | none |
| Other fields | `year`, `q`, `options`, `answer`, `optionExplanations` | same, plus `image` on 19 |
| Papers on disk | 6 papers + 6 marking guidelines | 5 papers + 5 marking guidelines |

Papers live in `NESA Exams Folder/Industrial Technology - Multimedia/` and
`NESA Exams Folder/VET - Construction/`. **Not in the repo** — copyright. Filenames are
inconsistent (`2025-hsc-ind-tech-multimedia.pdf` vs `2025-hsc-indus-tech-multimedia-mg.pdf`);
`scripts/build_answer_key.py` already handles this by matching the leading year and the
`-mg`/`feedback` markers.

---

## Step 1 — generate the key files (safe, already proven)

```bash
python scripts/build_answer_key.py multimedia
python scripts/build_answer_key.py vet-construction
```

Both subjects are already configured in the script's `SUBJECTS` dict with the right folder
and MC count. Extraction was verified clean this session on **all 17 papers** across the
three subjects — Multimedia 6/6 papers × 10 answers, VET 5/5 × 15. Expect 60 and 75 answers
with no warnings.

This step is safe on its own: `check_answer_key.cjs` will simply report every question as
`unverifiable` until `qNum` exists. It does **not** turn CI red.

## Step 2 — backfill `qNum` (the actual work)

This is what needs care. Recommended order:

1. **Render each paper's Section I pages to images and read them.** This is the method that
   worked this session where text parsing failed. `page.get_pixmap(matrix=fitz.Matrix(2,2))`
   at 2× produced perfectly legible pages, including one where the text layer rendered a
   stem as `mul\ntip\nle graphs`. Roughly 11 papers × ~7 pages.
2. **Match on the question stem and the four option texts together**, and confirm each
   assignment against what you actually read on the page.
3. **Write `qNum` into `subjects/*.json`** with targeted `Edit` calls — do not reserialise
   these files wholesale (`multimedia.json` is 183 KB, `vet-construction.json` 219 KB).
4. Re-run `node scripts/check_answer_key.cjs`. Anything still `unverifiable` should be
   *reported*, not forced.

### Sizing (a proposal, not an answer)

A scripted pass combining option-set and stem similarity proposed:

| | high confidence (≥0.80) | needs review (0.55–0.80) | manual (<0.55) |
|---|---|---|---|
| Multimedia | 49 | 3 | 8 |
| VET Construction | 54 | 11 | 10 |

**Treat these as candidates requiring confirmation, not as results.** The same class of
"high confidence" score is exactly what mis-assigned questions earlier today. The numbers
are here to size the job (~103 of 135 likely straightforward, ~32 needing real attention),
not to be written into the JSON unchecked. The scratch script that produced them was not
kept — it is trivial to rewrite and was not trustworthy enough to preserve.

## Step 3 — expect to find real errors

Maths had **5 wrong answers in 90** (5.6%), all concentrated in one year, and all five
solutions argued for the wrong answer. Multimedia and VET have never been checked against
anything. Budget for finding some, and for rewriting their `optionExplanations` where they
justify a wrong answer.

When you find one, verify it independently — not just against the key. Every Maths fix was
re-derived from first principles (counting graph degrees, running Kruskal, computing the
probability) before being applied. That is what makes the fix trustworthy rather than a
second opinion.

---

## Traps specific to these two subjects

- **VET Construction 2021's marking guidelines** report 20 `Question` headers against 15
  criteria blocks — the paper's structure differs from the others. Check it explicitly
  rather than assuming the 15-MC pattern holds.
- **19 VET questions carry an `image`.** If any have per-option images, check that the
  option text labels match their images — that exact defect was found in Maths 2025 Q2 and
  Q8, where position A read "Exponential decay" while `_A.png` was the growth curve.
- **Neither subject has a `category`/`topic` field**, so you cannot cross-check alignment
  using topic metadata the way Maths allows.
- **Multimedia's Section III** (15 marks/exam, rotating business/industry themes) has never
  been ported into the question bank. Out of scope here — see `CLAUDE.md` §11.

---

## Do not use hscmathsdb.jboxgames.com for this

Investigated in full this session. Its own About panel states *"most of these questions and
answers haven't been human QA'd"*; it carries no licence; its diagram crops are frequently
clipped (2021 Maths Q2 loses vertex D entirely, where CramIT's existing crop is complete);
and it tags Standard 2 papers with Standard 1 syllabus codes. It covers Maths only — it has
nothing for Multimedia or VET regardless.

---

## After this is done

Written answers are the next table: the marking guidelines are uniformly structured
(`Question N` → `Criteria` → `Sample answer`) and hold official sample answers plus mark-band
criteria for ~340 written questions across the three subjects. A scoped extractor reproduced
2020 Maths' 85-mark Section II total exactly, so the approach works — but note that a naive
digit regex over the whole block over-counted to 117, because sample-answer working contains
stray digits. Scope the extraction to the criteria table, before `Sample answer`.

Also still open from this session: **2020 and 2021 Maths split some multi-part questions into
separate rows (7 and 4 respectively) while 2022–2025 merge them.** Harmless today, but it
means `qNum` alone is not a sufficient join key for written answers.
