# -*- coding: utf-8 -*-
"""Reading aid for a written-answer review. NOT a checker, and NEVER a verdict.

Prints each written bank question beside NESA's official mark, sample answer and criteria
rows, so a reviewer can compare them without re-reading a marking guideline (which
CLAUDE.md section 10 forbids -- the key is the ground truth).

`--triage` orders the reading queue by the mechanical signals docs/porting-playbook.md
section 6 permits: a keyword absent from the model answer, a keyword absent from NESA's
sample, low substantive-term overlap, and answer length against the mark value.

    ORDERING ONLY. This project has been burned repeatedly by similarity scoring
    (backfill_qnum.py exists because of it; section 10 rule 3 is explicit that fuzzy
    text-matching is not a join). A low score means READ THIS ONE FIRST. It never means
    the question is wrong, and a high score never means it is right. Read all of them.

Usage
-----
    python scripts/review_triage.py <subject-id> --triage      queue order
    python scripts/review_triage.py <subject-id>               every question in full
    python scripts/review_triage.py <subject-id> "2023 19(b)"  one question
"""
import io, json, re, sys

if len(sys.argv) < 2 or sys.argv[1].startswith('-'):
    sys.exit(__doc__)
SUBJECT = sys.argv[1]
bank = json.load(io.open('subjects/%s.json' % SUBJECT, encoding='utf-8'))
key  = json.load(io.open('data/answer-key/written/%s.json' % SUBJECT, encoding='utf-8'))

def path_of(qnum):
    m = re.match(r'^(\d+)((?:\([a-z0-9ivx]+\))*)$', str(qnum))
    parts = re.findall(r'\(([a-z0-9ivx]+)\)', m.group(2))
    return m.group(1), parts

def leaves(year, qnum):
    q, parts = path_of(qnum)
    want = [q] + parts
    out = []
    for p in key['papers'][str(year)]:
        got = [str(p['question'])] + ([] if not p['part'] else p['part'].split('.'))
        if got[:len(want)] == want:
            out.append(p)
    return out

def strip(html):
    """Strip HTML the way a BROWSER does, not with /<[^>]+>/g.

    A naive tag regex is NOT how the page renders: the HTML parser only opens a
    tag when `<` is followed by a letter, `/`, `!` or `?`, so `P(0 < Z < 0.3)`
    is literal text on screen. The regex ate it, and a reviewer reading this
    output would report a damaged model answer that is perfectly fine -- the
    same measuring-instrument error that produced a false finding on
    mathematics-advanced 2024 Q30 (docs/HISTORY.md 2026-09-07).
    """
    s, out, i = html or '', [], 0
    while i < len(s):
        if s[i] == '<' and i + 1 < len(s) and re.match(r'[A-Za-z/!?]', s[i + 1]):
            g = s.find('>', i)
            if g != -1:
                out.append(' '); i = g + 1; continue
        out.append(s[i]); i += 1
    t = ''.join(out)
    for a, b in (('&nbsp;', ' '), ('&amp;', '&'), ('&lt;', '<'), ('&gt;', '>'),
                 ('&quot;', '"'), ('&#39;', "'"), ('&minus;', '−'), ('&deg;', '°'),
                 ('&sup2;', '²'), ('&frasl;', '/'), ('&hellip;', '…'),
                 ('&bull;', '•'), ('&middot;', '·'), ('&times;', '×')):
        t = t.replace(a, b)
    return re.sub(r'\s+', ' ', t).strip()

STOP = set('a an the and or of to in is are for with that this it be as on at by from will can '
           'you they their there which when what how not no if then than have has had do does '
           'should would could may might also its into more most such some any all one two'.split())
def terms(t):
    return {w for w in re.findall(r'[a-z]{4,}', t.lower()) if w not in STOP}

rows = []
for i, q in enumerate(bank['writtenQuestions']):
    ls = leaves(q['year'], q['qNum'])
    off_marks = sum(p['marks'] for p in ls)
    sample = ' || '.join(p['sampleAnswer'] for p in ls)
    ans = strip(q['answer'])
    kws = q.get('keywords', [])
    miss_ans = [k for k in kws if k.lower() not in ans.lower()]
    miss_sam = [k for k in kws if k.lower() not in sample.lower()]
    ta, ts = terms(ans), terms(sample)
    overlap = len(ta & ts) / len(ts) if ts else 0.0
    rows.append(dict(i=i, year=q['year'], qNum=q['qNum'], marks=q['marks'], off=off_marks,
                     overlap=overlap, miss_ans=miss_ans, miss_sam=miss_sam,
                     chars_per_mark=len(ans) // max(q['marks'], 1), leaves=ls, q=q, sample=sample))

if '--triage' in sys.argv:
    print('%-6s %-11s %-5s %-7s %-6s %-5s %s' % ('year','qNum','mk','overlap','c/mk','kwGap','signals'))
    for r in sorted(rows, key=lambda r: (r['overlap'], -len(r['miss_ans']))):
        sig = []
        if r['miss_ans']: sig.append('%d kw absent from modelAnswer: %s' % (len(r['miss_ans']), ','.join(r['miss_ans'])))
        if r['miss_sam']: sig.append('%d kw absent from NESA sample: %s' % (len(r['miss_sam']), ','.join(r['miss_sam'])))
        if not r['q'].get('keywords'): sig.append('NO keywords')
        print('%-6s %-11s %-5s %-7.2f %-6s %-5s %s' % (r['year'], r['qNum'], '%d/%d'%(r['marks'],r['off']),
              r['overlap'], r['chars_per_mark'], len(r['miss_ans']), ' | '.join(sig) or '-'))
    sys.exit()

sel = sys.argv[2] if len(sys.argv) > 2 else None
for r in rows:
    tag = '%s %s' % (r['year'], r['qNum'])
    if sel and sel not in tag: continue
    q = r['q']
    print('=' * 100)
    print('%s   bank marks=%d   official=%d   section=%s' % (tag, r['marks'], r['off'], q.get('section')))
    print('-- STEM --');            print(strip(q['q']))
    if q.get('image'): print('   [image] %s' % q['image'])
    if q.get('stem'): print('-- BANK stem (shared) --'); print(strip(q['stem']))
    print('-- BANK answer --');     print(strip(q['answer']))
    print('-- BANK keywords (minKeywords=%s) --' % q.get('minKeywords')); print(q.get('keywords'))
    if 'acceptableAnswers' in q: print('-- BANK acceptableAnswers --'); print(q['acceptableAnswers'])
    if q.get('anyOf'): print('-- BANK anyOf --'); print(q['anyOf'])
    if q.get('bandDescriptors'): print('-- BANK bandDescriptors --'); print(q['bandDescriptors'])
    # A question NESA prints with lettered parts is ONE bank entry but is marked
    # PART BY PART (CLAUDE.md section 10 rule 10), so a review that reads only the
    # question-level fields never sees the data the student is actually scored on.
    for pt in (q.get('parts') or []):
        print('   -- BANK part %s (%s marks, minKeywords=%s) --' % (pt.get('label'), pt.get('marks'), pt.get('minKeywords')))
        if pt.get('intro'): print('      intro:  %s' % strip(pt['intro']))
        print('      prompt: %s' % strip(pt.get('q','')))
        print('      answer: %s' % strip(pt.get('answer','')))
        if pt.get('keywords'):          print('      keywords: %s' % (pt['keywords'],))
        if pt.get('acceptableAnswers'): print('      acceptableAnswers: %s' % (pt['acceptableAnswers'],))
        if pt.get('anyOf'):             print('      anyOf: %s' % (pt['anyOf'],))
        bd = pt.get('bandDescriptors')
        if bd:
            for tier in ('full','partial','minimal'):
                if bd.get(tier): print('      band.%-8s %s' % (tier+':', bd[tier]))
        else:
            print('      band: (none - engine falls back to GENERIC_BAND)')
    for p in r['leaves']:
        lbl = 'Q%s%s' % (p['question'], '' if not p['part'] else ''.join('(%s)'%x for x in p['part'].split('.')))
        print('-- NESA %s (%d marks) criteria --' % (lbl, p['marks']))
        for c in p['criteria']: print('   [%d] %s' % (c['marks'], c['text']))
        print('-- NESA %s sample answer --' % lbl); print(p['sampleAnswer'] or '(none)')
