# -*- coding: utf-8 -*-
"""Close the dead-keyword class: a keyword its own model answer never demonstrates.

These became visible only after the keywordHit gate landed — the loose prefix rule
had been fake-matching them. They are NOT mark-affecting (the question still
self-scores full and a student who writes the keyword still earns it); the defect
is that the model answer, which is shown directly to the student, does not teach
the concept the marking rewards.

Two classes, same as the exposed set:
  LEAKED  the keyword belongs to a DIFFERENT part of the same question
  FORM    the concept is in the answer in words the matcher cannot reach

Every edit asserts its old value.
"""
import io
import json

EDITS = []


def bank(sid):
    p = 'subjects/%s.json' % sid
    raw = io.open(p, encoding='utf-8').read()
    d = json.loads(raw)
    assert json.dumps(d, indent=2, ensure_ascii=False) + '\n' == raw, sid + ' does not round-trip'
    return p, d


def save(p, d):
    io.open(p, 'w', encoding='utf-8', newline='\n').write(
        json.dumps(d, indent=2, ensure_ascii=False) + '\n')


def find(d, y, n):
    return [x for x in d['writtenQuestions']
            if str(x.get('year')) == str(y) and str(x.get('qNum')) == str(n)][0]


def part(q, label):
    return [p for p in q['parts'] if p['label'] == label][0]


def sub(o, field, old, new, why):
    cur = o[field]
    assert cur.count(old) == 1, (why, cur.count(old))
    o[field] = cur.replace(old, new)
    EDITS.append(why)


def drop(o, kws, why):
    cur = list(o.get('keywords') or [])
    for k in kws:
        assert k in cur, (why, k, cur)
        cur.remove(k)
    assert cur, (why, 'would leave no keywords')
    o['keywords'] = cur
    if o.get('minKeywords') and o['minKeywords'] > len(cur):
        o['minKeywords'] = len(cur)
    EDITS.append(why)


def swap(o, old_kw, new_kw, why):
    cur = list(o.get('keywords') or [])
    assert old_kw in cur, (why, cur)
    cur[cur.index(old_kw)] = new_kw
    o['keywords'] = cur
    EDITS.append(why)


# (Mathematics Standard 2 block already applied in the first run.)

# ═══ Mathematics Advanced ═════════════════════════════════════════════════
p, d = bank('mathematics-advanced')
drop(part(find(d, 2020, 21), '(a)'), ['5.2'], "MA 2020 Q21(a): drop the stray '5.2'")
drop(part(find(d, 2020, 21), '(b)'), ['5.2'], "MA 2020 Q21(b): drop the stray '5.2'")
sub(part(find(d, 2020, 29), '(b)'), 'answer', 'Therefore c = p = e.',
    'Therefore c = p, so c = e.',
    "MA 2020 Q29(b): state c = e")
sub(find(d, 2020, 29), 'answer', 'Therefore c = p = e.', 'Therefore c = p, so c = e.',
    "MA 2020 Q29: same on the combined answer")
drop(part(find(d, 2021, 28), '(c)'), ['x = 3', '2ˣ/ln 2'],
     "MA 2021 Q28(c): drop keywords belonging to parts (a)/(b)")
sub(part(find(d, 2022, 30), '(a)'), 'answer',
    'Setting 3/k = 1 gives k = 3, as required.',
    'Setting F(e³) = 1 gives 3/k = 1, so k = 3, as required.',
    "MA 2022 Q30(a): state F(e³) = 1 as the condition used")
sub(find(d, 2022, 30), 'answer',
    'Setting 3/k = 1 gives k = 3, as required.',
    'Setting F(e³) = 1 gives 3/k = 1, so k = 3, as required.',
    "MA 2022 Q30: same on the combined answer")
sub(find(d, 2023, 11), 'answer', 'a = 3 and d = 7 − 3 = 4.', 'a = 3 and d = 4 (since 7 − 3 = 4).',
    "MA 2023 Q11: state d = 4")
sub(find(d, 2024, 12), 'answer', 'common difference d = 57 − 50 = 7',
    'common difference d = 7 (since 57 − 50 = 7)',
    "MA 2024 Q12: state d = 7")
drop(part(find(d, 2024, 18), '(a)'), ['10'], "MA 2024 Q18(a): drop the stray '10'")
drop(part(find(d, 2024, 22), '(c)'), ['1 − x²'],
     "MA 2024 Q22(c): drop '1 − x²', which is the function from parts (a)/(b)")
drop(part(find(d, 2025, 15), '(c)'), ['2π/5'],
     "MA 2025 Q15(c): drop '2π/5', which belongs to the earlier parts")
sub(find(d, 2025, 18), 'answer', 'takes every real value except 5',
    'takes all real values except 5',
    "MA 2025 Q18: say 'all real'")
save(p, d)

# ═══ VET Construction ═════════════════════════════════════════════════════
# ⚠️ Ledgered subject. All five are mechanical: a word the answer already implies
# is written out, or a keyword is aligned to the answer's own notation. No
# assertion, figure or recommendation changes, so the reviewer's verdicts stand.
p, d = bank('vet-construction')
sub(part(find(d, 2021, 16), '(c)'), 'answer', 'more likely to skid off the timber',
    'more likely to slip or skid off the timber',
    "VET 2021 Q16(c): say 'slip'")
sub(part(find(d, 2021, 16), '(d)'), 'answer',
    'use the chisel only for the work it is designed for',
    'use the chisel only for its intended work — what it is designed for',
    "VET 2021 Q16(d): say 'intended'")
sub(find(d, 2021, 17), 'answer',
    'a range of personal attributes that make them safe, reliable and employable',
    'a range of personal attributes and a professional attitude that make them safe, '
    'reliable and employable',
    "VET 2021 Q17: say 'attitude'")
swap(part(find(d, 2023, 18), '(c)'), 'AS1100', '1100',
     "VET 2023 Q18(c): keyword 'AS1100' -> '1100', matching the answer's 'AS 1100' and a "
     "student's 'AS1100' alike")
sub(part(find(d, 2024, 19), '(b)'), 'answer', 'π × r² × depth', 'π × radius² × depth',
    "VET 2024 Q19(b): say 'radius'")
sub(part(find(d, 2025, 18), '(a)'), 'answer', 'PC (Prime Cost) items',
    'PC items (Prime Cost)',
    "VET 2025 Q18(a): say 'PC items'")
save(p, d)

# ═══ Multimedia ═══════════════════════════════════════════════════════════
# ⚠️ multimedia.json does NOT round-trip through json.dumps (CLAUDE.md), so this
# one is a targeted text replacement on the raw file.
P = 'subjects/multimedia.json'
raw = io.open(P, encoding='utf-8').read()
old = 'Low-angle shots'
assert raw.count(old) == 1, raw.count(old)
io.open(P, 'w', encoding='utf-8', newline='\n').write(raw.replace(old, 'Low angle shots'))
EDITS.append("MM 2024 Q14: 'Low-angle' -> 'Low angle', matching the keyword and 'high angle'")

# ═══ Health and Movement Science ══════════════════════════════════════════
p, d = bank('health-movement-science')
W = d['writtenQuestions']
swap(W[9], 'not early', 'early',
     "HMS idx9: keyword 'not early' -> 'early'; the answer says heat must not be used in "
     "the early (acute) stage")
sub(W[24], 'answer', 'rather than experiencing declining sprint quality in the second half',
    'rather than experiencing declining sprint quality and performance in the second half',
    "HMS idx24: say 'performance'")
sub(W[27], 'answer', 'as arousal increases from low to moderate levels',
    'as arousal increases from low (under-aroused) to moderate levels',
    "HMS idx27: say 'under-aroused'")
sub(W[32], 'answer', 'Before performance, both athletes require',
    'Pre-performance: before performance, both athletes require',
    "HMS idx32: say 'pre-performance'")
sub(W[33], 'answer', 'a soccer team may simplify their attacking play',
    'a soccer team may adjust and simplify their attacking play',
    "HMS idx33: say 'adjust'")
save(p, d)

print('applied %d edits' % len(EDITS))
for e in EDITS:
    print('   ', e)
