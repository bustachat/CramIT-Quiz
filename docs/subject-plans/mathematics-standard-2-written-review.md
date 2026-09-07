# Mathematics Standard 2 — Written-Answer Review (Stage 6b)

> ⚠️ **Provenance, first.** These verdicts were reached by an **assistant session**. The
> comparisons against NESA's committed sample answers and criteria rows were done by the
> assistant; the eight changed stems were additionally checked against the exam papers.
> **No human has signed off on any question.** The ledger's own `reviewMethod` field says
> so, and `check_written_key.cjs` prints it on every run. Read "reviewed" below as
> "assistant-compared", never as a human sign-off.

**Status: COMPLETE, 2026-09-07. All 145 questions reviewed; the ledger is committed and
CI now ENFORCES this subject.**

| | Before | After |
|---|---|---|
| Written questions in bank | 145 | 145 (unchanged) |
| Official parts covered | 235/235 | 235/235 (unchanged) |
| Reviewed against NESA | **0** | **145/145** |
| Verdicts | — | **90 ok, 22 corrected, 33 divergent-accepted** |

This is the **third** subject with a review ledger, after VET Construction (34) and
Multimedia (35), and by far the largest. Remaining backlog across the repo: **166** —
Mathematics Advanced 126, and HMS 40 which **cannot** be reviewed this way at all until an
answer key exists after the 2026 HSC.

---

## What the review found

**22 defects in 145 questions (15%)** — a rate in line with VET (6/34) and Multimedia
(9/35). **Every one was invisible to CI, because every mark was right.** They fall into
five classes, three of which had never been seen in this project before.

### Class 1 — `$1`..`$9` eaten by a JavaScript `String.replace()` (2 questions)

**The single most damaging find, and it is a whole class rather than a one-off.** In
JavaScript, `String.prototype.replace()` treats `$1`–`$9` in the **replacement string** as
capture-group references. Some historical authoring pass ran text through such a replace,
and every `$` followed by a digit vanished.

- **2020 Q20** — the *stem* read *"Wally had a taxable income of **22 680**. During the
  year, he paid **000** per month in PAYG tax."* The paper (p16) reads `$122 680` and
  `$3000`. **The question was unanswerable as printed.**
- **2021 Q40** — the *model answer* read *"Annuity: **000** per year … FV = 1000 × 8.2132
  = **213.20** … = **419.81**"* against NESA's `$8213.20` and `$8419.81`. The student was
  shown arithmetic that does not work.

⚠️ **How to find these.** The signature is a number that is a strict **suffix** of the same
number elsewhere in the question, with its `$` also gone — plus, as a cheap screen, any
number literally beginning with `0` (impossible in written maths outside a bearing or a
decimal). Swept across all five subject files: **exactly these two**, both in Standard 2.

### Class 2 — scoring data that pays full marks for a wrong answer (4 questions)

Found by a check no previous session had run: **score every question against fluent but
content-free student answers** and flag anything that earns ≥ 50% of the mark.

- **2020 Q26** — the critical path `C - D - E - F - H - I` had been split into six
  **single-letter keywords**. `keywordHit()` does a plain substring test, so `c`, `e`, `f`
  and `i` fire on almost any English sentence. **Measured in the real engine: a
  content-free answer scored 1/1 on part (a) and 2/2 on part (b).** After the fix, 0/5;
  a correct answer still scores 5/5.
- **2021 Q27(a)** — `acceptableAnswers` was `['4.38', '$4.38', '5']`. The bare `'5'` is
  **part (b)'s** answer, and `scoreOne()` short-circuits on `acceptableAnswers` with a
  plain `includes()`, so **any answer containing the digit 5 scored 2/2**. Now 0/4 for
  *"The answer is 5"*, 4/4 for the correct one.
- **2021 Q28(b)** — a 1-mark part whose only keyword was `increase`. `keywordHit`'s
  `kw.startsWith(word)` branch means the ordinary word **"in"** credits it, so a
  content-free answer scored **1/1**. Now 0/3 and 3/3.
- **2021 Q36(b)** — a **regex** was stored as a keyword: `'a.*c.*d.*e.*g.*j.*k'`.
  `keywordHit()` never evaluates regexes; it credited the string via the bare letter `a`,
  so it fired on almost anything while never matching as intended.

### Class 3 — stems that contradict the paper (8 questions)

Every one confirmed by opening the actual exam paper, which CLAUDE.md's exam-citation rule
requires. **All eight were wrong.**

| Question | Bank said | Paper says |
|---|---|---|
| 2020 Q20 | `22 680`, `000 per month` | `$122 680`, `$3000 per month` |
| 2021 Q23(b) | *"Queentown to **Fernville** along the minimum spanning tree"* | *"Queentown to **Underwood** using the **fastest route**"* |
| 2021 Q33 | `y = 29.2 − 0.00404x`, gradient `−0.00404` | `y = 29.2 − 0.011x`, gradient `−0.011` |
| 2023 Q21 | (a) 1, (b) **2**, (c) 1, (d) **1** | (a) 1, (b) **1**, (c) 1, (d) **2** |
| 2023 Q32 | (a) **3**, (b) **1** | (a) **2**, (b) **2** |
| 2024 Q19(b) | *"scored 5 for the assignment."* | *"scored 5 for the assignment **and 12 on the test**"* |
| 2024 Q34 | *"square **centimetres**, correct to the nearest whole number"* | *"square **metres** correct to 1 decimal place"* |
| 2024 Q35 | sd **12**; (a) *"less than 46"*; (c) *"top **5%**"* | sd **15**; (a) *"between 58 and 70"*; (c) *"top **10%**"* |
| 2025 Q26 | (b) *"What percentage…"*, (c) *"mass of plastic"* | (b) *"approximate **area** of the curved surface"*, (c) *"**percentage error** of the measurement of 10.2 cm"* |

⚠️ **2024 Q35 is the worst of these** — three errors in one question, and in every case the
model answer was already working NESA's version, so stem and answer contradicted each
other on all three parts. **2024 Q19(b) was simply unanswerable**: the student's test mark
was missing from the stem, yet NESA's own sample answer depends on it.

⚠️ **The mark-label errors (2023 Q21, 2023 Q32) are structurally invisible to CI.** The
per-part labels live in the combined `q` string; `check_written_key.cjs` joins on the
question's own `marks`, which still totalled correctly. A sweep comparing the sequence of
`(N marks)` labels in `q` against `parts[].marks` found exactly these two, repo-wide.

### Class 4 — authoring scratch-work shown to the student (6 questions)

`index.html` renders `answer` **directly to the student**. Six model answers still carried
the author's working-out, including notes to itself about the marking guidelines:

- **2024 Q41** — *"PV₁ = $2000 × 151.036 = $302 072 **Wait — let me re-read the MG. MG
  says:** …"*
- **2023 Q27(b)** — *"… cos θ = 7.5/40… **no.** … XC = √(XP² + CP²) should be 40… **wait
  Actually:** …"*
- **2023 Q26(a)** — two abandoned attempts plus *"**From MG:** Area of path = …"*
- **2024 Q34** — abandoned working with the wrong cylinder length, plus *"**Actual MG
  calculation:**"*
- **2025 Q26(b)** — *"**Using MG:**"* and a `480 cm∂...` typo
- **2024 Q36(b)**, **2024 Q39(c)**, **2025 Q35** — `Actually:` markers and
  self-cancelling parentheticals

Found by a regex sweep for `wait | Actually | no\. | From MG | \?\? | TODO` over every
student-facing `answer`. ⚠️ It also fires on legitimate prose (*"he needed to **wait** 57
minutes"*, *"the message has **actually** been received"*), so the hits must be read, not
batch-applied — VET and Mathematics Advanced produced 18 such false positives between them
and **none of theirs was a defect**.

### Class 5 — wrong results in the model answer (2 questions)

The class VET 2023 19(b)(i) established: the mark is right, so nothing reports it, and the
student is taught the wrong number.

- **2022 Q30** — gave Option 1 as **$45 093.59** and the difference as **$37.29**; NESA
  gives **$45 097.17** and **$40.87**, and 40 000 × (1.001)¹²⁰ confirms NESA. **The
  question's own `acceptableAnswers` already held `'45097.17'`, so the bank disagreed with
  itself.**
- **2021 Q23(a)** — the minimum-spanning-tree edge list was **fabricated**: it named
  *"Kingsville-Underwood=20"* where the paper's K–U edge is **65**, its listed edges summed
  to **95** against the stated 160, and it ended in a literal `+...` on screen. Recomputed
  from the committed crop (10 + 15 + 20 + 20 + 25 + 30 + 40), which reproduces NESA's 160
  exactly.
- **2025 Q19** — **the worst single question in the subject.** Wrong prerequisites (*E: B*
  and *F: A, C* against NESA's *E: C, D* and *F: E*), wrong critical path (*B–F–H = 16
  days* against NESA's *BDEFH = 26*), and a part (c) that **contradicted itself**: it
  opened *"No — increasing A by 2 days does not affect the critical path"* and closed
  *"**Corrected:** … This **DOES** affect the critical path."* NESA says *"No, as the float
  time for activity A is 3."*

---

## The `divergent-accepted` 33

Maths sample answers extract as mangled equation layout, so a Maths model answer *should*
read nothing like NESA's — the standing exception in `docs/porting-playbook.md` §6. Applied
where the committed sample is genuinely unusable as prose: empty (2025 Q33), near-empty
(2025 Q32 is the single character `4`; 2025 Q37 is `60° 3 9 c`), or carrying the
`_=` / `#` / `^` MathType damage (*"PAYG tax = _= 3000 _$36 _000 × 12"*). Each was compared
**numerically** instead, and each entry's note quotes the actual damaged text as evidence.
Band descriptors were still checked against the **criteria rows**, which extract cleanly.

Deliberately **not** used for samples that are merely short but readable — 2023 Q16
(*"120 bpm 10:30 am"*) and 2024 Q16 (*"TYWH YWHMG is 89 km"*) are plain `ok`. The
distinction matters if the verdict is to mean anything.

---

## Method notes for the next subject

**1. Triage ordered the queue and decided nothing — and the numbers say why.** The queue's
top entries were calculation questions whose NESA sample is mangled (benign
`divergent-accepted`), while **2024 Q35's three wrong stem values, 2025 Q19's wrong
critical path and both mark-label errors sat well down the list**. A stem that contradicts
the paper scores as perfect agreement with the sample answer, because triage never reads
the paper. Read every question.

**2. Decide with the engine, never with a mirror of it.** `scoring.js` is `require()`-able
from Node, and `scripts/review_checks.cjs` (new, this session) drives the real file through
`node:vm`. Triage's plain-substring "keyword absent from modelAnswer" signal disagreed with
the engine constantly — the engine's 4-character stem rule and `kw.startsWith(word)` branch
credit far more than a substring test does.

**3. Run three mechanical checks before committing any ledger.** The first two are the
playbook's; **the third is new and it earned its keep twice.**

| Check | Result here |
|---|---|
| (a) every question/part scores **full** from its own model answer | 145/145 clean (was already clean — earlier sessions fixed this repo-wide) |
| (b) `round(minKeywords / n × marks)` is never **0** | 145/145 clean (likewise) |
| (c) **a fluent, content-free answer must score < 50%** — prose only, **no digits** | **caught 2020 Q26 and 2021 Q28, where a wrong answer scored FULL marks.** ⚠️ Put digits in the decoy and it reports **167 of 227 rows** and is useless — see finding 1 |

⚠️ Check (c) needs interpreting, not just running. Most of its hits are the documented
`kw.startsWith(word)` engine looseness paying 1 mark out of many on a long list — inherent
to a proportional grid, not a content defect. **The content defects are the ones where the
cause is in the data**: a single-letter keyword, a leaked short `acceptableAnswers` entry,
or a regex stored as a keyword. Five partial-credit hits remain and are recorded below as
engine-level, not fixed.

**4. Fix the measuring instrument before trusting it.** `review_triage.py` stripped HTML
with `/<[^>]+>/g`, which is **not** how a browser parses: the HTML parser only opens a tag
when `<` is followed by a letter, `/`, `!` or `?`, so `P(0 < Z < 0.3)` is literal text on
screen. The regex ate it and made 2021 Q38's model answer look damaged when it is
perfectly fine — the same error that produced a false finding on Mathematics Advanced 2024
Q30 (`docs/HISTORY.md` 2026-09-07). Fixed in the tool; it now strips the way a browser does.

**5. Probe scoring changes, don't reason about them.** 2025 Q19's keyword list was chosen by
running four candidate lists against a correct answer, a differently-phrased correct
answer, the old wrong answer and a decoy **in the running engine**. The list that looked
best on paper (`['26','float time','prerequisite','unchanged']`) under-marked a correct
answer at 4/5. The one adopted keeps both correct phrasings at 5/5 while dropping the wrong
answer from 4/5 to 3/5.

---

## Verification performed

Full local CI, all green:

- `node scripts/validate_subjects.cjs` — `MC=706 Written=380 imageRefs=337 missingImages=0`, `Issues: 0`
- `node scripts/check_answer_key.cjs` — **285 answers, 0 wrong, 0 unverifiable**
- `node scripts/check_written_key.cjs` — **340 written questions, 0 wrong**; Standard 2
  coverage **235/235** and review **145/145**
- `node --check` on all five Cloudflare function files
- `npm test` — **112 pass, 0 fail**

**Staleness guarantee tested, not assumed.** Corrupting one entry's fingerprints makes
`check_written_key.cjs` report `1 STALE` for that exact question and **exit 1**; restoring
it returns exit 0.

**Blast radius machine-checked against `HEAD`.** Exactly **22 of 145** questions changed,
and only `answer` / `keywords` / `minKeywords` / `acceptableAnswers` / `bandDescriptors` /
`q` / `stem` / `parts` moved. `mcQuestions`, `studyNotes`, `tips` and every other top-level
key are **byte-identical**; no `marks`, `qNum`, `section`, `category`, `image`,
`omittedParts` or part label/mark was touched.

**Browser, against the local preview:**

- **Six widths — 320, 375, 430, 768, 1400, 1920** — driving the real renderer over all
  **145** questions and opening **every part of every multi-part question** (148 part-opens
  per width): **0 `.question-area` overflows, 0 occurrences of `undefined`, 0 missing marks
  badges, 0 images wider than their container, 0 render errors**, and `body.scrollWidth`
  never exceeding the viewport.
- **All 145 score full from their own model answers in the page's own engine** — 227 part
  rows, **0 generic band fallbacks, 0 `undefined`** in band text.
- **All 75 distinct images load** (forced `loading='eager'` first — lazy images read
  `naturalWidth` 0 otherwise).
- **Real end-to-end flows**, typed into the real handlers, proving the fixes move marks:

| | Before | After |
|---|---|---|
| 2020 Q26, content-free answer | **full marks on 2 of 3 parts** | **0/5** |
| 2020 Q26, correct answer | 5/5 | 5/5 (screenshotted, with NESA's own criteria per row) |
| 2021 Q27, *"The answer is 5"* | 2/4 | **0/4** |
| 2021 Q27, correct answer | 4/4 | 4/4 |
| 2021 Q28, content-free answer | **1/1 on part (b)** | **0/3** |
| 2021 Q28, correct answer | 3/3 | 3/3 |
| 2025 Q19, correct answer | — | **5/5**, with the corrected model answer on screen |
| 2025 Q19, the old wrong answer | — | 3/5 |

- Corrected stems read back **off the rendered page**, not out of the JSON: 2020 Q20 shows
  `$122 680` / `$3000 per month`; 2024 Q35 shows `standard deviation 15`, *"between 58 and
  70"* and *"top 10% of the candidates"*; 2025 Q26 shows *"approximate area of the curved
  surface"* and *"percentage error of the measurement of 10.2 cm"*.
- **No console errors.**

---

## GATE 6b — passed

- [x] Every written question read against NESA's sample answer **and** criteria rows — 145/145
- [x] All three artefacts reviewed: `modelAnswer`, `keywords`, `bandDescriptors`
- [x] Review committed to the ledger with both sample-answer fingerprints
- [x] `divergent-accepted` used with a note quoting the unusable text — never a silent pass
- [x] Checker **enforces** this subject; staleness proved to exit 1
- [x] Full local CI green; browser-verified at six widths
- [x] No mark, MC answer or omission declaration altered
- [ ] **Human sign-off — NOT done.** `reviewMethod` says so.

---

## Findings recorded, deliberately NOT acted on

1. ⚠️ **On the offline path, an answer of nothing but digits scores full marks on most
   maths questions.** `keywordHit`'s `kw.startsWith(word)` branch credits any numeric keyword
   from a bare digit that prefixes it, so *"1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 + 0 = 45"*
   matches `320000`, `45097` and `8213.20` alike. **Measured while building the decoy check:
   167 of Standard 2's 227 question/part rows.** The looseness itself is already documented
   in `scoring.js` and CLAUDE.md as deliberately unfixed — changing it would move marks on
   live questions in every subject — but nobody had put a number on it. It is also why the
   committed decoy set is **prose-only**: a digit decoy buries every content defect under the
   engine's own behaviour. The AI marking path is unaffected; this is the logged-out fallback.
2. ⚠️ **The same rule is materially wrong on network questions.** A critical-path answer is
   full of single-letter activity names, and any one of them prefix-matches a keyword starting
   with that letter — so `critical path` is credited by a bare `C` and `float` by a bare `F`.
   This is why 2025 Q19's old wrong answer still scored 3/5 after its keyword list was
   tightened. An **engine** change, not a content one.
3. **Five questions still give a prose-only content-free answer partial credit** — 2021 Q17
   (1/2), 2024 Q21(a) (1/2), 2023 Q19(b) (1/2), 2022 Q35 (1/4) and 2025 Q22(b) (1/4). The
   committed check reports the first three, which clear its 50% threshold. Every one is the
   same looseness paying one keyword out of several; none is a data defect.
4. **The `bandDescriptors` on single-part questions are authored paraphrases, not NESA
   verbatim.** `scripts/refresh_band_descriptors.py` regenerates only **per-part**
   descriptors, so Standard 2's 79 single-part questions still carry hand-written text
   (`"2/2 — Correct method: …"`) rather than NESA's criteria rows. They were read against
   the criteria and are faithful, but they are not the verbatim collapse the playbook
   specifies. Regenerating them is a mechanical pass worth doing deliberately.
5. ⚠️ **The generated non-attainment wording reads badly.** A 1-mark part whose criteria
   table has a single row gets `partial`/`minimal` = `"Does not meet the criterion: provides
   correct answer"`, which is student-facing and confusing — and on 2023 Q21(b) it
   lowercases NESA's own text (`"…graphs provider a's charges"`). It is generated
   identically for Mathematics Advanced, so changing it is a generator change across two
   subjects.
6. **Drawing tasks are silently reworded.** 2021 Q24(c) *"draw the graph"* has *"Describe
   the key features of this graph"* appended, and 2022 Q20(a) / 2023 Q17(a) / 2023 Q21(b)
   keep a "draw the network / graph on the grid" instruction with a prose answer. The
   established convention elsewhere is an `omittedParts` entry or a **visibly separate**
   note; these blend the substitution into NESA's own sentence.
7. **90 Standard 2 stems end in a literal `(N marks)`** duplicating the badge the renderer
   already draws. VET has the same on ten 2025 stems. Recorded since 2026-09-01 and still
   wanting one pass across both subjects.
8. **2020 Q37 and every paper's last question carry the whole Mapping Grid** inside their
   committed `sampleAnswer` — the known `parse_paper()` artefact. Harmless to the mark
   check; noted because the fingerprint therefore covers more text than the sample alone.

---

## Reproducing this

```bash
python scripts/review_triage.py mathematics-standard-2 --triage   # order the queue
python scripts/review_triage.py mathematics-standard-2 2020       # read one year in full
node   scripts/review_checks.cjs mathematics-standard-2           # the mechanical gates
python scripts/archive/ms2_review_apply_2026-09-07.py             # the corrections (one-shot)
python scripts/build_review_ledger.py mathematics-standard-2      # write the ledger
node   scripts/check_written_key.cjs                              # enforce it
```

The apply script asserts every old value before replacing it, so it is deliberately **not**
idempotent — a second run fails loudly rather than double-applying.
