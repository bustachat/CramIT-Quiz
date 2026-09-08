# -*- coding: utf-8 -*-
"""Mathematics Advanced Stage 6b - apply the review's corrections.

Every edit asserts its old value, so a re-run on changed data fails loudly
rather than silently doing something else.

Content was clean: all 126 questions' RESULTS agree with NESA. What is fixed
here is teaching/scoring/presentation only - no mark, stem meaning, MC
question or omission declaration is touched.

  A  one broken <img alt="..."> whose bare '>' closed the tag early, so the
     rest of the attribute rendered as visible text (1 instance repo-wide)
  B  four sibling-part keyword leaks - a keyword belonging to a DIFFERENT
     part, credited in its own part only as a SUFFIX FRAGMENT of a longer
     number ("83" inside 783.7168)
  C  one model answer that justified its result by forward-referencing a
     later part, where NESA's argues from the values the question gives
  D  nine part prompts carrying a duplicated "(N marks)" the accordion
     header already prints

Also folded in, found by the same two sweeps run repo-wide (Standard 2 is
ledgered, so these are recorded in that ledger's notes as well):
  E  two more sibling-part keyword leaks
  F  three part prompts whose duplicated label sweep E missed because a
     TABLE follows it, so it is not at the end of the raw string

DELIBERATELY NOT CHANGED, and this is the point of probing rather than
reasoning: 2020 Q11(b) also carries part (c)'s answer '45'. Dropping it
measured 2/2 -> 1/2 on a fully correct working, because that working writes
"450" and the keyword was carrying the match. It stays.
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
            if x.get('year') == y and str(x.get('qNum')) == str(n)][0]


def part(q, label):
    return [p for p in q['parts'] if p['label'] == label][0]


def sub(o, field, old, new, why):
    cur = o[field]
    assert cur.count(old) == 1, (why, 'expected 1 occurrence, found', cur.count(old))
    o[field] = cur.replace(old, new)
    EDITS.append(why)


def drop_kw(o, kw, why):
    cur = list(o.get('keywords') or [])
    assert kw in cur, (why, kw, cur)
    cur.remove(kw)
    assert cur, (why, 'would leave no keywords')
    o['keywords'] = cur
    if o.get('minKeywords') and o['minKeywords'] > len(cur):
        o['minKeywords'] = len(cur)
    EDITS.append(why)


def strip_label(o, label, why):
    """Remove ONE duplicated '(N marks)' from a part prompt.

    Two wrappers occur, and each is matched exactly rather than by a regex, so
    an unexpected third shape fails the assertion instead of being mangled:
      Maths Advanced  ' <strong>(N marks)</strong>' followed by <br><br>
      Standard 2      ' (N marks)' (sometimes double-spaced) before a table
    The separator that follows is kept - it divides the prompt from the
    omission note, image or table underneath.
    """
    cur = o['q']
    assert cur.count(label) == 1, (why, cur.count(label))
    for old in (' <strong>%s</strong>' % label, '  %s' % label, ' %s' % label):
        if old in cur:
            nxt = cur.replace(old, '', 1)
            break
    else:
        raise AssertionError((why, 'no known wrapper around the label'))
    assert label not in nxt, (why, 'label survived')
    assert len(cur) - len(nxt) <= len(label) + 20, (why, 'removed too much')
    o['q'] = nxt
    EDITS.append(why)


# =====================================================================
# Mathematics Advanced
# =====================================================================
p, d = bank('mathematics-advanced')

# --- A. the broken alt attribute -------------------------------------
# A bare '>' inside a quoted attribute still closes the tag: the HTML parser
# ends <img at the first '>' it sees, so everything after it rendered as
# literal text. One instance repo-wide.
sub(find(d, 2020, 29), 'q',
    'alt="Graph of y = c ln x for c > 0,',
    'alt="Graph of y = c ln x for c &gt; 0,',
    "MA 2020 Q29: escape the '>' inside the img alt so the tag does not close early")

# --- B. sibling-part keyword leaks -----------------------------------
drop_kw(part(find(d, 2020, 14), '(c)'), '5',
        "MA 2020 Q14(c): drop '5' - it is part (b)'s figure and matched (c) only "
        "inside 1560; a correct '10/39' now scores 2/2 instead of 1/2")
drop_kw(part(find(d, 2022, 17), '(a)'), '23',
        "MA 2022 Q17(a): drop '23' - part (b)'s answer, matched (a) only inside 234")
drop_kw(part(find(d, 2022, 32), '(a)'), '83',
        "MA 2022 Q32(a): drop '83' - part (b)'s answer, matched (a) only inside 783.7168")
drop_kw(part(find(d, 2023, 15), '(a)'), '40',
        "MA 2023 Q15(a): drop '40' - part (b)'s period count, matched (a) only inside 34 140")

# --- C. a model answer that forward-references a later part ----------
OLD31 = ('No. If F and S were independent then P(S|F) would equal P(S). Here '
         'P(S|F) = 1/3, while P(S) = 4/5 (found in part (b)), and 1/3 ≠ 4/5, '
         'so the two events are not independent.')
NEW31 = ('No. Independence would require P(F|S) = P(F). The question gives '
         'P(F|S) = 1/8 and P(F) = 3/10, and 1/8 ≠ 3/10, so the two events are '
         'not independent. (Equivalently, independence would require '
         'P(S|F) = P(S): P(S|F) = 1/3 while P(S) = 4/5 from part (b).)')
q31 = find(d, 2023, 31)
sub(part(q31, '(a)'), 'answer', OLD31, NEW31,
    "MA 2023 Q31(a): justify non-independence from the GIVEN values, as NESA does, "
    "instead of forward-referencing part (b)'s P(S)")
sub(q31, 'answer', OLD31, NEW31,
    "MA 2023 Q31: same on the combined answer")

# --- D. duplicated mark labels in part prompts -----------------------
for y, n, lab, label in [
        (2020, 11, '(c)', '(1 mark)'),
        (2021, 17, '(b)', '(1 mark)'),     # a stray label mid-sentence, not a sub-part
        (2021, 27, '(d)', '(1 mark)'),
        (2021, 28, '(c)', '(1 mark)'),
        (2022, 27, '(b)', '(2 marks)'),
        (2023, 18, '(c)', '(1 mark)'),
        (2024, 17, '(c)', '(2 marks)'),
        (2024, 25, '(c)', '(2 marks)'),
        (2025, 15, '(c)', '(2 marks)')]:
    strip_label(part(find(d, y, n), lab), label,
                "MA %d Q%d%s: remove the duplicated %s the accordion header already prints"
                % (y, n, lab, label))
save(p, d)

# =====================================================================
# Mathematics Standard 2 - same two sweeps, run repo-wide
# =====================================================================
p, d = bank('mathematics-standard-2')
drop_kw(part(find(d, 2022, 31), '(b)'), '5',
        "MS2 2022 Q31(b): drop '5' - part (c)'s figure, matched (b) only inside 35")
drop_kw(part(find(d, 2025, 40), '(b)'), '600',
        "MS2 2025 Q40(b): drop '600' - part (a)'s male count, matched (b) only inside 12 600")
for y, n, lab, label in [(2020, 26, '(c)', '(2 marks)'),
                         (2022, 24, '(b)', '(2 marks)'),
                         (2023, 21, '(a)', '(1 mark)')]:
    strip_label(part(find(d, y, n), lab), label,
                "MS2 %d Q%d%s: remove the duplicated %s - sweep E missed it because a "
                "TABLE follows, so it is not at the end of the raw string" % (y, n, lab, label))
save(p, d)

print('applied %d edits' % len(EDITS))
for e in EDITS:
    print('   ', e)
