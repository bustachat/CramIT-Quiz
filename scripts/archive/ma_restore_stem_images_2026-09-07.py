# -*- coding: utf-8 -*-
"""Restore 14 Mathematics Advanced stimulus images that stopped rendering.

FOUND BY RENDERING, not by reading the data. A multi-part written question is
drawn by the accordion as `stem` + each part's own prompt; the combined `q` is
never rendered in the quiz (it feeds CI and the test-mode results breakdown).
When scripts/archive/mathsadv_add_parts.py split `stem` out of `q` on
2026-09-05 it copied the intro TEXT but left the <img> behind in `q`, so 14
questions have been telling students "The diagram shows..." above no diagram.

Proved rather than inferred: rendering 2020 Q29 with its `parts` deleted shows
1 image; with `parts` present it shows 0.

Nothing else in the repo is affected -- Standard 2's builder put the image in
`stem`, and VET's two candidates keep theirs in each part's `intro`, which the
accordion does render. Both were checked, not assumed.

Also here, from the same on-screen sweep: four SINGLE-part questions whose `q`
(which IS the stem on screen for them) ends in a literal "(N marks)" directly
under the badge that already says it, immediately before an omission note.
Questions carrying SEVERAL labels are left alone -- there each label is the
only place that sub-part's value appears.
"""
import io
import json
import re

EDITS = []
P = 'subjects/mathematics-advanced.json'
raw = io.open(P, encoding='utf-8').read()
d = json.loads(raw)
assert json.dumps(d, indent=2, ensure_ascii=False) + '\n' == raw, 'does not round-trip'


def find(y, n):
    return [x for x in d['writtenQuestions']
            if x.get('year') == y and str(x.get('qNum')) == str(n)][0]


# --- 1. move the <img> from `q` into `stem` ---------------------------
LOST = [(2020, '15'), (2020, '29'), (2020, '30'), (2020, '31'),
        (2022, '17'), (2022, '31'),
        (2023, '26'), (2023, '27'), (2023, '32'),
        (2024, '14'), (2024, '20'), (2024, '22'),
        (2025, '11'), (2025, '29')]

for y, n in LOST:
    q = find(y, n)
    stem, body = q['stem'], q['q']
    assert q.get('parts'), ('%d Q%s is not multi-part' % (y, n))
    assert '<img' not in stem, ('%d Q%s: stem already has an image' % (y, n))
    assert body.startswith(stem), ('%d Q%s: stem is not a prefix of q' % (y, n))
    rest = body[len(stem):]
    m = re.match(r'\s*<img\b[^>]*>', rest)
    assert m, ('%d Q%s: q does not continue with an <img> right after the stem -- '
               'refusing to guess where the picture belongs' % (y, n))
    tag = m.group(0).strip()
    assert 'src="/diagrams/' in tag, ('%d Q%s: unexpected img src' % (y, n))
    assert 'max-width' in tag, ('%d Q%s: img carries no inline max-width (see CLAUDE.md '
                                'section 10) -- fix that before moving it' % (y, n))
    q['stem'] = stem + tag
    EDITS.append('MA %d Q%s: move the stimulus <img> into `stem` so the accordion renders it'
                 % (y, n))

# --- 2. four single-part stems ending in a duplicated mark label ------
for y, n, label in [(2022, '12', '(2 marks)'), (2023, '19', '(2 marks)'),
                    (2023, '30', '(3 marks)'), (2025, '16', '(4 marks)')]:
    q = find(y, n)
    assert not q.get('parts'), ('%d Q%s is multi-part' % (y, n))
    cur = q['q']
    labels = re.findall(r'\(\s*\d+\s*marks?\s*\)', cur)
    assert labels == [label], ('%d Q%s: expected exactly one %s, found %s'
                               % (y, n, label, labels))
    old = ' <strong>%s</strong>' % label
    assert old in cur, ('%d Q%s: unexpected wrapper' % (y, n))
    q['q'] = cur.replace(old, '', 1)
    EDITS.append('MA %d Q%s: remove the duplicated %s from the stem (single-part question, '
                 'so `q` IS what the student reads)' % (y, n, label))

io.open(P, 'w', encoding='utf-8', newline='\n').write(
    json.dumps(d, indent=2, ensure_ascii=False) + '\n')

print('applied %d edits' % len(EDITS))
for e in EDITS:
    print('   ', e)
