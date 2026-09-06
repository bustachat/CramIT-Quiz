# Industrial Technology — Multimedia · Section III — port runbook

**Scheduled: after Mathematics Advanced Stage 7 (Release).** Do not start this while that
port is still open — it is the only other in-flight subject work, and both depend on the same
Stage 7 `index.html` engine fixes.

This is **not a new subject port.** Multimedia is live: 60 MC + 29 written, Study Mode complete
at 7 topics, keys committed and CI-enforced. This runbook covers the one hole left in it —
**Section III, Question 16, never ported, 90 marks across 2020–2025.**

Because the subject already exists, the playbook's Stage 0 (feasibility), Stage 2 (syllabus
grounding, done for the 7 Study Mode topics) and Stage 3 (schema, fixed by the live file) do
not re-run in their usual form. **This runbook starts at Stage 1.**

| Stage | Status | Session |
|---|---|---|
| **1 Survey** | ✅ **done 2026-09-06** | 1 session |
| 2 Syllabus grounding (Section III scope only) | ⬜ **next** | 1 session |
| 4 Port | ⬜ | 1–2 sessions |
| 6 Ground truth — **marks** | ➡️ already done — folded into Stage 4's gate | — |
| **6b Written-answer review** | ⬜ **NEW** — covers Section III's 6 new entries **and** Multimedia's existing 29 → **35** | 1 session |
| 7 Release | ⬜ | 1 session |
| 8 Study Mode topic (optional) | ⬜ | separate project — playbook §9 |

### How to start a session

> Read `docs/subject-plans/multimedia-section-iii.md` and `docs/porting-playbook.md`.
> Run **Stage N** for Multimedia Section III. Do not re-derive anything this runbook
> already records. Write the result back here and tick its gate before finishing.

---

## Established facts — carry these forward, do not re-measure

| | |
|---|---|
| Scope | **Section III only.** Q11–Q15 (Section II) are already ported for all six years and are not touched |
| Shape, every year | **Question 16, 15 marks, two parts.** (a) is *Describe* at 5 marks; (b) is *Discuss / Explain / Analyse* at 10. **2023 is the only exception: 3 + 12** |
| Total | **12 official parts, 90 marks, 2020–2025** |
| Timing | NESA allows ~35 minutes for the section — an extended-response task, not a short answer |
| Ground truth | ✅ **Already committed.** `data/answer-key/written/multimedia.json` holds all 12 parts' official marks, **NESA's sample answers**, and — since the 2026-09-01 extractor extension, repaired 2026-09-06 — **the criteria rows** each part is banded against. Nothing to extract; `bandDescriptors` are *derived*, not authored |
| Assets | ✅ **ZERO** — confirmed at Stage 1 by reading all six pages and rendering two. No image, table or content graphic on any Section III page |
| Bank shape | ✅ **Decided at Stage 1: one merged entry per year, `parts[]` of two.** All six papers use **one** Writing Booklet — this is NOT VET Q20/Q21's separate-booklet case |
| Current coverage | `check_written_key.cjs` reports **30/42** official leaf parts claimed. Porting these 12 closes it to **42/42** |
| Existing bank content | **None.** Unlike Study Mode topics 1–7, there is nothing to build from — original authoring against NESA's sample answers |
| Papers | Local, never committed — `NESA Exams Folder/Industrial Technology - Multimedia/`. Section III is the **last page** of the exam PDF, page 9 in all six years |
| Field names | Use the **canonical** names (`marks`, `category`, `keywords`, `modelAnswer`) — playbook §4. `multimedia.json`'s existing deviations are debt, not precedent |
| ⚠️ File format | **Never round-trip `multimedia.json` through `json.dumps`** — it reformatted into a 461-line diff once by expanding the compact inline arrays in `studyNotes`. Targeted text replacement only (`docs/HISTORY.md`, 2026-08-27 later) |

### The six papers' themes — measured from the papers, 2026-09-01

| Year | (a) | marks | (b) | marks |
|---|---|---|---|---|
| 2020 | Describe environmental factors in selecting a new site | 5 | Discuss strategies to minimise continuing environmental impact | 10 |
| 2021 | Describe Industrial Relations issues arising from modified operations | 5 | Explain career and training opportunities arising from them | 10 |
| 2022 | Describe the role of WHS legislation in a multimedia workplace | 5 | Explain strategies to improve workplace safety | 10 |
| 2023 | Describe how ONE new technology is improving the industry | **3** | Discuss the impact of mass production and automation, with industry examples | **12** |
| 2024 | Compare marketing/advertising across a hierarchical partnership vs a flat sole trader | 5 | Analyse how organisational structure influences production and efficiency | 10 |
| 2025 | Describe the effects of legislative requirements on sustainable practices | 5 | Analyse how historical developments in manufacturing have affected the industry | 10 |

⚠️ **This is a different strand from everything already in the subject.** These are
**business-and-industry** questions — environment/sustainability, industrial relations, WHS,
careers, automation, organisational structure, marketing, historical development. **None of the
seven Study Mode topics covers any of it** (Text & Document Design, Graphics, Animation, Video,
Audio, WWW, IP & Ethics are all Section I/II *production* content). Do not file these under an
existing topic.

⚠️ **2024 carries shared stimulus prose** ("Organisation A is a partnership-owned firm with a
hierarchical structure…") that **both** parts depend on. Whatever bank shape Stage 1 picks must
keep it attached to both.

---

## Stage 1 — Survey ⬜ NEXT

**Purpose: decide the bank shape and classify all 12 parts.** Small enough for one session, but
four real decisions must be taken and recorded, not assumed.

1. **One bank entry per question, or one per part? This is now a resolved decision test, not
   an open UX call** (CLAUDE.md §10 rule 9 and `docs/porting-playbook.md` §4, both added
   2026-09-02 after VET Construction's Section II shipped with exactly this defect — a shared
   stimulus rendered on some parts of a merged-looking question and not others, because the
   parts were actually stored, and shuffled, as independent cards). **The test: does NESA's
   own paper put the parts on the same page in one continuous answer space, or send them to
   separate writing booklets?** Same space → one merged entry, one inline `<img>`, one
   `keywords` list, an authored `bandDescriptors`. Separate booklets → keep every part its own
   entry, exactly as VET's own Section III/IV (Q20/Q21) were correctly left split.

   ⚠️ **This runbook previously asserted that "Section III's own text already says (a)/(b) go
   to separate writing booklets in four of the six years", and pointed at keeping the bank
   split. That was wrong — it was written without reading the pages, which is exactly why the
   runbook told the next session to read them.** All six instruction lines were read
   2026-09-06. **It is zero of six, and the conclusion inverts.** See the resolved decision
   below.
2. ⚠️ **Does the engine present and mark a 10–12 mark extended response acceptably?** Measure
   it; do not assume. `mark-written.js` marks against `keywords` + `bandDescriptors` — it is
   **never sent the model answer** — and the longest thing it has ever handled is a 5-mark
   answer. **This is the one genuine feasibility
   risk in the whole runbook.** If a band-marked 12-mark response needs a different prompt, a
   band rubric, or a larger `max_tokens`, that is a `mark-written.js` change and must be flagged
   here **before** Stage 4 starts — not discovered mid-port. HMS's `writingScaffolds` (two
   mark-band scaffolds, 6–10 and 12) are the nearest existing precedent for the shape.
3. **Assets.** Check each of the six Section III pages for a diagram or table. 2024's stem is
   prose; verify the other five. Expect **zero crops**, but confirm it — Stage 1's asset count
   was found to be a lower bound three separate times on Maths Advanced.
4. **`category`.** Multimedia's 89 existing questions carry **no `category`/`topic` field at
   all**, and its mapping grid names topics in prose rather than codes, so it was never parsed.
   Decide whether Section III introduces one (and what), or matches the subject's existing
   absence. Matching is the lower-risk default.

---

### Stage 1 — RESULTS, measured 2026-09-06

Everything below was measured from the six papers and the live code, not inferred. Two of the
runbook's own recorded assumptions turned out to be wrong; both are corrected in place above
and restated here.

#### Decision 1 — bank shape: **ONE MERGED ENTRY PER YEAR, each carrying `parts[]`**

Every one of the six papers carries the identical instruction line:

> *"Answer the question in **the** Section III Writing Booklet. Extra writing booklets are available."*

**One booklet, every year.** 2020 and 2021 additionally allocate pages *inside that same
booklet* — *"Answer part (a) … on pages 2–4 of the Writing Booklet"* / *"part (b) … on pages
5–8 of the Writing Booklet"* — which is one continuous answer space, not two booklets.
2022–2025 carry no per-part allocation at all.

The contrast with VET's genuinely-split questions is unambiguous — VET Q20/Q21 read:

> *"Answer this question in **TWO SEPARATE** writing booklets. Use one writing booklet to answer
> part (a) of the question. Use **the other** writing booklet to answer part (b) of the question."*

So by CLAUDE.md §10 rule 9's own test — *same page in one continuous answer space, or separate
booklets?* — Section III is **same space, all six years**. It follows Q16–19 / Maths / VET
Section II, **not** VET Q20/Q21. **No mixed shape across years.**

Consequently, per §10 rule 10, each of the six entries **must** carry `parts[]` — one answer box
and one mark per NESA part. Verified this routes correctly: `isMultiPart()` requires
`parts.length > 1`, and two parts satisfy it.

| | |
|---|---|
| Bank entries added | **6** — one per year, `qNum: 16` |
| `parts[]` per entry | **2** — `(a)` and `(b)` |
| Official leaf parts closed | **12** → coverage 30/42 becomes **42/42** |
| `stem` | Holds the shared prose where the paper prints it — 2020, 2021, 2022 and 2024 have one; 2023 and 2025 have none (parts stand alone) |

⚠️ **2024's stimulus is explicitly bound to both parts** by the paper itself — *"Use the
following information to answer parts (a) and (b)."* — which is the strongest single piece of
evidence for the merge. It goes in `stem`, rendered once. Note the paper italicises the
organisation letters (*Organisation A*, *Organisation B*); preserve with `<em>`.

#### Decision 2 — extended-response marking: **RESOLVED, no `mark-written.js` change needed**

⚠️ **The runbook called this "the one genuine feasibility risk in the whole runbook", on the
grounds that "the longest thing it has ever handled is a 5-mark answer". That is true of
`multimedia.json` alone and false of the engine.** Measured across the live bank:

| Subject | Longest single answer box in production |
|---|---|
| **vet-construction** | **15 marks** — 2021 Q20, 2022 Q20, 2023 Q21, 2024 Q21, 2025 Q21; plus five more at 10 |
| health-movement-science | **12 marks** — 4 questions |
| multimedia (today) | 5 marks |

**Ten VET extended responses at 10–15 marks are already live and were browser-verified in the
2026-09-01 VET completion session.** Section III's parts are 5+10 and 3+12 — every one *smaller*
than the 15-mark single box already shipping. The risk is retired by precedent, not by argument.

The working precedent to author against is **VET 2021 Q20 (15 marks): 18 `keywords`,
`minKeywords: 7`, NESA-derived `bandDescriptors`.**

Path-by-path check:

- `isMultiPart()` → 2 parts → the **`parts` path**, not the single-question path.
- `buildPartsPrompt()` sends each part its own max, keywords and band descriptors, and
  instructs the model to mark each part separately without pooling.
- The server **clamps each part to its own maximum**, discards labels the question doesn't
  have, and derives the total from the parts.
- `max_tokens: 1024` on the parts path is ample: output is two 1–2 sentence part feedbacks plus
  the overall feedback/improvement pair. The student's prose is *input* and is not bounded by it.
- `scoreOne()` (offline path) is **mark-agnostic** — `round(matched / keywords.length × maxMark)`
  — so it scales to 12 marks unchanged.

⚠️ **One real quality caveat for Stage 4 — a caveat, not a blocker.** The bank's
`bandDescriptors` is a fixed 3-tier `{full, partial, minimal}`, but NESA bands these parts across
**5 rows** (10 / 8 / 6 / 4 / 2). The standing collapse rule joins the three middle rows into
`partial`, and `buildPartsPrompt` sends the band text **without its mark numbers**. For a 10–12
mark part that leaves the model a wide middle tier. Mitigate with a **keyword list rich enough to
carry the granularity** — VET's 18 keywords for 15 marks is the calibration to match.

#### Decision 3 — assets: **ZERO crops, confirmed by reading all six pages**

| Year | images | tables | drawings |
|---|---|---|---|
| 2020–2025 (all six, identical) | **0** | **0** | 2 |

Both drawings are **page furniture, byte-identical across all six years**: the NESA year badge
box (`33.5 × 14.4 pt` at y = 68.3) and the horizontal rule under the section header
(`453.5 pt` wide at y = 269.5). No content graphic, no table, on any Section III page.

Confirmed **visually**, not just from the text layer — 2020 and 2024 page 9 rendered at 110 dpi
and read (§10 rule 3). Both are pure prose. **Stage 1's asset count was a lower bound three
separate times on Maths Advanced; here all six pages were read individually and the inventory is
identical across years, so the zero is trustworthy.**

#### Decision 4 — `category`: **match the subject's existing absence — do not introduce one**

Measured: **all 60 MC and all 29 written questions in `multimedia.json` carry neither `category`
nor `topic`.** Introducing the field for these 6 questions alone would light the topic badge on
Section III and nowhere else in the subject — a visible inconsistency for no gain, since the
subject has no populated category filter to join to.

Matching the absence is the runbook's own stated lower-risk default. If a Section III topic is
ever wanted, it belongs with the optional **Stage 8** Study Mode topic, which is where the
business-and-industry strand would be defined from the syllabus.

`section: "III"` **is** set (existing entries carry `section: "II"`). Verified this is
informational only — no code path reads `q.section`.

#### All 12 parts classified

The six-paper theme table in *Established facts* above was checked against the papers
word-for-word and is **correct as recorded**. Marks confirmed against
`data/answer-key/written/multimedia.json`: five years at 5 + 10, **2023 at 3 + 12**, every paper
totalling the front-page Section III total of **15**.

**GATE 1** — [x] all 12 parts classified · [x] bank shape decided and recorded (merged, six
entries, `parts[]`) · [x] extended-response marking risk **resolved — retired by production
precedent, no engine change** · [x] asset count confirmed by reading all six pages (**zero**)

---

## Stage 2 — Syllabus grounding (Section III scope only) ⬜

⚠️ **CLAUDE.md §10's mandatory syllabus rule applies, and this is the case it exists for.** The
seven Study Mode topics were re-grounded in the real NESA syllabus on 2026-07-29 precisely
because a mapping-grid-derived list had been wrong twice. Section III's scope is the Industrial
Technology syllabus's **industry-study / business strand**, which no session has yet read.

Do **not** derive the scope from these six papers. Six years of questions is exam history, not
syllabus scope — VET is the standing counter-example, with 80 rows of "Working in the industry"
content including material never once examined.

⚠️ **BLOCKED — the syllabus is not on disk, and downloading it needs the owner's permission.**
Checked 2026-09-06: `NESA Exams Folder/Industrial Technology - Multimedia/` holds **only** the
six papers, six marking guidelines and five marking-feedback PDFs. No syllabus. (For contrast,
Maths Advanced, Maths Standard 2 and VET Construction each have theirs saved.)

Ask the owner before downloading, then save it into
`NESA Exams Folder/Industrial Technology - Multimedia/` under the same copyright treatment as
the papers — not committed to git.

**Where to look:** `site:educationstandards.nsw.edu.au` and `site:nsw.gov.au` for the
*Industrial Technology Stage 6 Syllabus*; NESA has moved some syllabus hosting to nsw.gov.au
and old links 301-redirect. Section III's scope is the **industry-study / business strand**.
For a DOCX, `pandoc` was unavailable in this environment on a previous port — `python-docx`
worked, and **both `document.paragraphs` and `document.tables` must be read**, since NESA's
templates put scope-of-learning content in tables.

**GATE 2** — [ ] primary syllabus document located and read · [ ] Section III scope stated from
it, not from the papers · [ ] stated plainly whether the list is primary-sourced

---

## Stage 4 — Port ⬜

Twelve parts, authored against NESA's committed sample answers in
`data/answer-key/written/multimedia.json`. Ground truth already exists, so unlike a normal
Stage 4 the marks **cannot go wrong without CI catching it immediately**.

**Shape, decided at Stage 1 — do not re-open it:** **six bank entries, one per year**, each
`qNum: 16`, `section: "III"`, `marks: 15`, carrying **`parts[]` of two** — `(a)` and `(b)` —
with the shared prose in `stem` for 2020, 2021, 2022 and 2024. No `category`. No images.
`validate_subjects.cjs` asserts `sum(parts[].marks) === marks`, so each entry must total 15.

- Author `modelAnswer` and `keywords` **per part**, using NESA's sample answer as the source,
  and `bandDescriptors` per part from that part's **criteria rows** (see Stage 6b — these are
  committed ground truth, not authored prose).
- ⚠️ **Keyword lists must be rich enough to carry a 10–12 mark part's granularity** — the
  offline path scores `matched / keywords.length × maxMark`, and the 3-tier band collapse
  leaves the AI a wide middle tier. **VET 2021 Q20 — 18 keywords, `minKeywords: 7`, for 15
  marks — is the calibration.**
- ⚠️ **Never re-read the marking guidelines to "check" a mark** — §10 forbids it, and the key is
  already committed.
- Run `node scripts/check_written_key.cjs` after each year: coverage climbs toward 42/42 and
  stays at 0 wrong.
- Targeted text edits only — see the `json.dumps` warning above.

**GATE 4** — [ ] validator green · [ ] `check_written_key.cjs` 0 wrong, **coverage 42/42** ·
[ ] every paper reconciles to its front-page Section III total of 15

---

## Stage 6 — Ground truth (marks) ➡️ ALREADY DONE

`data/answer-key/written/multimedia.json` was built at Maths Advanced Stage 6 (2026-08-31) and
already holds all 12 Section III parts with official marks and sample answers. **Nothing to
build**; the stage collapses into Stage 4's gate.

---

## Stage 6b — Written-answer review ⬜ NEW

**The marks are ground truth and CI-enforced. Everything a written question actually teaches
is not.** `check_written_key.cjs` enforces the mark only — prose cannot be compared for
equality — so `modelAnswer`, `keywords` and `bandDescriptors` all sit outside CI.

**Design lives in `docs/porting-playbook.md` §6** (the review ledger, the fingerprint, the
report-then-enforce ramp, the triage-never-decides rule). Read it before starting; this
section records only what is specific to Multimedia.

### Scope for this session

| | |
|---|---|
| Section III's new entries | **6** questions / **12** parts — reviewed as they are authored in Stage 4, so they land reviewed |
| Multimedia's existing written bank | **29** — never reviewed, ported before the ledger existed |
| **Total** | **35 bank questions**, the whole subject |

⚠️ **This was 41 before Stage 1.** The ledger has one entry per **bank question**, and Stage 1
resolved Section III to **six merged entries**, not twelve split ones — so the target is
**35 / 35**, not 41.

Do the existing 29 in the same session. The reviewer is already holding the marking
guidelines' sample answers and the subject's conventions in their head; splitting it wastes
that context, and it takes Multimedia to 100% review coverage in one pass — the first subject
to get there, and the reference the others are measured against.

### Multimedia's measured artefact coverage — re-measured 2026-09-06

| Field | Present | Missing |
|---|---|---|
| `modelAnswer` (stored as `answer`) | 29 / 29 | — |
| a scoring mechanism (`keywords` **or** `acceptableAnswers`) | **29 / 29** | — |
| `keywords` specifically | 25 / 29 | 4 |
| `bandDescriptors` | **25 / 29** | 4 |

⚠️ **The "four questions with no scoring data" is a false alarm, and the runbook's own framing
of it was wrong.** It called them *"AI-marked against a generic 0/50%/100% fallback rubric with
no key concepts at all … a real marking-quality defect"*. Identified 2026-09-06, they are:

| Year | Q | Marks | Mechanism |
|---|---|---|---|
| 2020, 2021, 2023, 2024 | **Q11** | **1 each** | `acceptableAnswers` |

All four are **1-mark acronym-recall questions** (*"What does RTSP stand for?"*) carrying an
exact-match `acceptableAnswers` list — which is the **correct** mechanism for them, not a
missing one. `scoreOne()` short-circuits on `acceptableAnswers` and returns full or zero
exactly; keywords alongside it would be **inert**, which is precisely the dead-data finding
made on VET 2023 Q16(a)(i) on 2026-09-06.

What remains genuinely true is narrower: the **AI** path still sends these four
`keywords: []` and `bandDescriptors: null`, so a logged-in student's AI mark falls to the
generic rubric. On a 1-mark exact-recall item that is close to harmless, and the offline path
is exact. **Recommendation: explicitly defer with this reason** — GATE 6b already allows it —
rather than authoring band descriptors for a one-word answer.

⚠️ **Section III raises the stakes on `bandDescriptors` specifically.** A 10–12 mark
band-marked extended response is exactly where a generic rubric produces a meaningless mark.
These 12 parts need real band descriptors, not the fallback. Stage 1 confirmed the engine
handles the *length* fine; the *rubric* is the part that must be authored well.

✅ **`bandDescriptors` DO have ground truth now — this runbook's prerequisite is already met.**
`build_written_key.py` was extended on 2026-09-01 to extract the **criteria rows**, and the
repaired extractor landed 2026-09-06. Verified present for all 12 Section III parts:

| Part | Criteria rows committed |
|---|---|
| 2020 (a) 5 / (b) 10 | 5 / 5 |
| 2023 (a) 3 / (b) 12 | **3** / 5 |
| 2025 (a) 5 / (b) 10 | 5 / 5 |

Apply the standing collapse rule — **top row / middle rows joined / bottom row, all verbatim**
(`docs/subject-plans/vet-construction-written-review.md`). Note 2023 (a) has only **3** rows, a
degenerate N=3 case: top / middle / bottom maps one-to-one with no joining.

### Gate

**GATE 6b** — [ ] all **35** Multimedia written questions reviewed against NESA's sample
answers · [ ] ledger committed at `data/answer-key/written/reviews/multimedia.json`, coverage
**35/35** · [ ] the 4 one-mark `acceptableAnswers` questions resolved or explicitly deferred
with a reason · [ ] any deliberate divergence recorded as `divergent-accepted` with a note ·
[ ] **`REVIEW_METHOD` states honestly who compared what** — assistant-compared is a legitimate
method to record, inheriting VET's old wording is not

---

## Stage 7 — Release ⬜

1. Browser-verify at mobile width: load Multimedia, open Written Response, render a 15-mark
   Q16, submit an answer, confirm AI marking returns a sane band and no console errors.
2. Confirm the **marks** badge renders. ✅ The `q.topic` blocker is **cleared** — the written
   renderer was changed to `q.category || q.topic` at Maths Advanced Stage 7 (2026-09-01), so
   it no longer blocks here. Note that Stage 1 decided Section III carries **no** `category`,
   so **no topic badge is expected on these six questions** — that is the intended result, not
   a regression; the rest of the subject shows none either.
3. `docs/HISTORY.md` entry; CLAUDE.md §7 row (written **29 → 35**) and §11 roadmap.

**GATE 7** — [ ] full local CI green · [ ] exercised in a browser at mobile width · [ ] AI
marking tested on a 10+ mark response · [ ] docs updated

---

## The rest of the backlog — not part of this runbook

Multimedia is the **second** subject to get review coverage, not the only one that needs it.
**Re-measured 2026-09-06** across every written question in the repo — the previous figures
here predated both the VET Section II merge (72 entries → 34) and the Standard 2 consolidation
(151 → 145), so several were stale:

| Subject | Written | `modelAnswer` | scoring mechanism | `bandDescriptors` | reviewed |
|---|---|---|---|---|---|
| health-movement-science | 40 | 40 | 40 | 40 | 0 |
| mathematics-advanced | 126 | 126 | 126 | 126 | 0 |
| mathematics-standard-2 | **145** | 145 | **145** | **145** | 0 |
| multimedia | 29 | 29 | **29** | **25** | 0 |
| vet-construction | **34** | 34 | 34 | 34 | **34** |
| **Total** | **374** | **374** | **374** | **370** | **34** |

*"Scoring mechanism" counts `keywords` **or** `acceptableAnswers` — the earlier table counted
`keywords` alone and so under-reported Standard 2 and Multimedia, both of which use
`acceptableAnswers` where an exact-match answer is the right mechanism.*

**Remaining to review: 340 of 374.** Porting Section III adds 6 entries (12 parts), taking the
repo to **380 written questions** and Multimedia to **35**.

~~**None of the 369 model answers has ever been reviewed against NESA's sample answers.**~~

**UPDATE 2026-09-01 — VET Construction is done, 34/34 entries (76/76 official parts).** It
went first exactly as the two findings below argued, and both were vindicated: its
`bandDescriptors` were missing data rather than an unreviewed field, and **6 of its written
questions carried a real defect**, every one invisible to CI because the mark was right.

⚠️ **But VET's ledger is NOT the per-question human sign-off it was described as** — corrected
by the owner 2026-09-06. The comparison was **assistant-performed with a human spot-check on a
couple of questions**, and the ledger now records that in `reviewMethod`. **No subject has yet
had the full per-question human review Gate 6b asks for.** Read
`scripts/reviews/vet_construction.py`'s `REVIEW_METHOD` before treating VET as the standard to
copy: copy its *mechanism*, and state this session's own method honestly rather than inheriting
VET's wording. See
`docs/subject-plans/vet-construction-written-review.md` — it is the reference implementation
for this runbook's own Stage 6b, and the mechanism (ledger, fingerprints, CI ramp, triage tool)
now exists rather than being designed. VET was also **COMPLETED** in the same session — its
written bank went 23 → **72** questions and 23/76 → **76/76** official parts, so
**Multimedia's Section III is now the only remaining reverse-coverage gap in the repo**.
Two findings worth carrying into whoever picks up the rest:

- ⚠️ ~~**VET has 0 of 23 `bandDescriptors`**~~ — **resolved 2026-09-01**: all 34 now carry
  NESA-derived band descriptors. The general point stands for whoever picks up the rest —
  distinguish *missing data* from *unreviewed data*, because they need different work.
- ⚠️ **VET is also the subject where the 2026-08-27 MC pass found 6 wrong answers in 75**, and
  **every one carried an `optionExplanations` entry arguing for the wrong answer**. Same
  authoring, same period, and its written prose has never been read back. If the backlog is
  ever prioritised rather than done in full, **VET goes first** — worst data coverage and the
  only subject with a demonstrated authoring-accuracy problem.

Tracked as a §11 roadmap row in CLAUDE.md. Sequencing beyond Multimedia is undecided.
