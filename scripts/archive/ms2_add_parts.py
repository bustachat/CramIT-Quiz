"""One-off (2026-09-05): brings Mathematics Standard 2's written bank up to the
per-part standard (CLAUDE.md §10 rules 9 and 10), and fixes three defects found
while surveying it.

Runs four passes, each independently asserted:

  1. MARKDOWN   31 model answers contain literal `**bold**` markdown, which the
                renderer prints verbatim as asterisks. Converted to <strong>.
  2. MERGE      11 entries are still one-per-part (2020 Q23/Q34/Q35, 2021
                Q26/Q27) -> merged to 5, per rule 9.
  3. BANDS      57 questions carry bandDescriptors the engine can never read —
                38 keyed {high,mid,low} and 19 keyed {1,2,3,...} — so the
                student is shown the literal string "undefined" as their
                feedback. Normalised to {full,partial,minimal}: {high,mid,low}
                is a pure key rename (content untouched), and the numbered ones
                are rebuilt from the OFFICIAL criteria rows in
                data/answer-key/written/, using the same top/middle/bottom
                collapse rule VET's review established.
  4. PARTS      parts[] for every question covering more than one official part.
                Per-part marks come from the committed answer key (ground
                truth). Prompts are split out of the stem, model answers out of
                `answer`, and per-part bandDescriptors from that part's own
                criteria rows. Per-part keywords are assigned from the
                question's existing list by evidence, then GATED: a part must
                score full marks when fed its own model answer, or the build
                fails and reports it.

Re-run safely (2026-09-06): the damage test and band collapse are IMPORTED from
`scripts/refresh_band_descriptors.py` so this build cannot drift from it, and the
keyword gate now matches the engine exactly (ASCII-only word split, and a keyword
must also pass the engine's own keyword_hit on the part's model answer). Re-running
against the repaired criteria rows dropped the 6 per-part keywords the engine could
never credit and gained one acceptableAnswer NESA's own criteria support.

Run:  python scripts/archive/ms2_add_parts.py [--write]
"""
import json
import math
import pathlib
import re
import sys
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[2]
BANK = ROOT / "subjects" / "mathematics-standard-2.json"
KEY = ROOT / "data" / "answer-key" / "written" / "mathematics-standard-2.json"

# ── shared helpers ───────────────────────────────────────────────────────────

# A part label in a stem: at the start, or after a newline / <br> / a closing tag.
# An optional roman sub-label may follow immediately — 2021 Q33 prints "(a)(i)"
# and "(a)(ii)", which a `\)\s` pattern misses entirely.
STEM_LAB = re.compile(
    r"(?:^|\n|<br\s*/?>|</div>|</p>)\s*\(([a-z]{1,3})\)\s*(?:\(([ivx]{1,4})\))?\s")
# A part label in a model answer: always at the start of a line.
ANS_LAB = re.compile(r"(?:^|\n)\s*\(([a-z]{1,3})\)\s*", re.M)
# Trailing "(2 marks)" on a stem prompt — the renderer draws its own badge.
STEM_MARKS = re.compile(r"\s*\(\s*\d+\s*marks?\s*\)\s*$", re.I)
ROMAN = ("i", "ii", "iii", "iv", "v")


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


def md_to_html(s):
    """`**x**` -> <strong>x</strong>. Only balanced pairs on one line."""
    return re.sub(r"\*\*(?!\s)(.+?)(?<!\s)\*\*", r"<strong>\1</strong>", str(s))


# ⚠️ The damage test and the band collapse are IMPORTED, not copied. Both used to be
# duplicated here and in the sibling build, and they drifted: this file's copy was written
# against the pre-2026-09-05 scrambled rows and is far too strict for the repaired ones,
# so re-running it with the local copy would have stripped real NESA wording from parts
# that now have it. scripts/refresh_band_descriptors.py owns the single implementation.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from refresh_band_descriptors import criteria_damaged, collapse_criteria  # noqa: E402


def norm(s):
    return re.sub(r"[^a-z0-9.$%\- ]", "", str(s).lower())


def squash(s):
    """Letters and digits only — so a path keyword like 'abfgd' still matches a
    model answer that writes it as 'A -> B -> F -> G -> D'."""
    return re.sub(r"[^a-z0-9]", "", str(s).lower())


# ── the offline scorer, mirrored from index.html's scoreOne() ────────────────
# Used ONLY as an acceptance gate here: a part must score full marks when fed
# its own model answer. Kept in step with the engine by the constants below.

def keyword_hit(kw, sa):
    if kw in sa:
        return True
    # ⚠️ ASCII-only split, to match JavaScript's `sa.split(/\W+/)`. Python's \W is
    # Unicode-aware and treats θ, π, √ as WORD characters; JavaScript's does not and
    # splits on them, so Python's default makes this gate strictly MORE GENEROUS than the
    # engine and can pass a part the engine then scores below full. Found on the sibling
    # Advanced build by scoring every question in the real engine.
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


def norm_raw(s):
    """The part's model answer as the ENGINE sees it: HTML stripped, lowercased."""
    return strip_html(s).lower()


def strip_html(s):
    return re.sub(r"<[^>]+>", " ", str(s))


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    write = "--write" in sys.argv
    bank = json.loads(BANK.read_text(encoding="utf-8"))
    key = json.loads(KEY.read_text(encoding="utf-8"))

    official = defaultdict(list)
    for yr, parts in key["papers"].items():
        for p in parts:
            official[(int(yr), str(p["question"]))].append(p)

    W = bank["writtenQuestions"]
    report = {"markdown": 0, "merged": 0, "bands": 0, "parts": 0}
    failures = []
    orphan_log = []
    skipped = []
    damaged = []

    # ── pass 1: markdown in model answers ───────────────────────────────────
    for q in W:
        a = str(q.get("answer", ""))
        if "**" in a:
            fixed = md_to_html(a)
            if "**" in fixed:
                failures.append(f"{q['year']} Q{q['qNum']}: unbalanced ** left after conversion")
            q["answer"] = fixed
            report["markdown"] += 1

    # ── pass 2: merge the one-entry-per-part stragglers (rule 9) ────────────
    groups = defaultdict(list)
    for q in W:
        qn = str(q["qNum"])
        if not re.fullmatch(r"\d+", qn):
            groups[(q["year"], qn.split("(")[0])].append(q)
    merged_out = []
    for (yr, base), members in sorted(groups.items()):
        members.sort(key=lambda m: str(m["qNum"]))
        labels = [re.sub(r"^\d+", "", str(m["qNum"])) for m in members]
        stems, answers, kws, accs = [], [], [], []
        for m, lab in zip(members, labels):
            body = str(m.get("q", "")).strip()
            if m.get("image"):
                body += (f'<img src="{m["image"]}" alt="Question diagram" '
                         'style="max-width:100%;height:auto;display:block;margin:14px auto">')
            stems.append(f'{lab} {body} <strong>({m["marks"]} mark'
                         f'{"s" if m["marks"] > 1 else ""})</strong>')
            answers.append(f'{lab} {str(m.get("answer","")).strip()}')
            kws += m.get("keywords") or []
            accs += m.get("acceptableAnswers") or []
        first = members[0]
        merged = {k: v for k, v in first.items()
                  if k not in ("q", "answer", "keywords", "acceptableAnswers",
                               "image", "qNum", "marks", "minKeywords", "bandDescriptors")}
        merged["year"] = yr
        merged["qNum"] = base
        merged["marks"] = sum(m["marks"] for m in members)
        merged["q"] = "<br><br>".join(stems)
        merged["answer"] = "\n\n".join(answers)
        seen = set()
        merged["keywords"] = [k for k in kws if not (k in seen or seen.add(k))]
        if accs:
            seen = set()
            merged["acceptableAnswers"] = [a for a in accs if not (a in seen or seen.add(a))]
        merged["_mergedFrom"] = [str(m["qNum"]) for m in members]
        merged_out.append(merged)
        report["merged"] += 1
    if merged_out:
        keep = [q for q in W if re.fullmatch(r"\d+", str(q["qNum"]))]
        by_year_pos = {}
        for i, q in enumerate(W):
            by_year_pos.setdefault((q["year"], str(q["qNum"]).split("(")[0]), i)
        for m in merged_out:
            keep.append(m)
        keep.sort(key=lambda q: by_year_pos.get((q["year"], str(q["qNum"]).split("(")[0]), 10**6))
        W = keep
        bank["writtenQuestions"] = W

    # ── pass 3 + 4: bands and parts ─────────────────────────────────────────
    for q in W:
        q.pop("_mergedFrom", None)
        qn = str(q["qNum"])
        o_all = official.get((q["year"], qn), [])
        # A part the bank deliberately excludes (a drawing task the engine
        # cannot present) is declared in omittedParts. It has no stem, no model
        # answer and no marks in the bank, so it must not become a part[] —
        # 2020 Q24(a) is exactly this, and treating it as missing text would
        # wrongly disqualify the whole question.
        omitted = {str(op.get("part")) for op in (q.get("omittedParts") or [])}
        o = [p for p in o_all if str(p["part"] or "").split(".")[0] not in omitted]
        # top-level letters, in official order
        letters = []
        for p in o:
            L = str(p["part"] or "").split(".")[0]
            if L and L not in letters:
                letters.append(L)
        multi = len(o) > 1 and len(letters) > 1

        # criteria rows grouped by top-level letter
        crit_by_letter = defaultdict(list)
        marks_by_letter = defaultdict(int)
        for p in o:
            L = str(p["part"] or "").split(".")[0]
            crit_by_letter[L] += (p.get("criteria") or [])
            marks_by_letter[L] += int(p["marks"])

        # ---- pass 4: parts[] --------------------------------------------
        if multi:
            stem_pre, stem_parts = split_labelled(str(q.get("q", "")), STEM_LAB)
            _, ans_parts = split_labelled(str(q.get("answer", "")), ANS_LAB)
            missing = [L for L in letters if L not in stem_parts or L not in ans_parts]
            if missing:
                failures.append(
                    f"{q['year']} Q{qn}: no stem/answer text for part(s) {missing} "
                    f"(stem has {sorted(stem_parts)}, answer has {sorted(ans_parts)})")
            else:
                # keyword -> part, assigned ONLY where the keyword appears in
                # that part's own model answer. Weaker evidence (the official
                # sample answer / criteria wording) was tried and rejected: it
                # hands a part keywords its own model answer does not contain,
                # so the part becomes unwinnable — which is exactly what the
                # acceptance gate below caught. `evidence` is kept for
                # acceptableAnswers, where an exact-match list is not scored
                # proportionally and so cannot make a part unwinnable.
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
                all_kw = q.get("keywords") or []
                all_acc = q.get("acceptableAnswers") or []
                assigned = {L: [] for L in letters}
                orphaned = []
                answer_raw = {L: norm_raw(ans_parts[L]) for L in letters}
                for kw in all_kw:
                    k, ks = norm(kw), squash(kw)
                    # ⚠️ Also require the engine's OWN matcher to fire. squash() strips
                    # every separator, so it can match across a word boundary the scorer
                    # never joins -- on the sibling Advanced build it found `odd` inside
                    # "...x sin x. So d/dx..." -> "...sinxsoddxsin...". Without this a part
                    # is scored against a concept the engine cannot credit there.
                    hits = [L for L in letters
                            if ((k and k in answer_text[L]) or (ks and ks in answer_sq[L]))
                            and keyword_hit(kw.lower(), answer_raw[L])]
                    for L in hits:
                        assigned[L].append(kw)
                    if not hits:
                        orphaned.append(kw)
                if orphaned:
                    # Not dropped from the question — `keywords` is untouched;
                    # they simply take no part in per-part scoring, because no
                    # part's model answer contains them.
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
                elif bare:
                    # Not a build failure: some parts genuinely have nothing a
                    # keyword can match — "Plot these two points on the
                    # scatterplot", "Complete the table" — or the question is
                    # one of the ~40 Standard 2 entries that never had keywords.
                    # Such a question keeps today's single box and single score
                    # rather than being given a part that can only ever score 0.
                    skipped.append((q["year"], qn, bare))
                else:
                    # ACCEPTANCE GATE: each part, fed its own model answer,
                    # must earn full marks for that part.
                    bad = []
                    for p in parts:
                        if "keywords" not in p:
                            continue
                        got = score(p["keywords"], p.get("minKeywords"),
                                    p["marks"], strip_html(p["answer"]))
                        if got < p["marks"]:
                            bad.append(f'{p["label"]} {got}/{p["marks"]}')
                    if bad:
                        failures.append(f"{q['year']} Q{qn}: model answer does not self-score full: {bad}")
                    else:
                        if stem_pre:
                            q["stem"] = stem_pre
                        q["parts"] = parts
                        report["parts"] += 1

        # ---- pass 3: question-level bands the engine can actually read ---
        bd = q.get("bandDescriptors") or {}
        if not all(k in bd for k in ("full", "partial", "minimal")):
            if {"high", "mid", "low"} <= set(bd):
                # pure key rename — wording untouched
                q["bandDescriptors"] = {"full": bd["high"], "partial": bd["mid"], "minimal": bd["low"]}
            elif q.get("parts"):
                # compose from the NESA-derived per-part descriptors
                def join(tier):
                    return " ".join(f'{p["label"]} {p["bandDescriptors"][tier]}'
                                    for p in q["parts"] if p.get("bandDescriptors"))
                if all(p.get("bandDescriptors") for p in q["parts"]):
                    q["bandDescriptors"] = {t: join(t) for t in ("full", "partial", "minimal")}
                else:
                    failures.append(f"{q['year']} Q{qn}: cannot rebuild bands (missing per-part criteria)")
                    continue
            else:
                rows = [c for p in o for c in (p.get("criteria") or [])]
                newbd = collapse_criteria(rows)
                if not newbd:
                    failures.append(f"{q['year']} Q{qn}: no criteria rows to rebuild bands from")
                    continue
                q["bandDescriptors"] = newbd
            report["bands"] += 1

    print(f"markdown answers fixed : {report['markdown']}")
    print(f"split entries merged   : {report['merged']} groups")
    print(f"bandDescriptors fixed  : {report['bands']}")
    print(f"questions given parts[]: {report['parts']}")
    if skipped:
        print(f"\nnot given parts[] — a part has nothing a keyword can match "
              f"({len(skipped)} questions):")
        for y, qn, bare in skipped:
            print(f"   {y} Q{qn}: {bare}")
    if damaged:
        print(f"\nparts left WITHOUT bandDescriptors (criteria row damaged in the "
              f"committed key): {len(damaged)}")
        print("   " + ", ".join(damaged[:10]) + (" ..." if len(damaged) > 10 else ""))
    orphans = sum(len(o[2]) for o in orphan_log)
    print(f"keywords in NO part's model answer (kept on the question, unused per-part): "
          f"{orphans} across {len(orphan_log)} questions")
    print(f"written entries now    : {len(W)}")
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
