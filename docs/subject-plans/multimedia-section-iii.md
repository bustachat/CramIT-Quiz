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
| 6 Ground truth | ➡️ already done — folded into Stage 4's gate | — |
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
   it; do not assume. `mark-written.js` marks against `keywords` + `modelAnswer`, and the
   longest thing it has ever handled is a 5-mark answer. **This is the one genuine feasibility
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

## Stage 6 — Ground truth ➡️ ALREADY DONE

`data/answer-key/written/multimedia.json` was built at Maths Advanced Stage 6 (2026-08-31) and
already holds all 12 Section III parts with official marks and sample answers. **Nothing to
build**; the stage collapses into Stage 4's gate.

The one thing Stage 6 cannot do here: NESA's sample answers are prose and are **never
enforced**, only committed for review. Whoever ports these is the *only* check on whether the
authored `modelAnswer` reflects NESA's — read them side by side.

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

## Known adjacent gap — deliberately NOT part of this runbook

**Multimedia and VET written model answers have never been checked against NESA's committed
sample answers.** Only the *mark* is CI-enforced; the prose is not, and cannot be. That is
29 + 23 = **52 existing questions** whose authored model answers no session has ever reviewed.

Weight it against this: the 2026-08-27 MC pass found the same subject pair's authored
`optionExplanations` arguing for the wrong answer on **all six** defective VET questions — the
same authoring, on the same subjects, in the same period. Ground truth for the review already
sits in `data/answer-key/written/`, so the work is reading, not extraction.

Raised 2026-09-01. A separate decision, deliberately not folded into this port.
