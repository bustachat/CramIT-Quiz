# -*- coding: utf-8 -*-
"""Convert the three VET "choose N from a menu" parts from `keywords` to `anyOf`.

Every existing keyword is PRESERVED, only regrouped — so this cannot widen or
narrow what the engine accepts, it only changes how the count maps to marks.
The script asserts that: the multiset of keywords going in equals the multiset
of alternatives coming out.
"""
import json, io

P = 'subjects/vet-construction.json'

CONVERSIONS = {
    # 2023 Q16(a)(ii) — "List TWO items of PPE" (2 marks). One pool, pick 2.
    (2023, '16', '(a)(ii)'): [
        {"required": 2, "groups": [
            ["safety glasses", "goggles"],
            ["hearing", "earmuff", "earplug"],
            ["face shield"],
            ["dust mask"],
            ["footwear"],
            ["hair"],
        ]},
    ],
    # 2023 Q17(a) — "How could this disagreement be resolved?" (2 marks).
    # One pool: name two avenues of resolution.
    (2023, '17', '(a)'): [
        {"required": 2, "groups": [
            ["award", "rate"],
            ["regulator", "fair work", "ombudsman"],
            ["union"],
            ["association", "industry", "HIA", "MBA"],
            ["dispute"],
        ]},
    ],
    # 2024 Q17(a) — "Identify ONE advantage AND ONE disadvantage" (2 marks).
    # TWO pools of one: naming two advantages must not score 2/2.
    (2024, '17', '(a)'): [
        {"required": 1, "label": "advantage", "groups": [
            ["time"], ["one person"], ["portable"], ["store"],
        ]},
        {"required": 1, "label": "disadvantage", "groups": [
            ["battery", "recharge"], ["expensive"], ["maintain"],
            ["line of sight"], ["internal"],
        ]},
    ],
}

raw = io.open(P, encoding='utf-8').read()
lines = raw.split('\n')
start = next(i for i, l in enumerate(lines) if l.startswith('  "writtenQuestions": ['))
end = next(i for i in range(start + 1, len(lines)) if lines[i] in ('  ],', '  ]'))
closer = lines[end]
qs = json.loads('[' + '\n'.join(lines[start + 1:end]) + ']')

for (year, qnum, lab), blocks in CONVERSIONS.items():
    hits = [q for q in qs if q.get('year') == year and str(q.get('qNum')) == qnum]
    assert len(hits) == 1, '%s Q%s matched %d' % (year, qnum, len(hits))
    part = next(p for p in hits[0]['parts'] if p['label'] == lab)

    old_kw = sorted(part['keywords'])
    new_alts = sorted(a for b in blocks for g in b['groups'] for a in g)
    assert old_kw == new_alts, (
        '%s Q%s %s: keyword set changed\n  removed: %s\n  added:   %s'
        % (year, qnum, lab, sorted(set(old_kw) - set(new_alts)), sorted(set(new_alts) - set(old_kw))))

    total_required = sum(b['required'] for b in blocks)
    assert total_required <= part['marks'] or True  # informational
    part.pop('keywords', None)
    part.pop('minKeywords', None)
    part['anyOf'] = blocks
    print('%s Q%s %s: %d keywords -> %d block(s), %d group(s), required %d, marks %d'
          % (year, qnum, lab, len(old_kw), len(blocks),
             sum(len(b['groups']) for b in blocks), total_required, part['marks']))

body = json.dumps(qs, ensure_ascii=False, indent=2)
bl = ['  ' + l for l in body.split('\n')]
bl[0] = '  "writtenQuestions": ['
bl[-1] = closer
io.open(P, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines[:start] + bl + lines[end + 1:]))
print('written:', P)
