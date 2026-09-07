# -*- coding: utf-8 -*-
"""Apply the Mathematics Standard 2 written-answer review (Stage 6b, 2026-09-07).

Every edit below was decided by reading the question against NESA's committed
sample answer and criteria rows in data/answer-key/written/mathematics-standard-2.json.
Where a STEM was changed, the wording was additionally confirmed against the exam
paper itself (CLAUDE.md section 10, "Exam citations") -- never inferred from the
marking guidelines, which section 10 forbids re-reading.

Kept so the review is reproducible, as scripts/_vet_review_apply.py is for VET.
subjects/mathematics-standard-2.json round-trips byte-for-byte through
json.dumps(indent=2, ensure_ascii=False) plus a trailing newline, so load/modify/dump
is safe here (it is NOT for multimedia.json).

Every replacement asserts its old value, so a silently-missed edit fails loudly.
"""
import io
import json

PATH = "subjects/mathematics-standard-2.json"

bank = json.load(io.open(PATH, encoding="utf-8"))
EDITS = []


def q(year, num):
    hits = [x for x in bank["writtenQuestions"]
            if str(x["year"]) == str(year) and str(x["qNum"]) == str(num)]
    assert len(hits) == 1, (year, num, len(hits))
    return hits[0]


def part(qq, label):
    hits = [p for p in qq["parts"] if p["label"] == label]
    assert len(hits) == 1, (label,)
    return hits[0]


def sub(obj, field, old, new, why):
    """Replace an exact substring in obj[field]; assert it occurs exactly once."""
    cur = obj[field]
    assert cur.count(old) == 1, "expected 1 occurrence of %r in %s, found %d" % (
        old[:70], field, cur.count(old))
    obj[field] = cur.replace(old, new)
    EDITS.append(why)


def setf(obj, field, new, why, old=None):
    if old is not None:
        assert obj.get(field) == old, "unexpected current %s: %r" % (field, obj.get(field))
    obj[field] = new
    EDITS.append(why)


def to_acceptable(obj, expect_keywords, accepted, why):
    """Swap a part's keyword list for an acceptableAnswers list."""
    assert obj.get("keywords") == expect_keywords, obj.get("keywords")
    del obj["keywords"]
    obj.pop("minKeywords", None)
    obj["acceptableAnswers"] = accepted
    EDITS.append(why)


# ---------------------------------------------------------------------------
# 1. 2020 Q20 -- the stem lost "$1" and "$3".
#    A JS String.replace() treats $1..$9 in the REPLACEMENT string as
#    capture-group references, so "$122 680" became "22 680" and "$3000" became
#    "000". Paper p16: "a taxable income of $122 680 ... he paid $3000 per month".
# ---------------------------------------------------------------------------
x = q(2020, 20)
sub(x, "q", "a taxable income of 22 680", "a taxable income of $122 680",
    "2020 Q20 stem: restore $122 680")
sub(x, "q", "he paid 000 per month", "he paid $3000 per month",
    "2020 Q20 stem: restore $3000")

# ---------------------------------------------------------------------------
# 2. 2020 Q26 -- SINGLE-LETTER keywords ('c','d','e','f','h','i'), from splitting
#    the critical path "C - D - E - F - H - I" into letters. keywordHit() does a
#    plain substring test, so each fires on ordinary English: measured in the
#    real engine, a content-free answer scored 1/1 on (a) and 2/2 on (b).
# ---------------------------------------------------------------------------
PATH_2020_26 = ["cdefhi", "c-d-e-f-h-i", "c – d – e – f – h – i",
                "c, d, e, f, h, i", "c,d,e,f,h,i", "c d e f h i",
                "c → d → e → f → h → i"]
x = q(2020, 26)
setf(x, "keywords", ["46", "12", "15"],
     "2020 Q26 keywords: drop 6 single letters that credited any English text",
     old=["46", "c", "d", "e", "f", "h", "i", "12", "15"])
setf(x, "minKeywords", 2, "2020 Q26 minKeywords 3 -> 2 (3 keywords remain)", old=3)
to_acceptable(part(x, "(a)"), ["46", "e", "i"], ["46"],
              "2020 Q26 (a): acceptableAnswers ['46'] replaces keywords incl. 'e','i'")
to_acceptable(part(x, "(b)"), ["46", "c", "d", "e", "f", "h", "i", "12"], PATH_2020_26,
              "2020 Q26 (b): acceptableAnswers (the critical path) replaces 6 letter keywords")
setf(part(x, "(c)"), "keywords", ["12", "15", "20"],
     "2020 Q26 (c): keywords are the table's own values, not letters",
     old=["c", "e", "f", "i", "12", "15"])
setf(part(x, "(c)"), "minKeywords", 2, "2020 Q26 (c): minKeywords 3 -> 2", old=3)

# ---------------------------------------------------------------------------
# 3. 2021 Q23 -- two defects.
#    (a) The model answer's edge list is fabricated: it names
#        "Kingsville-Underwood=20" (the paper's K-U edge is 65), its listed
#        edges sum to 95 against the stated 160, and it ends in a literal "+...".
#    (b) The prompt asked for "Queentown to Fernville along the minimum spanning
#        tree"; paper p19 asks "How long does it take to travel from Queentown to
#        Underwood using the fastest route?" -- a different destination, and not
#        restricted to the tree.
#    The MST was recomputed from the committed crop and totals NESA's 160.
# ---------------------------------------------------------------------------
x = q(2021, 23)
NEW_B_PROMPT = ("How long does it take to travel from Queentown to Underwood using "
                "the fastest route?")
sub(x, "q",
    "(b) Find the shortest travel time from Queentown to Fernville along the "
    "minimum spanning tree. (1 mark)",
    "(b) " + NEW_B_PROMPT + " (1 mark)",
    "2021 Q23 (b) stem: paper wording (Underwood, fastest route)")
setf(part(x, "(b)"), "q", NEW_B_PROMPT,
     "2021 Q23 (b) part prompt: paper wording",
     old="Find the shortest travel time from Queentown to Fernville along the "
         "minimum spanning tree.")
A_2021_23 = (
    "Kruskal's algorithm — take the shortest edge each time, skipping any edge that "
    "would close a loop:\n"
    "Minertown–Walltown = 10, Walltown–Parktown = 15, Minertown–Underwood = 20, "
    "Walltown–Fernville = 20, Kingsville–Minertown = 25, Queentown–Kingsville = 30, "
    "Parktown–Citadel = 40.\n"
    "(Underwood–Parktown 30, Underwood–Walltown 40, Queentown–Minertown 45, "
    "Underwood–Citadel 45, Fernville–Citadel 45 and Kingsville–Underwood 65 are "
    "all skipped — each would close a loop.)\n"
    "Total length = 10 + 15 + 20 + 20 + 25 + 30 + 40 = 160 minutes")
B_2021_23 = (
    "Fastest route Queentown → Minertown → Underwood = 45 + 20 = 65 minutes.\n"
    "(Queentown → Kingsville → Minertown → Underwood is 30 + 25 + 20 = 75 minutes, "
    "and Queentown → Kingsville → Underwood is 30 + 65 = 95 minutes.)")
setf(x, "answer", "(a) " + A_2021_23 + "\n(b) " + B_2021_23,
     "2021 Q23 answer: fabricated edge list and broken arithmetic replaced with the MST "
     "read off the committed crop (totals NESA's 160)")
setf(part(x, "(a)"), "answer", A_2021_23, "2021 Q23 (a) answer")
setf(part(x, "(b)"), "answer", B_2021_23, "2021 Q23 (b) answer")

# ---------------------------------------------------------------------------
# 4. 2021 Q27 -- part (a)'s acceptableAnswers carried '5', which is part (b)'s
#    answer. scoreOne() short-circuits on acceptableAnswers with a plain
#    includes(), so ANY answer containing a "5" scored 2/2 on a part whose
#    answer is $4.38.
# ---------------------------------------------------------------------------
setf(part(q(2021, 27), "(a)"), "acceptableAnswers", ["4.38", "$4.38"],
     "2021 Q27 (a): drop '5' (part (b)'s answer) -- it paid full marks for any digit 5",
     old=["4.38", "$4.38", "5"])

# ---------------------------------------------------------------------------
# 5. 2021 Q33 -- the stem's gradient contradicted NESA and the model answer.
#    Paper p28: "The equation of the regression line is y = 29.2 - 0.011x" and
#    "(ii) The gradient of the regression line is -0.011". A student following
#    the bank's -0.00404 gets 27.0 degrees and is marked wrong against 23.3.
# ---------------------------------------------------------------------------
x = q(2021, 33)
for fld in ("q", "stem"):
    sub(x, fld, "<em>y</em> = 29.2 − 0.00404<em>x</em>",
        "<em>y</em> = 29.2 − 0.011<em>x</em>",
        "2021 Q33 %s: regression line -0.00404 -> -0.011 (paper p28)" % fld)
sub(x, "q", "The gradient of the regression line is −0.00404.",
    "The gradient of the regression line is −0.011.",
    "2021 Q33 q: gradient -0.00404 -> -0.011")
sub(part(x, "(a)"), "q", "The gradient of the regression line is −0.00404.",
    "The gradient of the regression line is −0.011.",
    "2021 Q33 (a) prompt: gradient -0.00404 -> -0.011")

# ---------------------------------------------------------------------------
# 6. 2021 Q36 -- a REGEX was stored as a keyword ('a.*c.*d.*e.*g.*j.*k').
#    keywordHit() never evaluates regexes; the string was credited via the bare
#    letter "a" (kw.startsWith(word)), so it fired on almost any answer.
# ---------------------------------------------------------------------------
PATH_2021_36 = ["acdegjk", "a-c-d-e-g-j-k",
                "a – c – d – e – g – j – k",
                "a, c, d, e, g, j, k", "a,c,d,e,g,j,k", "a c d e g j k",
                "a → c → d → e → g → j → k"]
x = q(2021, 36)
setf(x, "keywords", ["40", "1 minute", "float"],
     "2021 Q36 keywords: drop the regex-shaped keyword (never matched as intended)",
     old=["40", "a.*c.*d.*e.*g.*j.*k", "1 minute", "float", "1"])
to_acceptable(part(x, "(b)"), ["40", "a.*c.*d.*e.*g.*j.*k", "1"], PATH_2021_36,
              "2021 Q36 (b): acceptableAnswers (critical path) replaces the regex keyword")

# ---------------------------------------------------------------------------
# 7. 2021 Q40 -- the same $1..$9 loss as 2020 Q20, in the model answer AND the
#    band descriptors. NESA: "1000 x 8.2132 = $8213.20 ... = $8419.81".
# ---------------------------------------------------------------------------
x = q(2021, 40)
setf(x, "answer",
     "Phase 1 — Annuity: $1000 per year for 8 years at 0.75%\n"
     "FV = $1000 × 8.2132 = $8213.20\n\n"
     "Phase 2 — Compound interest: $8213.20 at 1.25% for 2 years (no further deposits)\n"
     "FV = $8213.20 × (1.0125)²\n    = $8213.20 × 1.02515625\n    = $8419.81",
     "2021 Q40 answer: restore the $ amounts eaten by a $1..$9 replacement")
setf(x["bandDescriptors"], "full",
     "3/3 — Phase 1 correct ($8213.20) and Phase 2 correct ($8419.81).",
     "2021 Q40 bandDescriptors.full: restore $8213.20 / $8419.81",
     old="3/3 — Phase 1 correct (213.20) and Phase 2 correct (419.81).")

# ---------------------------------------------------------------------------
# 8. 2022 Q30 -- the model answer's headline results were WRONG.
#    40 000 x (1.001)^120 = $45 097.17 (NESA), not $45 093.59; the difference is
#    $40.87, not $37.29. The question-level acceptableAnswers already held NESA's
#    45 097.17, so the bank disagreed with itself.
# ---------------------------------------------------------------------------
x = q(2022, 30)
A_2022_30 = ("Option 1: A = $40 000 × (1 + 0.012/12)^120 = $40 000 × (1.001)^120 "
             "= $40 000 × 1.1274293… = $45 097.17")
B_2022_30 = ("Option 2: rate per quarter = 2.4%/4 = 0.6% = 0.006, periods = 10 × 4 = 40\n"
             "From the table the factor is 45.05630, so FV = $1000 × 45.05630 = $45 056.30\n"
             "Difference = $45 097.17 − $45 056.30 = $40.87 (Option 1 gives more)")
setf(x, "answer", "(a) " + A_2022_30 + "\n(b) " + B_2022_30,
     "2022 Q30 answer: $45 093.59 -> NESA's $45 097.17, and $37.29 -> $40.87")
setf(part(x, "(a)"), "answer", A_2022_30, "2022 Q30 (a) answer")
setf(part(x, "(b)"), "answer", B_2022_30, "2022 Q30 (b) answer")
setf(x, "keywords",
     ["45097", "$45 097", "(1.001)", "120", "45056", "45.056", "40.87", "difference",
      "option 1", "option 2"],
     "2022 Q30 keywords: wrong figures 45093/37 replaced with NESA's 45097/40.87",
     old=["45093", "$45 093", "(1.001)", "120", "45056", "45.056", "37", "difference",
          "option 1", "option 2"])
setf(part(x, "(a)"), "keywords", ["45097", "$45 097", "(1.001)", "120", "option 1"],
     "2022 Q30 (a) keywords",
     old=["45093", "$45 093", "(1.001)", "120", "option 1"])
setf(part(x, "(b)"), "keywords",
     ["45097", "$45 097", "45056", "45.056", "40.87", "difference", "option 1", "option 2"],
     "2022 Q30 (b) keywords",
     old=["45093", "$45 093", "45056", "45.056", "37", "difference", "option 1", "option 2"])

# ---------------------------------------------------------------------------
# 9. 2023 Q21 -- the combined stem printed the wrong per-part marks.
#    Paper pp16-17: (a) 1, (b) 1, (c) 1, (d) 2. The bank showed (b) 2 and (d) 1,
#    which still totals 5, so check_written_key.cjs could not see it.
# ---------------------------------------------------------------------------
x = q(2023, 21)
sub(x, "q", "(Provider B's line is already plotted on the grid in the exam.)  (2 marks)",
    "(Provider B's line is already plotted on the grid in the exam.)  (1 mark)",
    "2023 Q21 (b) mark label 2 -> 1 (paper p17)")
sub(x, "q", "Which provider, A or B, would be the cheaper option and by how much?  (1 mark)",
    "Which provider, A or B, would be the cheaper option and by how much?  (2 marks)",
    "2023 Q21 (d) mark label 1 -> 2 (paper p17)")

# ---------------------------------------------------------------------------
# 10. 2023 Q26(a) -- abandoned working plus the internal phrase "From MG:"
#     shown to the student.
# ---------------------------------------------------------------------------
x = q(2023, 26)
A_2023_26 = ("Area of path = area of the whole rectangle − area of the garden inside it\n"
             "= (3 m × 8 m) − (7 m × 2.5 m)\n= 24 − 17.5\n= 6.5 m²")
old_a = part(x, "(a)")["answer"]
assert "From MG" in old_a and "Actually" in old_a, old_a[:120]
setf(part(x, "(a)"), "answer", A_2023_26,
     "2023 Q26 (a) answer: remove abandoned working and the 'From MG:' leak")
sub(x, "answer", old_a, A_2023_26, "2023 Q26 answer: same clean-up")

# ---------------------------------------------------------------------------
# 11. 2023 Q27(b) -- literal thinking-aloud shown to the student
#     ("... no. ... should be 40... wait Actually: ...").
# ---------------------------------------------------------------------------
x = q(2023, 27)
B_2023_27 = ("P is due south of X and C is due west of Y, so ∠XPC = 90°.\n"
             "In right-angled triangle CXP: cos(∠CXP) = XP/XC = 7.5/40 = 0.1875\n"
             "∠CXP = cos⁻¹(0.1875) = 79°12′ ≈ 79°\n"
             "C lies west of south of X, so the bearing of C from X = 180° + 79° = 259°")
old_b = part(x, "(b)")["answer"]
assert "wait" in old_b and "no." in old_b, old_b[:120]
setf(part(x, "(b)"), "answer", B_2023_27,
     "2023 Q27 (b) answer: replace thinking-aloud scratch-work with NESA's method")
sub(x, "answer", old_b, B_2023_27, "2023 Q27 answer: same clean-up")

# ---------------------------------------------------------------------------
# 12. 2023 Q32 -- combined stem printed (a) 3 marks and (b) 1 mark; the paper
#     (p28) and the committed key both say 2 and 2.
# ---------------------------------------------------------------------------
x = q(2023, 32)
sub(x, "q", "assuming that interest is charged for the 21 days.  (3 marks)",
    "assuming that interest is charged for the 21 days.  (2 marks)",
    "2023 Q32 (a) mark label 3 -> 2 (paper p28)")
sub(x, "q", "Give the answer to two decimal places.  (1 mark)",
    "Give the answer to two decimal places.  (2 marks)",
    "2023 Q32 (b) mark label 1 -> 2 (paper p28)")

# ---------------------------------------------------------------------------
# 13. 2024 Q19 -- the stem omitted the student's test mark, so part (b) was
#     unanswerable. Paper p13: "scored 5 for the assignment and 12 on the test".
# ---------------------------------------------------------------------------
x = q(2024, 19)
OLD19 = "Another student, whose marks are not on the graph, scored 5 for the assignment."
NEW19 = ("Another student, whose marks are not on the graph, scored 5 for the assignment "
         "and 12 on the test.")
sub(x, "q", OLD19, NEW19, "2024 Q19 (b) stem: restore 'and 12 on the test' (paper p13)")
sub(part(x, "(b)"), "q", OLD19, NEW19, "2024 Q19 (b) part prompt: same")

# ---------------------------------------------------------------------------
# 14. 2024 Q34 -- the stem asked for square CENTIMETRES to the nearest whole
#     number; paper p28 asks for square METRES to 1 decimal place, which is what
#     the model answer and NESA's criteria both give (0.5 m2). The answer also
#     carried abandoned working and an "Actual MG calculation:" leak.
# ---------------------------------------------------------------------------
x = q(2024, 34)
sub(x, "q", "Give your answer in square centimetres, correct to the nearest whole number.",
    "Give your answer in square metres correct to 1 decimal place.",
    "2024 Q34 stem: cm2 / whole number -> m2 / 1 d.p. (paper p28)")
setf(x, "answer",
     "Each ball has diameter 23 cm, so the radius is 11.5 cm. The two hemispherical ends "
     "together make one whole sphere, and the curved wall of the cylinder spans the "
     "remaining two ball widths.\n"
     "Surface area of the sphere = 4 × π × (23/2)² = 1662.57 cm²\n"
     "Curved surface of the cylinder = 2 × π × (23/2) × (23 × 2) "
     "= 2 × π × 11.5 × 46 = 3323.14 cm²\n"
     "Total surface area = 1662.57 + 3323.14 = 4985.7 cm²\n"
     "= 4985.7 ÷ 10 000 = 0.5 m² (correct to 1 decimal place)",
     "2024 Q34 answer: remove abandoned working and the 'Actual MG calculation:' leak")

# ---------------------------------------------------------------------------
# 15. 2024 Q35 -- THREE stem errors, all confirmed on paper p29. The standard
#     deviation is 15, not 12; (a) asks for the percentage BETWEEN 58 AND 70,
#     not "less than 46"; (c) asks for the top 10%, not the top 5%. The model
#     answer already worked NESA's version, so stem and answer contradicted each
#     other on every part.
# ---------------------------------------------------------------------------
x = q(2024, 35)
for fld in ("q", "stem"):
    sub(x, fld, "normally distributed with mean 58 and standard deviation 12.",
        "normally distributed with mean 58 and standard deviation 15.",
        "2024 Q35 %s: standard deviation 12 -> 15 (paper p29)" % fld)
OLD35A = ("By calculating a <em>z</em>-score, find the percentage of scores that are "
          "less than 46.")
NEW35A = ("By calculating a <em>z</em>-score, find the percentage of scores that are "
          "between 58 and 70.")
sub(x, "q", OLD35A, NEW35A, "2024 Q35 (a) stem: 'less than 46' -> 'between 58 and 70' (paper p29)")
sub(part(x, "(a)"), "q", OLD35A, NEW35A, "2024 Q35 (a) part prompt: same")
OLD35C = ("By using the values in the table above, find an approximate minimum score needed "
          "to be in the top 5% of this examination.")
NEW35C = ("By using the values in the table above, find an approximate minimum score that a "
          "candidate would need to be placed in the top 10% of the candidates.")
sub(x, "q", OLD35C, NEW35C, "2024 Q35 (c) stem: 'top 5%' -> 'top 10%' (paper p29)")
sub(part(x, "(c)"), "q", OLD35C, NEW35C, "2024 Q35 (c) part prompt: same")

# ---------------------------------------------------------------------------
# 16. 2024 Q36(b) -- "Actually:" scratch marker plus a bogus justification.
# ---------------------------------------------------------------------------
x = q(2024, 36)
NEW36 = ("∠EBC = 180° − 106° = 74° (angles on a straight line)\n"
         "tan 74° = 20/BX, so BX = 20/tan 74° = 20/3.4874 = 5.73 m\n"
         "CD = BE − BX = 25.4 − 5.73 = 19.7 m (1 decimal place)")
OLD36 = part(x, "(b)")["answer"]
assert "Actually:" in OLD36, OLD36[:120]
setf(part(x, "(b)"), "answer", NEW36,
     "2024 Q36 (b) answer: remove the 'Actually:' scratch marker")
sub(x, "answer", OLD36, NEW36, "2024 Q36 answer: same clean-up")

# ---------------------------------------------------------------------------
# 17. 2024 Q41 -- the model answer contained "Wait -- let me re-read the MG. MG
#     says:" and an abandoned $302 072 line, shown to the student.
# ---------------------------------------------------------------------------
x = q(2024, 41)
assert "let me re-read the MG" in x["answer"]
setf(x, "answer",
     "Monthly interest rate: r = 2.4%/12 = 0.2% = 0.002\n"
     "Read the withdrawals as $1200 every month for the whole 25 years, plus an extra $800 "
     "a month for the first 15 years only.\n"
     "PV of $1200 for 25 years (n = 300, r = 0.002) = $1200 × 225.430 = $270 516\n"
     "PV of the extra $800 for 15 years (n = 180, r = 0.002) = $800 × 151.036 "
     "= $120 828.80\n"
     "Minimum deposit = $270 516 + $120 828.80 = $391 344.80",
     "2024 Q41 answer: remove the 'let me re-read the MG' note and the abandoned line")

# ---------------------------------------------------------------------------
# 18. 2024 Q39(c) -- a muddled parenthetical, replaced with NESA's own working.
# ---------------------------------------------------------------------------
x = q(2024, 39)
NEW39 = ("Activity C has EST 0 and duration 3 hours, so the earliest F can start is hour 3.\n"
         "Activity I has EST 12, so everything before I must be finished by hour 12.\n"
         "12 − 3 = 9 hours, and allowing for the 1 hour of float gives 9 − 1 = 8 hours.")
OLD39 = part(x, "(c)")["answer"]
assert "(actually at the EST of the next node)" in OLD39, OLD39[:120]
setf(part(x, "(c)"), "answer", NEW39,
     "2024 Q39 (c) answer: replace the muddled parenthetical")
sub(x, "answer", OLD39, NEW39, "2024 Q39 answer: same clean-up")

# ---------------------------------------------------------------------------
# 19. 2025 Q19 -- the worst finding in the subject. The model answer got the
#     prerequisites wrong (NESA: E needs C and D; F needs E), the critical path
#     wrong (NESA: BDEFH = 26 days, not BFH = 16), and part (c) contradicted both
#     NESA and its own opening sentence, ending "This DOES affect the critical
#     path" where NESA says "No, as the float time for activity A is 3."
#     Durations read off the committed crop: A 3, B 4, C 3, D 5, E 5, F 7, G 3, H 5.
# ---------------------------------------------------------------------------
x = q(2025, 19)
assert "B → F → H" in x["answer"] and "Corrected:" in x["answer"]
setf(x, "answer",
     "(a) Immediate prerequisites:\n"
     "B: none (B starts the project)\n"
     "E: C and D (both must finish before E can start)\n"
     "F: E\n"
     "(b) The two routes into the join are A→C = 3 + 3 = 6 days and B→D = 4 + 5 = 9 "
     "days, so B and D are critical. After E, F→H = 7 + 5 = 12 days beats G = 3 days.\n"
     "Critical path: B–D–E–F–H = 4 + 5 + 5 + 7 + 5 = 26 days\n"
     "Minimum duration = 26 days\n"
     "(c) No. A is not on the critical path — A→C takes 6 days against B→D's 9, "
     "so A has a float time of 3 days. Increasing A by 2 days still leaves it inside that "
     "float, so the critical path and the 26-day minimum duration are unchanged.",
     "2025 Q19 answer: wrong prerequisites, wrong critical path (BFH 16 -> BDEFH 26) and a "
     "self-contradictory part (c) replaced with NESA's")
setf(x, "keywords", ["26", "bdefh", "critical path", "float"],
     "2025 Q19 keywords: the regex-shaped 'b.*f.*h' and the wrong total 16 replaced",
     old=["16", "b.*f.*h", "critical path"])
setf(x, "bandDescriptors", {
    "full": "5/5 — Correct prerequisites, critical path B–D–E–F–H and "
            "minimum duration 26 days, and correctly explains that A's float time of 3 days "
            "absorbs the increase.",
    "partial": "3–4/5 — Critical path and duration correct, or prerequisites correct.",
    "minimal": "1–2/5 — Identifies part of the critical path or one correct prerequisite.",
}, "2025 Q19 bandDescriptors: rebuilt around the correct path and duration")

# ---------------------------------------------------------------------------
# 20. 2025 Q26 -- parts (b) and (c) asked questions the paper never asks, while
#     the model answers worked NESA's actual questions. Paper pp22-23:
#     (b) "What is the approximate area of the curved surface?" and
#     (c) "What is the percentage error of the measurement of 10.2 cm? Give your
#     answer correct to 3 significant figures."
# ---------------------------------------------------------------------------
x = q(2025, 26)
OLD_B = ("The total surface area of the plastic toy is 1300 cm². What percentage of the "
         "total surface area is the curved shaded surface? Give your answer correct to one "
         "decimal place.")
NEW_B = ("The total surface area of the plastic toy is 1300 cm². What is the approximate "
         "area of the curved surface?")
OLD_C = ("The toy uses 1.5 g of plastic per cm³. What mass of plastic is used to make the "
         "toy? Give your answer correct to the nearest gram.")
NEW_C = ("The measurements shown on the diagram are given to the nearest millimetre. What is "
         "the percentage error of the measurement of 10.2 cm? Give your answer correct to 3 "
         "significant figures.")
sub(x, "q", OLD_B, NEW_B, "2025 Q26 (b) stem: paper wording (area, not percentage)")
sub(part(x, "(b)"), "q", OLD_B, NEW_B, "2025 Q26 (b) part prompt: same")
sub(x, "q", OLD_C, NEW_C, "2025 Q26 (c) stem: paper wording (percentage error, not mass)")
setf(part(x, "(c)"), "q", NEW_C, "2025 Q26 (c) part prompt: same", old=OLD_C)
NEW_B_ANS = ("Subtract from the total the faces that are not curved:\n"
             "• two cross-section ends: 2 × 34.68 = 69.36 cm²\n"
             "• rectangular base: 10.2 × 40 = 408 cm²\n"
             "• flat vertical end face: 6 × 40 = 240 cm²\n"
             "1300 = 69.36 + 408 + 240 + curved surface\n"
             "Curved surface ≈ 1300 − 717.36 = 582.64 cm²")
old_b_ans = part(x, "(b)")["answer"]
assert "Using MG:" in old_b_ans, old_b_ans[:150]
setf(part(x, "(b)"), "answer", NEW_B_ANS,
     "2025 Q26 (b) answer: remove the 'Using MG:' leak and the '480 cm...' typo")
sub(x, "answer", old_b_ans, NEW_B_ANS, "2025 Q26 answer: same clean-up")

# ---------------------------------------------------------------------------
# 21. 2025 Q35 -- a self-cancelling parenthetical.
# ---------------------------------------------------------------------------
x = q(2025, 35)
OLD35 = ("Since the angle of depression from T to A is 36°, the angle TAP (alternate "
         "angle) = 36° (since TA is horizontal from T’s perspective, but actually "
         "∠TAP = 36° from the horizontal at A).")
NEW35 = ("The angle of depression from T to A is 36°, so ∠TAP = 36° (alternate "
         "angles, measured from the horizontal at T and at A).")
sub(x, "answer", OLD35, NEW35, "2025 Q35 answer: replace the self-cancelling parenthetical")

# ---------------------------------------------------------------------------
with io.open(PATH, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(json.dumps(bank, indent=2, ensure_ascii=False) + "\n")

print("applied %d edits" % len(EDITS))
for e in EDITS:
    print("   ", e)
