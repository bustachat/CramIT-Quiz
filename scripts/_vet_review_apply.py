# -*- coding: utf-8 -*-
"""Apply the 2026-09-01 VET written-answer review to subjects/vet-construction.json.

ONE-OFF. Kept only so the review is reproducible and auditable; it is not app tooling.

What it does
------------
1. Writes `bandDescriptors` on all 23 written questions, DERIVED from the official
   criteria rows now carried in data/answer-key/written/vet-construction.json. Every
   descriptor is NESA's own wording except the two noted below.
2. Fills the three missing `keywords`/`minKeywords`.
3. Applies the five content corrections the review found (see CORRECTIONS).

Safe to run because vet-construction.json round-trips byte-for-byte through
json.dumps(indent=2, ensure_ascii=False) + newline -- verified before writing, and
asserted again below. (multimedia.json does NOT: see CLAUDE.md.)
"""
import io
import json
import re
import sys

BANK = "subjects/vet-construction.json"
KEY = "data/answer-key/written/vet-construction.json"

# --- N official bands -> the engine's three -------------------------------------------
#
# The app's shape is fixed at {full, partial, minimal} -- both consumers read exactly
# those three keys (index.html buildKeywordFeedback, functions/mark-written.js). VET's
# criteria tables carry 1 to 5 rows. The collapse, applied to every question without
# exception:
#
#   full     = NESA's TOP row (worth the maximum), verbatim
#   minimal  = NESA's BOTTOM row, verbatim
#   partial  = every row BETWEEN them, verbatim, joined with " OR "
#
# Two degenerate shapes:
#   N = 2 -> there is no middle row, so partial repeats the bottom row. NESA defines
#           exactly two standards here; repeating an official sentence is truthful
#           where inventing a third would not be.
#   N = 1 -> the 1-mark identify questions. NESA defines one standard and the mark is
#           all-or-nothing, so partial and minimal state its non-attainment. This is the
#           ONLY authored (non-NESA) descriptor text in the subject, and it is flagged
#           in the ledger. All three of these questions are scored by `acceptableAnswers`,
#           where the engine reads only `full` and `minimal`.
ALL_OR_NOTHING = {
    ("2021", "16(a)"): "Does not correctly identify a chisel. The mark is awarded in full or not at all.",
    ("2022", "19(a)"): "Does not correctly read the table and select the correct answer. The mark is awarded in full or not at all.",
    ("2023", "16(a)(i)"): "Does not correctly name the saw pictured. The mark is awarded in full or not at all.",
}

# NESA prints several criteria as separate bulleted lines inside one cell, so the
# extractor joins them with a space and they read as a run-on. Punctuating them is
# presentation only -- no word is added, removed or reordered. Every substitution is
# printed, the discipline build_mapping_grid.py's SOURCE_TYPOS uses.
PUNCT = [
    ("handling Uses", "handling; uses"),
    ("industry Provides", "industry; provides"),
    ("industry Uses", "industry; uses"),
    ("response Uses", "response; uses"),
    ("terminology Uses", "terminology; uses"),
]


def descriptors(rows, label):
    texts = []
    for r in rows:
        t = r["text"]
        for pat, rep in PUNCT:
            if pat in t and pat != rep:
                print("    punctuated %s: %r -> %r" % (label, pat, rep))
                t = t.replace(pat, rep)
        texts.append(t)
    if len(texts) == 1:
        neg = ALL_OR_NOTHING[label]
        return {"full": texts[0], "partial": neg, "minimal": neg}
    full, minimal, mids = texts[0], texts[-1], texts[1:-1]
    return {"full": full,
            "partial": " OR ".join(mids) if mids else minimal,
            "minimal": minimal}


# --- the five content corrections the review found ------------------------------------
Q2023_19BI_STEM = (
    "A shed is to be built on a concrete slab with concrete footings. The drawing shows "
    "the hidden detail of the edge and centre beams required for the footings of the "
    "shed. Calculate how many cubic metres of concrete are required for the footings."
)
Q2023_19BI_ANSWER = (
    "The footings are 300 mm × 300 mm, i.e. 0.3 m × 0.3 m in section. The drawing shows "
    "FIVE beams: two running the 8500 length, and THREE running the 6000 width — the two "
    "edge beams and a centre beam.<br><br>"
    "Long beams (8500 direction), taken full length: 2 × 8.5 = 17 m. "
    "Volume = 17 × 0.3 × 0.3 = 1.53 m³.<br>"
    "Cross beams (6000 direction): shorten each by the 300 mm width of a long beam at each "
    "end so the overlaps are not counted twice — 6.0 − (2 × 0.3) = 5.4 m each, and "
    "3 × 5.4 = 16.2 m. Volume = 16.2 × 0.3 × 0.3 = 1.46 m³.<br><br>"
    "Total concrete = 1.53 + 1.46 = 2.99 m³.<br><br>"
    "The centre beam is the part most often missed. Working from the outer perimeter alone "
    "— 2 × (8.5 + 6) = 29 m, giving 29 × 0.3 × 0.3 = 2.61 m³ — omits it and also "
    "double-counts the four corners, so it is not the required answer."
)
Q2022_19A_ANSWER = (
    "$450. Convert the load to the units the table uses: 3700 kg = 3.7 tonnes, which falls "
    "in the <em>3.00–4.99</em> tonne row. 54 km falls in the <em>51–70</em> km column. "
    "Reading across to that column gives a delivery cost of $450."
)
Q2022_17C_ANSWER = (
    "RWT = rainwater tank.<br><br>"
    "The second symbol — a broken (dashed) circle with a small circle at its centre — is a "
    "tree to be removed. On a site plan a feature drawn with a continuous outline is to "
    "remain, while a broken outline marks one that is to be removed or demolished; the "
    "small centre circle is the trunk."
)

CORRECTIONS = {
    ("2022", "19(a)"): {
        "answer": Q2022_19A_ANSWER,
        "keywords": ["450", "tonne", "3.00–4.99", "51–70", "table"],
        "minKeywords": 2,
    },
    ("2022", "17(c)"): {
        "q": "Identify each of the architectural symbols shown.",
        "answer": Q2022_17C_ANSWER,
        "keywords": ["rainwater", "tank", "tree", "removed", "demolished", "broken"],
        "minKeywords": 3,
    },
    ("2023", "16(a)(i)"): {
        "acceptableAnswers": ["drop saw", "mitre", "compound", "sliding", "cut-off", "chop saw"],
        "keywords": ["drop saw", "mitre", "compound", "sliding", "cut-off", "chop saw"],
        "minKeywords": 1,
    },
    ("2023", "19(b)(i)"): {
        "q": Q2023_19BI_STEM,
        "answer": Q2023_19BI_ANSWER,
        "keywords": ["2.99", "1.53", "1.46", "5.4", "16.2", "centre beam", "edge beam",
                     "0.3", "volume", "footing"],
        "minKeywords": 4,
    },
    ("2025", "18(b)"): {
        "q": ("Identify the meaning of the following symbols or abbreviations that are "
              "found on construction drawings."),
    },
    ("2021", "16(a)"): {
        "keywords": ["chisel", "firmer", "bevelled", "mortice", "mortise"],
        "minKeywords": 1,
    },
}

# The image lives in the stem for 19(b)(i) and 17(c); preserve whatever <img> the stem
# already carried rather than retyping the path.
IMG = re.compile(r"<img\b[^>]*>")


def main():
    # core.autocrlf=true, so the working copy may hold CRLF while the committed blob is
    # LF. Normalise before comparing, or the round-trip guard fires on line endings alone.
    raw = io.open(BANK, encoding="utf-8", newline="").read().replace("\r\n", "\n")
    bank = json.loads(raw)
    assert json.dumps(bank, indent=2, ensure_ascii=False) + "\n" == raw, \
        "vet-construction.json does not round-trip -- refusing to rewrite it"
    key = json.load(io.open(KEY, encoding="utf-8"))

    def leaves(year, qnum):
        m = re.match(r"^(\d+)((?:\([a-z0-9ivx]+\))*)$", str(qnum))
        want = [m.group(1)] + re.findall(r"\(([a-z0-9ivx]+)\)", m.group(2))
        out = []
        for p in key["papers"][str(year)]:
            got = [str(p["question"])] + ([] if not p["part"] else p["part"].split("."))
            if got[:len(want)] == want:
                out.append(p)
        return out

    changed = 0
    for q in bank["writtenQuestions"]:
        label = (str(q["year"]), q["qNum"])
        ls = leaves(*label)
        assert len(ls) == 1, "%s joins to %d official parts" % (label, len(ls))
        assert ls[0]["marks"] == q["marks"], "%s mark mismatch" % (label,)
        assert ls[0]["criteria"], "%s has no official criteria rows" % (label,)

        print("  %s %s (%d marks, %d official bands)"
              % (label[0], label[1], q["marks"], len(ls[0]["criteria"])))
        q["bandDescriptors"] = descriptors(ls[0]["criteria"], label)

        for field, value in CORRECTIONS.get(label, {}).items():
            if field == "q":
                img = IMG.search(q["q"])
                value = value + (("<br>" + img.group(0)) if img else "")
            before = q.get(field)
            q[field] = value
            if before != value:
                changed += 1
                print("      %-16s CHANGED" % field)

    # Every question must now carry all three artefacts, non-empty.
    for q in bank["writtenQuestions"]:
        bd = q["bandDescriptors"]
        for k in ("full", "partial", "minimal"):
            assert isinstance(bd.get(k), str) and bd[k].strip(), \
                "%s %s: bandDescriptors.%s empty" % (q["year"], q["qNum"], k)
        assert q.get("keywords"), "%s %s: no keywords" % (q["year"], q["qNum"])
        assert q.get("minKeywords"), "%s %s: no minKeywords" % (q["year"], q["qNum"])

    out = json.dumps(bank, indent=2, ensure_ascii=False) + "\n"
    io.open(BANK, "w", encoding="utf-8", newline="\n").write(out)
    print("\n  %d field values changed; bandDescriptors written on %d questions"
          % (changed, len(bank["writtenQuestions"])))


if __name__ == "__main__":
    sys.exit(main())
