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
| **1 Survey** | ⬜ **next** | 1 session |
| 2 Syllabus grounding (Section III scope only) | ⬜ | 1 session |
| 4 Port | ⬜ | 1–2 sessions |
| 6 Ground truth — **marks** | ➡️ already done — folded into Stage 4's gate | — |
| **6b Written-answer review** | ⬜ **NEW** — covers Section III's 12 new parts **and** Multimedia's existing 29 | 1 session |
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
| Ground truth | ✅ **Already committed.** `data/answer-key/written/multimedia.json` holds all 12 parts' official marks **and NESA's sample answers**, from Stage 6 (2026-08-31). Nothing to extract |
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

1. **One bank entry per question, or one per part?** The project rule (Maths Advanced Stage 4,
   and `check_written_key.cjs`'s prefix-sum join) is **one entry per NESA question**, and
   Multimedia's existing Q11–Q15 already store it that way. But a merged 15-mark entry is far
   larger than anything else in this bank, and (a) and (b) are answered in separate writing
   booklets in four of the six years. **Both shapes reconcile under the prefix-sum join**, so
   this is a UX call, not a correctness one. Record which and why.
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

**GATE 1** — [ ] all 12 parts classified · [ ] bank shape decided and recorded · [ ] extended-
response marking risk resolved or escalated · [ ] asset count confirmed by reading all six pages

---

## Stage 2 — Syllabus grounding (Section III scope only) ⬜

⚠️ **CLAUDE.md §10's mandatory syllabus rule applies, and this is the case it exists for.** The
seven Study Mode topics were re-grounded in the real NESA syllabus on 2026-07-29 precisely
because a mapping-grid-derived list had been wrong twice. Section III's scope is the Industrial
Technology syllabus's **industry-study / business strand**, which no session has yet read.

Do **not** derive the scope from these six papers. Six years of questions is exam history, not
syllabus scope — VET is the standing counter-example, with 80 rows of "Working in the industry"
content including material never once examined.

Ask the owner before downloading the syllabus, and save it into
`NESA Exams Folder/Industrial Technology - Multimedia/` under the same copyright treatment as
the papers.

**GATE 2** — [ ] primary syllabus document located and read · [ ] Section III scope stated from
it, not from the papers · [ ] stated plainly whether the list is primary-sourced

---

## Stage 4 — Port ⬜

Twelve parts, authored against NESA's committed sample answers in
`data/answer-key/written/multimedia.json`. Ground truth already exists, so unlike a normal
Stage 4 the marks **cannot go wrong without CI catching it immediately**.

- Author `modelAnswer` and `keywords` per part, using NESA's sample answer as the source.
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
| Section III's new parts | **12** — reviewed as they are authored in Stage 4, so they land reviewed |
| Multimedia's existing written bank | **29** — never reviewed, ported before the ledger existed |
| **Total** | **41**, the whole subject |

Do the existing 29 in the same session. The reviewer is already holding the marking
guidelines' sample answers and the subject's conventions in their head; splitting it wastes
that context, and it takes Multimedia to 100% review coverage in one pass — the first subject
to get there, and the reference the others are measured against.

### Multimedia's measured artefact coverage — 2026-09-01

| Field | Present | Missing |
|---|---|---|
| `modelAnswer` | 29 / 29 | — |
| `keywords` | **25 / 29** | 4 |
| `bandDescriptors` | **25 / 29** | 4 |

⚠️ **Four questions have neither `keywords` nor `bandDescriptors`.** Those are AI-marked
against a generic 0/50%/100% fallback rubric with no key concepts at all. Identify them and
decide whether to author both — this is a real marking-quality defect, not a tidiness issue,
and it is invisible to every check in the repo today.

⚠️ **Section III raises the stakes on `bandDescriptors` specifically.** A 10–12 mark
band-marked extended response is exactly where a generic rubric produces a meaningless mark.
Whatever Stage 1 concludes about `mark-written.js` handling long responses, these 12 parts
need real band descriptors, not the fallback.

⚠️ **`bandDescriptors` have no ground truth.** `build_written_key.py` extracts the mark and
the sample answer but **not the criteria table** they are banded against, so band descriptors
can only be reviewed for plausibility. Extending the extractor to capture the criteria rows is
the prerequisite (playbook §6) — worth doing once, before this session, since Section III's
criteria are the most band-dependent content in the subject.

### Gate

**GATE 6b** — [ ] all 41 Multimedia written questions reviewed against NESA's sample answers ·
[ ] ledger committed at `data/answer-key/written/reviews/multimedia.json`, coverage 41/41 ·
[ ] the 4 questions missing `keywords`/`bandDescriptors` resolved or explicitly deferred with a
reason · [ ] any deliberate divergence recorded as `divergent-accepted` with a note

---

## Stage 7 — Release ⬜

1. Browser-verify at mobile width: load Multimedia, open Written Response, render a 15-mark
   Q16, submit an answer, confirm AI marking returns a sane band and no console errors.
2. Confirm the topic/marks badge renders. The written renderer reads `q.topic` rather than
   `category` (Stage 3 defect, fixed during Maths Advanced Stage 7) — **if that fix has not
   landed, it blocks here too.**
3. `docs/HISTORY.md` entry; CLAUDE.md §7 row (written 29 → 41) and §11 roadmap.

**GATE 7** — [ ] full local CI green · [ ] exercised in a browser at mobile width · [ ] AI
marking tested on a 10+ mark response · [ ] docs updated

---

## The rest of the backlog — not part of this runbook

Multimedia is the **first** subject to get review coverage, not the only one that needs it.
Measured 2026-09-01, across every written question in the repo:

| Subject | Written | `modelAnswer` | `keywords` | `bandDescriptors` |
|---|---|---|---|---|
| health-movement-science | 40 | 40 | 40 | 40 |
| mathematics-advanced | 126 | 126 | 126 | 126 |
| mathematics-standard-2 | 151 | 151 | **111** | 151 |
| multimedia | 29 | 29 | **25** | **25** |
| vet-construction | 23 | 23 | **20** | **0** |
| **Total** | **369** | 369 | **322** | **342** |

**None of the 369 model answers has ever been reviewed against NESA's sample answers.**

Two findings worth carrying into whoever picks up the rest:

- ⚠️ **VET has 0 of 23 `bandDescriptors`** — every VET written question is AI-marked against
  the generic fallback rubric. That is the single worst cell in the table and it is not a
  review problem, it is missing data.
- ⚠️ **VET is also the subject where the 2026-08-27 MC pass found 6 wrong answers in 75**, and
  **every one carried an `optionExplanations` entry arguing for the wrong answer**. Same
  authoring, same period, and its written prose has never been read back. If the backlog is
  ever prioritised rather than done in full, **VET goes first** — worst data coverage and the
  only subject with a demonstrated authoring-accuracy problem.

Tracked as a §11 roadmap row in CLAUDE.md. Sequencing beyond Multimedia is undecided.
