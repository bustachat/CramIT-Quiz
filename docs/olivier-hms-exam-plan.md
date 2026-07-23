# Olivier HMS Exam Prep — Recalibration & Enrichment Plan

> **Side-project plan only.** Scope is `olivier-hms-exam-prep.html` and its supporting
> files. **Do not touch `index.html`, billing, auth, Supabase, or any CramIT app
> architecture** — same rule as the file itself (see `CLAUDE.md` §6). This plan was
> written at the end of a research session so a **fresh session** can execute it without
> re-deriving the findings below.

---

## Context — why this plan exists

`olivier-hms-exam-prep.html` was built by reading the ATAR Notes "HSC Health and
Movement Science — Summary Sheets" book and writing 93 original MC + 10 original
written questions from scratch, using a generic 3/5/12-mark Mock Exam (10 MC + 3
written, 50 min) modelled on the *older* `olivier-hms-prep.html` tool.

A follow-up research pass found:

1. **The real HSC exam has a completely different structure** — the app's Mock Exam
   doesn't resemble it. This was discovered by reading NESA's own sample paper.
2. **CramIT's live "HMS Depth Study" subject** (`subjects/pdhpe-hms.json`, 165 MC + 35
   written) is a *different, older syllabus* (PDHPE HMS Depth Study), but its
   **FA2 (training/injury) content overlaps heavily** with this app's FA2 and is a
   strong curation source — especially Injury, which is this app's thinnest topic.
3. **CramIT's HMS bank is itself downstream of source files already sitting in
   Olivier's Google Drive** — `CLAUDE.AI - HMS_In_Depth_Study_YR12_quiz.html` and the
   `DLSR 12 HMS_ Depth Study` slide deck it was built from. Pulling from the original
   deck is cleaner than porting CramIT's copy (which carries "Slide N" citation cruft).
4. **Year 11 HMS flashcard decks** in the same Drive folder cover foundational
   definitions (WHO health definition, morbidity/mortality, incidence/prevalence,
   epidemiology) that partially fill this app's otherwise-source-free FA1 topic
   ("The Health of Australians").

This plan has two parts: **(A) recalibrate the exam-format features** to match the real
HSC paper, and **(B) enrich content** using the sources above, curated and rewritten in
original wording (never copied verbatim — see Guardrails).

---

## Source materials (all local, already located — re-locate if paths changed)

| File | What it is | Use |
|---|---|---|
| `G:\My Drive\Y11 - Y12 HSC Papers, Exams, Guidelines\Health and Movement Science\Study Material\YR12\HMS SAMPLE HSC PAPER 2026.pdf` | NESA sample HSC paper, 23 pages, scanned (no text layer — render with PyMuPDF like the ATAR book was) | **Format/structure template only** — see Part A findings below, already fully extracted, no need to re-read unless verifying |
| `...\YR12\DLSR 12 HMS_ Depth Study - Explain the management and prevention of sporting injuries.pptx.pdf` | 43-slide injury depth-study deck | Source for FA2 Topic 5 (Biomechanics, Recovery & Injury) — the app's thinnest topic |
| `...\YR12\CLAUDE.AI - HMS_In_Depth_Study_YR12_quiz.html` | Existing HTML quiz built from the DLSR deck; 57 of CramIT's 165 MC questions are copied verbatim from this file | Reference only — prefer going to the DLSR deck directly for new content |
| `...\YR11\HMS_Short_Answer_All.pptx` (110 slides) | Q&A flashcards: WHO health definition, mortality, morbidity, infant mortality, life expectancy, incidence, prevalence | Source for FA1 Topic 1 fundamentals |
| `...\YR11\HMS_Extended_Answer_All.pptx` (110 slides) | Extended-answer flashcards: differing definitions of health, dynamic nature of health, epidemiology | Source for FA1 Topic 1 depth + written-question style |
| `...\YR11\Health & Movement Y11 Prelim Flash Card Q&A.pptx` (26 slides) | Mixed prelim flashcards (WHO def, dimensions of health, joint types/movement, muscle contraction types) | Mostly biomechanics/anatomy — check fit before using (may be too Prelim-specific) |
| `C:\Claude Code Space\CRAMIT QUIZ Code Folder\CODE\CramIT-Quiz\subjects\pdhpe-hms.json` | CramIT's live HMS bank, 165 MC + 35 written, `optionExplanations` per-option rationale pattern | Curation source for all 5 FA2 topics — see Part B mapping table |
| `ATAR Notes year 12 HSC healthand Movement Science.pdf` (already used) | Commercial summary book — already mined for the current build | No further extraction needed unless a topic needs more depth |

**Rendering scanned PDFs:** none of the HSC-paper-family PDFs have a text layer. Use the
same PyMuPDF render-to-PNG approach already used for the ATAR book and the diagram crops
(`scripts/crop_olivier_hms_exam.py` is a working reference for the PyMuPDF pattern):

```python
import fitz
doc = fitz.open(path)
for i in range(doc.page_count):
    doc[i].get_pixmap(dpi=140).save(f'{out_dir}/p{i+1:02d}.png')
```
Then `Read` the PNGs (Claude has vision) — do not attempt `pdftotext`/`pdfplumber` text
extraction on these files, it returns nothing.

---

## Guardrails (copyright — carry forward from the original build)

- **NESA sample paper**: use only as a **format/style template** — section structure,
  mark values, command verbs, stimulus style. **Never copy its actual question text.**
  Write original questions in the same style, exactly as CramIT already does with real
  NESA past papers elsewhere in this project.
- **DLSR deck / YR11 flashcards**: these are Olivier's own study materials, but still
  write **original wording** when porting into the app, not verbatim copy-paste. Strip
  any "Slide N" style citations if sourced via the intermediate quiz HTML.
- **ATAR Notes book**: already established as copyrighted commercial material (owner
  explicitly accepted the risk of cropping diagrams from it into the public repo in the
  original build — same policy carries forward for any new diagram needs).
- This file (`olivier-hms-exam-prep.html`) is committed to the **public** `CramIT-Quiz`
  repo, same as before — keep that in mind for anything sourced from the Drive folder.

---

## PART A — Recalibrate to the real HSC exam structure

### A.1 — Confirmed exam blueprint (from the NESA sample paper, already fully read)

**Total: 100 marks, 3 hours working time + 10 min reading. Three compulsory sections,
no optional questions** (paper explicitly notes this differs from the old PDHPE format).

| Section | Marks | Questions | Format | Recommended time |
|---|---|---|---|---|
| **I** | 20 | Q1–20 | Multiple choice, 1 mark each. FA1 and FA2 interleaved. Some use stimulus (a data table to read a row from, a line graph to interpret). | ~35 min |
| **II** | 56 | Q21–27 | Short/extended answer, several multi-part (a)/(b). Command verbs: Outline, Describe, Explain, Discuss, Analyse. Individual parts range 2–8 marks. | ~1 h 35 |
| **III** | 24 | Q28–29 | Two 12-mark extended responses, **one FA1, one FA2**, each with a stimulus (an infographic / a written scenario). Shared rubric: apply knowledge & understanding; apply critical thinking; use relevant examples/concepts/terms; present a logical, cohesive response. | ~50 min |

**Section II exact mark structure from the sample paper** (use as the "slot" template,
not literal content):

| Q | Total | Parts |
|---|---|---|
| 21 | 3 | single part, "Why…" |
| 22 | 6 | (a) 2 — Outline; (b) 4 — Explain, sport-specific |
| 23 | 7 | (a) 3 — Outline; (b) 4 — Explain |
| 24 | 10 | (a) 4 — Explain; (b) 6 — Discuss |
| 25 | 8 | single part — Analyse, "provide examples" |
| 26 | 12 | (a) 4 — Describe; (b) 8 — Explain, "provide examples" |
| 27 | 10 | (a) 4 — How/Explain; (b) 6 — continues |

**Section III examples from the sample paper** (style reference only):
- Q28 (FA1, 12 marks) — infographic stimulus about a fictional "City X" demographic/health
  data, prompt: *"To what extent could [SDG X] and [SDG Y] assist in improving the health
  status of young people in City X?"*
- Q29 (FA2, 12 marks) — written scenario (an athlete injury + a coach's questionable
  advice), prompt: *"Evaluate the coach's advice and propose a suitable rehabilitation
  program."*

### A.2 — What's wrong with the current app and what to change

| Feature | Now | Target |
|---|---|---|
| Mock Exam MC count | 10 | **20**, drawn with a realistic FA1/FA2 mix (roughly 1/3 FA1, 2/3 FA2 based on the sample paper's interleaving) |
| Mock Exam written | 3 generic (3/5/12 mark) | **Section II** (a bank of "slot" questions matching the 3/6/7/8/10/10/12 mark pattern, multi-part where the real paper is) + **Section III** (a small bank of FA1-tagged and FA2-tagged 12-mark stimulus questions, always draw one of each) |
| Written scaffolds tab | 3 tabs: 12-mark / 5-mark / 3-mark | **3 tabs relabelled to match real bands**: "Short Answer (2–4 marks)" [Outline/Describe/Explain], "Extended Answer (6–10 marks)" [multi-part a/b, Explain/Discuss/Analyse], "Extended Response (12 marks — Section III)" [stimulus-based, To-what-extent/Evaluate, structured around the 4 shared-rubric criteria] |
| Stimulus material | None — all MC/written are plain text prompts | Add stimulus to a handful of MC (a small data table, a simple line/bar chart via inline SVG — no copyrighted images needed, build original) and to the Section III bank (an original infographic-style stat block or scenario box, matching the sample paper's style) |
| Timer | Fixed 50 min | Recommend section-aware timing: **35 / 95 / 50 min** (180 total), shown as a running total with section breaks, OR keep a single 3-hour countdown with on-screen section labels — pick one during implementation, both are reasonable; a shorter "quick practice" mode (e.g. a partial mock) is a nice-to-have, not required |

### A.3 — New data shapes needed (design already worked out — implement as-is)

Keep `QUESTIONS` (Section I MC) as-is, just widen the Mock Exam draw from
`.slice(0,10)` to `.slice(0,20)` — the bank already has 93 MC, no new authoring
strictly required for this part, though adding a few stimulus-based MC (see A.2) is
recommended for realism.

**Replace `WRITTEN_Q`'s flat model with two new arrays** (keep the old
`WRITTEN_Q` shape working for the *Written Help* scaffold tab if easier — or fully
replace, implementer's call):

```js
// Section II — short/extended answer "slots". Maintain 2–3 candidate questions per
// slot so mocks vary; assembly always draws exactly one full slot set (21 through 27)
// so the total is always 56 marks, matching the real paper's structure.
const SECTION2_SLOTS = [
  { slot: 21, totalMarks: 3, parts: [
      { marks: 3, verb: 'Explain', focusArea: 'FA2', topic: 'fuel',
        prompt: '...', keywords: [...], bandDescriptors: {...} }
  ]},
  { slot: 22, totalMarks: 6, parts: [
      { marks: 2, verb: 'Outline', focusArea: 'FA2', topic: 'training', prompt: '...', keywords:[...], bandDescriptors:{...} },
      { marks: 4, verb: 'Explain', focusArea: 'FA2', topic: 'training', prompt: '...', keywords:[...], bandDescriptors:{...} }
  ]},
  // ... 23 (7: 3+4), 24 (10: 4+6), 25 (8: single), 26 (12: 4+8), 27 (10: 4+6)
];
// If variety is wanted, make each slot an array of candidate slot-objects and pick
// one at random per mock — same total marks guaranteed either way.

// Section III — two stimulus-based 12-mark extended responses, one per focus area.
const SECTION3_BANK = [
  { id:'s3-fa1-1', focusArea:'FA1', marks:12, stimulusHtml:'<div>...</div>',
    prompt:'To what extent could ... ?', keywords:[...], bandDescriptors:{...} },
  // more FA1 candidates ...
  { id:'s3-fa2-1', focusArea:'FA2', marks:12, stimulusHtml:'<div>...</div>',
    prompt:'Evaluate ... and propose ...', keywords:[...], bandDescriptors:{...} },
  // more FA2 candidates ...
];
```

**Mock assembly logic** (replace `renderMockQuestions()`):
1. `mockQs = QUESTIONS.sort(random).slice(0,20)` (up from 10).
2. `section2 = SECTION2_SLOTS.map(slot => pickRandomCandidate(slot))` — always 7 items,
   always sums to 56.
3. `section3 = [pickRandom(SECTION3_BANK.filter(q=>q.focusArea==='FA1')), pickRandom(SECTION3_BANK.filter(q=>q.focusArea==='FA2'))]`.
4. Render three visually distinct sections (reuse the existing `.mock-q-card` /
   `.written-section` styling, add a section header banner per the real paper's
   "Section I / II / III" convention).
5. `submitMock()` needs updating: MC score out of 20 (not 10), keyword-mark every
   Section II part individually then sum, keyword-mark both Section III responses
   against their own `keywords`/`bandDescriptors`. Total score display should mirror
   the real paper's /100.

**Minimum content to author for A.3 to work:** 7 Section II slots (ideally 2 candidates
each = 14 short/extended questions) + at least 2 FA1 + 2 FA2 Section III stimulus
questions (4 total, more is better for variety). This is new original-question writing,
same process as the original 10 written questions — just restructured to the real
mark/part shape.

### A.4 — Scaffold tab content rewrite

Replace the current `scaffold-s12` / `scaffold-s5` / `scaffold-s3` content (keep the
`showScaffold(id)` mechanism, just change the 3 ids/labels and their inner content):

- **`scaffold-short`** (2–4 marks) — teach: state the term/fact precisely (Outline),
  or state + one reason (Describe), or state + mechanism (Explain). 1 short worked
  example.
- **`scaffold-extended`** (6–10 marks, multi-part) — teach: treat each part
  independently, use the mark value to gauge depth (2 marks = 1–2 sentences, 4 marks =
  a full paragraph with an example), Discuss/Analyse parts need a judgement sentence.
  Show a worked (a)/(b) example.
- **`scaffold-response`** (12 marks, Section III) — teach: read the stimulus first and
  reference it explicitly in the response (this is what the real rubric rewards),
  structure = Intro (define + address the "to what extent"/"evaluate" framing) → Body
  (2–3 points, each explicitly tied back to the stimulus) → Judgement/Evaluation →
  Conclusion. Show a full worked model answer using one of the `SECTION3_BANK`
  questions.

---

## PART B — Content enrichment (curated, original wording)

### B.1 — Priority order

1. **FA2 Topic 5 (Injury/Recovery/Biomechanics)** — currently the thinnest topic (12
   MC, ~3 written) despite being the richest source (DLSR deck 43 slides + CramIT's
   57 MC / 17 written). Highest-value target.
2. **FA2 other topics** (Training, Groups, Sleep/Nutrition, Assessment) — curate from
   CramIT's `fa2_*` sets, lower urgency since current coverage (9–11 MC each) is
   already reasonable.
3. **FA1 Topic 1 (Health of Australians)** — curate foundational definitions from the
   YR11 flashcard decks to reinforce/cross-check what's already there.
4. **FA1 Topics 2–4** (Healthcare System, Technology, Community) — no external source
   exists; leave as-is unless the owner wants more original authoring here too.

### B.2 — CramIT → this app topic mapping (already computed, reuse directly)

| CramIT `pdhpe-hms.json` topic | → this app topic | MC available | Written available |
|---|---|---|---|
| `classification`, `assessment`, `management`, `rehabilitation`, `returnplay`, `concussion` | **injury** | **57** | **17** |
| `fa2_methods`, `fa2_principles`, `fa2_adaptations` | training | 46 | 8 |
| `fa2_periodisation`, `fa2_individual_group`, `fa2_psychology` | groups | 34 | 7 |
| `fa2_nutrition`, `fa2_sleep` | fuel | 20 | 2 |
| `fa2_assessment` | assess | 8 | 1 |

**Curation checklist per question ported:**
- [ ] Rewrite in original wording (don't copy CramIT's `q`/`explanation` text verbatim)
- [ ] Strip any "(Slide N)" references
- [ ] Confirm it fits the *new* HMS syllabus's FA2 emphasis (not a PDHPE-only nuance)
- [ ] Match this app's question shape: `{topic, q, options, answer, explanation}` —
      consider also adopting CramIT's **`optionExplanations`** pattern (per-option
      rationale, not just one explanation) as an engine upgrade; it's strictly richer
      and the CramIT bank already has it for every question, making the source data
      easy to adapt
- [ ] Add to `QUESTIONS`/`WRITTEN_Q`, re-run the Node validation one-liner used in the
      original build (checks `answer` index in range, options length, required fields)

**Engine change if adopting `optionExplanations`:** in `selectOpt()`, when present,
show the specific rationale for the clicked (wrong) option instead of/alongside the
generic `explanation` — CramIT's live UI (see screenshot from the review session) is a
good reference: each option, once revealed, gets its own green/neutral rationale block.

### B.3 — DLSR deck extraction (Injury topic)

The deck is a `.pptx.pdf` (flattened slides, scanned/no text layer per the earlier
`fitz` page-count check — verify text-layer presence before assuming; some `.pptx.pdf`
exports do retain text). Render to PNG at ~140 DPI and read visually, same as the ATAR
book. 43 slides — budget reading it in 3–4 batches of ~12 pages via the `Read` tool.
Extract: injury classification systems, management/prevention principles, RICER/TOTAPS
variants if present, rehabilitation staging — cross-check against what's already in the
app's Topic 5 card so notes are *added to*, not duplicated.

### B.4 — YR11 flashcard extraction (FA1 Topic 1)

`HMS_Short_Answer_All.pptx` and `HMS_Extended_Answer_All.pptx` (110 slides each) already
had their text pulled via a `zipfile`/regex extraction of `<a:t>` runs (no need to
render as images — these are native PowerPoint text, not scans). Reuse this approach:

```python
import zipfile, re
z = zipfile.ZipFile(path)
slides = sorted(n for n in z.namelist() if re.match(r'ppt/slides/slide[0-9]+.xml$', n))
for s in slides:
    xml = z.read(s).decode('utf8', 'ignore')
    runs = re.findall(r'<a:t>(.*?)</a:t>', xml)
    print(' '.join(runs))
```

Already confirmed present: WHO health definition, morbidity, mortality, infant
mortality, life expectancy, incidence, prevalence, differing definitions of health,
dynamic nature of health, epidemiology. Cross-check each against the current FA1
Topic 1 card (`olivier-hms-exam-prep.html`, "Key measurement terms" / "Life expectancy
& causes" note-boxes) — most of this is *already covered*; the main value is (a)
verifying accuracy against a second source and (b) mining the **extended-answer** deck
for additional written-question material at the Section II short/extended style (since
these flashcards are already Q&A-shaped, they're a natural fit for new
`SECTION2_SLOTS` candidates on FA1 topics).

`Health & Movement Y11 Prelim Flash Card Q&A.pptx` is lower priority — skim first, it
leans biomechanics/joint-anatomy which may be too Preliminary-course-specific for a
Year 12 exam-prep tool; use judgement per-card rather than bulk importing.

---

## Suggested execution order

1. **A.3 data shapes + A.2 Mock Exam engine rewrite** (20 MC, Section II/III assembly,
   scoring) — this is the structural fix and doesn't require new source reading beyond
   what's already in this plan.
2. **Author the minimum Section II/III question set** (7 slots × ~2 candidates + 4
   Section III stimulus questions) in the real format — original writing, following
   A.1's verb/mark-value template.
3. **A.4 scaffold tab rewrite** to match the new bands.
4. **B.3 — read the DLSR deck**, port/rewrite Injury content (biggest single content
   gap).
5. **B.2 — curate remaining FA2 topics** from CramIT (lower urgency, do if time
   allows).
6. **B.4 — cross-check FA1 Topic 1** against YR11 flashcards, mine the extended-answer
   deck for FA1 Section II candidates.
7. **Verify** (see below), update `CLAUDE.md` §6 entry text if the file's description
   changes meaningfully, append a `docs/HISTORY.md` entry, then the usual
   `git add` → commit → push flow (specific files only, per project git rules).

## Verification checklist (mirror the original build's approach)

- [ ] Node one-liner: `QUESTIONS` count/topic breakdown, all `answer` indices in range,
      `SECTION2_SLOTS` sum to exactly 56 marks, `SECTION3_BANK` has ≥1 FA1 + ≥1 FA2
      candidate.
- [ ] Browser pane: open the file, run a full Mock Exam start→submit cycle via
      `javascript_tool` (same pattern used in the original verification pass) —
      confirm 20 MC render, Section II shows 7 parts summing to 56 on-screen, Section
      III shows 2 stimulus questions, submit produces a combined score display and
      keyword feedback for every written part.
  - [ ] Confirm the scaffold tabs show the 3 relabelled bands with correct content.
  - [ ] Confirm no broken images if any new stimulus graphics were added (inline SVG
      recommended over cropped images to avoid new copyright exposure — the sample
      paper's own graphs/infographics should be **redrawn originally**, not
      screenshotted, consistent with this project's established diagram policy).
- [ ] Screenshot or JS-based check that Section I MC pool still mixes FA1/FA2 (not all
      one focus area).

## Explicit non-goals

- No changes to `index.html`, `functions/`, `subjects/*.json`, billing, auth, or any
  CramIT production path.
- No bulk copy of CramIT's HMS question text — curate and rewrite.
- No verbatim reproduction of NESA sample paper questions — structure/style only.
- Do not merge this tool into CramIT's app in this pass — that's a separate, later
  decision the owner has explicitly deferred (see prior conversation: "focus on this
  app first").
