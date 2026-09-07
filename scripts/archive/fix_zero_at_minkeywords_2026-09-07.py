# -*- coding: utf-8 -*-
"""Fix the 9 questions that award ZERO marks at their own declared `minKeywords`.

`scoreOne()` computes `round(matched / n * marks)` and uses `minKeywords` only to
CAP. So a large keyword list beside a small `minKeywords` declares a bar that
earns nothing: n=9, min=1, marks=2 gives round(0.22) = 0.

⚠️ THE OBVIOUS FIX IS WRONG. Removing "duplicate" keywords to shrink n looks like
it should raise every partial mark, and it does the opposite: a strong answer
matches the duplicates too, so removing k of them takes k off the numerator AND
the denominator, and (m−k)/(n−k) < m/n whenever m < n. Measured in the real
engine, a first attempt cost real marks on three probes — Standard 2 2023 Q30
3→2, 2023 Q36 3→2, and 2024 Q37 1→0 for a student answering "8:00 am". Reverted.

The safe lever is to RAISE `minKeywords` to the smallest count that actually earns
a mark. That is provably a no-op for every student: below the new bar the ratio
score is 0 by construction, and the cap can only clamp downward, so
min(0, floor(marks/2)) = 0 either way. It makes the declared bar honest without
touching anyone's mark. The script asserts that per question.

Also folded in: two genuinely uncreditable keywords on Standard 2 2024 Q37
('-3' against an answer writing the Unicode-minus 'UTC−3', and '13 hours' never
stated at all) — the same FORM/ABSENT classes fixed on 2026-09-07. A UTC offset
is conventionally written with an ASCII hyphen anyway.
"""
import json, io, re, math

def jsround(x):
    return math.floor(x + 0.5)

S2  = 'subjects/mathematics-standard-2.json'
VET = 'subjects/vet-construction.json'

# (file, year, qNum-stem, part label or None)
TARGETS = [
    (S2,  2023, '18', None),
    (S2,  2023, '30', None),
    (S2,  2023, '36', None),
    (S2,  2024, '33', None),
    (S2,  2024, '37', None),
    (S2,  2025, '23', None),
    (VET, 2023, '16', '(a)(ii)'),
    (VET, 2023, '17', '(a)'),
    (VET, 2024, '17', '(a)'),
]

def unit_of(q, lab):
    if lab is None:
        return q
    for p in q.get('parts', []):
        if p['label'] == lab:
            return p
    raise AssertionError('no part %s' % lab)

report = []
for f in (S2, VET):
    raw = io.open(f, encoding='utf-8').read()
    lines = raw.split('\n')
    start = next(i for i, l in enumerate(lines) if l.startswith('  "writtenQuestions": ['))
    end = next(i for i in range(start + 1, len(lines)) if lines[i] in ('  ],', '  ]'))
    closer = lines[end]
    qs = json.loads('[' + '\n'.join(lines[start + 1:end]) + ']')

    for (ff, year, qnum, lab) in TARGETS:
        if ff != f:
            continue
        hits = [q for q in qs if q.get('year') == year and str(q.get('qNum')).split('(')[0] == qnum]
        assert len(hits) == 1, '%s %s Q%s matched %d' % (f, year, qnum, len(hits))
        q = hits[0]
        o = unit_of(q, lab)
        kw = o['keywords']
        n = len(kw)
        marks = o.get('marks') or q.get('marks')
        cur = o.get('minKeywords')
        cur = (cur if cur is not None else -(-n // 2))
        before = jsround((cur / n) * marks)
        assert before == 0, '%s Q%s %s: expected 0 at its bar, got %d' % (year, qnum, lab, before)

        need = next((m for m in range(1, n + 1) if jsround((m / n) * marks) >= 1), n)
        assert need > cur, 'no raise needed?'

        # A raise must not cost any student a mark. Below the new bar the ratio
        # score is 0 by construction, and the cap only clamps downward.
        cap = marks // 2
        for m in range(cur, need):
            r = jsround((m / n) * marks)
            assert r == 0 and min(r, cap) == r, \
                '%s Q%s: raising min to %d would change the mark at matched=%d' % (year, qnum, need, m)

        o['minKeywords'] = need
        report.append((f.split('/')[-1][:-5], year, q.get('qNum'), lab or '-', marks, n,
                       cur, need, before, jsround((need / n) * marks)))

    # ── Standard 2 2024 Q37: two genuinely uncreditable keywords ────────────
    if f == S2:
        q = [x for x in qs if x.get('year') == 2024 and str(x.get('qNum')) == '37'][0]
        a = q['answer']
        old1 = '3 pm in Rio (UTC−3)'
        assert a.count(old1) == 1, 'UTC offset anchor not found'
        a = a.replace(old1, '3 pm in Rio (UTC-3)')
        old2 = 'Convert to UTC:'
        assert a.count(old2) == 1
        a = a.replace(old2, 'Sydney (UTC+10) is 13 hours ahead of Rio (UTC-3).\nConvert to UTC:')
        q['answer'] = a
        print("also: 2024 Q37 answer — '-3' now matchable (ASCII offset) and '13 hours' stated")

    body = json.dumps(qs, ensure_ascii=False, indent=2)
    bl = ['  ' + l for l in body.split('\n')]
    bl[0] = '  "writtenQuestions": ['
    bl[-1] = closer
    io.open(f, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines[:start] + bl + lines[end + 1:]))

print()
print('%-24s %-5s %-8s %-9s %-6s %-4s %-9s %s' % ('subject','year','qNum','part','marks','n','min','markAtMin'))
for r in report:
    sub, year, qn, lab, marks, n, cur, new, b, a = r
    print('%-24s %-5s %-8s %-9s %-6d %-4d %-9s %d -> %d' % (sub, year, qn, lab, marks, n, '%d -> %d' % (cur, new), b, a))
print()
print('questions fixed:', len(report), '| keyword lists unchanged, only minKeywords raised')
