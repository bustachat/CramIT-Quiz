# VET Construction — Written-Answer Review (Stage 6b)

**Status: COMPLETE, 2026-09-01. Gate passed.** Branch `review/vet-written`, **not merged**.

The first written-answer review ever run in this project. It takes one subject to 100% and
builds the standing mechanism the playbook designed (`docs/porting-playbook.md` §6) so the
remaining 346 questions have a reference to copy.

VET went first for the reason the Multimedia runbook's backlog table records: worst data
coverage in the repo (**0 of 23 `bandDescriptors`**), and the only subject with a
*demonstrated* authoring-accuracy problem — the 2026-08-27 MC pass found **6 wrong answers
in 75**, every one carrying an `optionExplanations` entry arguing for the wrong answer.
Same authoring, same period, prose never read back. That expectation was correct: **6 of
23 written questions carried a real defect.**

---

## Result

| | Before | After |
|---|---|---|
| `modelAnswer` (stored as `answer`) | 23/23 present, **0 reviewed** | 23/23 present, **23 reviewed** |
| `keywords` | **20**/23 | **23**/23 |
| `minKeywords` | **20**/23 | **23**/23 |
| `bandDescriptors` | **0**/23 | **23**/23, from NESA's own criteria |
| Review ledger | did not exist | 23 entries, fingerprinted, **enforced in CI** |

Verdicts: **15 `ok`, 6 `corrected`, 2 `divergent-accepted`.**

No mark, no MC answer and no `omittedParts`/`omittedQuestions` declaration was touched.
CI's mark check is unchanged at 23/23, 0 wrong.

---

## Prerequisite discharged — `bandDescriptors` now have ground truth

Before this session `build_written_key.py` extracted a part's **mark** and NESA's **sample
answer**, but not the **criteria table** the marks are banded against. Band descriptors
could therefore be reviewed for plausibility and nothing else — which is not review.

`scripts/build_written_key.py` now also keeps each criteria row's **text** beside the mark
it already read positionally:

```jsonc
{ "question": 16, "part": "a", "marks": 3,
  "sampleAnswer": "Spirit level, used to test if a surface is level or plumb …",
  "criteria": [
    { "marks": 3, "text": "Correctly names the tool and outlines TWO uses" },
    { "marks": 2, "text": "Correctly outlines TWO uses OR Correctly names the tool AND outlines ONE use" },
    { "marks": 1, "text": "Correctly names the tool OR outlines ONE use" } ] }
```

⚠️ **A criteria row's mark is vertically CENTRED in its cell**, so a row whose wording runs
over three lines carries its mark on the *middle* line. 2024 VET Q16(a) is exactly that: the
`2` sits beside the word `OR`, between the two clauses it applies to. Bracketing a row by
the mark-bearing lines above and below it therefore leaks wording in **both directions** —
the identical bug `build_mapping_grid.py` was fixed for on 2026-08-28, in a different file.
These tables are really ruled, so the extractor reads the boundaries the page itself draws
(`row_rules()` / `band_of()`, lifted from that script for the same reason). A table with no
usable rules degrades to one row per mark-bearing line; it never merges rows silently.

**Inertness verified, which was the condition on the change.** All four committed written
keys regenerate with **every previously existing field byte-identical**; the only diffs are
the added `criteria` arrays and the four `note` strings that now mention them. Machine-checked
by stripping `criteria` and comparing against `HEAD`: **all four inert**, 1 446 criteria rows
added (Maths Advanced 540, Standard 2 510, Multimedia 146, VET 250), **0 parts with no
criteria**. Every paper still reconciles to its front-page total (Maths Adv 90, Std 2 85,
Multimedia 30, VET 65). HMS has no key and is unaffected. The raw diff confirms it: of 591
removed lines, 587 are `sampleAnswer` lines that gained a trailing comma and 4 are the `note`
blocks — nothing else moved.

---

## THE DECISION: how N official bands collapse to the engine's three

**The problem.** `bandDescriptors` is fixed at `{full, partial, minimal}` — both consumers
read exactly those three keys (`index.html` `buildKeywordFeedback()`, `functions/mark-written.js`).
VET's criteria tables carry **1 to 5 rows**:

| Bands | Questions | Shape |
|---|---|---|
| 1 | 3 | 1-mark identify — `[1]` |
| 2 | 7 | `[2,1]` |
| 3 | 7 | `[3,2,1]` |
| 4 | 1 | `[4,3,2,1]` |
| 5 | 5 | `[5,4,3,2,1]`, and the extended responses `[10,8,6,4,2]` / `[15,12,9,6,3]` |

**The rule adopted, applied to all 23 without exception:**

- **`full`** = NESA's **top** row (worth the maximum), **verbatim**
- **`minimal`** = NESA's **bottom** row, **verbatim**
- **`partial`** = every row **between** them, verbatim, joined with `" OR "`

**Why top/middle/bottom and not something keyed to the mark arithmetic.** The engine's tiers
do not map cleanly onto NESA's rows — `buildKeywordFeedback()` picks `full` at ≥70% of the
maximum, `partial` above zero, `minimal` at exactly zero, and NESA prints no row for zero at
all. Any mapping that tried to honour that arithmetic would have to **author** the `minimal`
slot for every question. Top/middle/bottom keeps all three slots as NESA's own sentences,
which is the entire point of building the criteria extractor. It also matches the plain
meaning of the field names, and it lines up with the prompt `mark-written.js` already sends:
its grading guide for a 10-mark question is 10 / 5–9 / 0–4 against NESA's 10 / 8-6-4 / 2 —
top, middle, floor.

**The two degenerate shapes, and how each is handled:**

- **N = 2** (7 questions) — there is no middle row, so **`partial` repeats the bottom row**.
  NESA defines exactly two standards here; repeating an official sentence is truthful where
  inventing a third would not be.
- **N = 1** (3 questions: 2021 16(a), 2022 19(a), 2023 16(a)(i)) — NESA prints one row and the
  mark is all-or-nothing, so `partial` and `minimal` state its **non-attainment**
  ("Does not correctly identify a chisel. The mark is awarded in full or not at all."). ⚠️
  **This is the only authored, non-NESA descriptor text in the subject**, it is flagged on
  each of the three ledger entries, and it is low-consequence: all three questions score
  through `acceptableAnswers`, where the engine reads only `full` and `minimal`, so the
  authored `partial` is seen by the AI marker alone.

**One presentation liberty, and its limit.** NESA prints several criteria as separate
bulleted lines inside one cell, which the extractor faithfully joins with spaces into a
run-on ("…construction industry Provides a precise logical and cohesive response Uses…").
Those are punctuated to "…industry; provides a precise…". **No word is added, removed or
reordered**, and every substitution is printed at build time — the discipline
`build_mapping_grid.py`'s `SOURCE_TYPOS` table uses. Nine substitutions across two questions
(2025 20(b), 2025 21).

⚠️ **Known cosmetic consequence, accepted deliberately.** For the 4- and 5-band questions
`partial` is three official rows joined by `" OR "`, which reads as a wall of text in the
offline feedback box (seen in the 2025 20(b) screenshot). It is
NESA's exact standard and it is honest; shortening it would mean choosing which of NESA's
bands to discard. If it is ever changed, change it as a rendering decision in `index.html`,
not by trimming the data.

---

## The six corrections

Every one was invisible to CI: the mark was right in all six cases, so
`check_written_key.cjs` passed throughout.

**1. 2023 Q19(b)(i) — the model answer's headline result was wrong (2.61 m³ vs NESA's 2.99 m³).**
The worst finding. The bank computed the footing volume from the shed's **outer perimeter**
(2 × (8.5 + 6) = 29 m → 2.61 m³), which **omits the centre beam entirely** and double-counts
the four corners. The stimulus is captioned, in NESA's own words, *"the hidden detail of the
edge and centre beams"*, and the drawing plainly shows the centre beam. The bank then
explained the gap away as *"corners (overlap) giving approximately 2.61–2.99 m³ depending on
method"* — a fabricated reconciliation of its own error. NESA's sample gives 2.99 m³ by two
independent routes. The stem compounded it, describing *"300mm × 300mm **perimeter** beam
footings"*; it is now the paper's own wording. Answer rewritten to NESA's method, keeping
2.61 named as the common error rather than hidden. Keywords `29` and `2.61` **removed** —
they credited the wrong method.

**2. 2022 Q19(a) — both stimulus band labels were fabricated.** The model answer said 3700 kg
falls in a *"3001–4000 kg"* range and 54 km in a *"51–60 km"* range. The table (crop opened
and read) is in **tonnes** — 0–2.99 / 3.00–4.99 / 5.00–6.99 / 7.00–8.99 — with distance
columns 1–30 / 31–50 / **51–70**. Neither quoted band exists on the page. A student following
the prose looks for rows that are not there, and the **kg → tonne conversion the question
actually tests** was absent from the answer entirely. The `$450` result was right, so nothing
reported it — **the same failure class as Multimedia 2022 Q2** (CLAUDE.md §10 rule 7), this
time in the model answer instead of the options.

**3. 2023 Q16(a)(i) — `acceptableAnswers` omitted one of NESA's own accepted answers.**
NESA lists *"Sliding saw • Compound saw • Mitre saw • Cut off saw"*; the bank had
`['drop saw','mitre','compound','cut-off','chop saw']`. A student writing **"sliding saw"** —
NESA's first listed alternative — was marked **incorrect**. Added. `chop saw` is kept: not on
NESA's list, but a genuine synonym.

**4. 2022 Q17(c) — the stem gave away one of the two marks.** It read *"Identify the meaning
of the symbols shown (RWT and **tree symbol**)"*. The paper says only *"Identify each of the
architectural symbols shown."* — naming the tree hands the student half the question.
Restored. The model answer also attributed removal to *"(the specific marking on the plan)"*,
which says nothing; the actual indicator, visible in the committed crop, is the **broken
(dashed) outline** against the continuous one used for RWT. Both identifications were correct
and are unchanged.

**5. 2025 Q18(b) — the stem gave away the third of three marks.** It named *"the **horizontal
sliding window** symbol shown"*, which is the answer. The paper says *"Identify the meaning of
the following symbols or abbreviations that are found on construction drawings."* Restored.
The three meanings match NESA and the model answer's description of the two-arrow symbol
matches the crop.

**6. 2021 Q16(a) — no keywords at all** (with 2022 19(a) and 2023 16(a)(i)). All three scored
through `acceptableAnswers`, so `validate_subjects.cjs`'s "no scoring mechanism" warning
never fired and the offline path worked — but `mark-written.js` was being sent an **empty
concept list** (`KEY CONCEPTS EXPECTED: See question context`). Filled from NESA's own
alternatives. The offline path is unchanged, because `acceptableAnswers` takes priority over
`keywords` in `buildKeywordFeedback()` — verified in the browser, not assumed.

### Two `divergent-accepted`

**2024 Q19(a) and Q19(b).** NESA's sample answers extract as mangled equation layout
(`!3! 4! + = 5 4 + 6 + 8 + 3 + 5 = 26 m`; `pr2 12 ´ ´ ´ depth`), so the bank's worked prose
necessarily reads nothing like them. Compared **numerically** instead — hypotenuse 5 and
perimeter 26 m; slab 7.2 m³, hole 0.471 m³, net 6.73 m³ — all agree. This is the standing
Maths exception appearing in a VET calculation question, and it is noted rather than passed
silently.

---

## The standing mechanism (this is the part that outlives the session)

**Ledger** — `data/answer-key/written/reviews/vet-construction.json`, beside the ground truth
it cites. A sidecar, not fields on the question, because `subjects/*.json` is downloaded by
every student. Built by **`scripts/build_review_ledger.py`** from a hand-typed verdict table
at **`scripts/reviews/{subject_id}.py`**; the script computes fingerprints and shape and
**decides nothing**. It refuses to write if the table misses a bank question, names one that
does not exist, uses an unknown verdict, or gives a non-`ok` verdict without a note.

**Fingerprint** — sha256 of NESA's sample answer for that entry, whitespace-normalised, **as
it read at review time**. Regenerate the key and any part whose official text moved has its
review **automatically voided** rather than quietly stale. Normalised so an irrelevant
re-wrap of the PDF text layer does not void a review, while any change of *words* does.

**Checker ramp** — `check_written_key.cjs` now prints review coverage per subject, and
**enforces it for any subject that has committed a ledger**:

```
OK    vet-construction: 23 questions checked, 0 wrong, 0 unverifiable
        coverage: 23/76 official parts claimed …
        review:   23/23 reviewed against NESA — 6 corrected, 2 divergent-accepted, 15 ok
OK    multimedia: …
        review:   0/29 model answers reviewed against NESA — no ledger (reported, not enforced)
```

Opting in by *committing a ledger* is what makes the ramp work: the four subjects carrying
historical debt report 0% and stay green, while VET can no longer regress — a new or edited
VET written question fails CI until it is reviewed. **Proved, not assumed:** corrupting one
fingerprint byte produces `1 STALE`, the right message, and **exit code 1**; restoring it
returns exit 0.

**Triage tool** — `scripts/review_triage.py <subject-id>` prints each bank question beside
NESA's mark, sample answer and criteria rows (so no marking guideline is ever re-read), and
`--triage` orders the queue by keyword-absent-from-answer, keyword-absent-from-sample,
substantive-term overlap and length-per-mark. ⚠️ **Ordering only, never a verdict** — all 23
were read regardless of position. Worth noting how weak the signals were here: the queue's
**top** entry (2024 19(a), overlap 0.00) turned out `divergent-accepted` on mangled equation
text, while **2023 19(b)(i)**, the session's worst defect, sat at position 2 and **2022 17(c)
and 2025 18(b) sat at overlap 1.00 and 1.00 — the very bottom**. Two of six defects were
invisible to every mechanical signal, because a stem that gives the answer away and an
answer that misdescribes a picture both score as *perfect agreement*. Generalised from the
VET-only version so the next subject can use it directly.

**Apply script** — `scripts/_vet_review_apply.py`, kept so the review is reproducible. It
regenerates all 23 `bandDescriptors` from the committed criteria on every run, so they cannot
drift from the key by hand.

---

## Schema drift — checked before touching anything, and the brief's premise corrected

VET stores its model answer as **`answer`**, not `modelAnswer`. All three fields are
**load-bearing** and none was canonicalised:

| Field | Where it is read | Consequence of renaming it |
|---|---|---|
| `answer` | `index.html:1823` and `:2227`, via `q.answer \|\| q.modelAnswer \|\| q.sampleAnswer`; `validate_subjects.cjs:74` | none immediately (the chain absorbs it) — but it is the field **shown directly to the student** |
| `acceptableAnswers` | `index.html:1994–2006` — a complete all-or-nothing scoring branch that **takes priority over `keywords`**; the AI-marking gate at `:2121`; `validate_subjects.cjs:73` | 1-mark questions silently fall through to keyword-grid scoring |
| `minKeywords` | `index.html:2012` — the threshold below which the grid caps at ⌊max/2⌋; defaults to `ceil(keywords.length / 2)` | scoring shifts on every question that has one |

⚠️ **The brief's premise that `acceptableAnswers` and `minKeywords` are fields "no other
subject has" is wrong, and worth correcting because it would misdirect the next reviewer.**
Measured across all five subject files:

| Subject | written | `answer` | `acceptableAnswers` | `minKeywords` |
|---|---|---|---|---|
| health-movement-science | 40 | 40 | 0 | 0 |
| mathematics-advanced | 126 | 126 | **6** | **126** |
| mathematics-standard-2 | 151 | 151 | **47** | **111** |
| multimedia | 29 | 29 | **4** | **25** |
| vet-construction | 23 | 23 | **3** | **23** |

Every subject except HMS uses both, and **no subject anywhere uses `modelAnswer`** — `answer`
is the de facto canonical name, not a VET deviation. The real outlier is **HMS**, which uses
`topic`/`maxMark` instead of `qNum`/`marks` and carries no `year` or `section`. Nothing was
changed on that basis; recorded so the playbook's canonical-names section can be corrected
deliberately rather than as a side-effect here.

---

## Verification performed

Full local CI, all green:

- `node scripts/validate_subjects.cjs` — `MC=706 Written=369 imageRefs=311 missingImages=0`, `Issues: 0`
- `node scripts/check_answer_key.cjs` — **285 answers, 0 wrong, 0 unverifiable**
- `node scripts/check_written_key.cjs` — **329 written questions, 0 wrong, 0 unverifiable**; VET review **23/23**
- `node --check` on all five Cloudflare function files
- `npm test` — **67 pass, 0 fail**

Browser, at a **430 px** viewport against the local preview:

- All **23** VET written questions rendered one by one: `body.scrollWidth` never exceeds 430
  and **no `.question-area` overflows** (the per-question check from the Maths Advanced 2021
  session — page-level measurement misses it).
- All **13** stimulus images load (`naturalWidth > 0`) at 388 px. ⚠️ They must be forced to
  `loading='eager'` and awaited first, or every one reads 0 — the known lazy-load artefact.
- **2025 Q20(b), 10 marks:** marks badge renders `10 marks`; a deliberately partial answer
  scores **4/10, 36% matched**, and the feedback text is now **NESA's own middle band**
  instead of the old generic *"Good — solid understanding…"*. The model answer renders in
  full below it. Screenshot taken.
- All five corrected questions re-rendered and read: the restored stems are live, the
  `acceptableAnswers` branch still takes priority on the three 1-mark questions (2022 19(a)
  showed its authored all-or-nothing `minimal` text, not a keyword grid), and 2023 19(b)(i)
  scores 5/5 with `full` = *"Calculates the cubic metres of concrete required correctly"*.

**AI marking — what was and was not checked.** The client payload was captured live from
`tryAiMarking()` with `fetch` stubbed: it now carries the three real NESA descriptors where
it previously sent `bandDescriptors: null`. That payload was then run through
`functions/mark-written.js`'s **own prompt source, sliced from the file rather than retyped**,
confirming the band block is well formed for a 10-mark question and that no slot interpolates
`undefined`. ⚠️ **The live Claude call was NOT made** — no `ANTHROPIC_API_KEY` is available in
this environment (only `ANTHROPIC_BASE_URL`), and the function additionally requires a
verified Supabase JWT and an active subscription row. So the *marking behaviour* of a 10-mark
question is verified as far as the prompt boundary and no further. Whoever next has a key
should submit one 10-mark and one 15-mark VET answer against the deployed function and
confirm `marksAwarded` lands in the band the rubric implies.

---

## Findings recorded, deliberately NOT acted on

1. ⚠️ **Ten VET 2025 stems end with a literal `(N marks)`**, duplicating the marks badge the
   renderer already draws — visible in the 2025 20(b) screenshot as *"…workplace examples.
   (10 marks)"* under a `10 marks` pill. **Mathematics Standard 2 has the same thing on 90
   stems.** Fixing VET's ten alone would leave the repo *less* consistent, and it is a
   rendering-cosmetic issue rather than a written-answer-review finding, so it is left for a
   single pass across both subjects.
2. ⚠️ **`parse_paper()` swallows the Mapping Grid into the last question of every paper.**
   Because the final `Question N` header has no successor, its sample block runs to the end of
   the document — so VET 2025 Q21's committed `sampleAnswer` also contains the whole mapping
   grid. **Pre-existing, not introduced here**, harmless to the mark check, and noted on that
   ledger entry because it means the fingerprint covers more text than the sample alone.
   Fixing it would change committed `sampleAnswer` bytes in every subject and would have
   broken this session's inertness guarantee, so it is left for a deliberate pass.
3. **Loose keywords.** `pi` (2024 19(b)) is two characters, so `keywordHit()` fires on any
   student word beginning "pi" — "pipe" scores it. Numeric keywords like `5` match a
   substring of "0.15". Left as authored and noted; tightening `keywordHit()` is an engine
   change, not a data one.
4. **VET's written bank still covers 23 of 76 official parts** (65 marks/paper). That gap is
   the pre-existing, documented one and is out of scope here — this review covers what is in
   the bank, not what is missing from it.

---

## GATE 6b — passed

- [x] Every written question read against NESA's sample answer **and** criteria rows — 23/23
- [x] All three artefacts reviewed: `modelAnswer`, `keywords`, `bandDescriptors`
- [x] `bandDescriptors` present on 23/23, derived from NESA's criteria, collapse rule recorded
- [x] `keywords`/`minKeywords` present on 23/23
- [x] Review committed to the ledger with sample-answer fingerprints
- [x] `divergent-accepted` used with a note where NESA's text is unusable — never a silent pass
- [x] Checker reports coverage for all subjects and **enforces** it for VET; staleness proved to exit 1
- [x] Full local CI green; browser-verified at 430 px
- [x] No mark, MC answer or omission declaration altered
- [ ] Live AI marking on a 10+ mark question — **not verifiable in this environment**, see above

**Next.** Multimedia Stage 6b (`docs/subject-plans/multimedia-section-iii.md`) is the
scheduled follow-up; the mechanism and the tooling are now in place for it. Remaining backlog:
**346 of 369** written answers unreviewed — Maths Advanced 126, Standard 2 151, Multimedia 29,
HMS 40. Standard 2 also still has **40 missing `keywords`** and Multimedia **4**.
