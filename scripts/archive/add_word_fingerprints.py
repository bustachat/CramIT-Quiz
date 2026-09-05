"""One-off (2026-09-05): backfill `sampleAnswerWordsFingerprint` into an existing review
ledger, computed from the text the reviewer ACTUALLY READ.

Why this is not just a ledger rebuild
-------------------------------------
Fixing build_written_key.py's word-order bug re-laid out 45 of VET Construction's 76
official sample answers, which voided 23 of its 34 completed human reviews. The words did
not change -- measured, every one of the 45 has an identical word multiset -- so the
reviews are still sound, and `check_written_key.cjs` now distinguishes the two cases with
a second, order-insensitive fingerprint.

But that second fingerprint has to record the multiset of the text AS AT REVIEW TIME. Just
re-running `build_review_ledger.py` would compute BOTH hashes from today's key, which makes
the new one tautologically true and quietly discards the guarantee the ledger exists for --
precisely the "do not just re-fingerprint it" the runbook warns against.

So the reviewed text is recovered from git (the key as committed at the given ref, before
the extractor fix), and every entry's EXISTING exact fingerprint is verified against it
first. If any entry fails that check the ledger was not built from that key and this script
refuses to write anything.

Run:  python scripts/archive/add_word_fingerprints.py <subject-id> <git-ref> [--write]
      python scripts/archive/add_word_fingerprints.py vet-construction HEAD --write
"""
import hashlib
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]


def fingerprint(text):
    return "sha256:" + hashlib.sha256(
        re.sub(r"\s+", " ", text or "").strip().encode("utf-8")).hexdigest()


def word_fingerprint(text):
    words = sorted(re.findall(r"[^\W_]+", (text or "").lower()))
    return "sha256:" + hashlib.sha256(" ".join(words).encode("utf-8")).hexdigest()


def leaves(key, year, qnum):
    """Official parts joining to one bank qNum — the same prefix rule the ledger uses."""
    m = re.match(r"^(\d+)((?:\([a-z0-9ivx]+\))*)$", str(qnum))
    if not m:
        return []
    q, path = m.group(1), [p for p in re.findall(r"\(([a-z0-9ivx]+)\)", m.group(2))]
    out = []
    for p in key["papers"].get(str(year), []):
        if str(p["question"]) != q:
            continue
        leaf = [s for s in str(p["part"] or "").split(".") if s]
        if leaf[:len(path)] == path:
            out.append(p)
    return out


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    subject, ref = sys.argv[1], sys.argv[2]
    write = "--write" in sys.argv
    led_path = ROOT / "data" / "answer-key" / "written" / "reviews" / f"{subject}.json"
    key_rel = f"data/answer-key/written/{subject}.json"

    old_key = json.loads(subprocess.run(
        ["git", "show", f"{ref}:{key_rel}"], cwd=ROOT,
        capture_output=True, check=True).stdout.decode("utf-8"))
    ledger = json.loads(led_path.read_text(encoding="utf-8"))

    ok = mismatched = 0
    for year, qs in ledger["reviews"].items():
        for qnum, entry in qs.items():
            sample = " ".join(p["sampleAnswer"] for p in leaves(old_key, year, qnum))
            if fingerprint(sample) != entry["sampleAnswerFingerprint"]:
                print(f"  MISMATCH {year} Q{qnum}: the ledger was not built from {ref}")
                mismatched += 1
                continue
            entry["sampleAnswerWordsFingerprint"] = word_fingerprint(sample)
            ok += 1
    print(f"\n{ok} entries verified against {ref} and backfilled, {mismatched} mismatched")
    if mismatched:
        sys.exit("refusing to write — every entry must verify against the reviewed key")
    if write:
        led_path.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n",
                            encoding="utf-8")
        print(f"written -> {led_path}")
    else:
        print("dry run — pass --write to save")


if __name__ == "__main__":
    main()
