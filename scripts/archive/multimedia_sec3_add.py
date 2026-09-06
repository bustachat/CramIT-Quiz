# -*- coding: utf-8 -*-
"""Stage 4 build: insert Multimedia Section III (Q16, 2020-2025) into the bank.

Refuses to write unless every gate passes:
  * per-part marks come from the COMMITTED KEY, never from this script
  * sum(parts[].marks) == question marks == 15 (validate_subjects.cjs asserts this)
  * bandDescriptors are generated VERBATIM from the key's criteria rows
  * every keyword is creditable from its OWN part's model answer, using a faithful
    mirror of index.html's keywordHit() with an ASCII-only word split (JS \\W is
    ASCII-only, Python's is Unicode-aware - the discrepancy that passed two bad
    questions during the Mathematics Advanced per-part build)
  * every part self-scores FULL marks against its own model answer
  * only the writtenQuestions array is rewritten; mcQuestions and studyNotes stay
    byte-identical (multimedia.json must never round-trip through json.dumps)
"""
import json, io, re, sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from multimedia_sec3_content import CONTENT

SUBJ = 'subjects/multimedia.json'
KEY = 'data/answer-key/written/multimedia.json'

# ── engine mirror ──────────────────────────────────────────────────────────
def strip_html(h):
    h = re.sub(r'<[^>]+>', ' ', h)
    h = h.replace('&nbsp;', ' ').replace('&amp;', '&')
    return re.sub(r'\s+', ' ', h).strip()

def keyword_hit(kw, sa):
    """Faithful mirror of index.html keywordHit(). ASCII-only split, as JS does."""
    kw = kw.lower(); sa = sa.lower()
    if kw in sa:
        return True
    for word in re.split(r'[^A-Za-z0-9_]+', sa):   # JS \W+ is ASCII-only
        if not word:
            continue
        if word.startswith(kw) or kw.startswith(word):
            return True
        stem = min(4, len(word), len(kw))
        if stem >= 4 and word[:stem] == kw[:stem]:
            return True
    return False

def score_one(keywords, min_kw, max_mark, student):
    matched = sum(1 for k in keywords if keyword_hit(k, student))
    earned = round((matched / len(keywords)) * max_mark)
    if matched < min_kw:
        earned = min(earned, max_mark // 2)
    return matched, earned

# ── band descriptor collapse (the standing rule) ───────────────────────────
def collapse(criteria):
    """top row -> full | middle rows joined -> partial | bottom row -> minimal."""
    rows = sorted(criteria, key=lambda c: -int(c['marks']))
    texts = [r['text'].strip() for r in rows]
    assert len(texts) >= 3, "unexpected band count %d" % len(texts)
    return {
        'full': texts[0],
        'partial': ' OR '.join(texts[1:-1]),
        'minimal': texts[-1],
    }

# ── load ground truth ──────────────────────────────────────────────────────
key = json.load(io.open(KEY, encoding='utf-8'))
official = {}
for y, entries in key['papers'].items():
    for e in entries:
        if str(e['question']) == '16':
            official[(int(y), '(%s)' % e['part'])] = e

print("official Section III parts in key:", len(official))
assert len(official) == 12, len(official)

# ── build entries ──────────────────────────────────────────────────────────
new_entries = []
failures = []

for year in sorted(CONTENT):
    spec = CONTENT[year]
    parts_out = []
    total = 0
    for p in spec['parts']:
        off = official[(year, p['label'])]
        marks = int(off['marks'])
        assert marks == p['marks'], "%d %s: content says %d, KEY says %d" % (year, p['label'], p['marks'], marks)
        total += marks

        band = collapse(off['criteria'])

        # acceptance gate: every keyword creditable from this part's own model answer
        plain = strip_html(p['answer'])
        missing = [k for k in p['keywords'] if not keyword_hit(k, plain)]
        if missing:
            failures.append("%d %s: %d keyword(s) NOT creditable: %s" % (year, p['label'], len(missing), missing))

        matched, earned = score_one(p['keywords'], p['minKeywords'], marks, plain)
        if earned != marks:
            failures.append("%d %s: self-score %d/%d (matched %d/%d)" % (
                year, p['label'], earned, marks, matched, len(p['keywords'])))

        parts_out.append({
            'label': p['label'],
            'marks': marks,
            'q': p['q'],
            'answer': p['answer'],
            'keywords': p['keywords'],
            'minKeywords': p['minKeywords'],
            'bandDescriptors': band,
        })

    assert total == 15, "%d totals %d, expected 15" % (year, total)

    # combined q / answer
    bits = []
    if spec['stem']:
        bits.append(spec['stem'])
    for p in parts_out:
        bits.append('%s %s <strong>(%d marks)</strong>' % (p['label'], p['q'], p['marks']))
    q_combined = '<br><br>'.join(bits)
    a_combined = '<br><br>'.join('%s %s' % (p['label'], p['answer']) for p in parts_out)

    kw_all = []
    for p in parts_out:
        for k in p['keywords']:
            if k not in kw_all:
                kw_all.append(k)

    entry = {
        'year': year,
        'marks': 15,
        'section': 'III',
        'qNum': 16,
        'q': q_combined,
        'answer': a_combined,
        'keywords': kw_all,
        'minKeywords': max(1, round(len(kw_all) * 0.4)),
        'bandDescriptors': spec['band'],
    }
    if spec['stem']:
        entry['stem'] = spec['stem']
    entry['parts'] = parts_out
    new_entries.append(entry)

if failures:
    print("\n*** REFUSING TO WRITE - %d gate failure(s) ***" % len(failures))
    for f in failures:
        print("   ", f)
    sys.exit(1)

print("all gates pass: 6 entries, 12 parts, every part self-scores full")

# ── splice into the bank, writtenQuestions array ONLY ──────────────────────
raw = io.open(SUBJ, encoding='utf-8').read()
lines = raw.split('\n')

start = next(i for i, l in enumerate(lines) if l.startswith('  "writtenQuestions": ['))
end = next(i for i in range(start + 1, len(lines)) if lines[i] == '  ],')
print("writtenQuestions occupies lines %d..%d (1-based %d..%d)" % (start, end, start + 1, end + 1))

existing = json.loads('[' + '\n'.join(lines[start + 1:end]) + ']')
print("existing written entries:", len(existing))

# Idempotent: drop any Section III entries already present, so a re-run
# REPRODUCES the file rather than duplicating Q16.
existing = [q for q in existing if int(q.get("qNum", 0)) != 16]
print("existing after dropping Q16:", len(existing))

merged = existing + new_entries
merged.sort(key=lambda q: (q['year'], int(q['qNum'])))
print("merged written entries:", len(merged))

body = json.dumps(merged, ensure_ascii=False, indent=2)
body_lines = ['  ' + l for l in body.split('\n')]      # indent to the file's level
body_lines[0] = '  "writtenQuestions": ['              # replace the bare '['
body_lines[-1] = '  ],'                                # replace the bare ']'

out = lines[:start] + body_lines + lines[end + 1:]
io.open(SUBJ, 'w', encoding='utf-8', newline='\n').write('\n'.join(out))
print("written:", SUBJ)
