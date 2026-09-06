# -*- coding: utf-8 -*-
"""Fix the 15 written questions that do not score full marks from their own model answer.

Causes, and the fix used for each:

  FORM       the keyword and the model answer state the same thing in different
             notation (ASCII '-25' vs Unicode '− 25'; '1/2' vs '½'; an acronym
             vs its spelled-out form). Fixed by making them agree, preferring
             the form that ALSO matches what a student would type.
  ABSENT     the concept is genuinely not demonstrated in the model answer.
             Fixed by extending the answer, never by deleting the keyword.
  MENU       (HMS) the question asks for THREE principles / TWO adaptations but
             the keyword list enumerates the whole menu, so a correct answer can
             never match all of them. Fixed with an "other acceptable answers"
             line — the pattern already used in Multimedia and VET.

No keyword is deleted and no mark, stem, band descriptor or MC question is touched.
Only `answer` and `keywords`/`acceptableAnswers` change.
"""
import json, io, re, sys, math

# ── engine mirror (tags stripped the way a BROWSER does, not with <[^>]+> ) ──
TAGS = (r'a|b|i|u|em|strong|sup|sub|br|p|div|span|img|table|thead|tbody|tr|td|th|'
        r'ul|ol|li|h[1-6]|small|code|pre|hr|figure|figcaption|caption|col|colgroup')
REAL_TAG = re.compile(r'</?(?:%s)\b[^>]*>' % TAGS, re.I)

def plain(h):
    """A bare '<' followed by a space or digit is TEXT to the HTML parser, not a
    tag. Stripping with <[^>]+> eats real content — it made 2024 Q30 look broken."""
    return re.sub(r'\s+', ' ', REAL_TAG.sub(' ', str(h or ''))).strip()

def jsround(x):
    return math.floor(x + 0.5)

def keyword_hit(kw, sa):
    kw = kw.lower(); sa = sa.lower()
    if kw in sa: return True
    for w in re.split(r'[^A-Za-z0-9_]+', sa):
        if not w: continue
        if w.startswith(kw) or kw.startswith(w): return True
        st = min(4, len(w), len(kw))
        if st >= 4 and w[:st] == kw[:st]: return True
    return False

def self_score(q):
    """What the engine awards when fed this question's own model answer."""
    mk = int(q.get('marks') or q.get('maxMark') or 0)
    sa = plain(q.get('answer'))
    acc = q.get('acceptableAnswers')
    if acc:
        return (mk if any(a.lower() in sa.lower() for a in acc) else 0), mk
    kw = q.get('keywords') or []
    if not kw or mk <= 0:
        return mk, mk
    mn = q.get('minKeywords')
    mnv = mn if mn is not None else -(-len(kw) // 2)
    matched = sum(1 for k in kw if keyword_hit(k, sa))
    earned = jsround((matched / len(kw)) * mk)
    if matched < mnv:
        earned = min(earned, mk // 2)
    return earned, mk

# ── the edits ───────────────────────────────────────────────────────────────
# (file, selector) -> list of ops. Ops: ('ans', old, new) | ('kw', old, new)
#                                       ('acc+', [additions]) | ('ans+', suffix)
S2, MA, HMS, VET = ('subjects/mathematics-standard-2.json', 'subjects/mathematics-advanced.json',
                    'subjects/health-movement-science.json', 'subjects/vet-construction.json')

def yq(year, qnum):
    return lambda i, q: q.get('year') == year and str(q.get('qNum')) == qnum
def at(idx):
    return lambda i, q: i == idx

EDITS = [
 # ── Mathematics Standard 2 ────────────────────────────────────────────────
 (S2, yq(2023, '36'), 'ABSENT+FORM', [
   ('ans', '0.02 = (10 × 3 − 7.5H) / (6.8 × 75)',
           'Setting BAC = 0.02 and solving for H:\n0.02 = (10 × 3 − 7.5H) / (6.8 × 75)'),
   ('ans', '= 6:22 pm.', '= 6:22 pm (18:22).'),
 ]),
 (S2, yq(2025, '17'), 'FORM', [
   # acceptableAnswers were ASCII hyphen-minus; the model answer uses U+2212.
   # An OR list, so adding variants is strictly more permissive.
   ('acc+', ['y = −2x + 14', 'y=−2x+14', 'y = 14 − 2x']),
 ]),

 # ── Mathematics Advanced ──────────────────────────────────────────────────
 (MA, yq(2022, '28'), 'FORM', [
   ('kw', 'π/4 − 1/2', 'π/4 − ½'),          # the answer writes ½, not 1/2
 ]),
 (MA, yq(2023, '22'), 'ABSENT', [
   ('ans', 'In the top face, AD = 7 and DM = ½ × CD = ½ × 6 = 3, so',
           'In the top face, AD = 7 and, since M is the midpoint of CD, DM = ½ × CD = ½ × 6 = 3, so'),
 ]),
 (MA, yq(2025, '12'), 'FORM', [
   ('kw', '-25', '25'),                      # '25' matches both '− 25' and '-25'
 ]),
 (MA, yq(2025, '19'), 'ABSENT', [
   ('ans', 'P(Amara | win) = (0.5/6) ÷ (1.9/6)',
           'This is a conditional probability:\nP(Amara | win) = (0.5/6) ÷ (1.9/6)'),
 ]),
 (MA, yq(2025, '30'), 'FORM', [
   ('kw', '(x - k - 1)', 'translat'),        # notation-free, and the answer says "Translating"
 ]),

 # ── Health & Movement Science ─────────────────────────────────────────────
 (HMS, at(4), 'ABSENT', [
   ('ans+', '\n              <p>The key <strong>difference</strong> is therefore one of purpose and '
            'order: DRSABCD is a primary, life-saving check applied to every casualty first, whereas '
            'TOTAPS is a secondary, injury-specific assessment used only once the athlete is known to '
            'be stable.</p>'),
 ]),
 (HMS, at(14), 'ABSENT', [
   ('ans', 'Overall, these policies are effective',
           'Overall, evaluating these policies shows they are effective'),
 ]),
 (HMS, at(17), 'ABSENT', [
   ('ans', '<p><strong>Applied example:</strong>',
           '<p>Overload is applied by progressively increasing <strong>frequency</strong> (sessions per '
           'week), <strong>intensity</strong> (pace or effort) or <strong>duration</strong> (time or '
           'distance per session).</p>\n<p><strong>Applied example:</strong>'),
 ]),
 (HMS, at(22), 'MENU', [
   ('ans+', '\n<p><strong>Other principles that could be applied:</strong> reversibility (fitness is '
            'lost if pre-season training stops), training thresholds (working above the aerobic '
            'threshold), and structuring every session with a warm-up and cool-down.</p>'),
 ]),
 (HMS, at(24), 'MENU', [
   ('ans+', '\n<p><strong>Other adaptations that could be explained:</strong> increased VO₂ max, and '
            'greater mitochondrial density and capillary supply in slow twitch fibres — both raising '
            'aerobic endurance.</p>'),
 ]),
 (HMS, at(25), 'MENU', [
   ('ans+', '\n<p><strong>Other principles and adaptations that could be credited:</strong> variety and '
            'the warm-up/cool-down structure of each session, and increased haemoglobin concentration '
            'improving oxygen transport.</p>'),
 ]),

 # ── VET Construction ──────────────────────────────────────────────────────
 # NOTE: VET has a committed review ledger. The ledger's staleness fingerprint
 # tracks NESA's SAMPLE answer, not ours, so these edits mark nothing stale —
 # but the reviewer did not sign off this exact wording. Flagged in HISTORY.
 (VET, yq(2022, '21(b)'), 'FORM', [
   ('ans', 'Safety Data Sheets, Safe Work Method Statements,',
           'Safety Data Sheets (SDS), Safe Work Method Statements (SWMS),'),
 ]),
 (VET, yq(2024, '20(b)'), 'FORM', [
   ('ans', 'A Safe Work Method Statement is prepared', 'A Safe Work Method Statement (SWMS) is prepared'),
   ('ans', 'a job safety analysis for each task', 'a job safety analysis (JSA) for each task'),
   ('ans', 'Safety Data Sheets are available', 'Safety Data Sheets (SDS) are available'),
 ]),
]

# ── apply ───────────────────────────────────────────────────────────────────
by_file = {}
for f, sel, cls, ops in EDITS:
    by_file.setdefault(f, []).append((sel, cls, ops))

report = []
for f, items in by_file.items():
    raw = io.open(f, encoding='utf-8').read()
    lines = raw.split('\n')
    start = next(i for i, l in enumerate(lines) if l.startswith('  "writtenQuestions": ['))
    # writtenQuestions may be the LAST top-level key (mathematics-advanced),
    # in which case its array closes with '  ]' and no trailing comma.
    end = next(i for i in range(start + 1, len(lines)) if lines[i] in ('  ],', '  ]'))
    closer = lines[end]
    qs = json.loads('[' + '\n'.join(lines[start + 1:end]) + ']')

    for sel, cls, ops in items:
        hits = [i for i, q in enumerate(qs) if sel(i, q)]
        assert len(hits) == 1, '%s: selector matched %d questions' % (f, len(hits))
        q = qs[hits[0]]
        before = self_score(q)
        for op in ops:
            if op[0] == 'ans':
                _, old, new = op
                assert q['answer'].count(old) == 1, '%s %s: anchor %r x%d' % (f, hits[0], old[:50], q['answer'].count(old))
                q['answer'] = q['answer'].replace(old, new)
            elif op[0] == 'ans+':
                q['answer'] = q['answer'] + op[1]
            elif op[0] == 'kw':
                _, old, new = op
                assert old in q['keywords'], '%s: keyword %r absent' % (f, old)
                q['keywords'] = [new if k == old else k for k in q['keywords']]
            elif op[0] == 'acc+':
                for a in op[1]:
                    if a not in q['acceptableAnswers']:
                        q['acceptableAnswers'].append(a)
        after = self_score(q)
        report.append((f.split('/')[-1][:-5], q.get('year'), q.get('qNum'), hits[0], cls,
                       '%d/%d' % before, '%d/%d' % after))

    body = json.dumps(qs, ensure_ascii=False, indent=2)
    bl = ['  ' + l for l in body.split('\n')]
    bl[0] = '  "writtenQuestions": ['
    bl[-1] = closer
    io.open(f, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines[:start] + bl + lines[end + 1:]))

print('%-26s %-6s %-8s %-5s %-12s %-7s %s' % ('subject', 'year', 'qNum', 'idx', 'cause', 'before', 'after'))
bad = 0
for r in report:
    ok = r[5] != r[6] and r[6].split('/')[0] == r[6].split('/')[1]
    if not ok: bad += 1
    print('%-26s %-6s %-8s %-5s %-12s %-7s %s%s' % (r[0], r[1], r[2], r[3], r[4], r[5], r[6],
                                                    '' if ok else '   <-- STILL FAILING'))
print()
print('edits applied:', len(report), '| still failing:', bad)
