# Olivier HMS Exam Prep — Recalibration & Enrichment Plan

> **Side-project plan only.** Scope is `olivier-hms-exam-prep.html` and its supporting
> files. **Do not touch `index.html`, billing, auth, Supabase, or any CramIT app
> architecture** — same rule as the file itself (see `CLAUDE.md` §6). This plan was
> written at the end of a research session so a **fresh session** can execute it without
> re-deriving the findings below.

---

## 🔵 HANDOVER — START HERE (session closed 2026-07-24)

**Parts A and B are fully shipped** (Mock Exam recalibrated to the real 100-mark NESA
structure, FA2 depth ported, content-accuracy audit done — see `docs/HISTORY.md` for
the full trail). **Part C is in progress.** Read Part C below in full before doing
anything — it has the topic tree, sourcing rules and the decisions already made. Short
version of where things stand:

**Done — Part C, Phase 1 (Y12 FA2 gap-fill).** Biomechanics/Role of Technology/
Supplements & Micronutrients checked against pdhpe.net; Role of Technology and
Supplements were real gaps, both filled with note-boxes + 7 Practice MC (bank now
157). Commit `7e05cb8`.

**Done — Part C, Phase 2 (Y12 FA1 dot-point audit).** All 19 Y12 FA1 subtopics read
against pdhpe.net (health/system/tech/community clusters, §C.2 mapping). Tech (4/4)
and most of health/system were already well covered — no change. Confirmed real gaps,
each traced to a specific NESA content point: (1) the "ATSI **+ one other group**"
inequity requirement had no second group — added a rural &amp; remote case study
(AIHW life-expectancy-by-remoteness data, verified via websearch); (2) "CVD, cancer
**+ one other condition**" only had 2 of 3 — extended the existing disease table to a
3rd column, Injury (AIHW youth-injury-mortality data, verified); (3) gender-specific
sociological causes of risky behaviour (masculinity/beauty-standard norms) were
missing; (4) the healthcare system's "future opportunities" content point (rural,
ATSI, disability) had no content; (5) "healthcare vs prevention" spending trade-off
was missing; (6) "current & emerging challenges" (wait times, workforce, privatisation)
had no content; (7) added the syllabus's own named example, Healthy Cities Illawarra,
to the community card's SDGs-in-action box (verified via websearch — WHO Healthy
Cities movement, 1987 Australian pilot). +10 Practice MC (157 → 167: health 17→22,
system 9→13, community 12→13). Verified: Node data check green (167 MC, Section II
still sums to 56), browser pane — all 3 touched cards expand and render the new
content correctly, Practice MC topic counts match (Health 22, System 13, Community
13), no console errors.

**Done — Y12 FA2 full dot-point audit (not in the original C.5 order — inserted at owner's
request).** Phase 1 had only checked 3 of FA2's 17 subtopics individually (the ones with
no obvious topic-card home); the other 14 had only been matched to a card **by name**,
never actually read against pdhpe.net — exactly the risk §C.6 warns about. Owner asked
for the same full audit FA1 got. All 14 remaining subtopics read individually and diffed
against the 5 FA2 cards (`assess`/`training`/`groups`/`fuel`/`injury`). 10 of 14 were
already well covered — no change (Pre-Exercise Questionnaire, Types of Training,
Application/Relationships of Training Principles [principles matched but "apply to both
aerobic AND strength" was thin — see below], Applied Strategies, Dietary Requirements,
Sleep/Nutrition/Hydration, Recovery Strategies, Sporting Injury Prevention). Confirmed
real gaps: (1) the syllabus's own named fitness tests, Yo-yo and Wingate, weren't listed
— added to the `assess` card; (2) the "evaluate principles applied to **both** aerobic
**and** strength training" content point wanted an explicit side-by-side, not just a
list of principles — added a 6-row aerobic-vs-strength table to `training`; (3) "Factors
that influence how strategies/tactics are applied" (nature of sport, skill level,
environmental conditions, opposition, team cohesion, communication, fatigue) was an
**entire content point with zero prior coverage** — added a full note-box to `groups`;
(4) "Drug use — health implications, ethics, drug testing" only had one line about
painkillers, missing the WADA/TUE/PED side entirely — added two note-boxes to `injury`
(verified via websearch: WADA sets the Prohibited List, TUE criteria). +8 Practice MC
(167 → 175: assess 11→13, training 22→24, groups 26→28, injury 28→30). Verified: Node
data check green (175 MC, Section II still 56, Section III still 2 FA1 + 2 FA2), browser
pane — all 4 touched cards expand/render correctly, Practice MC counts confirmed
on-screen (Assessment 13, Injury 30), no console errors.

**Immediate correction, same day.** Owner spotted a real miss: the Fitness Testing
page's "Benefits" slide had returned as a bare heading from `get_page_text` (no bullet
content — see the new C.6 rule above), and the audit wrongly assumed the app's existing
table already covered it. It didn't — rewrote the "Why fitness testing differs by
athlete" table to the syllabus's actual 3-category framework (Health Monitoring/
Motivation & Goal Setting/Program Design vs Performance Optimisation/Talent
Identification/Injury Prevention & Recovery), renamed "Yo-yo test" to its precise name
**Yo-Yo Intermittent Recovery Test**, +2 Practice MC (175 → 177, assess 13→15).

**Not started — Phases 3–7, in this order (per C.5):**
3. **Y11 FA1 build** — 15 new subtopics, no topic cards exist yet for these. Cross-check
   against `HMS_Short_Answer_All.pptx` / `HMS_Extended_Answer_All.pptx` (already
   confirmed to cover the first 3 of 15 — Meanings of Health, Dynamic Nature,
   Epidemiology).
4. **Y11 FA2 build — the big one.** 18 new subtopics (body systems, biomechanics
   fundamentals, energy systems, motor learning/psychology). Primary source is now
   confirmed: `Health & Movement Y11 Prelim Flash Card Q&A.pptx` (26 slides, already
   fully extracted in this session's transcript — re-extract via the zipfile/regex
   method in §B.4 if needed, it's native PowerPoint text, not scans). **Diagrams: pull
   from the owner's PowerPoint decks** (extract embedded images via
   `ppt/media/*` inside the pptx zip), not Wikimedia/redrawn SVG — this was explicitly
   decided over the initially-proposed Wikimedia/OpenStax route.
5. **Navigation/engine update** — add a `year:11|12` tag to every question, add Year
   11 topic cards to the picker, make sure Mock Exam only ever draws Y12-tagged
   questions (confirmed via NESA's actual sample HSC paper: zero Year 11 content in
   it — this is not a guess, it's verified, see §C.4.1).
6. **Verify** — Node check extended to assert every question has a valid `year` tag;
   full browser pass; confirm Mock Exam draw excludes Y11.
7. **Docs + commit** — `HISTORY.md` entry, `CLAUDE.md` §6 description update (question
   counts will be well out of date once Y11 lands), then the usual git flow.

**Rules that must not get dropped when picking this back up** (see §C.6 for why):
- Verify every suspected Y11/Y12 topic overlap against the actual pdhpe.net page
  before merging or skipping content — **don't pattern-match by topic name.** (RICER
  looked like a Y11/Y12 duplicate by name; it wasn't — Y11's "first aid" dot point
  covers different ground entirely. Checked and documented in §C.4.4.)
- Any numeric claim gets an independent second-source check before being typed in —
  this caught two real errors already (pre-season duration, over-65 %).
- Diff existing content before adding new content to the same topic card — don't add
  next to something that might already be wrong.
- CramIT's live `subjects/pdhpe-hms.json` is reference/cross-check only — never edit
  it as part of this work (§C.3).
- A `get_page_text` heading with no bullet content underneath it means the real content
  is only in that slide's image — screenshot it, don't assume the app already covers it
  (caught during the Y12 FA2 audit — see §C.6).

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

---

## PART C — Year 11 + Year 12 gap-fill against the official syllabus (hms.pdhpe.net)

> **Written after Parts A/B shipped and a content-accuracy audit caught two sourcing
> errors (pre-season "6–12 months" instead of weeks; over-65 "22%" instead of ~16%),
> both traced to uncritical copying from the ATAR Notes book.** Owner asked for a
> systematic plan to prevent that class of error while closing a much bigger gap:
> **the tool only covers Year 12. Year 11 (the Preliminary course) is entirely
> missing**, and even Year 12's coverage hasn't been checked dot-point-by-dot-point
> against the real syllabus, only against a commercial summary book.

### C.1 — What `hms.pdhpe.net` actually is

Not NESA itself — it's a syllabus-outline site run by "The Learning Network" (Kelly
Bell, a former HSC PDHPE Supervisor of Marking). Each subtopic page reproduces the
**official NESA syllabus dot points verbatim** ("Content Point One: Explain the
interrelationship between... Including: [dot points]... NESA Glossary of Key Words:
Explain — ...") as a slide carousel, then illustrates them with **images sourced from
Wikimedia Commons and OpenStax** (both CC-licensed, credited on-page — e.g. "OpenStax
College. (2013). Anatomy of a Long Bone. [Image]." linking to
`commons.wikimedia.org`). Two implications:
1. **The syllabus dot points themselves are the authoritative scope reference** — better
   than the ATAR Notes book for scope, because they're NESA's own wording, not a
   publisher's interpretation.
2. **The images are a legitimate diagram-sourcing lead.** Instead of redrawing every
   anatomy diagram as original SVG (slow, and SVG struggles with real anatomical
   accuracy) or risking copyright by screenshotting pdhpe.net's own slides, go to
   the **original Wikimedia Commons / OpenStax source** the page cites and pull that
   image directly (OpenStax content is CC BY 4.0; most Commons anatomy diagrams are
   CC BY-SA or public domain) — attribute in an image credits section. This is a much
   better diagram strategy for the Year 11 body-systems content than anything used so
   far in this project.
3. Page text extraction via `get_page_text` returns the dot points + image captions on
   repeat (one repeat per carousel slide) but **not the explanatory prose** — that's
   only visible in the slide images themselves. Treat each subpage as: read the dot
   points for scope, then screenshot each carousel slide for the actual teaching
   content (same visual-reading approach already used for the ATAR book / DLSR deck).

### C.2 — Confirmed scope: the full topic tree

**Year 11 FA1 — "Health for Individuals and Communities"** (15 subtopics, all currently
**absent** from the tool):
Meanings of Health · Dynamic Nature of Health · Epidemiology · Social Justice
Principles · Determinants · Generations · Investigate Meanings · Health Status ·
Health Issue · Strengthening the Individual · Personal Health and Health Behaviours ·
Young People Advocate Health · Organisations and Communities Advocate for Health ·
Nature of Health Promotion in Australia · United Nations SDGs

**Year 11 FA2 — "The Body and Mind in Motion"** (18 subtopics, all currently
**absent**):
Skeletal and Muscular Systems Interrelationship · Biomechanical Principles of Muscles,
Bones & Joints · Respiratory & Circulatory System Interrelationship · Digestive &
Endocrine Systems Interrelationship · Nervous System & Movement Interrelationship ·
How the Systems of the Body Work Together · Role First Aid Plays in Response to
Movement · ATP-PCR/Glycolytic/Aerobic Energy Systems · Role of Nutrition to Energy
Systems · Aerobic and Anaerobic Training · FITT Principle · Immediate Physiological
Response to Training · Physiological Responses to Aerobic Training · Purpose and
Outcomes of Physical Fitness Testing · How Movement Skills are Acquired · Movement
Skills and Sports of Choice · Psychology, Movement and Performance · Communities of
Exercise

**This matches the `Health & Movement Y11 Prelim Flash Card Q&A.pptx` content exactly**
(joints/bones/muscle types, Newton's 3 Laws, fluid mechanics/drag, cardiovascular
structure, respiratory gas exchange, digestion, blood components, macronutrients,
motor learning/motivation, nervous system) — confirming that deck is genuinely Year 11
FA2 material, not off-topic as the original plan's B.4 flagged it might be. It's now a
**primary source**, not a "skim and use judgement" one.

**Year 12 FA1 — "Health in an Australian and Global Context"** (19 subtopics) — the
tool's existing 4 topics (`health`/`system`/`tech`/`community`) cluster-match this list
well (health status+inequities+chronic+ageing → `health`; healthcare system+org+
expenditure+approaches+consumer+challenges → `system`; technology/digital/big data →
`tech`; SDGs → `community`). **No new topic cards needed for Y12 FA1** — just a
dot-point-level audit for gaps within each.

**Year 12 FA2 — "Training for Improved Performance"** (17 subtopics) — the tool's 5
existing topics (`assess`/`training`/`groups`/`fuel`/`injury`) mostly cluster-match,
**except three subtopics with no obvious current home**:
- **Biomechanics** (as its own FA2 dot point — force/levers/projectile motion applied
  to sporting technique, distinct from Y11's foundational biomechanics)
- **Role of Technology** (GPS trackers, wearables, video analysis used in
  training/strategy — distinct from Y12 FA1's healthcare-technology topic)
- **Supplements and Micronutrients** (may be thinly covered under the existing
  nutrition note-boxes; the syllabus treats it as its own dot point — protein,
  creatine, caffeine, iron, vitamin D)

### C.3 — CramIT's live app (`subjects/pdhpe-hms.json`)

Re-confirmed: 165 MC / 35 written, **all Year-12-shaped topics** (`classification`,
`assessment`, `management`, `rehabilitation`, `returnplay`, `concussion`,
`fa2_methods`, `fa2_principles`, `fa2_adaptations`, `fa2_periodisation`,
`fa2_individual_group`, `fa2_psychology`, `fa2_nutrition`, `fa2_sleep`,
`fa2_assessment`) — no Year 11 content, and per `CLAUDE.md` §6 it's a **different,
older PDHPE syllabus** than this standalone tool targets. Per the original plan's
non-goals, it stays a **curation/cross-check source only** — never edited as part of
this work, since editing the live subject touches production content, entitlements
and the app's hardcoded `SUBJECT_ID_MAP` (a decision the owner has separately
deferred). "Run it against CramIT" = diff its FA2 content against whatever's newly
authored here for consistency, not rewrite it.

### C.4 — Decisions (resolved 2026-07-24)

1. **Does Year 11 get a Mock Exam? → No — verified, not assumed.** Owner pushed back
   on the initial recommendation ("doesn't the syllabus say HSC could cover both
   years?"), so this was checked against the actual **NESA sample HSC exam PDF**
   (`health-and-movement-science-11-12-2023-annotated-sample-examination-materials.pdf`,
   39 pages, text-layer present — full-text searched for "Year 11"/"Preliminary": zero
   hits; every Section I MC question is unambiguously Year 12 content — SDGs, OECD
   healthcare approaches, recovery strategies, psychological strategy for an athlete,
   pre-exercise questionnaires). Confirmed: **the HSC written exam only examines Year
   12 content** — standard NESA structure (Year 11 = Preliminary, school-assessed via
   a Collaborative Investigation per the syllabus overview; Year 12 = HSC, externally
   examined). **Decision: Mock Exam stays Year-12-only. Year 11 content populates
   Study + Practice modes only.**
2. **Execution order → confirmed as recommended: Y12 gap-fill → Y11 FA1 → Y11 FA2.**
3. **Diagram sourcing → owner's PowerPoint decks** (not Wikimedia/OpenStax as
   initially proposed) — reuse the images already in
   `Health & Movement Y11 Prelim Flash Card Q&A.pptx` and the other YR11/YR12 decks
   in the Drive folder where they contain usable diagrams; extract via the zipfile/XML
   media-parts approach (`ppt/media/*`), not screenshots.
4. **Cross-year duplication → explicit new rule (owner-flagged).** Before authoring
   any topic, check whether the *other* year already covers it and treat Year 11 as
   the foundational introduction, Year 12 as the applied/deeper layer that
   cross-references rather than re-defines. **First check already ran and corrected
   an assumption**: Year 11's "Role First Aid Plays in Response to Movement" dot
   point (Content Point Seven) turned out to be about general movement-related
   conditions (dehydration, hyperthermia, stress fractures — discussed broadly, "for
   and against"), **not** the RICER/TOTAPS/DRSABCD acronym framework, which is
   entirely a Year 12 "Sporting Injury Prevention"/"Drug Use and Injury Management"
   dot point. Lesson: **verify each suspected overlap against the actual pdhpe.net
   dot-point text before merging/skipping content — topic names can look identical
   while covering different scope.** Where a school genuinely teaches a technique
   (like RICER) practically in Year 11 ahead of its formal Year 12 assessment point,
   still put the full definition in the Year 11 card and have Year 12 reference it
   (a short recap line, not a re-teach) — apply this per-topic after checking, not by
   name-matching alone.

### C.5 — Execution order

1. **✅ DONE (2026-07-24) — Y12 FA2 gap-fill.** Checked all 3 flagged subtopics
   against pdhpe.net's dot points: **Biomechanics** was already reasonably covered
   (movement analysis, stride length, injury-prevention link in the Injury topic) —
   no change needed. **Role of Technology** was a real gap (only a one-line mention)
   — added a full note-box to the `groups` card: training innovations (force plates,
   reaction lights, VR sims), equipment advances (carbon-fibre shoes, aero helmets),
   recording/monitoring (GPS, wearables, video analysis), plus a considerations line
   (cost/access inequity). **Supplements & Micronutrients** was fully absent (only
   whole-food protein was covered) — added a note-box to the `fuel` card covering
   protein, creatine (ATP-PCR link), caffeine (CNS stimulant), and micronutrient
   supplementation, framed as NESA's "Discuss" verb requires (benefit *and*
   limitation for each). +7 Practice MC (150 → 157 total). Verified: Node data check
   green, browser pane confirms both note-boxes render, no console errors.
2. **✅ DONE (2026-07-24) — Y12 FA1 dot-point audit.** Read all 19 Y12 FA1 subpages
   (`get_page_text`, not screenshots — the dot points/captions were sufficient to
   diff against the existing note-boxes without needing carousel-slide images) and
   diffed against the 4 existing cards. Tech cluster (4/4) and most of health/system
   were already adequately covered — no change. Real gaps found and filled: rural &
   remote as the required "one other group" inequity case study (health card);
   Injury as the required 3rd chronic condition alongside CVD/cancer, folded into the
   existing disease table rather than a separate box (health card); gender-specific
   sociological causes of risky behaviour (health card); healthcare system's "future
   opportunities" content point (system card); "healthcare vs prevention" spending
   trade-off (system card); "current & emerging challenges" — wait times, workforce,
   privatisation (system card); Healthy Cities Illawarra as the syllabus's own named
   community example (community card). All new numeric claims (life expectancy by
   remoteness, youth injury mortality) verified via websearch against AIHW before
   being typed in, per §C.6. +10 Practice MC (157 → 167). Verified: Node data check
   green, browser pane confirms all 3 touched cards render correctly, no console
   errors.
3. **Y11 FA1 build** — new topic card(s) (likely 1 combined card given FA1 is
   text/definitions-heavy, or split to mirror the pdhpe.net clusters), screenshot all
   15 subpages, cross-check against `HMS_Short_Answer_All.pptx` /
   `HMS_Extended_Answer_All.pptx` (already confirmed to cover Meanings of Health,
   Dynamic Nature, Epidemiology — the first 3 of 15), author note-boxes + Practice MC.
4. **Y11 FA2 build** — the big one. New topic card(s) for body systems (skeletal/
   muscular, cardio/respiratory, digestive/endocrine, nervous system, energy systems,
   training basics, motor learning/psychology — likely 3–4 cards given 18 subtopics).
   Screenshot all 18 subpages, cross-check against `Health & Movement Y11 Prelim
   Flash Card Q&A.pptx` (already fully extracted — see C.2), source diagrams from the
   Wikimedia/OpenStax links each pdhpe.net page cites, author note-boxes + Practice MC
   + an image-credits section.
5. **Navigation/engine update** — add a Year 11/12 toggle or combined topic list with
   Y11 cards visually grouped; tag every question with `year:11|12` so Mock Exam
   (Y12-only per C.4.1) and Practice (both) filter correctly; update `TOPIC_LABELS`
   and the practice-topic picker.
6. **Verify** — Node data-shape check extended to assert every question has a valid
   `year` tag and Mock Exam draw excludes Y11; browser pane full pass per the existing
   verification checklist; screenshot new diagrams; confirm image attributions render.
7. **Docs + commit** — `docs/HISTORY.md` entry, `CLAUDE.md` §6 description update,
   image-credits note if new licensed images are added, then the standard git flow.

### C.6 — Error-prevention rules for this pass (the reason this plan exists)

Directly answering "how did errors get in / how do we stop it happening again":
- **Every screenshot-derived fact gets sourced from the syllabus page's own dot
  points/slides first** — that's NESA's authoritative scope, not a summary book's
  paraphrase.
- **Every numeric statistic (%, durations, thresholds) gets a second, independent
  source check** (a websearch against AIHW/ABS/pdhpe.net/a sports-science body) before
  it's typed into the tool — the same step that caught the two ATAR Notes errors.
  Don't trust a single source for numbers, even a good one.
- **When porting from a secondary source (ATAR Notes, CramIT, the PPTX decks) that
  disagrees with the primary syllabus source, the primary source (pdhpe.net's stated
  dot points, or a direct websearch) wins** — flag the discrepancy in the HISTORY.md
  entry rather than silently picking one.
- **Diff, don't just add.** The FA2-depth port mistake (Part B) was adding new content
  *next to* existing-but-inaccurate content instead of reconciling both. For every
  topic touched in this pass, read what's already there before writing anything new.
- **A `get_page_text` heading with no bullet content underneath it is a red flag, not a
  green light.** Caught during the Y12 FA2 audit: the Fitness Testing page's "Benefits
  to health, participation and performance" slide returned as a bare heading with no
  text — that's the carousel-image content §C.1 already warned isn't captured by text
  extraction. The audit wrongly assumed the app's existing table already covered it and
  moved on without checking. **When this happens, screenshot that specific slide before
  concluding "already covered" — don't assume.**
