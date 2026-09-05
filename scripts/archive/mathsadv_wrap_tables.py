"""One-off (2026-09-05): wraps Mathematics Advanced's three unwrapped wide
tables in the standard horizontal scroller (CLAUDE.md §10).

Found by sweeping viewport widths rather than only 430px. At 320px (iPhone SE)
three questions overflow their question area, every one of them an unwrapped
`.q-table`:

  2021 Q25   399px in a 280px box   (future-value table: 2 header cells, but
                                     the second is colspan=5, so it is really
                                     six columns — the classic §10 case)
  2024 Q26   335px in a 280px box   (5 columns)
  2022 Q11   355px in a 280px box   (4 columns; blank cells the student fills)

⚠️ §10's rule names "7+ columns" as the test. That threshold was measured at
430px and does not hold at 320px, where a 2-column table with long cells already
spills. The durable test is the MEASUREMENT, not the column count.

2021 Q25 and 2024 Q26 overflowed identically before this session's per-part work
(verified by re-rendering them with `parts` deleted) — they are pre-existing.
2022 Q11 went 375px -> 390px when its table moved into the shared `.parts-stem`,
so 15px of it is new; it overflowed at 320px either way.

The wrapper deliberately does NOT set `min-width`. §10's recipe includes one,
but these three already fit at 430px and forcing a min-width would introduce a
scrollbar where none is needed. Without it the table scrolls only when it
genuinely does not fit.

Run:  python scripts/archive/mathsadv_wrap_tables.py [--write]
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
BANK = ROOT / "subjects" / "mathematics-advanced.json"

TARGETS = [(2021, "25"), (2024, "26"), (2022, "11")]
OPEN = ('<div style="overflow-x:auto;-webkit-overflow-scrolling:touch;'
        'margin:14px 0">')
CLOSE = "</div>"
TABLE = re.compile(r'<table class="q-table">.*?</table>', re.S)


def wrap(html):
    """Wrap every unwrapped .q-table. Returns (html, count)."""
    n = 0

    def sub(m):
        nonlocal n
        start = m.start()
        # already wrapped? the scroller is written immediately before the table
        if html[max(0, start - len(OPEN)):start] == OPEN:
            return m.group(0)
        n += 1
        return OPEN + m.group(0).replace(
            '<table class="q-table">', '<table class="q-table" style="margin:0">', 1) + CLOSE

    return TABLE.sub(sub, html), n


def main():
    write = "--write" in sys.argv
    bank = json.loads(BANK.read_text(encoding="utf-8"))
    total = 0
    for q in bank["writtenQuestions"]:
        if (q["year"], str(q["qNum"])) not in TARGETS:
            continue
        for field in ("stem", "q"):
            if q.get(field) and "<table" in q[field]:
                q[field], n = wrap(q[field])
                total += n
                print(f'{q["year"]} Q{q["qNum"]} .{field}: wrapped {n}')
        for p in (q.get("parts") or []):
            for field in ("q", "answer"):
                if p.get(field) and "<table" in p[field]:
                    p[field], n = wrap(p[field])
                    total += n
                    print(f'{q["year"]} Q{q["qNum"]} {p["label"]} .{field}: wrapped {n}')
    print(f"\ntables wrapped: {total}")
    if total == 0:
        print("nothing to do — refusing to write")
        sys.exit(1)
    if write:
        BANK.write_text(json.dumps(bank, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"written -> {BANK}")
    else:
        print("dry run — pass --write to save")


if __name__ == "__main__":
    main()
