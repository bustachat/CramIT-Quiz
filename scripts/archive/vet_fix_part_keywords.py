"""One-off (2026-09-06): fix the 18 VET Construction per-part keywords the engine can
never credit in their own part.

Surfaced by measuring every part in the real engine after the Standard 2 equivalents were
closed. A keyword that `keywordHit()` cannot match against that part's own model answer
inflates the denominator of `scoreOne()`, so a partial answer is marked harsher than
intended, and the AI marker is handed a "key concept" the model answer does not
demonstrate. Every VET part still scored full from its own model answer, so nothing was
blocked -- this is accuracy, not breakage.

⚠️ These are NOT the same defect as Standard 2's six. There a script had mis-assigned a
question-level keyword to a part, so removal was simply undoing a bad assignment. VET's
were authored PER PART by a human, so each one was read and classified on its merits:

  FORM (4)   The concept IS in the model answer, in a form the matcher cannot reach:
             "paring" vs `pare`, "honing" vs `hone`, "hiring" vs `hire`. The keyword takes
             the model answer's own form.
             ⚠️ This is NOT free, and an assertion caught the claim that it was. No single
             keyword can match both forms: keywordHit's prefix branches compare `paring`
             against `pare` and diverge at the fourth character, and its 4-character stem
             rule sees "pari" vs "pare". So a student who writes the bare stem loses that
             one keyword. It is still strictly better than what was there, because before
             the change NO answer could earn it -- not even a perfect one -- so the mark
             was unreachable rather than merely harder.

  INERT (1 part, 2 keywords)   2023 Q16(a)(i) carries `keywords` and `acceptableAnswers`
             holding the IDENTICAL six accepted names. scoreOne() short-circuits on
             `acceptableAnswers`, so that part's `keywords` never scores anything offline,
             and index.html sends `p.keywords || p.acceptableAnswers` to the AI marker --
             the same six either way. The duplicate is deleted as dead data. This is a
             no-op in behaviour, not a defect that was costing marks.

  REDUNDANT (12)   The concept is genuinely absent from the model answer, and in every
             case another keyword already covers it (`recycl` for `reuse`, `circle` /
             `circumference` for `pi`, `time` for `quick`, `safety glasses` / `goggles`
             for `eye`, `material` for `timber`, `sides` for `perimeter`, ...). Removed.
             The alternative -- extending each model answer until it demonstrates the
             concept -- is authoring content in the one subject a human has reviewed end
             to end, and is not done here.

`minKeywords` is deliberately left alone. It stays valid (never exceeds the shortened
list), and removing a keyword already makes a partial answer score slightly better;
lowering the threshold too would compound that.

Run:  python scripts/archive/vet_fix_part_keywords.py [--write]
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
BANK = ROOT / "subjects" / "vet-construction.json"

# (year, qNum, part label) -> {old keyword: new keyword}
FORM = {
    (2021, "16", "(b)"): {"pare": "paring"},
    (2021, "16", "(d)"): {"hone": "honing"},
    (2022, "16", "(b)"): {"hone": "honing"},
    (2022, "16", "(c)"): {"hire": "hiring"},
}

# (year, qNum, part label) -> [keywords to drop], each with the keyword that already
# carries the concept, recorded so the judgement is auditable rather than asserted.
REDUNDANT = {
    (2021, "18", "(b)"): {"pi": "circumference"},
    (2023, "16", "(a)(ii)"): {"eye": "safety glasses"},
    (2023, "17", "(c)"): {"reuse": "recycl"},
    (2023, "18", "(c)"): {"understood": "clarity"},
    (2024, "17", "(a)"): {"quick": "time"},
    (2024, "17", "(b)"): {"rework": "reorder"},
    (2024, "18", "(a)"): {"expectation": "client"},
    (2024, "19", "(a)"): {"perimeter": "sides"},
    (2024, "19", "(b)"): {"pi": "circle"},
    (2024, "19", "(d)"): {"delivery": "km"},
    (2025, "17", "(a)"): {"timber": "material"},
    (2025, "18", "(a)"): {"finish": "specification"},
}

# A 1-mark "name the tool" part whose keywords are really an accept-list.
NAMING = {(2023, "16", "(a)(i)")}


def strip_html(s):
    return re.sub(r"<[^>]+>", " ", str(s))


def keyword_hit(kw, sa):
    """index.html's keywordHit(), mirrored. ASCII-only split, as JavaScript's \\W is."""
    if kw in sa:
        return True
    for word in re.split(r"[^A-Za-z0-9_]+", sa):
        if not word:
            continue
        if word.startswith(kw) or kw.startswith(word):
            return True
        stem = min(4, len(word), len(kw))
        if stem >= 4 and word[:stem] == kw[:stem]:
            return True
    return False


def main():
    write = "--write" in sys.argv
    bank = json.loads(BANK.read_text(encoding="utf-8"))
    failures, changed = [], []

    for q in bank["writtenQuestions"]:
        for part in (q.get("parts") or []):
            key = (q["year"], str(q["qNum"]), part["label"])
            sa = strip_html(part["answer"]).lower()
            kws = part.get("keywords") or []

            if key in FORM:
                for old, new in FORM[key].items():
                    if old not in kws:
                        failures.append(f"{key}: FORM keyword {old!r} not present")
                        continue
                    if not keyword_hit(new.lower(), sa):
                        failures.append(f"{key}: replacement {new!r} still does not match the model answer")
                        continue
                    kws[kws.index(old)] = new
                    kept = keyword_hit(new.lower(), old.lower())
                    changed.append(
                        f"{key[0]} Q{key[1]}{key[2]}: {old!r} -> {new!r}  (form; "
                        f"{'still credits' if kept else 'no longer credits'} a bare {old!r})")

            if key in REDUNDANT:
                for drop, covered_by in REDUNDANT[key].items():
                    if drop not in kws:
                        failures.append(f"{key}: keyword {drop!r} not present")
                        continue
                    if keyword_hit(drop.lower(), sa):
                        failures.append(f"{key}: {drop!r} DOES match its model answer — do not drop it")
                        continue
                    if covered_by not in kws:
                        failures.append(f"{key}: cover keyword {covered_by!r} missing")
                        continue
                    if not keyword_hit(covered_by.lower(), sa):
                        failures.append(f"{key}: cover keyword {covered_by!r} does not match either")
                        continue
                    kws.remove(drop)
                    changed.append(f"{key[0]} Q{key[1]}{key[2]}: dropped {drop!r}  (covered by {covered_by!r})")

            if key in NAMING:
                acc = part.get("acceptableAnswers")
                # Only safe to delete because the two lists are IDENTICAL: offline scoring
                # short-circuits on acceptableAnswers, and the AI marker is sent
                # `p.keywords || p.acceptableAnswers`, so both paths keep the same six.
                if list(acc or []) != list(kws):
                    failures.append(f"{key}: keywords and acceptableAnswers differ — "
                                    f"deleting the duplicate would change marking")
                    continue
                part.pop("keywords", None)
                part.pop("minKeywords", None)
                kws = []
                changed.append(f"{key[0]} Q{key[1]}{key[2]}: deleted {len(acc)} duplicate "
                               f"keywords (identical to acceptableAnswers, never scored)")

            if kws:
                part["keywords"] = kws
                mk = part.get("minKeywords")
                if mk and mk > len(kws):
                    failures.append(f"{key}: minKeywords {mk} now exceeds {len(kws)} keywords")

    # Whole-bank invariant: no part may carry a keyword its own model answer cannot credit.
    remaining = []
    for q in bank["writtenQuestions"]:
        for part in (q.get("parts") or []):
            sa = strip_html(part["answer"]).lower()
            for k in (part.get("keywords") or []):
                if not keyword_hit(k.lower(), sa):
                    remaining.append(f'{q["year"]} Q{q["qNum"]}{part["label"]} {k!r}')

    for line in changed:
        print("  " + line)
    print(f"\n{len(changed)} change(s); uncreditable keywords remaining: {len(remaining)}")
    for r in remaining:
        print("   still uncreditable:", r)
    if failures:
        print(f"\n{len(failures)} FAILURE(S):")
        for f in failures:
            print("  ", f)
    if remaining or failures:
        sys.exit("refusing to write" if write else "dry run ended with problems")
    if write:
        BANK.write_text(json.dumps(bank, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"written -> {BANK}")
    else:
        print("dry run — pass --write to save")


if __name__ == "__main__":
    main()
