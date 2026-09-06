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

⚠️ **One exception, found on the first live run: Stage 2 does not depend on Stage 1.** Stage 1
surveys *questions*; Stage 2 reads the *syllabus*. Neither consumes the other's artifact, and
Stage 2 is the one that needs the owner's go-ahead to download a document — so start it early
rather than letting it queue behind the survey. Everything else is genuinely sequential:
Stage 3 needs Stage 2's topics, Stage 4 needs Stage 3's field names, Stage 6 needs Stage 4's
`qNum`.

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

### ⚠️ A recorded claim is not evidence — re-verify what an earlier stage wrote down

Every stage here hands the next one a **written artifact**, and the whole point of the artifact
is that the next session does not re-derive it. That is the right default for *measurements* —
crop counts, mark totals, field names. **It is the wrong default for a stage's stated
conclusions and its forward-looking risk calls**, and this playbook's own runbooks have now
produced several that were confidently written and simply untrue.

**The distinction that matters: did the earlier stage MEASURE it, or did it REASON to it?**

| A measurement — inherit it | A conclusion or a risk call — re-verify it |
|---|---|
| "121 crops, 28 tables" | "Section III sends the parts to separate booklets" |
| "all six papers reconcile to 100" | "the longest response the engine has handled is 5 marks" |
| "`build_written_key.py` extracts no criteria table" | "these four questions are a real marking-quality defect" |
| "60 MC answers, 0 wrong" | "`optionImagesWide` is not needed for this subject" |

**Every entry in the right-hand column is a real one that was wrong**, and each was written into
a runbook as settled fact:

- **Multimedia Section III, Stage 1 (2026-09-06).** The runbook recorded that NESA sends
  Q16 (a)/(b) *"to separate writing booklets in four of the six years"* and concluded the bank
  should be split. Reading all six instruction lines: **zero of six** — every year says *"the
  Section III Writing Booklet"*, singular, and 2020/2021 merely allocate pages inside it. The
  correct shape is the **opposite** of the one recorded. It was caught only because that same
  runbook told the next session to read the lines — the one place it distrusted itself.
- **Multimedia Section III, Stage 1, again.** The same runbook named a 10–12 mark extended
  response *"the one genuine feasibility risk in the whole runbook"*, on the premise that *"the
  longest thing it has ever handled is a 5-mark answer"*. True of that one subject's JSON; false
  of the engine, which already ships **ten VET responses at 10–15 marks and four HMS at 12**. A
  whole stage had been scoped around a risk that production had retired months earlier.
- **Maths Advanced, Stage 1 → Stage 4.** Its Section II crop list was treated as complete and was
  a **lower bound three separate times** (2023 Q16 absent; 2025 Q29 absent from the table though
  named in the same document's prose; 2022 Q28 one entry for two diagrams). Its
  *"`optionImagesWide` not needed anywhere"* was wrong too — 2021 Q4 needs it.
- **VET Construction, review ledger.** Recorded as *"a human compared each question against
  NESA"*; the comparison was assistant-performed with a spot-check on a couple. **Seven
  documents inherited the overstatement**, and it became a Gate 6 exemplar before anyone checked.

The failure mode is always the same and it is cheap to avoid: **a claim gets written down once,
and from then on it is quoted rather than checked** — including by the person who wrote it. The
more confidently a runbook words something, the less likely the next session is to test it.

**Rules:**

1. **When a stage's conclusion determines what you build, re-derive it from the primary source
   before building.** Not the whole stage — the one claim. Reading six instruction lines cost
   about a minute and inverted a bank-shape decision.
2. **A claim about "the engine" or "the repo" must be measured against the engine or the repo**,
   never against the one subject in front of you. `multimedia.json`'s longest answer is not the
   engine's longest answer. Grep or script it across all of `subjects/`.
3. **Write claims so their scope is visible.** *"multimedia.json's longest written answer is 5
   marks"* would have been true and harmless; *"the longest thing it has ever handled"* was
   neither. Name the thing measured.
4. **Record HOW a claim was established, next to the claim** — measured / read from the source /
   reasoned / assumed. The review ledger's `reviewMethod` exists for exactly this reason; the
   same discipline applies to prose in a runbook.
5. **When you find a recorded claim was wrong, correct it in place AND say so in the write-up.**
   Silently building the right thing leaves the wrong claim to mislead the next session, and this
   project has had one propagate through seven documents.

⚠️ **Applies with most force to a stage that scopes work it will not do itself** — Stage 0's
feasibility calls, Stage 1's asset counts and risk escalations, Stage 3's schema decisions.
Those are read months later, by a session with no memory of how firm the evidence was.

---

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
| Official NESA syllabus | Usually *not* pre-saved — **ask here, at Stage 0**, not at Stage 2 | Stage 2 cannot proceed |

⚠️ **Filenames are not a convention, they are whatever the owner saved.** Maths Advanced uses
`{year}_exam.pdf` / `{year}_marking_guidelines.pdf`, not the NESA-original `-mg` names the other
four subjects carry. `find_papers()` in `build_answer_key.py` copes (it pattern-matches);
`build_written_key.py` does **not** (see Stage 6). Check both before assuming a subject is
tooling-ready.

Some folders also hold a **third PDF per year** — `{year}_marking_feedback.pdf`, NESA's notes
from the marking centre. No stage needs it. `find_papers()` classifies it correctly only because
it tests `"feedback"` *before* `"marking"`; that ordering is load-bearing and easy to break.

### Source acquisition — who fetches what, and from where

Two different paths exist, and they are **not** equivalent. Know which one you are on.

**Path A — human, local (every port done so far).** The owner saves NESA PDFs by hand
into `NESA Exams Folder/{subject}/`: papers plus marking guidelines (`-mg` suffix), one
subfolder per subject. These are **copyright and never committed to the repo** — which is
exactly why the *generated* answer keys in `data/answer-key/` are committed, since CI can
never regenerate them. The syllabus is fetched only after asking the owner, and is saved
alongside under the same treatment.

**Path B — Content Agent, automated (built, never run).** `discoverNewPapers()` uses
Sonnet 5 with the `web_search` tool, system-scoped to `educationstandards.nsw.edu.au`, and
returns a direct `pdfUrl` per newly published paper. `downloadFile()` (plain `https.get`,
follows up to 3 redirects, rejects >25MB) pulls the PDF **into memory only** — it is
base64'd for the API and never written to disk or committed.

⚠️ **Path B fetches the exam paper and nothing else.** This is the single most important
limitation to understand before relying on it:

| Source | Path A (human) | Path B (agent) | Needed by |
|---|---|---|---|
| Exam paper | ✅ saved locally | ✅ discovered + downloaded | Stages 0, 1, 4 |
| **Marking guidelines** | ✅ saved locally | ❌ **never fetched** — the discovery prompt asks only for "exam papers" | **Stage 6** |
| **Syllabus** | ✅ on request | ❌ never referenced in the code | Stage 2 |
| Band descriptors / marking criteria | manual | ❌ Agent 21, Phase 3, not built | AI marking, `bandDescriptors` |

`build_answer_key.py` and `build_written_key.py` both parse the **marking guidelines**,
not the paper. So the Content Agent as built can triage a paper and generate questions
from it, but **cannot produce the ground truth needed to verify them.** Agent-generated
questions arrive unverifiable by construction — which is a second, independent reason for
the Level 1 cap in §10, on top of the accuracy history.

**Closing this gap** means extending discovery to return the `-mg` URL alongside the paper
(NESA publishes them on the same subject page, and Path A's local filenames already encode
the convention). Until then, **Stage 6 is a human step even in a fully agentic pipeline.**

⚠️ **Compliance.** Automated retrieval of NESA material is a terms-of-use question, not
just a technical one, and the volume/cadence of Path B differs from a human saving a file.
The Blueprint assigns this to the **Compliance Agent (12), Phase 5** — "monthly NESA terms
+ Privacy Act check". Confirm NESA's terms permit automated download before Path B runs at
any scale. Nothing fetched by either path is ever committed or redistributed.

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

### Dry-run the Stage 6 extractors here, not at Stage 6

Both ground-truth builders can be run **read-only** against the marking guidelines before a
single question is ported — import them and call `extract_mc_key()` / `parse_paper()` directly,
writing nothing. On the Maths Advanced run this cost minutes and produced the strongest single
feasibility signal in that Fit Report: every paper reconciled **exactly** to its front-page
Section II total with zero unresolved parts. It also surfaced the `build_written_key.py` glob
gap recorded in Stage 6, which would otherwise have appeared at Stage 6 as an empty result.

A subject whose guidelines *don't* parse cleanly is not a NO-GO, but it is a cost the Fit Report
must state up front.

### Output: the Fit Report

Write to `docs/paper-reports/{subject}.md` — the directory the Content Agent already targets.
**It did not exist until the Maths Advanced run; the agent has never run.**

Per-paper files (`{subject}-{year}.md`) are the Content Agent's shape, because `triagePaper()`
genuinely runs once per paper. A human Stage 0 on a subject whose paper format is stable across
years should write **one subject-level report with per-year rows** instead — six near-identical
files carry no more information. Split per paper only where the years actually differ in
structure. Either way the report covers:

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

### Worked example — Mathematics Advanced (assessed 2026-08-27, the first live run)

**GO.** `docs/paper-reports/mathematics-advanced.md`. 10 MC + 90 written marks per paper across
2020–2025; ~93% portable once ~42/540 drawing marks go to `omittedParts`; notation `basic` (no
∑, matrices, vectors or complex numbers, so the no-MathJax constraint holds); Standard 2 is a
near-exact structural precedent.

The two findings worth carrying forward are the ones the tests were *not* designed to catch:
test 3 came back at roughly **100 image assets**, about five times VET Construction's load, and
the papers' **text layer is garbled** (NESA's MathType font mapping renders `(x − 1)²` as
`^x - 1h2`), so Section II must be transcribed from rendered pages rather than extracted. Both
are scheduling facts rather than blockers — but they are the port's actual cost, and neither
appears in the mark-share arithmetic that drives the verdict.

### GATE 0

- [ ] Papers **and** marking guidelines present for every year in scope
- [ ] Portable mark share computed from the papers' front pages, not estimated
- [ ] Notation verdict recorded
- [ ] Stage 6 extractors dry-run read-only; reconciliation result recorded
- [ ] Explicit GO / NO-GO written down, with the reason

---

## 2. Stage 1 — Survey (the per-question work plan)

**Purpose: replace judgement calls with measurements.** Stage 0 says whether to port;
Stage 1 says exactly what porting will cost, question by question.

Most of this is mechanical and should be *measured from the PDF*, never estimated by
reading it — this project's repeated failure mode is a confident impression of a paper
that turned out wrong. Where the survey cannot decide, it must **report the question as
unresolved rather than guess** (the standard `backfill_qnum.py` already holds).

⚠️ **No single detector finds every graphic — union three, then look at the pages.** The first
live run (Mathematics Advanced) needed all of: text-gap bands (ink in a band with no body text),
`page.find_tables()` filtered to ≥6 cells, and an ink profile (dark pixels outside every
text-block bbox). Each missed assets the others caught — a band detector loses a chart whose axis
labels are wide text blocks, an ink profile loses a diagram whose labels sit inside one large
text block, and `find_tables()` reads graph axes as tables in both directions. Four Section II
diagrams surfaced only in the union. Then render every candidate to a labelled contact sheet and
classify by eye: crop-versus-table and aspect ratio are visual judgements, and the visual pass is
also what catches a detector's silent miss. Counting vector paths does not work at all —
straight-line graphs score zero and text underlines score false positives.

### Per-question classification

| Dimension | Values | Consumes |
|---|---|---|
| Question type | MC / short written / extended / **unportable** | `omittedQuestions` |
| Stimulus | none / raster / vector / table | Stage 5 |
| Options | text / images / bare letters-in-stimulus | `optionImages` |
| Option image height | measure the RENDERED height at 430px, not the ratio | `optionImagesWide` |
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
which (of the following|of these)? ?(best )?(represents|shows|depicts|illustrates|could be|could represent)
which (diagram|graph|drawing|image|picture|sketch|plan|symbol|section|histogram)
(is a |a )?possible (sketch|graph|diagram)
```

⚠️ **The first two lines alone are not enough — both have been caught short by a live run.**
Stage 0 for Mathematics Advanced used a version missing `could represent` and undercounted;
Stage 1 then found that `which of these …` (2024 Q8) and `a possible sketch of …` (2023 Q6) are
also picture-option questions and match none of the original patterns. Use all three lines.

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

   ⚠️ **Ask at Stage 0, not here.** On the first live run this rule read as a hard blocker
   discovered three stages in, after the port had already been declared a GO — which is a
   process failure, not caution. The syllabus is a known, predictable input for every subject;
   raise it once, up front, in the same breath as confirming the papers are present. Once the
   owner has said yes, that answer covers the download — do not re-ask at Stage 2.
3. Read the actual content. For DOCX, `pandoc` is unavailable in this environment;
   `python-docx` works — extract **both** `document.paragraphs` **and**
   `document.tables`, because NESA's VET template puts the substantive
   scope-of-learning content in tables, not paragraphs.
4. Marking-guideline mapping grids are a *secondary cross-check only*. They reflect exam
   history, not syllabus scope: VET's "Working in the industry" carries 80 rows of
   scope-of-learning against Safety's 48, and includes content (cultural diversity,
   anti-discrimination) that has **never appeared in any exam paper checked**.
5. State plainly whether the topic list came from the primary source or a proxy.

**Check whether the subject has more than one live syllabus.** NESA runs a new syllabus and the
one it replaces in parallel for years. Mathematics Advanced has a 2017 syllabus (governing the
2020–2025 papers *and* the 2026 HSC) and a 2024 syllabus (2027 HSC onwards, Year 11 teaching
from Term 1 2026). Ground the port in the one the **papers** were written against — and record
the other, because it dates the topic list to a known HSC year. New syllabuses may be web-only
on curriculum.nsw.edu.au with no PDF or DOCX to download.

### Derive `category` from the mapping grid — do not guess it

Every NESA marking guideline ends with a **Mapping Grid**: one row per question part giving its
marks, syllabus content code and outcome code. That is NESA's own answer to "what topic is this
question?", and `scripts/build_mapping_grid.py` extracts it to
`data/mapping-grid/{subject}.json` — committed, because CI can never regenerate it.

This is a *different question* from the topic list. The grid says what was **examined**; the
syllabus says what is in **scope**, and they diverge sharply. Measured on Mathematics Advanced,
the first subject where both axes exist:

| | Scope (syllabus dot points) | Examined (6 papers) |
|---|---:|---:|
| MA-C1 Introduction to Differentiation | 10.6% | **1.3%** |
| MA-T3 Trigonometric Functions and Graphs | 1.7% | **6.8%** |
| MA-C3 Applications of Differentiation | 5.3% | **15.7%** |

**Use the grid for per-question `category`; use the syllabus for topic weighting.** Grid-derived
weighting would have all but deleted MA-C1 — a Year 11 foundation subtopic every Year 12
calculus question silently assumes. That is the VET failure in a different subject.

The grid also **cross-checks the written key**: on Mathematics Advanced the two extractors agree
on every Section II part across all six papers. Two traps live in its docstring, each of which
produced a wrong number first — the code can split across words in the text layer (`MA- M1`),
and a row's cell text is vertically centred so it can begin *above* its own label line.

### Output: the working document

Stages 1–3 share one living file per port, `docs/subject-plans/{subject}.md` — Work Plan, topic
list and field mapping in the order the port produces them, with a status table at the top.
Stage 0's Fit Report stays separate in `docs/paper-reports/`, because it is the artifact that
decides whether the rest happens at all.

### GATE 2

- [ ] Primary syllabus document located, saved, and read
- [ ] Any second live syllabus identified, and the port's shelf life stated
- [ ] Topic list proportional to scope-of-learning size, not exam frequency
- [ ] Mapping grid extracted and reconciled to the paper's front-page total
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

**There is a second instance of the same defect, still live** (found 2026-08-27, Mathematics
Advanced Stage 3): the MC renderer badges a topic with `q.category || q.topic`, but the
**written** renderer reads `q.topic` alone. Every written question that follows the canonical
`category` therefore displays **no topic badge** — which today means all 151 Mathematics
Standard 2 written questions, since their port. Same signature: silent, invisible to CI, a
one-line fix mirroring the MC path. A new port should not work around it by writing `topic`.

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

### A multi-part written question is ONE bank entry — decide this here, not mid-port

**Found 2026-09-02, VET Construction — three separately-reported symptoms (an image showing
on some parts of a question but not others, a shared intro sentence duplicated across parts,
an oversized image) turned out to be one bug.** `getWritten()` calls `shuffle()` on the whole
bank array, so if a NESA question's parts are stored as separate entries, a student can see
part (a) now and part (d) minutes later as an unrelated card, and a shared stimulus can render
on one part while its sibling shows nothing. Mathematics Advanced and Standard 2 never had
this defect because they already store **one bank entry per whole NESA question** (confirmed
by reading a live example: Advanced 2020 Q14, three sub-parts folded into one `q` field, one
`keywords` list, one mark total, each part carrying its own inline `<strong>(N marks)</strong>`
badge). VET's 18 split Section II questions were merged into that same shape — not a new one.

**The decision test, and it resolves the call rather than leaving it a preference: does
NESA's own paper put these parts on the same page in one continuous answer space, or does it
send them to separate writing booklets** (*"Answer part (a) of the question in a writing
booklet… Use the other writing booklet to answer part (b)"*)? Same space → **one merged bank
entry**: one inline `<img>` positioned where NESA's text introduces it (never the top-level
`image` field on a written question — see the canonical table above), one combined `keywords`
list, a freshly **authored** `bandDescriptors` (NESA grades each part separately, so there is
no official combined rubric to copy). Separate booklets → **keep every part its own entry** —
those are genuinely independent responses on different topics with no shared stimulus, and
merging them would misrepresent the exam, not fix anything. VET's own Q20/Q21 (Section
III/IV) are the worked example of this second branch.

**This is mandatory for every future port, and for every existing subject's multi-part
written questions when next touched.** It is not folded into "canonical field names" above
because it is a bank-*shape* decision, not a field-name one, and `check_written_key.cjs`
being tolerant of either shape (its prefix-sum join, §6) is not permission for the rendering
to be wrong — only the ground truth is shape-agnostic, the shuffle is not.

### …and a merged question needs `parts[]`: an answer box and a mark per part

**Added 2026-09-05.** Merging the parts into one card fixed the shuffle, and left the
*answering* wrong: one textarea for a four-part, 9-mark question, scored as a single lump,
so a student who nailed (a), (b) and (d) and skipped (c) saw `6 / 9` with nothing saying
where the 3 marks went. **NESA's own paper prints a separate ruled answer space under every
lettered part**, so one box per part is the faithful shape, not a UX preference.

A merged entry therefore also carries, **alongside** its unchanged fields:

```jsonc
"q":     "…full combined text, UNCHANGED…",   // CI and the results screen still read this
"stem":  "…intro shared by every part, rendered once, sticky…",   // omit if there isn't one
"parts": [ { "label": "(a)", "marks": 2, "q": "…this part's prompt…",
             "intro": "…optional, shared by the (a)(i)/(a)(ii) sub-parts under it…",
             "answer": "…", "keywords": [...], "acceptableAnswers": [...],
             "minKeywords": 2, "bandDescriptors": {...} } ]
```

- **Never empty `q`.** `validate_subjects.cjs` requires it non-empty and `check_written_key.cjs`
  joins on the question's own `marks`, so `parts[]` is purely additive — a question without it
  renders and scores exactly as before. The engine supports `parts[]` for every subject; a
  subject opts in by adding the data.
- `validate_subjects.cjs` **asserts `sum(parts[].marks) === marks`** plus unique labels and a
  prompt/model answer/scoring mechanism per part. The per-part marks are the only ones the
  student sees on such a question, so without that they could drift from the NESA-verified
  total silently.
- **Per-part `keywords` and `bandDescriptors` must be derived, not invented.** For a *new*
  port that means authoring them from NESA's per-part criteria rows (which
  `build_written_key.py` already extracts — §6) at the same time as the merged entry, while
  the guidelines are open. Retro-fitting them later is a content job, which is exactly why
  four of the five existing subjects still don't have them.
- The AI marker takes all parts in **one** request and returns a mark per part; do not call
  it per part, or the student's monthly quota is multiplied by the part count.

### GATE 3

- [ ] Field mapping written down before any question is authored
- [ ] Every deviation from canonical is deliberate and recorded
- [ ] Every multi-part written question's bank shape decided by the same-page-vs-separate-
      booklet test above, before any question in that group is authored
- [ ] Every merged multi-part entry carries `parts[]` with per-part marks, prompt, model
      answer, keywords and NESA-derived `bandDescriptors`, and the marks sum to the
      question total (`validate_subjects.cjs` enforces the sum)

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
| Diagram / photo | Cropped JPG, `<img>` **carrying its own `max-width:100%` style**; never an SVG redraw |
| Table | Reconstructed `<table>` HTML — **not** a crop |
| Whole question the engine can't present | `omittedQuestions` entry |

Tables as HTML matter for mobile: text reflows and can be scrolled, which a screenshot of a
table cannot do.

⚠️ **This paragraph used to say the app's `.study-dtable` pattern collapses a question table
to stacked cards on mobile. It does not** — `.study-dtable` is applied in exactly one place,
`renderStudyBlock()`, and the *question* renderer never uses it. Question tables get
`.q-table` (hand-written HTML, or the pipe-markdown path in `formatQuestionText()`) or
`.nesa-table`, and **neither collapses nor scrolls**. Measured at a 430 px viewport, where the
stem is 390 px wide: a 6-column table fits; an 8-column table renders 513 px and, because
`body` sets `overflow-x: hidden`, its right-hand columns are **silently clipped** — no
scrollbar, no error, just missing data the student needs. Wrap any table of 7+ columns:

```html
<div style="overflow-x:auto;-webkit-overflow-scrolling:touch;margin:14px 0">
  <table class="q-table" style="min-width:520px;margin:0">…</table>
</div>
```

Corrected 2026-08-27 during Mathematics Advanced Stage 3, which measured it in a browser
rather than inferring it. Lookup tables (future value, z-scores) are where this bites.

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
- **Short option images need `optionImagesWide: true` — and the test is the rendered
  height, not the aspect ratio.** ⚠️ This bullet said "> ~3:1" until 2026-08-29, when
  Mathematics Advanced 2021 Q4 cropped at **2.94:1** — inside the supposed safe range —
  and rendered **160 × 54px** in the 2×2 grid at a 430px viewport, against 360 × 122px
  one-per-row. The 380px single-column fallback does not catch either case. **Render the
  option set and read the height off the DOM**; treat "> ~3:1" as a prompt to look, not
  as the threshold.

- **An inline `<img>` inside a `q` stem must carry its own
  `style="max-width:100%;height:auto;display:block;margin:14px auto"`.** ⚠️ There is
  **no `.q-text img` rule in `index.html`** — the only `max-width` on a question image
  is `.device-phone .q-image-wrap img`, which governs the separate `image` field. An
  unstyled stem image renders at its natural crop width (1767px inside a 390px stem, in
  the worst real case) and `body { overflow-x: hidden }` swallows the overflow rather
  than scrolling it. **Nothing reports this**: `body.scrollWidth` still reads 430,
  `validate_subjects.cjs` only existence-checks the path, and no console error fires —
  the diagram is simply cut off on the right. Found on Mathematics Advanced 2021, where
  nine stem images shipped without it; Mathematics Standard 2 has carried the inline
  style on all 71 of its stem images since its port. Verify with:

  ```js
  [...document.querySelectorAll('.question-area')]
    .filter(a => a.scrollWidth > a.clientWidth + 1)   // must be empty
  ```

### GATE 4/5

- [ ] `node scripts/validate_subjects.cjs` green, `missingImages: 0`
- [ ] Every crop opened and compared against the paper, option by option
- [ ] Every table renders as HTML, not as an image
- [ ] **No `.question-area` overflows its own client width at 430px** — the check that
      catches an unstyled stem image or an unwrapped wide table. `body.scrollWidth` does
      **not** catch either, because `body { overflow-x: hidden }` hides the overflow:
      `[...document.querySelectorAll('.question-area')].filter(a => a.scrollWidth > a.clientWidth + 1)`
      must be empty
- [ ] **Every option-image set rendered and its height read off the DOM** — the aspect
      ratio is not the test for `optionImagesWide`

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

✅ **Fixed 2026-08-31 (Maths Advanced Stage 6) — kept here because the failure mode recurs.**
The two builders used to disagree about how a marking guideline is recognised, and one failed
silently: `build_written_key.py` globbed `re.search(r"-mg\.pdf$", basename)`, so a subject saved
as `2020_marking_guidelines.pdf` never matched and the script exited `"no marking-guideline
PDFs"` — with nothing wrong with the PDFs at all. Both now share the same tolerant selector
(`build_answer_key.find_papers()` / `build_written_key.is_guidelines()`).

**The rule that outlives the bug: test `feedback` FIRST, then `-mg|marking`.** Some folders carry
a *third* PDF per year — `{year}_marking_feedback.pdf`, or Multimedia's
`{year} … HSC Marking Feedback.pdf`, which contains **both** words. Reverse the order and the
marking-centre notes get parsed as guidelines.

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

### The second residual gate — written answers

Symmetric with the image gate above, and larger. `check_written_key.cjs` enforces the
**mark only**. Prose cannot be compared for equality, so **everything a written question
teaches or is marked on is outside CI**. Three artefacts, three different consumers, three
different failure modes — review all three, not just the model answer:

| Field | Who consumes it | What a wrong value does |
|---|---|---|
| `modelAnswer` (stored as `answer` on most files) | **Shown directly to the student** after they answer — `index.html` reads `q.answer \|\| q.modelAnswer \|\| q.sampleAnswer` | **Teaches the student the wrong thing.** No AI involved, no error, nothing reports it |
| `keywords` | Sent to `mark-written.js`, **and** used by the offline keyword-grid fallback | Student is mis-marked, in both the AI and the no-AI path |
| `bandDescriptors` | Sent to `mark-written.js` as the band rubric | AI marks against the wrong standard; absent, it silently falls back to a generic 0/50%/100% rubric |

⚠️ **The model answer is student-facing and never reaches the AI marker.** This is the
opposite of the intuition that the AI is the risk. `mark-written.js` receives
`question`, `maxMarks`, `keywords`, `studentAnswer`, `bandDescriptors` — **not** the model
answer. A wrong model answer is a pure teaching defect, and the most invisible one in the
whole pipeline.

### Making the review a standing guarantee, not a one-off audit

The project's own rule is that *an audit is a claim about one moment; a test is a standing
guarantee*. Prose can't be asserted on — but **whether a human has compared it, and whether
that comparison is still current, absolutely can be.** So the review itself becomes the
committed, checkable artifact.

**A review ledger, beside the ground truth it reviews against:**

```
data/answer-key/written/reviews/{subject-id}.json
```

```jsonc
{ "subject": "multimedia",
  "reviews": {
    "2020": {
      "16(a)": {
        "reviewedAt": "2026-09-01",
        "verdict": "ok",                    // ok | corrected | divergent-accepted
        "fields": ["modelAnswer", "keywords", "bandDescriptors"],
        "sampleAnswerFingerprint": "sha256:1f3a…",   // the OFFICIAL answer, as at review time
        "note": null                        // required when verdict is divergent-accepted
      }
    }
  }
}
```

**Why a sidecar and not a field on the question.** `subjects/*.json` is downloaded by every
student, so review metadata there is dead weight on the wire; `validate_subjects.cjs` globs
that folder and would have to learn to ignore it; and the ledger belongs next to the ground
truth it cites, exactly as the keys do.

**What the fingerprint buys you — this is the whole point.** It is a hash of NESA's sample
answer *as it read when the review happened*. Regenerate the key, and any part whose official
text changed has its fingerprint diverge, so the review is **automatically void** rather than
quietly stale. That is the standing guarantee prose otherwise can't have.

**The checker reports before it enforces**, the same ramp used for reverse coverage. Built
2026-09-01: `check_written_key.cjs` prints per-subject review coverage and any stale reviews,
and **enforces for any subject that has committed a ledger**. Committing the ledger is how a
subject opts in — a new port lands reviewed and can never regress, while the subjects
carrying historical debt report 0% and keep CI green. Tooling: `scripts/build_review_ledger.py`
(from a hand-typed verdict table in `scripts/reviews/{subject_id}.py`) and
`scripts/review_triage.py <subject-id>` for the queue.

**Mechanical triage orders the reading queue. It never decides anything.**
⚠️ The VET run put numbers on how weak it is: its queue's **top** entry was a benign
`divergent-accepted`, and **two of the six real defects sat at the very bottom, on term
overlap 1.00** — a stem that gives away its own answer, and an answer that misdescribes a
picture, both score as *perfect agreement* with NESA. Read every question regardless of rank.
⚠️ This project has been burned repeatedly by similarity scoring (`backfill_qnum.py` exists
because of it, and §10 rule 3 is explicit that fuzzy text-matching is not a join). These
signals say *read this one first* — they are never a verdict, and never a substitute for
reading:

- a `keyword` that appears nowhere in the `modelAnswer` (it drives marking but the model
  answer never demonstrates it)
- a `keyword` that appears nowhere in NESA's `sampleAnswer`
- lowest substantive-term overlap between `modelAnswer` and `sampleAnswer` — the bottom of
  that list is where an answer to a *different question* hides
- `modelAnswer` length wildly out of step with the mark value

✅ **`bandDescriptors` HAVE ground truth since 2026-09-01.** `build_written_key.py` now keeps
each criteria row's **text** beside the mark it already read positionally, so a descriptor is
derived from NESA's own wording instead of authored for plausibility. 1 446 criteria rows
across the four subjects with papers; the extension is inert for every previously committed
field.

⚠️ **A criteria row's mark is vertically CENTRED in its cell**, so a row whose wording runs
over three lines carries its mark on the *middle* line — bracketing a row by the mark lines
around it leaks wording in BOTH directions, exactly the bug `build_mapping_grid.py` was fixed
for. Read the table's own **drawn horizontal rules** (`row_rules()`/`band_of()`).

**Collapsing N official bands to the engine's fixed `{full, partial, minimal}`** (VET's tables
carry 1 to 5 rows): `full` = NESA's top row verbatim, `minimal` = NESA's bottom row verbatim,
`partial` = every row between them, verbatim, joined with `" OR "`. Do **not** try to map the
slots onto the engine's mark arithmetic — it treats `minimal` as *zero* marks, and NESA
prints no row for zero, so that mapping forces authored prose into every question. Two
degenerate shapes: N = 2 has no middle row, so `partial` repeats the bottom row (repeating an
official sentence beats inventing a third); N = 1 (all-or-nothing 1-mark questions) has
neither, so `partial`/`minimal` state the row's non-attainment — the one place a descriptor
is not NESA's wording, and it must be flagged in the ledger. Worked through in
`docs/subject-plans/vet-construction-written-review.md`.

**Where a subject legitimately diverges, say so in the ledger.** Maths sample answers extract
as mangled equation layout (`x2 102 82 = + 2 = 164`), so a Maths model answer *should* read
nothing like NESA's. That is `divergent-accepted` with a note — not a silent pass, and not a
failure.

### GATE 6

- [ ] 100% of MC questions verifiable (`0 unverifiable`), `0 wrong`
- [ ] Written marks check `0 wrong`; every omission declared
- [ ] Every paper reconciles to its front-page totals
- [ ] Image questions manually compared against the paper
- [ ] **Every written question reviewed against NESA's sample answer, and the review
      committed to the ledger** — ⚠️ and the ledger's `reviewMethod` must say WHO did the
      comparing. VET's said "human review" when it was assistant-compared with a spot-check
      on a couple of questions; no subject has actually met this gate yet — `modelAnswer`, `keywords` and `bandDescriptors`, with
      `divergent-accepted` used and noted where the official text is unusable
- [ ] **Review coverage 100% for this subject**, and no stale fingerprints

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
  content and the human gate has nothing to check against. This is not hypothetical:
  the Content Agent **cannot fetch marking guidelines at all** (see Stage 0, Source
  acquisition), so today it can only ever generate questions no automated check can
  verify. Extending discovery to return the `-mg` URL is the highest-value single change
  to the agent, and a prerequisite for it porting anything unsupervised.
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
- [ ] Every multi-part written question's bank shape decided by the same-page-vs-separate-
      booklet test (Stage 3) — never one entry per part unless NESA sends those parts to
      separate writing booklets
- [ ] Every merged multi-part entry carries `parts[]` — per-part marks, prompt, model answer,
      keywords and NESA-derived `bandDescriptors`, marks summing to the question total
      (Stage 3/4), so the student gets an answer box and a mark per part
- [ ] `validate_subjects.cjs` green, `missingImages: 0` (Stage 4/5)
- [ ] Answer key **and** written key: 0 wrong, 0 unverifiable (Stage 6)
- [ ] Papers reconcile to front-page totals (Stage 6)
- [ ] Image questions compared against the paper by a human (Stage 6)
- [ ] **Written answers reviewed against NESA's sample answers and the review committed to
      `data/answer-key/written/reviews/{subject}.json` — 100% coverage, no stale
      fingerprints, and `reviewMethod` stating who compared them (Stage 6)**
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
