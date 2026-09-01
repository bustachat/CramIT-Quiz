# -*- coding: utf-8 -*-
"""Write a written-answer review ledger from a hand-authored verdict table.

The ledger at `data/answer-key/written/reviews/{subject-id}.json` is the committed,
checkable artifact of a human review (docs/porting-playbook.md section 6). Prose cannot be
asserted on -- but WHETHER a human compared it, and whether that comparison is still
current, can be. Each entry carries a fingerprint of NESA's sample answer as it read at
review time, so regenerating the key automatically VOIDS any review whose official text
moved, instead of letting it go quietly stale.

This script only computes the fingerprints and the file shape. The verdicts are typed in
by the reviewer; nothing here decides anything.

Usage
-----
    python scripts/build_review_ledger.py <subject-id>

The verdict table for a subject lives in `scripts/reviews/{subject-id}.py` as a module
defining REVIEWED = {(year, qNum): {"verdict": ..., "fields": [...], "note": ...}}.
"""

import hashlib
import importlib.util
import io
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERDICTS = ("ok", "corrected", "divergent-accepted")


def fingerprint(text):
    """sha256 of NESA's sample answer, whitespace-normalised.

    Normalised because the extractor joins the PDF's text layer line by line: an
    irrelevant re-wrap must not void a review, while any change of WORDS must.
    """
    norm = re.sub(r"\s+", " ", text or "").strip()
    return "sha256:" + hashlib.sha256(norm.encode("utf-8")).hexdigest()


def leaves(key, year, qnum):
    m = re.match(r"^(\d+)((?:\([a-z0-9ivx]+\))*)$", str(qnum))
    want = [m.group(1)] + re.findall(r"\(([a-z0-9ivx]+)\)", m.group(2))
    out = []
    for p in key["papers"][str(year)]:
        got = [str(p["question"])] + ([] if not p["part"] else p["part"].split("."))
        if got[:len(want)] == want:
            out.append(p)
    return out


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: python scripts/build_review_ledger.py <subject-id>")
    sid = sys.argv[1]

    table_path = os.path.join(REPO, "scripts", "reviews", sid.replace("-", "_") + ".py")
    if not os.path.exists(table_path):
        sys.exit("no verdict table at " + table_path)
    spec = importlib.util.spec_from_file_location("verdicts", table_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    bank = json.load(io.open(os.path.join(REPO, "subjects", sid + ".json"), encoding="utf-8"))
    key = json.load(io.open(os.path.join(REPO, "data", "answer-key", "written", sid + ".json"),
                            encoding="utf-8"))

    written = [(str(q["year"]), q["qNum"]) for q in bank["writtenQuestions"]]
    missing = [k for k in written if k not in mod.REVIEWED]
    extra = [k for k in mod.REVIEWED if k not in written]
    if missing:
        sys.exit("verdict table is missing %d bank questions: %s" % (len(missing), missing))
    if extra:
        sys.exit("verdict table names questions not in the bank: %s" % (extra,))

    reviews, counts = {}, {}
    for (year, qnum) in written:
        entry = mod.REVIEWED[(year, qnum)]
        if entry["verdict"] not in VERDICTS:
            sys.exit("%s %s: unknown verdict %r" % (year, qnum, entry["verdict"]))
        if entry["verdict"] != "ok" and not entry.get("note"):
            sys.exit("%s %s: verdict %r requires a note" % (year, qnum, entry["verdict"]))
        ls = leaves(key, year, qnum)
        if not ls:
            sys.exit("%s %s: no official part joins to this bank entry" % (year, qnum))
        sample = " ".join(p["sampleAnswer"] for p in ls)
        reviews.setdefault(year, {})[qnum] = {
            "reviewedAt": mod.REVIEWED_AT,
            "verdict": entry["verdict"],
            "fields": entry["fields"],
            "sampleAnswerFingerprint": fingerprint(sample),
            "note": entry.get("note"),
        }
        counts[entry["verdict"]] = counts.get(entry["verdict"], 0) + 1

    out = {
        "subject": sid,
        "note": ("Written-answer review ledger. One entry per written bank question, "
                 "recording that a human compared its modelAnswer, keywords and "
                 "bandDescriptors against NESA's official sample answer and criteria in "
                 "data/answer-key/written/. `sampleAnswerFingerprint` hashes the OFFICIAL "
                 "answer as at review time: regenerate the key and any review whose "
                 "official text moved is void, not stale. See docs/porting-playbook.md "
                 "section 6. Rebuild with scripts/build_review_ledger.py; never hand-edit."),
        "reviewer": "human review, assisted (session of %s)" % mod.REVIEWED_AT,
        "reviews": reviews,
    }
    out_dir = os.path.join(REPO, "data", "answer-key", "written", "reviews")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, sid + ".json")
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    print("%s: %d reviews -> %s" % (sid, len(written), path))
    for v in VERDICTS:
        if counts.get(v):
            print("   %-20s %d" % (v, counts[v]))


if __name__ == "__main__":
    main()
