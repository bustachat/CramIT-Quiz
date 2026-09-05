"""Extract the official WRITTEN-question mark allocations from NESA marking guidelines.

Companion to `build_answer_key.py`, which does the same for Section I multiple choice.
Official marks never change, so they are derived once, committed to
`data/answer-key/written/`, and enforced in CI by `scripts/check_written_key.cjs`.
CI can never regenerate this: the PDFs are not in the repo, by copyright.

What is extracted, and what is not
----------------------------------
For every question part the guidelines define, this records the **maximum mark**, the
official **sample answer** text, and the official **criteria rows** (each band's wording
beside the mark it earns). Only the mark is machine-checkable and only the mark is
enforced; the sample answer and criteria are stored for human reference, because prose
cannot be compared for equality. Storing them is still worthwhile -- they are the source
a reviewer needs when a bank answer looks wrong, and the criteria rows are the ONLY
ground truth for a question's `bandDescriptors` (added 2026-09-01, for the VET written
review; before that, band descriptors could be reviewed for plausibility but not against
NESA).

Why the criteria rows are bracketed by the table's drawn rules
--------------------------------------------------------------
A criteria row's mark is vertically CENTRED in its cell, so a row whose wording runs over
three lines has its mark on the middle line -- see 2024 VET Q16(a), where "2" sits beside
the word "OR" between the two clauses it applies to. Bracketing a row by the mark lines
above and below it therefore leaks wording in BOTH directions, which is exactly the bug
`build_mapping_grid.py` was fixed for on 2026-08-28. These tables are really ruled, so
`row_rules()`/`band_of()` (same technique, same reason) read the boundaries the page
itself draws. Where a table has no usable rules, each mark-bearing line falls back to
being its own row -- reported by shape, never silently merged.

Why the marks are read positionally
-----------------------------------
The guidelines lay each part out as `Question N (a)` -> a `Criteria`/`Marks` table ->
`Sample answer:`. The marks live in a right-hand column at x ~ 485. Reading that column
positionally, and stopping at `Sample answer`, is what keeps the count honest: a naive
digit regex over the whole block picks up stray digits in the sample working and
over-counts (2020 Maths Section II reads 117 that way, against a true 85).

Two header shapes must be discarded, or they become phantom questions: the Section I
answer key's `Question / Answer` table on page 1, and the `Question / Marks / Content /
Syllabus outcomes` mapping grid at the end. Both are rejected by requiring the token
after `Question` to be a number. Note the mapping grid also carries a `Marks` column
header, at x ~ 136 -- hence the x > 400 test rather than "find the Marks column".

Anything that cannot be parsed is REPORTED, never guessed: a part whose criteria table
yields no mark is written to stderr and omitted from the output.

Usage
-----
    python scripts/build_written_key.py <subject-id> [--dry-run]
    python scripts/build_written_key.py all

Subject ids: mathematics-standard-2, multimedia, vet-construction.
(Health and Movement Science has no past papers -- 2026 is its first HSC year.)
"""

import argparse
import glob
import json
import os
import re
import sys

import fitz  # PyMuPDF

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NESA = r"C:\Claude Code Space\CRAMIT QUIZ Code Folder\NESA Exams Folder"
OUT_DIR = os.path.join(REPO, "data", "answer-key", "written")

SUBJECTS = {
    "mathematics-advanced": "Maths Advanced",
    "mathematics-standard-2": "Maths Standard 2",
    "multimedia": "Industrial Technology - Multimedia",
    "vet-construction": "VET - Construction",
}

MARKS_COL_MIN_X = 440   # the mapping grid's Marks column sits at x~136; the real one at x~472
HEADER_MAX_X = 110      # "Question" starts in the left margin

# A stacked fraction's bar. ⚠️ "Shorter than row_rules()' 100 pt" is NOT a sufficient
# test, and assuming it was cost this extractor 145 of its 234 Maths Advanced parts on the
# first run: the criteria table is TWO cells, so every row is ruled twice -- once across
# the criteria column (~380 pt) and once across the Marks column (70.32 pt). The second is
# short, so it posed as a fraction bar and folded the mark digits of adjacent rows into
# "1/2" tokens, emptying the marks column. A table rule is recognised by SHARING ITS Y with
# the full-width rule of the same row, which needs no assumption about column widths.
FRAC_BAR_MIN_W = 4.0
FRAC_BAR_MAX_W = 60.0
ROW_RULE_MIN_W = 100.0  # must match row_rules(); a rule this wide brackets a criteria row

# Page furniture. This must be filtered out of the CRITERIA scan as well as the answer
# text: "Page 18 of 23" puts a 23 in the marks column, which is where 2022 Maths Q35
# picked up a phantom 23-mark part.
RUNNING = re.compile(r"^\s*(NESA\b|Page \d+ of \d+|\u2013 \d+ \u2013)", re.I)

# The criteria table ends at the official answer, which is headed either "Sample answer"
# or "Answers could include" depending on the question. Missing the second spelling lets
# the marks scan run on into the answer body and the page footer.
ANSWER_HEAD = re.compile(r"^\s*(Sample answer|Answers? could include)\b:?\s*", re.I)

# A criteria row's mark is either a single number or a band range ("9-10", "1-2").
# Ranges are used for extended-response questions; the part's maximum is the top of the
# highest band. Note the text layer can split a range across two words on the same line
# ("9-1" + "0"), which is why the marks column is joined per line before parsing.
MARK_VALUE = re.compile(r"^(\d+)(?:\s*[\u2013\u2212-]\s*(\d+))?$")

# The criteria bullet glyph has no Unicode mapping in these PDFs and extracts as U+FFFD
# (or, in some years, a literal bullet). It is layout, not wording -- strip it so a
# descriptor authored from a criteria row does not inherit a replacement character.
BULLET = re.compile("[\ufffd\u2022\u25cf\u25aa\uf0b7]" + r"\s*")


# Reassembling a line left-to-right can leave a space in front of punctuation, because the
# piece that now sits before the comma used to sit after it -- "as 20/40 , or equivalent".
# That is an artefact of the reassembly, never NESA's typesetting, and it also trips the
# damage heuristics that read these rows downstream.
TIGHTEN_PUNCT = re.compile(r"\s+([,.;:])")


def tidy(text):
    """Collapse whitespace and pull punctuation back onto the word before it."""
    return TIGHTEN_PUNCT.sub(r"\1", re.sub(r"\s+", " ", text)).strip()


def is_guidelines(name):
    """True for a marking-guidelines PDF, mirroring build_answer_key.find_papers().

    Filenames are not consistent across subjects: Maths Standard 2, Multimedia and
    VET use `{year}-hsc-...-mg.pdf`, while Maths Advanced uses
    `{year}_marking_guidelines.pdf`. An `-mg.pdf$` test alone matches only the
    former and exits "no marking-guideline PDFs" on the latter.

    `feedback` is tested FIRST and excluded: the marking-centre notes are a third
    PDF per year in some folders, named either `{year}_marking_feedback.pdf` or
    `{year} ... HSC Marking Feedback.pdf` -- both of which contain "marking" and
    would otherwise be parsed as guidelines.
    """
    lowered = name.lower()
    if "feedback" in lowered:
        return False
    return bool(re.search(r"-mg\b|marking", lowered))


def frac_bars(page):
    """The page's stacked-fraction bars: short horizontal rules that are NOT table rules.

    On 2020 Maths Advanced p4 the bar of 20/40 is a 13.97 pt rect at x 360.3-374.3, sitting
    exactly over its two digits. The trap is the Marks column's row rule at 70.32 pt --
    also short, and it fooled the first version of this function. Both cells of a ruled row
    are drawn at the SAME y, so a short rule level with a full-width one is a table rule and
    is dropped. See FRAC_BAR_MAX_W.
    """
    short, wide = [], []
    for drawing in page.get_drawings():
        for item in drawing["items"]:
            if item[0] == "l":
                a, b = item[1], item[2]
                if abs(a.y - b.y) >= 0.6:
                    continue
                y, w, x0, x1 = a.y, abs(a.x - b.x), min(a.x, b.x), max(a.x, b.x)
            elif item[0] == "re" and item[1].height < 1.5:
                r = item[1]
                y, w, x0, x1 = r.y0, r.width, r.x0, r.x1
            else:
                continue
            if w > ROW_RULE_MIN_W:
                wide.append(y)
            elif FRAC_BAR_MIN_W < w <= FRAC_BAR_MAX_W:
                short.append((y, x0, x1))
    return sorted(b for b in short if not any(abs(b[0] - y) < 1.5 for y in wide))


def assemble_fractions(words, bars, body_h):
    """Fold each stacked fraction into ONE token, `num/den`, sitting on its own bar.

    A stacked fraction is the one damage shape that no line-grouping rule can fix, because
    its numerator genuinely IS above the line and its denominator genuinely IS below it --
    see 2020 Maths Advanced Q14(c), where "as 20/40," extracted as a leading "20", the
    sentence, then a stranded "40" ("20 Obtains the probability ... as , or equivalent 40
    merit"). Reading order cannot be recovered from the glyph boxes alone; it comes from
    the bar the page draws between them.

    Tokens are claimed at most once, so a nested fraction's inner bar (processed first,
    bars being sorted top-down) keeps its own digits.
    """
    words = list(words)
    for by, bx0, bx1 in bars:
        near = [w for w in words
                if w[0] >= bx0 - 2 and w[2] <= bx1 + 2
                and abs((w[1] + w[3]) / 2 - by) <= 0.9 * body_h]
        num = sorted((w for w in near if (w[1] + w[3]) / 2 < by), key=lambda w: w[0])
        den = sorted((w for w in near if (w[1] + w[3]) / 2 > by), key=lambda w: w[0])
        if not num or not den:
            continue          # a rule that is not a fraction bar (a box edge, an underline)
        # A real bar is drawn to the width of what it divides. Requiring the digits to
        # span most of it rejects a rule that merely happens to have text above and below.
        span = max(w[2] for w in num + den) - min(w[0] for w in num + den)
        if span < 0.4 * (bx1 - bx0):
            continue
        text = "".join(w[4] for w in num) + "/" + "".join(w[4] for w in den)
        for w in num + den:
            words.remove(w)
        words.append((bx0, by - body_h / 2, bx1, by + body_h / 2, text))
    return words


# A tall bracket or integral sign is not one glyph in these PDFs: it is drawn as a stack
# of Unicode "piece" characters in a single x-column, one per line it spans. Each piece
# therefore lands on a DIFFERENT visual line, and the halves that fall outside the
# sentence's own line get appended to the row after it -- 2021 Advanced Q27(b) extracted as
# "...ofsin ⎛ π/12 t⎞, or equivalent merit ⎝ ⎠", the bottom halves stranded at the end.
# Folding the stack back into one glyph is the only way to place it, exactly as a stacked
# fraction needs its bar. Measured over all 23 guideline PDFs: 496 pieces on 43 pages,
# perfectly paired (⎛ = ⎝ = 59, ⌠ = ⌡ = ⎮ = 34), and NONE in VET or Multimedia.
DELIM_PIECES = {
    "⌠": "∫", "⎮": "∫", "⌡": "∫",   # ⌠ ⎮ ⌡ -> ∫
    "⎛": "(", "⎜": "(", "⎝": "(",                   # ⎛ ⎜ ⎝ -> (
    "⎞": ")", "⎟": ")", "⎠": ")",                   # ⎞ ⎟ ⎠ -> )
    "⎡": "[", "⎢": "[", "⎣": "[",                   # ⎡ ⎢ ⎣ -> [
    "⎤": "]", "⎥": "]", "⎦": "]",                   # ⎤ ⎥ ⎦ -> ]
    "⎧": "{", "⎨": "{", "⎩": "{", "⎪": "{",     # ⎧ ⎨ ⎩ ⎪ -> {
    "⎫": "}", "⎬": "}", "⎭": "}",                   # ⎫ ⎬ ⎭ -> }
}


def fold_delimiters(words, body_h):
    """Fold each stacked bracket/integral into ONE glyph on the line it belongs to.

    Every piece is SUBSTITUTED IN PLACE by its canonical glyph, and within a stack only
    the topmost survives; the rest are deleted and a token left empty is dropped. Editing
    in place rather than concatenating the stack is what makes a token carrying pieces of
    two DIFFERENT groups safe -- 2020 Advanced Q21(c) has the single token `⎛3⎞`, whose
    `⎛` belongs to one stack and whose `⎞` belongs to another; concatenating lost the `⎞`
    and scrambled the row around it.

    A surviving token that is nothing BUT its glyph is moved to the stack's vertical
    centre, so a two- or three-line-tall integral sign lands on the text line it is read
    with instead of the line its top piece happens to start on. One that also carries
    content stays where it is, because that content belongs on its own line.
    """
    occurrences = []
    for i, w in enumerate(words):
        for j, ch in enumerate(w[4]):
            if ch in DELIM_PIECES:
                occurrences.append((DELIM_PIECES[ch], i, j))
    if not occurrences:
        return words

    # Column by x-range OVERLAP, not by x0. A piece often shares its token with content
    # to its left, so the token's x0 is that content's edge: 2021 Advanced Q27(b) pairs
    # `t⎞` (x0 = 290.6, the `t`) with a bare `⎠` under the `⎞` itself, and bucketing on
    # x0 puts them in different columns and folds neither.
    groups = {}
    for canon, i, j in occurrences:
        w = words[i]
        for key, members in groups.items():
            if key[0] == canon and w[0] < key[2] and key[1] < w[2]:
                members.append((i, j))
                break
        else:
            groups[(canon, w[0], w[2])] = [(i, j)]

    edits = {}      # token index -> {char index: replacement}
    recentre = {}   # token index -> new vertical centre
    for (canon, _lo, _hi), members in groups.items():
        members.sort(key=lambda m: words[m[0]][1])
        stack = [members[0]]
        for m in members[1:] + [None]:
            if m is not None and words[m[0]][1] - words[stack[-1][0]][3] <= 0.75 * body_h:
                stack.append(m)
                continue
            for n, (i, j) in enumerate(stack):
                edits.setdefault(i, {})[j] = canon if n == 0 else ""
            if len(stack) > 1:
                top = words[stack[0][0]]
                if all(c in DELIM_PIECES for c in top[4]):
                    ys = [words[i][1] for i, _ in stack] + [words[i][3] for i, _ in stack]
                    recentre[stack[0][0]] = (min(ys) + max(ys)) / 2
            stack = [m] if m is not None else []

    out = []
    for i, w in enumerate(words):
        if i not in edits:
            out.append(w)
            continue
        text = "".join(edits[i].get(j, ch) for j, ch in enumerate(w[4]))
        if not text:
            continue
        if i in recentre:
            yc = recentre[i]
            out.append((w[0], yc - body_h / 2, w[2], yc + body_h / 2, text))
        else:
            out.append((w[0], w[1], w[2], w[3], text))
    return out


def join_split_words(toks):
    """Rejoin a word the text layer split mid-way, e.g. "studyin"+"g", "equiv"+"alent".

    These are span boundaries, not spaces: get_text("words") splits on whitespace, so two
    tokens whose boxes touch had no space between them. Real word gaps on these pages are
    ~3 pt, so the 0.2 pt threshold cannot swallow one.
    """
    out = []
    for t in toks:
        if out and 0 <= t[0] - out[-1][2] <= 0.2:
            p = out[-1]
            out[-1] = (p[0], min(p[1], t[1]), t[2], max(p[3], t[3]), p[4] + t[4])
        else:
            out.append(t)
    return out


def page_lines(page):
    """Group a page's words into visual lines, each sorted LEFT TO RIGHT.

    ⚠️ Lines are grouped by vertical CENTRE, not by top-y. Keying on `round(y0, 1)` (what
    this did until 2026-09-05) makes every inline superscript its own "line", and since
    the lines are then emitted in y order the fragment is hoisted in front of the sentence
    it belongs inside: 2020 Maths Advanced Q13 read "sec2 Finds the anti-derivative of x"
    for "Finds the anti-derivative of sec2 x". The two share a centre to within 0.7 pt
    while their tops differ by 2.0 pt, which is exactly why the centre is the right key.

    The tolerance is 0.6 x the page's own median glyph height. Consecutive real lines on
    these pages are ~22 pt apart with ~12 pt glyphs, so they never overlap and cannot be
    merged. An odd-height token (a tall integral sign, a bracket spanning three lines)
    attaches to the nearest line but NEVER becomes the line's anchor, so it cannot chain
    two lines together.
    """
    words = [w for w in page.get_text("words") if w[4].strip()]
    if not words:
        return []
    heights = sorted(w[3] - w[1] for w in words)
    body_h = heights[len(heights) // 2] or 12.0
    words = assemble_fractions(words, frac_bars(page), body_h)
    words = fold_delimiters(words, body_h)

    # ⚠️ An IMAGE's label is reported with the image's own box, not a glyph box, so it is
    # enormous and its centre is meaningless -- 2020 Maths Advanced p5 has "solution"
    # /"diagram" 138 pt tall (11x body), centred on the NEXT question's first criteria row,
    # and 2020 Standard 2 p2 has "spanning"/"trees" 313 pt tall starting at y = -79.9, off
    # the top of the page. Grouping either by centre files NESA's picture caption inside a
    # criteria row, which is then shown to a student as band wording. Measured over all 23
    # guideline PDFs, > 5x body height selects exactly these 63 tokens and nothing else
    # (real oversize tops out at 4.7x, on the mapping-grid page this parser discards).
    # They are kept -- "solution diagram" tells a reviewer the official answer has a
    # picture -- but as their own line, ordered by their TOP, which is where they visually
    # begin and which is the block they belong to.
    oversize = [w for w in words if (w[3] - w[1]) > 5 * body_h]
    words = [w for w in words if (w[3] - w[1]) <= 5 * body_h]

    normal = lambda w: 0.6 * body_h <= (w[3] - w[1]) <= 1.4 * body_h
    lines = []          # [anchor-centre, anchored?, [tokens]]
    for w in sorted(words, key=lambda w: ((w[1] + w[3]) / 2, w[0])):
        yc = (w[1] + w[3]) / 2
        if lines and abs(yc - lines[-1][0]) <= 0.6 * body_h:
            lines[-1][2].append(w)
            if normal(w) and not lines[-1][1]:
                lines[-1][0], lines[-1][1] = yc, True
        else:
            lines.append([yc, normal(w), [w]])
    attach_orphans(lines, body_h)
    out = [(anchor, join_split_words(sorted(toks, key=lambda t: t[0])), False)
           for anchor, _anchored, toks in lines]
    for w in oversize:
        out.append((w[1], [w], True))
    return [(round(y, 1), toks, layout) for y, toks, layout in sorted(out, key=lambda r: r[0])]


# Structural headings, which an orphan fragment must never be merged into. Matching one
# of these is what tells parse_paper where the criteria table ends and the official answer
# begins, so corrupting one costs a whole sample answer, not just a stray character.
HEADING = re.compile(r"^\s*(Sample answer|Answers? could include|Question\s+\d|Criteria)",
                     re.I)


def attach_orphans(lines, body_h):
    """Pull a stray fragment into the line it visually sits inside.

    A superscript raised off a tall neighbour clears the centre tolerance and becomes its
    own one-token "line", which then sorts before or after the sentence instead of inside
    it: 2025 Advanced Q27(b) extracted as "x Provides the correct antiderivative of 1/2"
    for "... of 1/2 ^x". The fragment is merged into the nearest line whose horizontal
    extent CONTAINS it, and marked `^` or `_` when it sits clearly above or below that
    line's centre, which is the ordinary way to write it in plain text.

    Deliberately narrow, because merging the wrong thing corrupts a criteria row:
      * only a line of at most 3 tokens spanning under 60 pt is ever a candidate;
      * NEVER a token in the Marks column -- pulling a mark digit into a neighbouring
        row would silently change that row's mark, which is the one thing here that is
        ground truth;
      * the target must be within 1.5 x body height, and must be the closest line.
    Mutates `lines` in place; emptied lines are dropped.
    """
    def span(toks):
        # The Marks column is excluded: a mark digit sits at x ~ 485 and would otherwise
        # stretch every line's span to the full page width, making any short line look
        # "inside" it.
        body = [t for t in toks if t[0] <= MARKS_COL_MIN_X] or toks
        return min(t[0] for t in body), max(t[2] for t in body)

    for orphan in list(lines):
        toks = orphan[2]
        if len(toks) > 3:
            continue
        ox0, ox1 = span(toks)
        if ox1 - ox0 > 60 or any(t[0] > MARKS_COL_MIN_X for t in toks):
            continue
        best, best_d = None, 1.5 * body_h
        for line in lines:
            if line is orphan or not line[2]:
                continue
            # ⚠️ NEVER annotate one of NESA's structural headings. An integral's upper
            # limit `k` sat nearer the "Sample answer:" heading than its own integral sign
            # and was merged into it as "Sample _k answer:", which stopped ANSWER_HEAD
            # matching and silently DISCARDED the whole sample answer of 2020 Advanced
            # Q23(a). A heading is never annotated with maths, so it is never a target.
            if HEADING.match(" ".join(t[4] for t in line[2])):
                continue
            tx0, tx1 = span(line[2])
            # ⚠️ Must start WELL RIGHT of the line's own left margin. Without this the
            # rule eats the wrapped continuation of a criteria sentence -- a second line
            # holding just "merit" or "building site" begins at the same margin and is
            # otherwise indistinguishable from a fragment, which turned
            # "...on a building site" into "Provides _building _site a description of...".
            # A superscript is always interior; a wrap never is.
            if not (ox0 > tx0 + 2 * body_h and ox1 < tx1):
                continue
            d = abs(orphan[0] - line[0])
            if d < best_d:
                best, best_d = line, d
        if best is None:
            continue
        offset = orphan[0] - best[0]
        for t in toks:
            text = t[4]
            if offset < -0.35 * body_h:
                text = "^" + text
            elif offset > 0.35 * body_h:
                text = "_" + text
            best[2].append((t[0], t[1], t[2], t[3], text))
        orphan[2] = []
    lines[:] = [l for l in lines if l[2]]


def marks_cell(toks, gap=15.0):
    """The line's Marks-column text: the RIGHTMOST cluster of tokens past MARKS_COL_MIN_X.

    Not simply everything past the boundary. A criteria sentence can wrap so that its
    last word spills over it while the real mark sits further right -- 2021 VET Q20's
    fifth band ends "...something to do with a" at x 441.9-447.9 with its "1-3" at
    x 479.1, and joining the two yields "a1-3", which MARK_VALUE rejects. The mark was
    then lost and, because criteria_rows() drops a bandless row, that band vanished
    from the criteria table entirely (the part's own `marks` survived only because it
    is a max() over the other bands).

    Clustering on a gap keeps the case the join exists for: a range split across two
    words on the same line ("9-1" + "0") is contiguous, so it stays in one cluster.

    Returns (text, tokens) so the caller can define the criteria wording by EXCLUSION --
    a wrapped sentence's last word must stay in the wording, not be dropped with the mark.
    """
    right = sorted((t for t in toks if t[0] > MARKS_COL_MIN_X), key=lambda t: t[0])
    if not right:
        return "", []
    cluster = [right[-1]]
    for tok in reversed(right[:-1]):
        if cluster[0][0] - tok[2] > gap:
            break
        cluster.insert(0, tok)
    return "".join(t[4] for t in cluster).strip(), cluster


def row_rules(page):
    """Y positions of the criteria table's own horizontal rules on this page.

    Mirrors build_mapping_grid.row_rules(). The width test (> 100 pt) keeps cell-border
    stubs and the page's header/footer hairlines from inventing bands; those two rules do
    appear, but they sit outside every criteria block and so bracket nothing.
    """
    ys = []
    for drawing in page.get_drawings():
        for item in drawing["items"]:
            if item[0] == "l":
                a, b = item[1], item[2]
                if abs(a.y - b.y) < 0.6 and abs(a.x - b.x) > 100:
                    ys.append(a.y)
            elif item[0] == "re":
                r = item[1]
                if r.height < 1.5 and r.width > 100:
                    ys.append(r.y0)
    ys.sort()
    merged = []
    for y in ys:
        if not merged or y - merged[-1] > 1.5:
            merged.append(y)
    return merged


def band_of(y, rules):
    """Index of the ruled band containing y, or None when the rules do not bracket it."""
    if len(rules) < 3 or y < rules[0] or y > rules[-1]:
        return None
    lo, hi = 0, len(rules) - 1
    while lo < hi - 1:
        mid = (lo + hi) // 2
        if rules[mid] <= y:
            lo = mid
        else:
            hi = mid
    return lo


def criteria_rows(lines):
    """Collapse scanned criteria lines into official rows: [{marks, text}], top band first.

    `lines` is [(page-index, y, ruled-band-index or None, criteria-text, mark or None)] in
    page order. Lines sharing a (page, band) are one row. A line the rules do not bracket
    stands alone, so an unruled table degrades to one row per mark-bearing line rather
    than merging rows that were never merged.
    """
    groups, order = {}, []
    for i, (pi, _y, band, text, mark) in enumerate(lines):
        key = (pi, band) if band is not None else ("solo", i)
        if key not in groups:
            groups[key] = {"text": [], "marks": None}
            order.append(key)
        if text:
            groups[key]["text"].append(text)
        if mark is not None and groups[key]["marks"] is None:
            groups[key]["marks"] = mark
    rows = []
    for key in order:
        g = groups[key]
        text = tidy(" ".join(g["text"]))
        text = BULLET.sub("", text).strip()
        if g["marks"] is None or not text:
            continue          # the "Criteria / Marks" header band, and any empty spacer
        rows.append({"marks": g["marks"], "text": text})
    return rows


def parse_paper(pdf_path):
    """Return ([{question, part, marks, sampleAnswer, criteria}], [unresolved-labels])."""
    doc = fitz.open(pdf_path)
    rows, rules = [], {}
    for pi in range(doc.page_count):
        rules[pi] = row_rules(doc[pi])
        for y, toks, layout in page_lines(doc[pi]):
            rows.append((pi, y, toks, layout))

    # Locate question headers: "Question 16", "Question 16 (a)", "Question 16 (a) (i)".
    headers = []
    for i, (pi, y, toks, _layout) in enumerate(rows):
        if toks[0][4] != "Question" or toks[0][0] >= HEADER_MAX_X:
            continue
        if len(toks) < 2 or not re.fullmatch(r"\d+", toks[1][4]):
            continue  # "Question Answer" key table, "Question Marks Content ..." grid
        parts = []
        for t in toks[2:]:
            m = re.fullmatch(r"\(([a-z]+|[ivx]+)\)", t[4])
            if not m:
                break
            parts.append(m.group(1))
        headers.append((i, int(toks[1][4]), parts))

    out, unresolved = [], []
    for n, (idx, qnum, parts) in enumerate(headers):
        end = headers[n + 1][0] if n + 1 < len(headers) else len(rows)
        marks, sample, in_sample = [], [], False
        crit_lines = []
        for j in range(idx + 1, end):
            pi, y, toks, layout = rows[j]
            text = " ".join(t[4] for t in toks)
            if RUNNING.match(text):
                continue
            if not in_sample and ANSWER_HEAD.match(text):
                in_sample = True
                rest = ANSWER_HEAD.sub("", text).strip()
                if rest:
                    sample.append(rest)
                continue
            if in_sample:
                sample.append(text)
                continue
            # Criteria row: join the marks column left-to-right before parsing, so a
            # range split across two words ("9-1" + "0") reads as one value.
            col, cell_toks = marks_cell(toks)
            m = MARK_VALUE.match(col)
            value = int(m.group(2) or m.group(1)) if m else None
            if m:
                marks.append(value)
            # The row's WORDING is every token that is NOT in the marks cell, collected
            # with the line's ruled band so criteria_rows() can rejoin a row split over
            # 2-3 lines. Defined by exclusion rather than by the x threshold so a
            # criteria sentence that wraps past MARKS_COL_MIN_X keeps its last word.
            # ⚠️ An image's label ("solution diagram", "graph") is layout, not criteria
            # wording, and its box is the IMAGE's -- 2020 Advanced Q24's "graph" is 428 pt
            # tall and starts 165 pt ABOVE the page, so it has no honest position at all
            # and landed at the front of the first criteria row on its page. It is kept in
            # the sample answer, where it usefully tells a reviewer the official answer has
            # a picture, and excluded here.
            crit_lines.append((pi, y, band_of(y, rules[pi]),
                               "" if layout else
                               " ".join(t[4] for t in toks if t not in cell_toks).strip(),
                               value))

        label = "Q%d%s" % (qnum, "".join("(%s)" % p for p in parts))
        if not marks:
            unresolved.append(label)
            continue
        out.append({
            "question": qnum,
            "part": ".".join(parts) if parts else None,
            "marks": max(marks),
            "sampleAnswer": tidy(" ".join(sample)),
            "criteria": criteria_rows(crit_lines),
        })
    return out, unresolved


def build_subject(subject_id, dry_run=False):
    folder = os.path.join(NESA, SUBJECTS[subject_id])
    if not os.path.isdir(folder):
        sys.exit("NESA folder not found (not in the repo, by copyright): " + folder)

    pdfs = sorted(p for p in glob.glob(os.path.join(folder, "*.pdf"))
                  if is_guidelines(os.path.basename(p)))
    if not pdfs:
        sys.exit("no marking-guideline PDFs in " + folder)

    papers, total_parts = {}, 0
    for pdf in pdfs:
        name = os.path.basename(pdf)
        m = re.match(r"(\d{4})", name)
        if not m:
            print("  SKIP (no year in filename): " + name, file=sys.stderr)
            continue
        year = m.group(1)
        parts, unresolved = parse_paper(pdf)
        if not parts:
            print("  NOT WRITTEN %s: no question parts parsed from %s" % (year, name), file=sys.stderr)
            continue
        for label in unresolved:
            print("  UNRESOLVED %s %s: no mark found in its criteria table" % (year, label),
                  file=sys.stderr)
        papers[year] = parts
        total_parts += len(parts)
        print("  %s: %3d parts, %3d marks  (%s)"
              % (year, len(parts), sum(p["marks"] for p in parts), name))

    data = {
        "subject": subject_id,
        "source": "NESA HSC marking guidelines (not in repo - copyright)",
        "note": ("Official maximum marks per question part, plus the official sample answer "
                 "and criteria rows for reference. Marks are enforced by "
                 "scripts/check_written_key.cjs; sample answers and criteria are not - prose "
                 "cannot be compared for equality. The criteria rows are the ground truth a "
                 "question's bandDescriptors are authored from. "
                 "Regenerate with scripts/build_written_key.py; never hand-edit."),
        "papers": papers,
    }
    out_path = os.path.join(OUT_DIR, subject_id + ".json")
    print("  => %d parts across %d papers -> %s" % (total_parts, len(papers), out_path))
    if dry_run:
        print("  dry run - nothing written")
        return
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("subject", help="subject id, or the word all")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    targets = list(SUBJECTS) if args.subject == "all" else [args.subject]
    for sid in targets:
        if sid not in SUBJECTS:
            sys.exit("unknown subject '%s'. Known: %s" % (sid, ", ".join(SUBJECTS)))
        print(sid + ":")
        build_subject(sid, args.dry_run)


if __name__ == "__main__":
    main()
