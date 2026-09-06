"""One-off (2026-09-06): correct a committed review ledger's PROVENANCE, without touching
a single review entry.

The VET Construction ledger recorded `reviewer: "human review, assisted"` and a note saying
each entry records "that a human compared its modelAnswer, keywords and bandDescriptors
against NESA". The owner corrected that on 2026-09-06: the per-question comparison was done
by an assistant session, and they spot-checked a couple of questions, not all 34. Every
document built on the ledger inherited the overstatement — CLAUDE.md called VET "the ONLY
fully reviewed subject", and `check_written_key.cjs` printed "34/34 reviewed against NESA"
on every CI run.

⚠️ Why this is not just `build_review_ledger.py <subject>` again. That recomputes
`sampleAnswerFingerprint` from TODAY's key, which would erase the "23 re-laid out" signal
earned on 2026-09-05 and silently re-validate every entry against text no one reviewed —
the exact "do not just re-fingerprint it" this ledger exists to prevent. So the entries are
asserted byte-identical and only the top-level provenance strings are rewritten.

Run:  python scripts/archive/correct_review_provenance.py <subject-id> [--write]
"""
import copy
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    sid = sys.argv[1]
    write = "--write" in sys.argv
    led_path = ROOT / "data" / "answer-key" / "written" / "reviews" / f"{sid}.json"
    table = ROOT / "scripts" / "reviews" / f'{sid.replace("-", "_")}.py'

    ledger = json.loads(led_path.read_text(encoding="utf-8"))
    before = copy.deepcopy(ledger["reviews"])

    # the single source of truth for how the review was actually done
    ns = {}
    exec(compile(table.read_text(encoding="utf-8"), str(table), "exec"), ns)
    method = ns.get("REVIEW_METHOD")
    if not method:
        sys.exit(f"{table} must define REVIEW_METHOD")

    ledger.pop("reviewer", None)
    ledger["reviewMethod"] = method
    ledger["reviewedAt"] = ns["REVIEWED_AT"]
    ledger["note"] = (
        "Written-answer review ledger. One entry per written bank question, recording that "
        "its modelAnswer, keywords and bandDescriptors were compared against NESA's "
        "official sample answer and criteria in data/answer-key/written/. ⚠️ "
        "`reviewMethod` says WHO did the comparing and how far a human checked it — do not "
        "read an entry as a per-question human sign-off unless that field says so. "
        "`sampleAnswerFingerprint` hashes the OFFICIAL answer as at review time: regenerate "
        "the key and any review whose official WORDS moved is void, not stale. "
        "`sampleAnswerWordsFingerprint` hashes the same text with word ORDER discarded, so a "
        "pure re-layout by the extractor is reported rather than treated as NESA changing. "
        "See docs/porting-playbook.md section 6. Rebuild with "
        "scripts/build_review_ledger.py; never hand-edit."
    )

    if ledger["reviews"] != before:
        sys.exit("refusing to write: a review entry changed")
    n = sum(len(v) for v in ledger["reviews"].values())
    print(f"{sid}: provenance rewritten, {n} review entries untouched")
    print(f"  reviewMethod: {method}")
    if write:
        led_path.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n",
                            encoding="utf-8")
        print(f"  written -> {led_path}")
    else:
        print("  dry run — pass --write to save")


if __name__ == "__main__":
    main()
