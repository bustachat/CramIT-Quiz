"""Re-derive every per-part `bandDescriptors` from the committed criteria rows.

Run this whenever `build_written_key.py` is rebuilt. The criteria rows in
`data/answer-key/written/` are the ONLY ground truth for a question's band wording
(CLAUDE.md §10 rule 8), so when they change the bank's derived descriptors are stale --
and nothing else in CI would notice, because only the MARK is enforced.

It exists because the 2026-09-05 extractor fix repaired 117 of the 147 scrambled criteria
rows, and the descriptors already committed for Mathematics Advanced, Mathematics
Standard 2 and VET Construction had been derived from the damaged text.

What it touches, and what it refuses to touch
---------------------------------------------
* Every `parts[].bandDescriptors` is recomputed from that part's own criteria rows.
* A question-level `bandDescriptors` is recomputed ONLY when it is provably the
  composition of the old per-part ones (the shape `ms2_add_parts.py` writes: each part's
  label followed by its descriptor). Anything else is hand-authored prose that predates
  this pipeline -- most of Mathematics Advanced -- and is left exactly as it is.
* Nothing else is written. Marks, model answers, keywords and stems are never touched.

Run:  python scripts/refresh_band_descriptors.py [--write]
"""
import json
import pathlib
import re
import sys
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[1]
KEYS = ROOT / "data" / "answer-key" / "written"
BANKS = ROOT / "subjects"

# ── the damage smell test ────────────────────────────────────────────────────
# A criteria row the extractor still cannot lay out in reading order. Such a row must
# never reach a student, so its part falls back to the engine's generic wording.
#
# ⚠️ RELAXED on 2026-09-05, after the extractor fix. The strict version carried a
# "trailing orphan" rule (a row ending in a lone letter or bare number), which was
# earning its keep when a stranded fragment landed at the end of a scrambled row. With
# the rows repaired it is almost pure false positive -- it flags "Shows that a = b",
# "Finds the correct value of H", "Attempts to solve the given equation when d = 1" --
# and every one of those costs a part its real NESA wording. Dropping it still catches
# all five rows that remain genuinely damaged, each of which is a multi-line stretched
# delimiter (an integral sign or a tall bracket) that no line model can place.
DANGLING_TAIL = re.compile(r"\b(and|or|of|the|to|for|with|from|in|a|an)\s*$", re.I)
SPACE_PUNCT = re.compile(r"\s[,.;:](\s|$)")
LEADING_FRAGMENT = re.compile(r"^\S+,\s")
MERIT_TAIL = re.compile(r"or equiv\w*\s+\w*merit\s*[.]?\s*$", re.I)


def criteria_damaged(text):
    t = str(text).strip()
    if not t:
        return True
    if DANGLING_TAIL.search(t) or SPACE_PUNCT.search(t) or LEADING_FRAGMENT.search(t):
        return True
    if not t[0].isupper():
        return True
    if "merit" in t.lower() and not MERIT_TAIL.search(t) and " OR " not in t and " AND " not in t:
        return True
    return False


def collapse_criteria(rows):
    """NESA's N criteria rows -> the engine's {full, partial, minimal}.

    Top row verbatim, middle rows joined with ' OR ', bottom row verbatim -- the rule
    VET's written review established. N=2 repeats the bottom row into `partial`; N=1 is
    all-or-nothing. None if ANY row is still damaged."""
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


def criteria_for(label, official_parts):
    """Every criteria row belonging to the bank part labelled `label`.

    ⚠️ A bank label is not always a single letter. VET stores sub-parts, so "(a)(i)" must
    map to the key's part path "a.i" -- `label.strip("()")` yields "a)(i" and silently
    matches nothing, which reported four perfectly good VET parts as damaged and stripped
    their descriptors. The key's paths are dotted, so the label's parenthesised groups are
    joined the same way, and a bank part that spans several official leaves (label "(a)"
    over "a.i" and "a.ii") takes all of them -- the prefix rule check_written_key.cjs uses
    for marks.
    """
    path = ".".join(re.findall(r"\(([^)]+)\)", label))
    rows = []
    for p in official_parts:
        p_path = str(p["part"] or "")
        if p_path == path or p_path.startswith(path + "."):
            rows += (p.get("criteria") or [])
    return rows


def composed(parts, tier, field="bandDescriptors"):
    """The question-level string ms2_add_parts.py composes from the per-part ones."""
    return " ".join(f'{p["label"]} {p[field][tier]}'
                    for p in parts if p.get(field))


def main():
    write = "--write" in sys.argv
    grand = defaultdict(int)
    for key_path in sorted(KEYS.glob("*.json")):
        subject = key_path.stem
        bank_path = BANKS / f"{subject}.json"
        if not bank_path.exists():
            continue
        key = json.loads(key_path.read_text(encoding="utf-8"))
        bank = json.loads(bank_path.read_text(encoding="utf-8"))

        official = defaultdict(list)
        for yr, parts in key["papers"].items():
            for p in parts:
                official[(int(yr), str(p["question"]))].append(p)

        changed = added = removed = same = damaged = qlevel = 0
        for q in bank["writtenQuestions"]:
            if not q.get("parts"):
                continue
            official_parts = official.get((q["year"], str(q["qNum"])), [])
            old_parts = [dict(p) for p in q["parts"]]
            for part in q["parts"]:
                rows = criteria_for(part["label"], official_parts)
                new = collapse_criteria(rows)
                old = part.get("bandDescriptors")
                # ⚠️ NESA prints no row for non-attainment, so on an all-or-nothing
                # 1-mark part `partial`/`minimal` are the ONLY authored text this
                # pipeline produces -- and VET's were written by hand during its 2026-09-01
                # review ("Does not correctly identify a chisel. The mark is awarded in
                # full or not at all."), which reads better than the mechanical default.
                # Refresh only `full`, which is the part that comes from NESA.
                if new and old and len([r for r in rows if str(r.get("text", "")).strip()]) == 1:
                    new = dict(new)
                    new["partial"] = old.get("partial", new["partial"])
                    new["minimal"] = old.get("minimal", new["minimal"])
                if new is None:
                    damaged += 1
                    if old is not None:
                        part.pop("bandDescriptors")
                        removed += 1
                elif old is None:
                    part["bandDescriptors"] = new
                    added += 1
                elif old != new:
                    part["bandDescriptors"] = new
                    changed += 1
                else:
                    same += 1
            # question level: only if it was provably composed from the OLD per-part set
            qbd = q.get("bandDescriptors") or {}
            if qbd and all(qbd.get(t) == composed(old_parts, t)
                           for t in ("full", "partial", "minimal")
                           if composed(old_parts, t)):
                rebuilt = {t: composed(q["parts"], t) for t in ("full", "partial", "minimal")}
                if all(rebuilt.values()) and rebuilt != qbd:
                    q["bandDescriptors"] = rebuilt
                    qlevel += 1
        print(f'{subject:26s} parts: {changed:3d} rewritten, {added:3d} added, '
              f'{removed:3d} removed, {same:3d} unchanged | {damaged:3d} still damaged '
              f'| {qlevel:3d} composed question-level rebuilt')
        grand["changed"] += changed; grand["added"] += added
        grand["removed"] += removed; grand["damaged"] += damaged; grand["q"] += qlevel
        # ⚠️ Only write when something actually changed. Round-tripping a subject file
        # through json.dumps reformats it wholesale — it expanded the compact inline
        # arrays in `studyNotes` into a 456-line diff on multimedia.json, which carries no
        # per-part data at all and had no business being touched. CLAUDE.md records this
        # trap from a previous session; it is easy to hit again.
        if write and (changed or added or removed or qlevel):
            bank_path.write_text(json.dumps(bank, indent=2, ensure_ascii=False) + "\n",
                                 encoding="utf-8")
    print(f'\nTOTAL parts rewritten {grand["changed"]}, added {grand["added"]}, '
          f'removed {grand["removed"]}, still damaged {grand["damaged"]}; '
          f'{grand["q"]} question-level rebuilt')
    print("written" if write else "dry run — pass --write to save")


if __name__ == "__main__":
    main()
