"""One-off (2026-09-05): adds a `parts[]` array to VET Construction's 18 merged
multi-part written questions, so the engine can render an answer box per NESA
part and award a mark per part.

Nothing here is authored. Each part's marks, prompt and position come from the
CURRENT merged `q` field (built and verified in the 2026-09-02 merge); each
part's scoring data (answer / keywords / acceptableAnswers / minKeywords /
bandDescriptors) comes from the PRE-MERGE bank recovered from git at 12a2c31^,
where every part was its own entry.

Schema added, alongside the existing fields which are left untouched:

    "stem":  shared intro shown once above all parts (omitted when there isn't one)
    "parts": [ { label, marks, q, intro?, answer, keywords?, acceptableAnswers?,
                 minKeywords?, bandDescriptors? } ]

`q` is deliberately NOT changed: it stays the full combined text, so
validate_subjects.cjs, check_written_key.cjs and the test-mode results
breakdown all keep working exactly as before. validate_subjects.cjs gains an
assertion that sum(parts[].marks) == marks so the two cannot drift.

Run:  python scripts/archive/vet_add_parts.py [--write]
"""
import json
import pathlib
import re
import sys
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[2]
BANK = ROOT / "subjects" / "vet-construction.json"
PREMERGE = pathlib.Path(
    r"C:/Users/pierr/AppData/Local/Temp/claude/vet_premerge.json"
)

# A part label starts the segment, and only ever follows a <br> or the string
# start -- which is what separates it from "(3 : 2 : 1)" or "(300 x 300)" mid-text.
LABEL_RE = re.compile(r"(?:^|<br\s*/?>)(?:\s*<br\s*/?>)*\s*\(([a-z]{1,3})\)\s")
# NOT anchored to end-of-segment: on 2022 Q19(a) and Q16(a) the stimulus image
# is printed AFTER the marks badge, so anchoring silently reclassified those
# parts as intros and lost them.
MARKS_RE = re.compile(r"<strong>\((\d+)\s*marks?\)</strong>")
ROMAN = {"i", "ii", "iii", "iv", "v"}


def split_parts(q):
    """Split a merged `q` into (shared stem, [(label, text), ...]).

    A segment carrying a trailing marks badge is a scorable part; one without is
    an intro belonging to the sub-parts that follow it (e.g. 2023 Q16's saw
    picture, shared by (a)(i) and (a)(ii))."""
    hits = list(LABEL_RE.finditer(q))
    if not hits:
        return q, []
    stem = q[: hits[0].start()].strip()
    segs = []
    for n, m in enumerate(hits):
        end = hits[n + 1].start() if n + 1 < len(hits) else len(q)
        segs.append((m.group(1), q[m.end(): end].strip()))
    return stem, segs


def build_parts(q):
    """Return (stem, parts) with roman sub-parts labelled under their letter."""
    stem, segs = split_parts(q)
    parts, cur_letter, pending_intro = [], None, ""
    for token, text in segs:
        if token in ROMAN and cur_letter:
            label = f"({cur_letter})({token})"
        else:
            # A new letter ends the previous letter's intro.
            cur_letter, pending_intro, label = token, "", f"({token})"
        m = MARKS_RE.search(text)
        if not m:
            # No marks badge -> this is an intro for the sub-parts that follow.
            pending_intro = text.rstrip()
            pending_intro = re.sub(r"(?:<br\s*/?>\s*)+$", "", pending_intro)
            continue
        prompt = MARKS_RE.sub("", text).rstrip()
        prompt = re.sub(r"(?:<br\s*/?>\s*)+$", "", prompt).strip()
        part = {"label": label, "marks": int(m.group(1)), "q": prompt}
        if pending_intro:
            part["intro"] = pending_intro
        parts.append(part)
    return stem, parts


def main():
    write = "--write" in sys.argv
    bank = json.loads(BANK.read_text(encoding="utf-8"))
    pre = json.loads(PREMERGE.read_text(encoding="utf-8"))["writtenQuestions"]

    groups = defaultdict(list)
    for p in pre:
        base = re.match(r"^(\d+)", str(p["qNum"])).group(1)
        groups[(p["year"], base)].append(p)

    # Scoring fields are carried across verbatim; nothing is re-authored here.
    CARRY = ("answer", "keywords", "acceptableAnswers", "minKeywords", "bandDescriptors")

    done = failures = 0
    for q in bank["writtenQuestions"]:
        qnum = str(q["qNum"])
        if not re.fullmatch(r"\d+", qnum):
            continue  # deliberately-split Section III/IV entry -- left alone
        group = groups.get((q["year"], qnum), [])
        if len(group) < 2:
            continue  # genuinely single-part question

        stem, parts = build_parts(q["q"])
        ctx = f"{q['year']} Q{qnum}"

        if len(parts) != len(group):
            print(f"FAIL {ctx}: split found {len(parts)} parts, pre-merge has {len(group)}")
            failures += 1
            continue

        total = sum(p["marks"] for p in parts)
        if total != q["marks"]:
            print(f"FAIL {ctx}: part marks sum to {total}, question says {q['marks']}")
            failures += 1
            continue

        ok = True
        for part, src in zip(parts, group):
            want = re.sub(r"^\d+", "", str(src["qNum"]))
            if part["label"] != want:
                print(f"FAIL {ctx}: label {part['label']} != pre-merge {want}")
                ok = False
                break
            if part["marks"] != src["marks"]:
                print(f"FAIL {ctx} {want}: marks {part['marks']} != pre-merge {src['marks']}")
                ok = False
                break
            for key in CARRY:
                if key in src:
                    part[key] = src[key]
            if "keywords" not in part and "acceptableAnswers" not in part:
                print(f"FAIL {ctx} {want}: no scoring mechanism in pre-merge entry")
                ok = False
                break
            if "answer" not in part:
                print(f"FAIL {ctx} {want}: no model answer in pre-merge entry")
                ok = False
                break
        if not ok:
            failures += 1
            continue

        if stem:
            q["stem"] = stem
        q["parts"] = parts
        done += 1
        print(f"ok   {ctx}: {len(parts)} parts, {total} marks"
              + (f", shared stem {len(stem)} chars" if stem else ""))

    print(f"\n{done} questions given parts[], {failures} failures")
    if failures:
        sys.exit(1)
    if write:
        BANK.write_text(
            json.dumps(bank, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        print(f"written -> {BANK}")
    else:
        print("dry run -- pass --write to save")


if __name__ == "__main__":
    main()
