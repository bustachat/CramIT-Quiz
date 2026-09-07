# Mathematics Advanced — written-answer review (Stage 6b)

**Status: COMPLETE, 2026-09-07.** 126 of 126 written questions reviewed; the ledger is
committed at `data/answer-key/written/reviews/mathematics-advanced.json` and
`scripts/check_written_key.cjs` now **enforces** the subject — an unreviewed or stale
question fails the build.

**Verdicts: 89 ok · 31 corrected · 6 divergent-accepted.**

> ⚠️ **Provenance.** `REVIEW_METHOD` reads *"assistant-compared against NESA's committed
> sample answers and criteria rows, question by question, with the mathematics checked
> rather than the wording; NO human sign-off on any question."* The checker prints that
> line on every run. Nothing downstream should describe this as a human review.

With this ledger, **every subject in the repo that has an answer key now has a committed
review ledger** — Standard 2 145/145, Advanced 126/126, VET 34/34, Multimedia 35/35. HMS
has no answer key and cannot have one until after the 2026 HSC.

---

## 1. The headline: the content was clean

Not one result, method or figure in this subject disagrees with NESA. That is a genuine
difference from the other ports — VET found 6 defects in 34 and Multimedia 9 in 35 — and it
is consistent with how Advanced was built: uniquely among the five subjects it was ported
from the papers with the official key already committed and reconciling to exactly 100
marks per paper at every stage.

**All 31 corrections are scoring, teaching, rendering or presentation defects, and every
one was invisible to CI because the marks were right.** Two of them could only be found by
*rendering* the questions.

---

## 2. What was found

### 2.1 A stimulus image that reached no student — 14 questions ⚠️

The most serious finding, and a **regression, not a porting gap**.

A multi-part written question is drawn by the accordion as `stem` + each part's own
prompt. The combined `q` is **never rendered in the quiz** — it feeds CI and the test-mode
results breakdown. When `scripts/archive/mathsadv_add_parts.py` split `stem` out of `q` on
2026-09-05 it copied the intro **text** and left the `<img>` behind, so 14 questions have
been telling students *"The diagram shows the graph of…"* above no diagram.

**Proved, not inferred:** rendering 2020 Q29 with its `parts` deleted shows 1 image; with
`parts` present it shows 0.

Fixed by moving the tag into `stem`, where the existing `.parts-stem img` cap
(`min(100%,600px)`, `max-height:30vh`, `object-fit:contain`) bounds it — measured at
**250×154 inside a 278 px stem** for a 1114 px source.

Affected: 2020 Q15, Q29, Q30, Q31 · 2022 Q17, Q31 · 2023 Q26, Q27, Q32 · 2024 Q14, Q20,
Q22 · 2025 Q11, Q29.

⚠️ **Checked, not assumed, elsewhere:** Standard 2, Multimedia and HMS have none, and
VET's two candidates are fine — their image sits in a part's `intro`, which the accordion
*does* render. A first version of the detector reported VET as broken because it did not
count `intro`.

### 2.2 A bare `>` inside an `alt` attribute — 1 question

> ⚠️ **Corrected 2026-09-08.** This was first written up as a *rendering* defect. That was
> wrong, and the browser was asked directly: the pre-fix string parses to exactly one
> `<img>` with its full alt and style intact and nothing leaked as text. Inside a
> double-quoted attribute value the HTML tokenizer treats `<` and `>` as ordinary
> characters — only `"` ends the value.

2020 Q29 carried `alt="Graph of y = c ln x for c > 0, …"`. It renders fine. What it breaks
is **this repo's own regex parsing of markup**: `<img[^>]*>` in
`scripts/archive/mathsadv_add_parts.py` — whose docstring records it losing this very
question's image, which is plausibly how §2.1 happened here — and the live
`/<img[^>]+src="([^"]+)"/g` in `validate_subjects.cjs`. Escaped to `&gt;` so the data is
safe for that tooling. **One instance repo-wide**, swept across all five subjects and both
question arrays.

### 2.3 Sibling-part keyword leaks — 4 questions (+2 in Standard 2)

A **new mechanical check**, written for this review: a *numeric* keyword whose only match
in its **own** model answer is preceded by a digit — i.e. it is a suffix fragment of a
longer number.

| question | keyword | matched only inside | really belongs to |
|---|---|---|---|
| 2020 Q14(c) | `5` | `1560` | part (b) |
| 2022 Q17(a) | `23` | `234` | part (b) |
| 2022 Q32(a) | `83` | `783.7168` | part (b)/(c) |
| 2023 Q15(a) | `40` | `34 140` | part (b) |
| MS2 2022 Q31(b) | `5` | `35` | part (c) |
| MS2 2025 Q40(b) | `600` | `12 600` | part (a) |

⚠️ **The one that was NOT dropped is the point of the method.** 2020 Q11(b) carries part
(c)'s answer `45` by the same signature. Dropping it **measured 2/2 → 1/2 on a fully
correct working**, because that working writes `450` and the keyword was carrying the
match. It stays. Every drop above was probed against four realistic student answers first;
2020 Q14(c) improves a correct `10/39` from 1/2 to 2/2 and the rest are no-ops.

⚠️ Two shapes the first version of this detector got **wrong**, both fixed by reading the
evidence rather than trusting the count: a trailing full stop (`= 15 000.`) and a decimal
continuation (`$45 097.17` containing `45 097`) are legitimate, not fragments.

### 2.4 A model answer that forward-references a later part — 1 question

2023 Q31(a) justified non-independence using `P(S) = 4/5`, which is part **(b)**'s result —
a student answering (a) first cannot use it. NESA argues from the values the question
gives (`P(F|S) = 1/8` against `P(F) = 3/10`). The model answer now leads with NESA's
argument and keeps the other form as a parenthetical.

### 2.5 Duplicated mark labels — 13 questions

A stem or part prompt ending in a literal `(N marks)` sitting directly under the badge
that already says it — 9 part prompts and 4 single-part stems, in every case immediately
before the note explaining an omitted part.

⚠️ **Questions carrying SEVERAL labels were left alone**: there each label is the only
place that sub-part's value appears (2021 Q17's merged `(i)`/`(ii)`, 2022 Q28, 2025 Q17,
Q25, Q26, Q27). Three more in Standard 2 were fixed by the same sweep — the 2026-09-07
label pass had missed them because a **table** follows the label, so it is not at the end
of the raw string.

---

## 3. `ok` vs `divergent-accepted`

NESA's maths sample answers extract as equation **layout**, not prose, so this bank's
worked solutions necessarily read nothing like them. The comparison made here was
**mathematical** — method, intermediate values, final result. That was possible for 120
questions (`ok`), and impossible for 6 where the key's `sampleAnswer` is simply **empty**,
all in 2025: Q12 (extracts as the single character `2`), Q14(c), Q17 (all three parts),
Q18, Q25(c), Q30. Those are `divergent-accepted`, checked against the question and against
the criteria rows, which do extract cleanly.

Four further blanks — 2020 Q11(a), 2021 Q28(b), 2023 Q19(a), 2024 Q17(a) — are for parts
the bank already declares in `omittedParts`, so nothing was lost.

⚠️ Triage reported term overlap **0.00 on almost every question**. That is the signature of
equation-layout extraction, not a signal about the bank. It ordered the reading queue and
decided nothing; every question was read.

---

## 4. Verification

- Full local CI green: `Issues: 0`; **285** MC and **340** written checks, 0 wrong;
  coverage 234/234; review **126/126**; `npm test` **124/124**;
  `content_audit.cjs --strict` exits 0 with **0 mark-affecting findings**.
- **Staleness guarantee tested, not assumed** — corrupting one fingerprint on a merged
  multi-part entry (2023 Q31) and one on a single-part entry (2025 Q18) makes the checker
  report both STALE and exit 1. Restored afterwards.
- Blast radius machine-checked against HEAD: only `q`, `stem`, `answer`, `parts.q`,
  `parts.answer` and `parts.keywords` moved. `marks`, `qNum`, `section`, `category`,
  `image`, `omittedParts`, `acceptableAnswers` and every MC question are unchanged.
- In the running app: all **126** questions render at 375 px and 320 px with **0
  overflows, 0 nested scrollbars, 0 `undefined`, 0 missing marks badges, 0 duplicated mark
  labels**; **47 distinct images all load**; all **207** question/part rows score **full**
  from their own model answers with **0** parts on generic band wording.
- A real end-to-end flow on 2020 Q29 (the restored-image question) through the app's own
  handlers scored **3 / 4** — part (a) 2/2, part (b) 1/2 — genuinely computed, each row
  captioned with NESA's own criteria wording, the stimulus rendering, the model answer
  revealed, no console errors.
- Standard 2's ledger was rebuilt after its five edits and machine-compared: **only the
  five notes moved**; no fingerprint, verdict or `reviewMethod` changed.

---

## 5. Left open

- **No human sign-off**, here or on any other subject's ledger.
- The **live AI marking call** has still never been made from this environment (no
  `ANTHROPIC_API_KEY`); the offline engine is what was exercised.
- `keywordHit`'s `normNum` joins two separate numbers separated by a space (`= 18 3x`
  normalises to `183x`). It is applied symmetrically to keyword and answer, so no
  behavioural defect was found from it, but it made two detector readings look like leaks
  when they were not. Recorded, not changed — this review is not the place for another
  engine edit.
