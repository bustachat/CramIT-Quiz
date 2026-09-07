# -*- coding: utf-8 -*-
"""Repair the 18 keywords the keywordHit fix exposed (2026-09-07).

None of these was ever a real match: each was being credited only because
`kw.startsWith(word)` accepted a 1-3 character fragment of the model answer. The
fix did not break them — it revealed them. Two classes:

  LEAKED  the keyword belongs to a DIFFERENT part of the same question and was
          copied into this one. Removed from the part it does not describe.
  FORM    the concept IS in the model answer, in a notation the keyword does not
          match. The ANSWER is extended/aligned (the established ABSENT/FORM
          precedent, docs/HISTORY.md 2026-09-07) rather than the keyword deleted.

Every replacement asserts its old value.
"""
import io
import json

EDITS = []


def load(p):
    return json.load(io.open(p, encoding='utf-8'))


def save(p, d):
    with io.open(p, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(json.dumps(d, indent=2, ensure_ascii=False) + '\n')


def sub(obj, field, old, new, why):
    cur = obj[field]
    assert cur.count(old) == 1, (why, cur.count(old))
    obj[field] = cur.replace(old, new)
    EDITS.append(why)


def setkw(obj, old, new, why):
    assert obj.get('keywords') == old, (why, obj.get('keywords'))
    obj['keywords'] = new
    EDITS.append(why)


def part(q, label):
    return [p for p in q['parts'] if p['label'] == label][0]


# ══ Mathematics Standard 2 ══════════════════════════════════════════════════
P = 'subjects/mathematics-standard-2.json'
b = load(P)
def q2(y, n):
    return [x for x in b['writtenQuestions'] if str(x['year']) == str(y) and str(x['qNum']) == n][0]

# LEAKED — '22' is part (b)'s answer (angle OBA = 22°); part (a) shows AB = 38.5.
setkw(part(q2(2022, '33'), '(a)'), ['22', '38.5'], ['38.5'],
      "MS2 2022 Q33(a): drop '22', which is part (b)'s answer")

# FORM — the answer writes the path with arrows, so neither 'abfgd' nor 'abfg'
# was ever literally present.
sub(part(q2(2023, '19'), '(a)'), 'answer',
    'Shortest path from A to D: A → B → F → G → D',
    'Shortest path from A to D: A → B → F → G → D (ABFGD)',
    "MS2 2023 Q19(a): name the path as ABFGD so its own keywords are creditable")
sub(q2(2023, '19'), 'answer',
    'Shortest path from A to D: A → B → F → G → D',
    'Shortest path from A to D: A → B → F → G → D (ABFGD)',
    "MS2 2023 Q19: same on the combined answer")

# FORM — 'y = 1.4x + 6' is one exact answer with two notations. A "state the
# equation" part is all-or-nothing, so acceptableAnswers is the right mechanism
# and covers both spacings.
pa = part(q2(2024, '19'), '(a)')
assert pa['keywords'] == ['1.4x + 6', '1.4x+6'], pa['keywords']
del pa['keywords']
pa.pop('minKeywords', None)
pa['acceptableAnswers'] = ['y = 1.4x + 6', 'y = 1.4x+6', '1.4x + 6', '1.4x+6']
EDITS.append("MS2 2024 Q19(a): keywords -> acceptableAnswers covering both spacings")

# FORM — the answer writes B–D–E–F–H with en dashes.
sub(q2(2025, '19'), 'answer',
    'Critical path: B–D–E–F–H = 4 + 5 + 5 + 7 + 5 = 26 days',
    'Critical path: B–D–E–F–H (BDEFH) = 4 + 5 + 5 + 7 + 5 = 26 days',
    "MS2 2025 Q19: name the path as BDEFH so its own keyword is creditable")

# FORM — '2 am' vs the answer's '2:00 am'.
sub(q2(2021, '20'), 'answer',
    '5:00 pm Thursday (City A) + 9 hours = 2:00 am Friday (Sydney)',
    '5:00 pm Thursday (City A) + 9 hours = 2:00 am Friday (Sydney).\n'
    'Robert should be ready at 2 am on Friday.',
    "MS2 2021 Q20: state '2 am' as well as '2:00 am'")
save(P, b)

# ══ Mathematics Advanced ════════════════════════════════════════════════════
P = 'subjects/mathematics-advanced.json'
b = load(P)
def qa(y, n):
    return [x for x in b['writtenQuestions'] if str(x['year']) == str(y) and str(x['qNum']) == n][0]

# FORM — neither 'arithmetic' nor 'd = 6' appeared; the answer wrote 'd = 10 − 4 = 6'.
sub(qa(2020, '12'), 'answer', 'a = 4 and d = 10 − 4 = 6.',
    'This is an arithmetic series with a = 4 and d = 6 (since 10 − 4 = 6).',
    "MA 2020 Q12: name the arithmetic series and state d = 6")

# FORM — the answer used the formula without naming it.
sub(qa(2020, '22'), 'answer', 'Area of △OAB = ½ r² sin 36°',
    'Area of △OAB = 1/2 ab sin C = ½ r² sin 36°',
    "MA 2020 Q22: write the 1/2 ab sin C form the keyword expects")

# LEAKED — '32/3' describes neither part; part (b) is answered by √2 − 1.
pb = part(qa(2020, '30'), '(b)')
setkw(pb, ['√2 − 1', '4/(a + 1)', 'between the curves', '32/3'],
      ['√2 − 1', '4/(a + 1)', 'between the curves'],
      "MA 2020 Q30(b): drop '32/3', which describes neither part's answer")
setkw(qa(2020, '30'), ['√2 − 1', '4/(a + 1)', 'between the curves', '32/3', 'upper minus lower'],
      ['√2 − 1', '4/(a + 1)', 'between the curves', 'upper minus lower'],
      "MA 2020 Q30: same on the question-level list")

# FORM — the answer gives 36 as a bound ('10 < t < 36'), not an equality.
pb = part(qa(2020, '31'), '(b)')
setkw(pb, ['15 000', '10 < t < 13', 't = 36'], ['15 000', '10 < t < 13', '36'],
      "MA 2020 Q31(b): 't = 36' -> '36'; the answer gives it as a bound")

# LEAKED — 32π is the semicircle area, which is part (b).
setkw(part(qa(2021, '12'), '(a)'), ['13.86', 'angle in a semicircle', '32π'],
      ['13.86', 'angle in a semicircle'],
      "MA 2021 Q12(a): drop '32π', which is part (b)'s working")
part(qa(2021, '12'), '(a)')['minKeywords'] = 1
EDITS.append("MA 2021 Q12(a): minKeywords 2 -> 1 (two keywords remain)")

# FORM — the answer bracketed the integrand as [(2x + 3) − x²].
sub(qa(2022, '16'), 'answer', '∫₋₁³ [(2x + 3) − x²] dx', '∫₋₁³ [2x + 3 − x²] dx',
    "MA 2022 Q16: drop the inner brackets so the integrand keyword is creditable")

# FORM — the answer only ever wrote the z-values inside a division.
sub(qa(2022, '26'), 'answer', '820 → z = −20/80 = −0.25\n920 → z = 80/80 = 1',
    '820 → z = −20/80, so z = −0.25\n920 → z = 80/80, so z = 1',
    "MA 2022 Q26: state z = −0.25 and z = 1 explicitly")

# FORM — 'S∞ = 2' never appeared as such.
sub(part(qa(2022, '29'), '(a)'), 'answer',
    'S∞ = a/(1 − r) = 1/(1 − ½) = 2, as required.',
    'S∞ = a/(1 − r) = 1/(1 − ½) = 2. Hence S∞ = 2, as required.',
    "MA 2022 Q29(a): state S∞ = 2 explicitly")
sub(qa(2022, '29'), 'answer', 'S∞ = a/(1 − r) = 1/(1 − ½) = 2, as required.',
    'S∞ = a/(1 − r) = 1/(1 − ½) = 2. Hence S∞ = 2, as required.',
    "MA 2022 Q29: same on the combined answer")

# LEAKED — x²/(x − 1) is the AREA, derived in part (b).
setkw(part(qa(2022, '31'), '(a)'), ['2x/(x − 1)', 'x²/(x − 1)'], ['2x/(x − 1)'],
      "MA 2022 Q31(a): drop 'x²/(x − 1)', which is part (b)'s area")

# LEAKED — E(X²) is computed in part (b); part (a) shows E(X) = 2.
pa = part(qa(2023, '12'), '(a)')
setkw(pa, ['E(X²)'], ['E(X)', '0.3', '0.5'],
      "MA 2023 Q12(a): 'E(X²)' is part (b)'s; use this part's own working")
pa['minKeywords'] = 2
EDITS.append("MA 2023 Q12(a): minKeywords 2")

# LEAKED — x = √A is derived in part (b).
setkw(part(qa(2024, '31'), '(a)'), ['½θ(2x + x²)', 'θ(2 + x) + 2x', 'x = √A'],
      ['½θ(2x + x²)', 'θ(2 + x) + 2x'],
      "MA 2024 Q31(a): drop 'x = √A', which is part (b)'s working")
part(qa(2024, '31'), '(a)')['minKeywords'] = 1
EDITS.append("MA 2024 Q31(a): minKeywords 2 -> 1")
save(P, b)

# ══ VET Construction ════════════════════════════════════════════════════════
# ⚠️ Ledgered subject. This is a mechanical edit — it adds the abbreviation beside
# the full Act name the answer already gives — so the reviewer's verdict stands,
# and the staleness fingerprint tracks NESA's sample rather than ours.
P = 'subjects/vet-construction.json'
b = load(P)
qv = [x for x in b['writtenQuestions'] if str(x['year']) == '2021' and str(x['qNum']) == '20'][0]
sub(qv, 'answer', 'The Work Health and Safety Act 2011 (NSW) provides the framework',
    'The Work Health and Safety Act 2011 (NSW) — the WHS Act — provides the framework',
    "VET 2021 Q20: give the WHS Act its abbreviation")
save(P, b)

# ══ Health and Movement Science ═════════════════════════════════════════════
P = 'subjects/health-movement-science.json'
b = load(P)
W = b['writtenQuestions']
sub(W[26], 'answer', 'Phases comparison', 'Phases and sub-phases comparison',
    "HMS idx26: name sub-phases")
sub(W[26], 'answer', 'to bring individual arousal to optimal levels',
    'to bring individual arousal and pre-competition anxiety to optimal levels',
    "HMS idx26: name anxiety")
save(P, b)

print('applied %d edits' % len(EDITS))
for e in EDITS:
    print('   ', e)
