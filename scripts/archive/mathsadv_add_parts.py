"""One-off (2026-09-05): brings Mathematics Advanced's written bank up to the
per-part standard (CLAUDE.md §10 rule 10).

This is `ms2_add_parts.py` with the two Standard-2-only repair passes removed
(markdown in model answers, one-entry-per-part stragglers) and one parsing rule
relaxed. The survey recorded on 2026-09-05 established that Advanced needs none
of that pre-work — 0 unreadable `bandDescriptors`, 0 literal `**`, 0 split
entries — so those are asserted here rather than fixed: if the assumption ever
stops holding, the build fails instead of silently doing nothing.

Three differences from the Standard 2 build, each forced by real data here and
each found by running it, not by reading it:

  1. STEM LABELS AFTER AN <img>. Standard 2 always prints a part label after a
     newline, `<br>` or a block close; Advanced prints `...<img ...>(a)` with the
     label straight after an inline tag, on 18 of its stems. Widening to "after
     any tag" would be wrong — `<em>f</em>(x)` and `function f(x)` are
     everywhere in this subject — so `<img ...>` is added explicitly. It must
     also tolerate a `>` INSIDE a quoted attribute: 2020 Q29's alt text reads
     `y = c ln x for c > 0`, and a plain `<img[^>]*>` stops there and loses the
     question's part (a).

  2. KEYWORD ASSIGNMENT MUST AGREE WITH THE SCORER. Standard 2 assigned a
     keyword to a part on a normalised/squashed substring match. `squash()`
     removes every separator, so it can match across a word boundary that the
     engine's own matcher never would: on 2025 Q25 part (a), `odd` was found
     inside "...x sin x. So d/dx..." -> "...sinxsoddxsin...". A part is now
     given a keyword only if it passes that test AND the engine's own
     `keyword_hit()` fires on that part's model answer — so a part is never
     scored against a concept the engine cannot credit there.

  3. (WAS: one recovered part label.) `build_written_key.py` used to lose the `(b)`
     label on 2023 Q31, swallowing it into the END of part (a)'s sample answer, and this
     script carried an explicit LABEL_RECOVERY table to put it back. The extractor was
     fixed at the root on 2026-09-05 -- the label was a casualty of the same word-order
     bug -- so it now reads `a`, `b`, `c` directly and the workaround is DELETED. Its
     shape assertion is what reported the change, rather than silently re-patching data
     that no longer needed patching.

Everything else is deliberately unchanged from the Standard 2 build, including
the acceptance gate that a part must score full marks when fed its own model
answer, so both subjects are built by the same rules.

⚠️ DO NOT RE-RUN THIS TO REFRESH BAND DESCRIPTORS. Since 2026-09-05 they are
maintained by `scripts/refresh_band_descriptors.py`, which re-derives them from
the committed criteria rows and carries the RELAXED damage test. The detector
below is the strict version written against the pre-fix, scrambled rows; on the
repaired rows it is mostly false positives, so re-running this would strip real
NESA wording from ~7 parts and replace it with the engine's generic text.

Run:  python scripts/archive/mathsadv_add_parts.py [--write]
"""
import json
import math
import pathlib
import re
import sys
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[2]
BANK = ROOT / "subjects" / "mathematics-advanced.json"
KEY = ROOT / "data" / "answer-key" / "written" / "mathematics-advanced.json"

# -- shared helpers (lifted verbatim from ms2_add_parts.py) -------------------

# A part label in a stem: at the start, or after a newline / <br> / a closing
# block tag / an <img> tag. The <img> case is Advanced-specific, and its body is
# `(?:[^>"]|"[^"]*")*` rather than `[^>]*` because an alt attribute can itself
# contain a `>` — see the module docstring. An optional roman sub-label may
# follow immediately.
STEM_LAB = re.compile(
    r"(?:^|\n|<br\s*/?>|</div>|</p>|<img(?:[^>\"]|\"[^\"]*\")*>)"
    r"\s*\(([a-z]{1,3})\)\s*(?:\(([ivx]{1,4})\))?\s")
# A part label in a model answer: always at the start of a line.
ANS_LAB = re.compile(r"(?:^|\n)\s*\(([a-z]{1,3})\)\s*", re.M)
# Trailing "(2 marks)" on a stem prompt — the renderer draws its own badge.
STEM_MARKS = re.compile(r"\s*\(\s*\d+\s*marks?\s*\)\s*$", re.I)

def split_labelled(text, rx):
    """-> (prefix before the first label, {top-level letter: chunk}).

    Sub-parts are folded into their parent letter, keeping their own "(i)"
    marker inline, because the engine's part is the top-level letter — that is
    what the official key's marks and criteria are grouped by here."""
    hits = list(rx.finditer(text))
    if not hits:
        return text, {}
    out = {}
    for n, m in enumerate(hits):
        end = hits[n + 1].start() if n + 1 < len(hits) else len(text)
        letter = m.group(1)
        sub = m.group(2) if m.re.groups >= 2 else None
        chunk = text[m.end():end].strip()
        if sub:
            chunk = f"({sub}) {chunk}"
        out[letter] = (out[letter] + "<br>" + chunk) if letter in out else chunk
    return text[: hits[0].start()].strip(), out


# A criteria row whose words have been emitted out of reading order by the PDF
# extractor (the build_written_key.py known issue). Advanced is by far the
# worst-hit subject, so a part with a damaged row gets NO bandDescriptors and
# falls back to the engine's generic wording rather than showing a student
# scrambled NESA text.
#
# ⚠️ The Standard 2 detector (empty / dangling function word / starts lowercase)
# is NOT strong enough here. It passed 2020 Q14(c)'s row through to the screen as
# "20 Obtains the probability of a student studyin g History as , or equivalent
# 40 merit" — found by reading a real scored answer in the browser, not by
# reading the data. Four more signals are added below; on this subject they take
# the flagged count from 42 rows to 84 of 540, and every one of the additional
# rows was read and is genuinely scrambled.
#
# This is a smell test, not a parser. It is deliberately biased toward flagging:
# a false positive costs one part the engine's generic band wording, while a
# false negative puts mangled NESA text in front of a student. The real fix is
# ordering the spans by x within each line in build_written_key.py — its own
# task, and it needs the local PDFs.
DANGLING_TAIL = re.compile(r"\b(and|or|of|the|to|for|with|from|in|a|an)\s*$", re.I)
# " ," / " ." — a space before punctuation is a layout artefact, never typed.
SPACE_PUNCT = re.compile(r"\s[,.](\s|$)")
# A trailing orphan: a lone letter or bare number stranded at the end of the row
# by the re-ordering ("... or equivalent merit x").
TRAILING_ORPHAN = re.compile(r"\s(?:[A-Za-z]|\d+)\s*$")
# NESA's stock qualifier is always the row's final clause. Anywhere else, the
# line was disturbed — except where the row genuinely joins two bulleted
# alternatives, which the extractor renders with an uppercase OR / AND.
MERIT_TAIL = re.compile(r"or equiv\w*\s+\w*merit\s*[.]?\s*$", re.I)
# A hoisted tail can land in front of the sentence and keep its own comma:
# "OFY, Finds angle or equivalent merit" is "Finds angle OFY, or equivalent
# merit". Caught by reading the shipped descriptors, not by the rules above —
# it starts uppercase and does end on the stock qualifier.
LEADING_FRAGMENT = re.compile(r"^\S+,\s")


def criteria_damaged(text):
    t = str(text).strip()
    if not t:
        return True
    if (DANGLING_TAIL.search(t) or SPACE_PUNCT.search(t)
            or TRAILING_ORPHAN.search(t) or LEADING_FRAGMENT.search(t)):
        return True
    if not t[0].isupper():          # digit-, symbol- or lowercase-initial
        return True
    if "merit" in t.lower() and not MERIT_TAIL.search(t) and " OR " not in t and " AND " not in t:
        return True
    return False


def collapse_criteria(rows):
    """NESA's N criteria rows -> the engine's fixed {full, partial, minimal}.

    Same rule VET's written review established: top row verbatim, middle rows
    joined with ' OR ', bottom row verbatim. N=2 repeats the bottom row into
    `partial`; N=1 is all-or-nothing. Returns None if ANY row is damaged."""
    rows = [r for r in rows if str(r.get("text", "")).strip()]
    if not rows or any(criteria_damaged(r["text"]) for r in rows):
        return None
    rows = sorted(rows, key=lambda r: -int(r.get("marks", 0)))
    texts = [str(r["text"]).strip() for r in rows]
    if len(texts) == 1:
        return {"full": texts[0],
                "partial": f"Does not meet the criterion: {texts[0].lower()}",
                "minimal": f"Does not meet the criterion: {texts[0].lower()}"}
    if len(texts) == 2:
        return {"full": texts[0], "partial": texts[1], "minimal": texts[1]}
    return {"full": texts[0], "partial": " OR ".join(texts[1:-1]), "minimal": texts[-1]}


def norm(s):
    return re.sub(r"[^a-z0-9.$%\- ]", "", str(s).lower())


def squash(s):
    """Letters and digits only — so a keyword written one way still matches a
    model answer that spaces or punctuates it differently."""
    return re.sub(r"[^a-z0-9]", "", str(s).lower())


# -- the offline scorer, mirrored from index.html's scoreOne() ----------------
# Used ONLY as an acceptance gate: a part must score full marks when fed its own
# model answer.

def keyword_hit(kw, sa):
    if kw in sa:
        return True
    # ⚠️ ASCII-only split, to match JavaScript's `sa.split(/\W+/)`. Python's \W
    # is Unicode-aware and treats θ, π, √ as WORD characters; JavaScript's does
    # not and splits on them. Using Python's default made this gate strictly
    # more generous than the engine, and it passed two questions the engine
    # then scored below full (2024 Q31 4/6 and 2025 Q28 3/4 — 'θ < 2' matched
    # the bare word 'θ' here and matched nothing in the browser). Found by
    # scoring every question in the real engine, not by reading the code.
    for word in re.split(r"[^A-Za-z0-9_]+", sa):
        if not word:
            continue
        if word.startswith(kw) or kw.startswith(word):
            return True
        stem = min(4, len(word), len(kw))
        if stem >= 4 and word[:stem] == kw[:stem]:
            return True
    return False


def score(keywords, min_kw, max_mark, answer):
    sa = str(answer).lower()
    if not keywords or max_mark <= 0:
        return 0
    matched = sum(1 for k in keywords if keyword_hit(k.lower(), sa))
    min_kw = min_kw or math.ceil(len(keywords) / 2)
    earned = round((matched / len(keywords)) * max_mark)
    # Python rounds .5 to even; JS Math.round always rounds .5 up.
    exact = (matched / len(keywords)) * max_mark
    if abs(exact - math.floor(exact) - 0.5) < 1e-9:
        earned = math.floor(exact) + 1
    if matched < min_kw:
        earned = min(earned, max_mark // 2)
    return earned


def strip_html(s):
    return re.sub(r"<[^>]+>", " ", str(s))


# -- main --------------------------------------------------------------------

def main():
    write = "--write" in sys.argv
    bank = json.loads(BANK.read_text(encoding="utf-8"))
    key = json.loads(KEY.read_text(encoding="utf-8"))

    official = defaultdict(list)
    for yr, parts in key["papers"].items():
        for p in parts:
            official[(int(yr), str(p["question"]))].append(p)

    W = bank["writtenQuestions"]
    failures = []
    orphan_log = []
    skipped = []
    damaged = []
    multi_count = 0
    built = 0

    # -- preconditions the survey established, asserted rather than fixed ----
    md = [f'{q["year"]} Q{q["qNum"]}' for q in W if "**" in str(q.get("answer", ""))]
    split = [f'{q["year"]} Q{q["qNum"]}' for q in W
             if not re.fullmatch(r"\d+", str(q["qNum"]))]
    unreadable = [f'{q["year"]} Q{q["qNum"]}' for q in W
                  if not all(k in (q.get("bandDescriptors") or {})
                             for k in ("full", "partial", "minimal"))]
    for label, hits in (("literal ** markdown in a model answer", md),
                        ("one-entry-per-part straggler (rule 9)", split),
                        ("bandDescriptors the engine cannot read", unreadable)):
        print(f"precondition — {label}: {len(hits)}")
        if hits:
            failures.append(f"precondition broken ({label}): {hits}")

    for q in W:
        qn = str(q["qNum"])
        o_all = official.get((q["year"], qn), [])
        # A part the bank deliberately excludes (a drawing task the engine
        # cannot present) is declared in omittedParts. It has no stem, no model
        # answer and no marks in the bank, so it must not become a part[].
        omitted = {str(op.get("part")) for op in (q.get("omittedParts") or [])}
        o = [p for p in o_all if str(p["part"] or "").split(".")[0] not in omitted]
        letters = []
        for p in o:
            L = str(p["part"] or "").split(".")[0]
            if L and L not in letters:
                letters.append(L)
        multi = len(o) > 1 and len(letters) > 1
        if not multi:
            continue
        multi_count += 1

        crit_by_letter = defaultdict(list)
        marks_by_letter = defaultdict(int)
        for p in o:
            L = str(p["part"] or "").split(".")[0]
            crit_by_letter[L] += (p.get("criteria") or [])
            marks_by_letter[L] += int(p["marks"])

        stem_pre, stem_parts = split_labelled(str(q.get("q", "")), STEM_LAB)
        _, ans_parts = split_labelled(str(q.get("answer", "")), ANS_LAB)
        missing = [L for L in letters if L not in stem_parts or L not in ans_parts]
        if missing:
            failures.append(
                f"{q['year']} Q{qn}: no stem/answer text for part(s) {missing} "
                f"(stem has {sorted(stem_parts)}, answer has {sorted(ans_parts)})")
            continue

        # keyword -> part, assigned ONLY where the keyword appears in that
        # part's own model answer AND the engine's own keyword_hit() would
        # credit it there. Weaker evidence makes a part unwinnable, which is
        # what the acceptance gate below exists to catch; the keyword_hit()
        # condition additionally stops squash() matching across a word boundary
        # the scorer would never join (2025 Q25(a), 'odd' inside "So d/dx").
        evidence = {}
        for L in letters:
            ev = ans_parts[L] + " "
            for p in o:
                if str(p["part"] or "").split(".")[0] == L:
                    ev += str(p.get("sampleAnswer", "")) + " "
                    ev += " ".join(c.get("text", "") for c in (p.get("criteria") or []))
            evidence[L] = norm(strip_html(ev))
        answer_text = {L: norm(strip_html(ans_parts[L])) for L in letters}
        answer_sq = {L: squash(strip_html(ans_parts[L])) for L in letters}
        answer_raw = {L: strip_html(ans_parts[L]).lower() for L in letters}
        all_kw = q.get("keywords") or []
        all_acc = q.get("acceptableAnswers") or []
        assigned = {L: [] for L in letters}
        orphaned = []
        for kw in all_kw:
            k, ks = norm(kw), squash(kw)
            hits = [L for L in letters
                    if ((k and k in answer_text[L]) or (ks and ks in answer_sq[L]))
                    and keyword_hit(kw.lower(), answer_raw[L])]
            for L in hits:
                assigned[L].append(kw)
            if not hits:
                orphaned.append(kw)
        if orphaned:
            # Not dropped from the question — `keywords` is untouched; they
            # simply take no part in per-part scoring.
            orphan_log.append((q["year"], qn, orphaned))

        parts = []
        for L in letters:
            prompt = STEM_MARKS.sub("", stem_parts[L]).strip()
            prompt = re.sub(r"(?:<br\s*/?>\s*)+$", "", prompt).strip()
            part = {
                "label": f"({L})",
                "marks": marks_by_letter[L],
                "q": prompt,
                "answer": ans_parts[L],
            }
            kwL = assigned[L]
            accL = [a for a in all_acc if norm(a) and norm(a) in evidence[L]]
            if accL and not kwL:
                part["acceptableAnswers"] = accL
            if kwL:
                part["keywords"] = kwL
                part["minKeywords"] = max(1, math.ceil(len(kwL) / 2))
            bd = collapse_criteria(crit_by_letter[L])
            if bd:
                part["bandDescriptors"] = bd
            else:
                damaged.append(f'{q["year"]} Q{qn}{part["label"]}')
            parts.append(part)

        total = sum(p["marks"] for p in parts)
        bare = [p["label"] for p in parts
                if "keywords" not in p and "acceptableAnswers" not in p]
        if total != q["marks"]:
            failures.append(f"{q['year']} Q{qn}: parts total {total}, question is {q['marks']}")
            continue
        if bare:
            # Not a build failure. Every case in this subject is a "Show
            # that ..." part whose result the stem already states, so the
            # question's keywords all target the results DERIVED in the later
            # parts and none of them belongs here. Authoring one from the
            # printed target would score a student full marks for copying the
            # prompt. Such a question keeps today's single box rather than
            # being given a part that can only ever score 0.
            skipped.append((q["year"], qn, bare))
            continue
        # ACCEPTANCE GATE: each part, fed its own model answer, must earn full
        # marks for that part.
        bad = []
        for p in parts:
            if "keywords" not in p:
                continue
            got = score(p["keywords"], p.get("minKeywords"), p["marks"],
                        strip_html(p["answer"]))
            if got < p["marks"]:
                bad.append(f'{p["label"]} {got}/{p["marks"]}')
        if bad:
            failures.append(f"{q['year']} Q{qn}: model answer does not self-score full: {bad}")
            continue
        if stem_pre:
            q["stem"] = stem_pre
        q["parts"] = parts
        built += 1

    print(f"\nmulti-part questions   : {multi_count}")
    print(f"questions given parts[]: {built}")
    if skipped:
        print(f'\nnot given parts[] — a "Show that ..." part whose result the '
              f"stem already states, so no keyword belongs to it "
              f"({len(skipped)} questions):")
        for y, qn, bare in skipped:
            print(f"   {y} Q{qn}: {bare}")
    if damaged:
        print(f"\nparts left WITHOUT bandDescriptors (criteria row damaged in the "
              f"committed key): {len(damaged)}")
        print("   " + ", ".join(damaged))
    orphans = sum(len(o[2]) for o in orphan_log)
    print(f"\nkeywords in NO part's model answer (kept on the question, unused "
          f"per-part): {orphans} across {len(orphan_log)} questions")
    for y, qn, ks in orphan_log:
        print(f"   {y} Q{qn}: {ks}")
    print(f"\nwritten entries        : {len(W)}")
    if failures:
        print(f"\n{len(failures)} FAILURE(S):")
        for f in failures:
            print("  ", f)
    if write:
        if failures:
            print("\nrefusing to write with failures outstanding")
            sys.exit(1)
        BANK.write_text(json.dumps(bank, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"\nwritten -> {BANK}")
    else:
        print("\ndry run — pass --write to save")


if __name__ == "__main__":
    main()
