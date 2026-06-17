"""
audit_written_2022_2024.py
PDF-verified audit of 2022–2024 written questions.

Issues found:
  2022: 8 questions split/truncated (Q16, Q19, Q22, Q24, Q25, Q27, Q30, Q36)
  2023: duplicates (Q24b, Q26b), fix Q21/Q25/Q29, add missing Q30/Q32/Q36
  2024: split Q20/Q24, add missing Q31/Q33/Q37
"""
import json, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

JSON = 'subjects/mathematics-standard-2.json'
with open(JSON, 'r', encoding='utf-8') as f:
    data = json.load(f)

written = data['writtenQuestions']

def find_q(year, qnum):
    for i, q in enumerate(written):
        if q.get('year') == year and str(q.get('qNum')) == str(qnum):
            return i, q
    return None, None

def remove_q(year, qnum):
    for i, q in enumerate(written):
        if q.get('year') == year and str(q.get('qNum')) == str(qnum):
            written.pop(i)
            return True
    return False

def insert_after(year, qnum_ref, new_q):
    """Insert new_q immediately after the question with qnum_ref in same year."""
    for i, q in enumerate(written):
        if q.get('year') == year and str(q.get('qNum')) == str(qnum_ref):
            written.insert(i + 1, new_q)
            return
    written.append(new_q)

changes = []

# ─────────────────────────────────────────────
# 2022 FIXES
# ─────────────────────────────────────────────

# Q16: merge Q16(a)(1m) + Q16(b)(2m) → Q16(3m)
remove_q(2022, '16(a)')
idx, q = find_q(2022, '16(b)')
if q:
    q['qNum'] = '16'
    q['marks'] = 3
    q['q'] = (
        'Tom is 25 years old, and likes to keep fit by exercising.\n\n'
        '(a) Use this formula to find his maximum heart rate (bpm).\n'
        'Maximum heart rate = 220 − age in years\n\n'
        '(b) Tom will get the most benefit from this exercise if his heart rate is '
        'between 50% and 85% of his maximum heart rate.\n'
        'Between what two heart rates should Tom be aiming for to get the most benefit '
        'from his exercise?'
    )
    q['answer'] = (
        '(a) Maximum heart rate = 220 − 25 = 195 bpm\n\n'
        '(b) Lower: 50% × 195 = 97.5 bpm; Upper: 85% × 195 = 165.75 bpm\n'
        'Tom should aim for a heart rate between 97.5 bpm and 165.75 bpm.'
    )
    q['keywords'] = ['195', '97.5', '165.75', '98', '166', '50%', '85%', 'maximum heart rate', 'range']
    q['minKeywords'] = 2
    q['bandDescriptors'] = {
        '1': 'Calculates maximum heart rate correctly (195 bpm).',
        '2': 'Finds correct lower heart rate target.',
        '3': 'Finds both correct heart rate targets.'
    }
    changes.append('2022 Q16: merged Q16(a)+(b) → Q16 (3m)')

# Q19: expand Q19(a)(2m) → Q19(3m) with full table + part (b)
idx, q = find_q(2022, '19(a)')
if q:
    q['qNum'] = '19'
    q['marks'] = 3
    q['q'] = (
        'The table shows the types of customer complaints received by an online business in a month.\n\n'
        '| Type of complaint | Frequency | Cumulative frequency | Cumulative percentage |\n'
        '|---|---|---|---|\n'
        '| Stock shortage | 98 | 98 | 49 |\n'
        '| Delivery fee | 62 | A | 80 |\n'
        '| Delivery time | 24 | 184 | 92 |\n'
        '| Damaged item | 8 | 192 | B |\n'
        '| Returns policy | 6 | 198 | 99 |\n'
        '| Product information | 2 | 200 | 100 |\n'
        '| Total | 200 | | |\n\n'
        '(a) What are the values of A and B?  (2 marks)\n\n'
        '(b) The data from the table are shown in a Pareto chart. '
        'The manager will address 80% of the complaints.\n'
        'Which types of complaints will the manager address?  (1 mark)'
    )
    q['answer'] = (
        '(a) A = 160 (cumulative: 98 + 62 = 160); B = 96 (192/200 × 100 = 96)\n\n'
        '(b) Stock shortage and Delivery fee '
        '(these two types account for 80% of complaints, up to the 80% cumulative percentage line).'
    )
    q['keywords'] = ['160', '96', 'stock shortage', 'delivery fee', '80%', 'pareto', 'two types']
    q['minKeywords'] = 2
    q['bandDescriptors'] = {
        '1': 'Finds one of A or B correctly.',
        '2': 'Finds both A and B correctly.',
        '3': 'Correctly identifies both complaint types that account for 80%.'
    }
    changes.append('2022 Q19: expanded Q19(a) → Q19 (3m) with full table + part (b)')

# Q22: merge Q22(a)(1m) + Q22(b)(2m) → Q22(3m)
remove_q(2022, '22(a)')
idx, q = find_q(2022, '22(b)')
if q:
    q['qNum'] = '22'
    q['marks'] = 3
    q['q'] = (
        'The formula C = 100n + b is used to calculate the cost of producing laptops, where '
        'C is the cost in dollars, n is the number of laptops produced and b is the fixed cost in dollars.\n\n'
        '(a) Find the cost when 1943 laptops are produced and the fixed cost is $20 180.  (1 mark)\n\n'
        '(b) Some laptops have extra features added. The formula to calculate the production cost for these is:\n'
        'C = 100n + an + 20 180\n'
        'where a is the additional cost in dollars per laptop produced.\n'
        'Find the number of laptops produced if the additional cost is $26 per laptop and '
        'the total production cost is $97 040.  (2 marks)'
    )
    q['answer'] = (
        '(a) C = 100 × 1943 + 20 180 = 194 300 + 20 180 = $214 480\n\n'
        '(b) 97 040 = 100n + 26n + 20 180\n'
        '97 040 − 20 180 = 126n\n'
        '76 860 = 126n\n'
        'n = 610 laptops'
    )
    q['keywords'] = ['214480', '214 480', '610', '126n', '76860', '76 860']
    q['minKeywords'] = 2
    q['bandDescriptors'] = {
        '1': 'Correctly calculates the cost in part (a).',
        '2': 'Sets up the correct equation for part (b).',
        '3': 'Correctly solves for the number of laptops in part (b).'
    }
    changes.append('2022 Q22: merged Q22(a)+(b) → Q22 (3m)')

# Q24: expand Q24(a)(2m) → Q24(4m) adding part (b)
idx, q = find_q(2022, '24(a)')
if q:
    q['qNum'] = '24'
    q['marks'] = 4
    q['q'] = (
        'A student believes that the time it takes for an ice cube to melt (M minutes) varies '
        'inversely with the room temperature (T °C). The student observes that at a room '
        'temperature of 15°C it takes 12 minutes for an ice cube to melt.\n\n'
        '(a) Find the equation relating M and T.  (2 marks)\n\n'
        '(b) By first completing this table of values, graph the relationship between '
        'temperature and time from T = 5°C to T = 30°C.  (2 marks)\n\n'
        '| T | 5 | 15 | 30 |\n'
        '|---|---|---|---|\n'
        '| M | | 12 | |'
    )
    q['answer'] = (
        '(a) M = k/T; at T = 15, M = 12: 12 = k/15 → k = 180\n'
        'Equation: M = 180/T\n\n'
        '(b) T = 5: M = 180/5 = 36; T = 30: M = 180/30 = 6\n'
        'Graph: decreasing hyperbola through (5, 36), (15, 12), (30, 6).'
    )
    q['keywords'] = ['M = 180/T', '180', 'k = 180', 'inversely', '36', '6', 'hyperbola', 'graph']
    q['minKeywords'] = 2
    q['bandDescriptors'] = {
        '1': 'Identifies inverse variation and finds k = 180.',
        '2': 'States the equation M = 180/T correctly.',
        '3': 'Correctly completes the table of values.',
        '4': 'Draws correct graph of the hyperbola from T = 5 to T = 30.'
    }
    changes.append('2022 Q24: expanded Q24(a)(2m) → Q24 (4m) adding part (b) with table')

# Q25: expand Q25(a)(2m) → Q25(4m) adding part (b) and full FV table
idx, q = find_q(2022, '25(a)')
if q:
    q['qNum'] = '25'
    q['marks'] = 4
    q['q'] = (
        'The table shows the future value of an annuity of $1.\n\n'
        '| Years | 1% | 2% | 3% | 4% |\n'
        '|---|---|---|---|---|\n'
        '| 4 | 4.060 | 4.122 | 4.184 | 4.246 |\n'
        '| 5 | 5.101 | 5.204 | 5.309 | 5.416 |\n'
        '| 6 | 6.152 | 6.308 | 6.468 | 6.633 |\n\n'
        'Zal is saving for a trip and estimates he will need $15 000. He opens an account '
        'earning 3% per annum, compounded annually.\n\n'
        '(a) How much does Zal need to deposit every year if he wishes to have enough '
        'money for the trip in 4 years time?  (2 marks)\n\n'
        '(b) How much interest will Zal earn on his investment over the 4 years? '
        'Give your answer to the nearest dollar.  (2 marks)'
    )
    q['answer'] = (
        '(a) FV factor = 4.184 (4 years, 3%)\n'
        'Annual deposit = $15 000 / 4.184 = $3585.11 ≈ $3585\n\n'
        '(b) Total deposited = 4 × $3585 = $14 340\n'
        'Interest earned = $15 000 − $14 340 = $660'
    )
    q['keywords'] = ['3585', '$3585', '4.184', '$660', '660', '14340', '14 340', 'interest']
    q['minKeywords'] = 2
    q['bandDescriptors'] = {
        '1': 'Uses the correct FV factor (4.184) from the table.',
        '2': 'Calculates correct annual deposit (~$3585).',
        '3': 'Calculates total deposited correctly.',
        '4': 'Finds interest earned correctly ($660).'
    }
    changes.append('2022 Q25: expanded Q25(a)(2m) → Q25 (4m) with full FV table + part (b)')

# Q27: expand Q27(a)(i)(1m) → Q27(4m) with all parts
idx, q = find_q(2022, '27(a)(i)')
if q:
    q['qNum'] = '27'
    q['marks'] = 4
    q['q'] = (
        'A company purchases a machine for $50 000. The two methods of depreciation being '
        'considered are the declining-balance method and the straight-line method.\n\n'
        '(a) For the declining-balance method, the salvage value of the machine after n years '
        'is given by the formula:\n'
        'S = V₀ × (0.80)ⁿ\n'
        'where S is the salvage value and V₀ is the initial value of the asset.\n\n'
        '(i) What is the annual rate of depreciation used in this formula?  (1 mark)\n\n'
        '(ii) Calculate the salvage value of the machine after 3 years, based on the '
        'given formula.  (1 mark)\n\n'
        '(b) For the straight-line method, the value of the machine is depreciated at a '
        'rate of 12.2% of the purchase price each year.\n'
        'When will the value of the machine, using this method, be equal to the salvage '
        'value found in part (a)(ii)?  (2 marks)'
    )
    q['answer'] = (
        '(a)(i) Annual rate of depreciation = 20% (since 0.80 = 1 − 0.20)\n\n'
        '(a)(ii) S = 50 000 × (0.80)³ = 50 000 × 0.512 = $25 600\n\n'
        '(b) Straight-line annual depreciation = 12.2% × $50 000 = $6100\n'
        'Value after n years = 50 000 − 6100n\n'
        'Set equal to $25 600: 50 000 − 6100n = 25 600\n'
        '6100n = 24 400 → n = 4 years'
    )
    q['keywords'] = ['20%', '20 percent', '25600', '$25 600', '4 years', 'after 4 years', '6100', '24400']
    q['minKeywords'] = 2
    q['bandDescriptors'] = {
        '1': 'States the correct annual rate of depreciation (20%).',
        '2': 'Correctly calculates the salvage value after 3 years ($25 600).',
        '3': 'Correctly calculates the straight-line depreciation amount per year.',
        '4': 'Correctly determines when the two values are equal (after 4 years).'
    }
    changes.append('2022 Q27: expanded Q27(a)(i)(1m) → Q27 (4m) with all parts')

# Q30: expand Q30(a)(2m) → Q30(4m) with FV table and part (b)
idx, q = find_q(2022, '30(a)')
if q:
    q['qNum'] = '30'
    q['marks'] = 4
    q['q'] = (
        'Eli is choosing between two investment options.\n'
        'Option 1: Depositing a single amount of $40 000 today, earning interest of 1.2% per '
        'annum, compounded monthly.\n'
        'Option 2: Depositing $1000 at the end of each quarter, earning interest of 2.4% per '
        'annum, compounded quarterly.\n\n'
        'A table of future value interest factors for an annuity of $1 is shown.\n\n'
        '| N \\ r | 0.002 | 0.006 | 0.020 | 0.024 | 0.060 | 0.240 |\n'
        '|---|---|---|---|---|---|---|\n'
        '| 10 | 10.09048 | 10.27437 | 10.94972 | 11.15211 | 13.18079 | 31.64344 |\n'
        '| 20 | 20.38460 | 21.18211 | 24.29737 | 25.28909 | 36.78559 | 303.60062 |\n'
        '| 30 | 30.88646 | 32.76227 | 40.56808 | 43.20983 | 79.05819 | 2640.91639 |\n'
        '| 40 | 41.60026 | 45.05630 | 60.40198 | 65.92708 | 154.76197 | 22728.80260 |\n\n'
        '(a) What is the value of Eli\'s investment after 10 years using Option 1?  (2 marks)\n\n'
        '(b) What is the difference between the future values after 10 years using Option 1 '
        'and Option 2?  (2 marks)'
    )
    q['answer'] = (
        '(a) Option 1: A = 40 000 × (1 + 0.001)^120 = 40 000 × (1.001)^120 ≈ $45 093.59\n\n'
        '(b) Option 2: rate per quarter = 0.6% = 0.006, periods = 40\n'
        'FV = 1000 × 45.056 = $45 056.30\n'
        'Difference = $45 093.59 − $45 056.30 ≈ $37.29 (Option 1 gives more)'
    )
    q['keywords'] = ['45093', '$45 093', '(1.001)', '120', '45056', '45.056', '37', 'difference', 'option 1', 'option 2']
    q['minKeywords'] = 2
    q['bandDescriptors'] = {
        '1': 'Identifies correct compound interest formula for Option 1.',
        '2': 'Correctly calculates Option 1 future value (~$45 094).',
        '3': 'Uses correct FV factor for Option 2 (r=0.006, N=40).',
        '4': 'Calculates the correct difference between the two options.'
    }
    changes.append('2022 Q30: expanded Q30(a)(2m) → Q30 (4m) with FV table + part (b)')

# Q36: expand Q36(a)(2m) → Q36(5m) adding part (b)
idx, q = find_q(2022, '36(a)')
if q:
    q['qNum'] = '36'
    q['marks'] = 5
    q['q'] = (
        'Frankie borrows $200 000 from a bank. The loan is to be repaid over 23 years at a '
        'rate of 7.2% per annum, compounded monthly. The repayments have been set at $1485 per month.\n\n'
        'The interest charged and the balance owing for the first three months of the loan are shown below.\n\n'
        '| Month | Principal (start of month) | Interest charged | Monthly repayment | Balance (end of month) |\n'
        '|---|---|---|---|---|\n'
        '| 1 | $200 000 | $1200 | $1485 | $199 715 |\n'
        '| 2 | $199 715 | A | $1485 | $199 428.29 |\n'
        '| 3 | $199 428.29 | $1196.57 | $1485 | B |\n\n'
        '(a) What are the values of A and B?  (2 marks)\n\n'
        '(b) After 50 months of repaying the loan, Frankie decides to make a lump sum payment '
        'of $40 000 and to continue making the monthly repayments of $1485. The loan will then '
        'be fully repaid after a further 146 monthly repayments.\n'
        'How much less will Frankie pay overall by making the lump sum payment?  (3 marks)'
    )
    q['answer'] = (
        '(a) A = 199 715 × 0.006 = $1198.29\n'
        'B = 199 428.29 + 1196.57 − 1485 = $199 139.86\n\n'
        '(b) Without lump sum: 23 years × 12 = 276 months × $1485 = $409 860\n'
        'With lump sum: (50 × $1485) + $40 000 + (146 × $1485)\n'
        '= $74 250 + $40 000 + $216 810 = $331 060\n'
        'Saving = $409 860 − $331 060 = $78 800'
    )
    q['keywords'] = ['1198.29', '$1198', '199139', '$199 139', '78800', '$78 800', '409860', '331060', 'lump sum']
    q['minKeywords'] = 2
    q['bandDescriptors'] = {
        '1': 'Correctly calculates A = $1198.29.',
        '2': 'Correctly calculates B = $199 139.86.',
        '3': 'Correctly calculates total repayments without lump sum ($409 860).',
        '4': 'Correctly calculates total repayments with lump sum ($331 060).',
        '5': 'Correctly finds the saving of $78 800.'
    }
    changes.append('2022 Q36: expanded Q36(a)(2m) → Q36 (5m) adding part (b)')


# ─────────────────────────────────────────────
# 2023 FIXES
# ─────────────────────────────────────────────

# Q21: Replace Q21(c,d)(3m) with full Q21(5m)
idx, q = find_q(2023, '21(c,d)')
if q:
    q['qNum'] = '21'
    q['marks'] = 5
    q['q'] = (
        'Electricity provider A charges 25 cents per kilowatt hour (kWh) for electricity, '
        'plus a fixed monthly charge of $40.\n\n'
        '(a) Complete the table showing Provider A\'s monthly charges for different levels '
        'of electricity usage.  (1 mark)\n\n'
        '| Electricity used (kWh) | 0 | 200 | 400 | 600 |\n'
        '|---|---|---|---|---|\n'
        '| Monthly charge ($) | 40 | | | |\n\n'
        'Provider B charges 35 cents per kWh, with no fixed monthly charge.\n\n'
        '(b) On a grid, graph Provider A\'s charges from the table above. '
        '(Provider B\'s line is already plotted on the grid in the exam.)  (2 marks)\n\n'
        '(c) Use the two graphs to determine the number of kilowatt hours per month for which '
        'Provider A and Provider B charge the same amount.  (1 mark)\n\n'
        '(d) A customer uses an average of 800 kWh per month.\n'
        'Which provider, A or B, would be the cheaper option and by how much?  (1 mark)'
    )
    q['answer'] = (
        '(a) 200 kWh: $90; 400 kWh: $140; 600 kWh: $190\n\n'
        '(b) Graph Provider A from (0, 40) to (600, 190) — straight line\n\n'
        '(c) Equate: 0.25k + 40 = 0.35k → 40 = 0.10k → k = 400 kWh\n\n'
        '(d) Provider A at 800 kWh: 0.25 × 800 + 40 = $240\n'
        'Provider B at 800 kWh: 0.35 × 800 = $280\n'
        'Provider A is cheaper by $40.'
    )
    q['keywords'] = ['400 kWh', '400', 'provider A', 'cheaper', '$40', '40', '$240', '$280', '0.25k', 'equation']
    q['minKeywords'] = 2
    q['bandDescriptors'] = {
        '1': 'Correctly completes the table for Provider A.',
        '2': 'Graphs Provider A\'s charges correctly.',
        '3': 'Correctly identifies the break-even point (400 kWh).',
        '4': 'Calculates costs for both providers at 800 kWh.',
        '5': 'Correctly identifies Provider A as cheaper by $40.'
    }
    changes.append('2023 Q21: replaced Q21(c,d)(3m) → Q21 (5m) full question with all parts')

# Q24: Remove duplicate Q24(b)(3m) — keep Q24(5m)
removed = remove_q(2023, '24(b)')
if removed:
    changes.append('2023 Q24: removed duplicate Q24(b)(3m) entry — Q24(5m) kept')

# Q25: Replace Q25(a)(2m) + Q25(b)(3m) → Q25(5m) with full FV table
removed = remove_q(2023, '25(a)')
idx, q = find_q(2023, '25(b)')
if q:
    q['qNum'] = '25'
    q['marks'] = 5
    q['q'] = (
        'A table of future value interest factors for an annuity of $1 is shown.\n\n'
        '| Period (n) | 1.5% | 3% | 4.5% | 6% |\n'
        '|---|---|---|---|---|\n'
        '| 5 | 5.152 | 5.309 | 5.471 | 5.637 |\n'
        '| 10 | 10.703 | 11.464 | 12.288 | 13.181 |\n'
        '| 20 | 23.124 | 26.870 | 31.371 | 36.786 |\n'
        '| 40 | 54.268 | 75.401 | 107.030 | 154.762 |\n\n'
        '(a) Micky wants to save $450 000 over the next 10 years.\n'
        'If the interest rate is 6% per annum compounding annually, how much should '
        'Micky contribute each year? Give your answer to the nearest dollar.  (2 marks)\n\n'
        '(b) Instead, Micky decides to contribute $8535 every three months for 10 years '
        'to an annuity paying 6% per annum, compounding quarterly.\n'
        'How much will Micky have at the end of 10 years?  (3 marks)'
    )
    q['answer'] = (
        '(a) FV factor: n = 10, r = 6% → 13.181\n'
        'Annual deposit = $450 000 / 13.181 = $34 140 (nearest dollar)\n\n'
        '(b) Quarterly rate = 6%/4 = 1.5%, periods = 10 × 4 = 40\n'
        'FV factor: n = 40, r = 1.5% → 54.268\n'
        'FV = $8535 × 54.268 = $463 177.38'
    )
    q['keywords'] = ['34140', '$34 140', '13.181', '463177', '$463 177', '54.268', '40 periods', 'quarterly', '1.5%']
    q['minKeywords'] = 2
    q['bandDescriptors'] = {
        '1': 'Uses correct FV factor for part (a) (13.181).',
        '2': 'Correctly calculates annual deposit for part (a) (~$34 140).',
        '3': 'Identifies correct quarterly rate (1.5%) and periods (40) for part (b).',
        '4': 'Uses correct FV factor for part (b) (54.268).',
        '5': 'Calculates correct future value for part (b) (~$463 177).'
    }
    changes.append('2023 Q25: removed Q25(a)+(b) split → Q25 (5m) with full FV table')

# Q26: Remove duplicate Q26(b)(3m) — keep Q26(5m)
removed = remove_q(2023, '26(b)')
if removed:
    changes.append('2023 Q26: removed duplicate Q26(b)(3m) entry — Q26(5m) kept')

# Q29: Fix content — currently has depreciation text, should be monthly repayment table
idx, q = find_q(2023, '29')
if q:
    q['image'] = None
    q['q'] = (
        'The table shows monthly repayments for each $1000 borrowed '
        '(Principal and Interest per $1000 borrowed):\n\n'
        '| Interest rate (p.a.) | 5 yrs | 10 yrs | 15 yrs | 20 yrs | 25 yrs | 30 yrs |\n'
        '|---|---|---|---|---|---|---|\n'
        '| 6.5% | 19.57 | 11.35 | 8.71 | 7.46 | 6.75 | 6.32 |\n'
        '| 7.0% | 19.80 | 11.61 | 8.99 | 7.75 | 7.07 | 6.65 |\n'
        '| 7.5% | 20.04 | 11.87 | 9.27 | 8.06 | 7.39 | 6.99 |\n'
        '| 8.0% | 20.28 | 12.13 | 9.56 | 8.36 | 7.72 | 7.34 |\n\n'
        '(a) A couple borrows $520 000 to buy a house at 8% per annum over 25 years.\n'
        'How much does the couple repay in total for this loan?  (3 marks)\n\n'
        '(b) Chris borrows some money at 7% per annum. Chris will repay the loan over '
        '15 years, paying $3596 per month.\n'
        'How much money does Chris borrow?  (1 mark)'
    )
    q['marks'] = 4
    q['answer'] = (
        '(a) Repayment per $1000 at 8%, 25 years = $7.72\n'
        'Monthly repayment = (520 000/1000) × 7.72 = $4014.40\n'
        'Total repaid = $4014.40 × 25 × 12 = $1 204 320\n\n'
        '(b) Monthly repayment per $1000 at 7%, 15 years = $8.99\n'
        '$3596 / $8.99 = 400 units → Amount borrowed = 400 × $1000 = $400 000'
    )
    q['keywords'] = ['4014.40', '$4014.40', '1204320', '$1 204 320', '400 000', '$400 000', '7.72', '8.99', 'monthly repayment']
    q['minKeywords'] = 2
    q['bandDescriptors'] = {
        '1': 'Identifies the correct table entry for 8%, 25 years ($7.72).',
        '2': 'Calculates the monthly repayment for the couple ($4014.40).',
        '3': 'Calculates the total amount repaid ($1 204 320).',
        '4': 'Correctly calculates Chris\'s loan amount ($400 000).'
    }
    changes.append('2023 Q29: corrected content — now monthly repayment table question (was depreciation)')

# Add missing Q30 (3m, 2023): Supermarket GST
idx30, q30_ref = find_q(2023, '29')  # insert after Q29
new_q30 = {
    'year': 2023, 'marks': 3, 'section': 'II', 'qNum': '30', 'category': 'F4',
    'image': None,
    'q': (
        'A receipt from a supermarket shows a total of $124.87. '
        'The GST shown on the receipt is $3.86.\n'
        'GST, at a rate of 10%, is only charged on some items.\n'
        'What was the value of the items which did NOT have GST charged?'
    ),
    'answer': (
        'Pre-GST value of items with GST = $3.86 / 0.10 = $38.60\n'
        'Total cost of items with GST (inc. GST) = $38.60 + $3.86 = $42.46\n'
        'Items without GST = $124.87 − $42.46 = $82.41'
    ),
    'keywords': ['82.41', '$82.41', '38.60', '$38.60', '42.46', 'gst', 'without gst', '10%'],
    'minKeywords': 1,
    'bandDescriptors': {
        '1': 'Correctly calculates pre-GST value of taxable items.',
        '2': 'Correctly identifies total with-GST amount.',
        '3': 'Correctly calculates the value of items without GST ($82.41).'
    }
}
insert_after(2023, '29', new_q30)
changes.append('2023 Q30: added missing supermarket GST question (3m)')

# Add missing Q32 (4m, 2023): Credit card interest (Ali)
idx_ref, _ = find_q(2023, '31')
new_q32 = {
    'year': 2023, 'marks': 4, 'section': 'II', 'qNum': '32', 'category': 'F4',
    'image': None,
    'q': (
        'Ali has a credit card which has no interest-free period. Interest is charged at '
        '13.5% per annum, compounding daily, on the amount owing.\n'
        'During the month, Ali made only one purchase of $450 using the credit card. '
        'The full amount owing was repaid 21 days later.\n\n'
        '(a) Calculate the amount of interest charged on the purchase, assuming that '
        'interest is charged for the 21 days.  (3 marks)\n\n'
        '(b) What percentage of the full amount repaid is the interest? '
        'Give the answer to two decimal places.  (1 mark)'
    ),
    'answer': (
        '(a) Daily rate = 13.5% ÷ 365 = 0.13500/365\n'
        'A = 450 × (1 + 0.135/365)^21 ≈ 450 × 1.007799 ≈ $453.51\n'
        'Interest = $453.51 − $450 = $3.51\n\n'
        '(b) Percentage = ($3.51 / $453.51) × 100 ≈ 0.77%'
    ),
    'keywords': ['3.51', '$3.51', '0.77%', '0.77', '13.5', '365', '21', 'compounding daily', 'interest'],
    'minKeywords': 1,
    'bandDescriptors': {
        '1': 'States correct daily interest rate formula.',
        '2': 'Sets up compound interest formula correctly.',
        '3': 'Calculates interest amount correctly (~$3.51).',
        '4': 'Calculates the correct percentage to 2 decimal places (0.77%).'
    }
}
insert_after(2023, '31', new_q32)
changes.append('2023 Q32: added missing credit card interest question (4m)')

# Add missing Q36 (4m, 2023): BAC formula Cameron
idx_ref, _ = find_q(2023, '35')
new_q36 = {
    'year': 2023, 'marks': 4, 'section': 'II', 'qNum': '36', 'category': 'A4',
    'image': None,
    'q': (
        'The following formula can be used to calculate an estimate for blood alcohol '
        'content (BAC) for males:\n\n'
        'BAC_male = (10N − 7.5H) / (6.8M)\n\n'
        'where N = number of standard drinks consumed, M = person\'s weight in kilograms, '
        'H = number of hours of drinking.\n\n'
        'Cameron weighs 75 kg. His BAC was zero when he began drinking alcohol. '
        'At 9:00 pm, after consuming 3 standard drinks, his BAC was 0.02.\n\n'
        'Using the formula, estimate at what time Cameron began drinking alcohol, '
        'to the nearest minute.'
    ),
    'answer': (
        '0.02 = (10 × 3 − 7.5H) / (6.8 × 75)\n'
        '0.02 × 510 = 30 − 7.5H\n'
        '10.2 = 30 − 7.5H\n'
        '7.5H = 19.8\n'
        'H = 2.64 hours = 2 hours 38.4 minutes ≈ 2 hours 38 minutes\n\n'
        'Cameron began drinking at 9:00 pm − 2 h 38 min = 6:22 pm.'
    ),
    'keywords': ['6:22', '6:22 pm', '18:22', '2.64', '2 hours 38', '7.5H = 19.8', '19.8', 'BAC', '510'],
    'minKeywords': 1,
    'bandDescriptors': {
        '1': 'Correctly substitutes values into the BAC formula.',
        '2': 'Correctly solves for H = 2.64 hours.',
        '3': 'Converts hours to hours and minutes correctly.',
        '4': 'States the correct starting time (6:22 pm).'
    }
}
insert_after(2023, '35', new_q36)
changes.append('2023 Q36: added missing BAC formula question (4m)')


# ─────────────────────────────────────────────
# 2024 FIXES
# ─────────────────────────────────────────────

# Q20: merge Q20(a)(1m) + Q20(b)(2m) → Q20(3m) with full FV table
remove_q(2024, '20(a)')
idx, q = find_q(2024, '20(b)')
if q:
    q['qNum'] = '20'
    q['marks'] = 3
    q['q'] = (
        'The table shows the future value for an annuity of $1 for varying interest rates '
        'and time periods.\n\n'
        '| Period | 1% | 2% | 3% | 4% | 5% |\n'
        '|---|---|---|---|---|---|\n'
        '| 1 | 1.0100 | 1.0200 | 1.0300 | 1.0400 | 1.0500 |\n'
        '| 2 | 2.0301 | 2.0604 | 2.0909 | 2.1216 | 2.1525 |\n'
        '| 3 | 3.0604 | 3.1216 | 3.1836 | 3.2465 | 3.3101 |\n'
        '| 4 | 4.1010 | 4.2040 | 4.3091 | 4.4163 | 4.5256 |\n'
        '| 5 | 5.1520 | 5.3081 | 5.4684 | 5.6330 | 5.8019 |\n'
        '| 6 | 6.2135 | 6.4343 | 6.6625 | 6.8983 | 7.1420 |\n'
        '| 7 | 7.2857 | 7.5830 | 7.8923 | 8.2142 | 8.5491 |\n'
        '| 8 | 8.3685 | 8.7546 | 9.1591 | 9.5828 | 10.0266 |\n\n'
        '(a) Ken invests $200 at the start of each year for eight years, at an interest '
        'rate of 5% per annum.\n'
        'Calculate the future value of Ken\'s investment.  (1 mark)\n\n'
        '(b) Shay is planning to take a holiday in three years. She needs $4500 for this '
        'holiday and will make regular six-monthly payments into an account that earns '
        'interest at the rate of 4% per annum, compounded 6 monthly.\n'
        'What is the minimum amount Shay needs to pay into this account every 6 months? '
        'Give your answer to the nearest $10. Support your answer with calculations.  (2 marks)'
    )
    q['answer'] = (
        '(a) FV factor: n = 8, r = 5% → 10.0266\n'
        'FV = $200 × 10.0266 = $2005.32\n\n'
        '(b) Rate per 6 months = 4%/2 = 2%; periods = 3 × 2 = 6\n'
        'FV factor: n = 6, r = 2% → 6.4343\n'
        'Payment = $4500 / 6.4343 = $699.46 → rounded up to nearest $10 = $700'
    )
    q['keywords'] = ['2005.32', '$2005', '10.0266', '$700', '700', '6.4343', '699', 'six-monthly', '2%', '6 periods']
    q['minKeywords'] = 2
    q['bandDescriptors'] = {
        '1': 'Uses correct FV factor (10.0266) and calculates Ken\'s investment ($2005.32).',
        '2': 'Identifies 2% rate and 6 periods for Shay\'s investment.',
        '3': 'Uses FV factor 6.4343 and correctly rounds to $700.'
    }
    changes.append('2024 Q20: merged Q20(a)+(b) → Q20 (3m) with full FV table')

# Q24: expand Q24(a)(2m) → Q24(4m) adding part (b)
idx, q = find_q(2024, '24(a)')
if q:
    q['qNum'] = '24'
    q['marks'] = 4
    q['q'] = (
        'Sarah, a 60 kg female, consumes 3 glasses of wine at a family dinner over 2.5 hours.\n'
        'Note: there are 1.2 standard drinks in one glass of wine.\n\n'
        'The blood alcohol content (BAC) for females can be estimated by:\n'
        'BAC_female = (10N − 7.5H) / (5.5M)\n\n'
        'where N = number of standard drinks, H = number of hours drinking, '
        'M = mass in kilograms.\n\n'
        '(a) Calculate Sarah\'s BAC at the end of the dinner, correct to 3 decimal places.  (2 marks)\n\n'
        '(b) The time it takes a person\'s BAC to reach zero is given by:\n'
        'Time = BAC / 0.015\n\n'
        'Calculate the time it takes for Sarah\'s BAC to return to zero, assuming she '
        'stopped drinking after 2.5 hours. Give your answer to the nearest minute.  (2 marks)'
    )
    q['answer'] = (
        '(a) N = 3 × 1.2 = 3.6 standard drinks; H = 2.5; M = 60\n'
        'BAC = (10 × 3.6 − 7.5 × 2.5) / (5.5 × 60) = (36 − 18.75) / 330 = 17.25/330 ≈ 0.052\n\n'
        '(b) Time = 0.052 / 0.015 = 3.47 hours = 3 hours 28 minutes'
    )
    q['keywords'] = ['0.052', '3.6', '3 hours 28', '3 h 28', '208 minutes', '17.25', '330', 'BAC', '0.015']
    q['minKeywords'] = 2
    q['bandDescriptors'] = {
        '1': 'Correctly calculates total standard drinks (3.6).',
        '2': 'Correctly calculates BAC to 3 decimal places (0.052).',
        '3': 'Sets up time = BAC/0.015 correctly.',
        '4': 'Converts time to hours and minutes correctly (3 h 28 min).'
    }
    changes.append('2024 Q24: expanded Q24(a)(2m) → Q24 (4m) adding BAC-to-zero part (b)')

# Add missing Q31 (3m, 2024): Biased coin
idx_ref, _ = find_q(2024, '30')
new_q31_2024 = {
    'year': 2024, 'marks': 3, 'section': 'II', 'qNum': '31', 'category': 'S4',
    'image': None,
    'q': (
        'A coin is biased so that it is twice as likely to show a head than a tail.\n\n'
        '(a) What is the probability of obtaining a head with one throw of this coin?  (1 mark)\n\n'
        '(b) In two throws of this coin, what is the probability of obtaining at least one head?  (2 marks)'
    ),
    'answer': (
        '(a) Let P(T) = p. Then P(H) = 2p. P(H) + P(T) = 1 → 3p = 1 → p = 1/3.\n'
        'P(H) = 2/3\n\n'
        '(b) P(at least one head) = 1 − P(no heads) = 1 − (1/3)² = 1 − 1/9 = 8/9'
    ),
    'keywords': ['2/3', '8/9', '1/3', '1 − 1/9', 'complement', 'at least one', 'biased'],
    'minKeywords': 1,
    'bandDescriptors': {
        '1': 'Correctly finds P(H) = 2/3.',
        '2': 'Uses the complement rule correctly.',
        '3': 'Calculates P(at least one head) = 8/9.'
    }
}
insert_after(2024, '30', new_q31_2024)
changes.append('2024 Q31: added missing biased coin probability question (3m)')

# Add missing Q33 (3m, 2024): Wombat speed
idx_ref, _ = find_q(2024, '32')
new_q33_2024 = {
    'year': 2024, 'marks': 3, 'section': 'II', 'qNum': '33', 'category': 'M1',
    'image': None,
    'q': (
        'Wombats can run at a speed of 40 km/h over short distances.\n'
        'At this speed, how many seconds would it take a wombat to run 150 metres?'
    ),
    'answer': (
        '40 km/h = 40 000 m / 3600 s = 100/9 m/s ≈ 11.11 m/s\n'
        'Time = 150 / (100/9) = 150 × 9/100 = 13.5 seconds'
    ),
    'keywords': ['13.5', '13.5 seconds', '11.11', '100/9', '40 000', '3600', 'speed', 'seconds'],
    'minKeywords': 1,
    'bandDescriptors': {
        '1': 'Converts speed from km/h to m/s correctly.',
        '2': 'Sets up time = distance/speed correctly.',
        '3': 'Calculates the correct time of 13.5 seconds.'
    }
}
insert_after(2024, '32', new_q33_2024)
changes.append('2024 Q33: added missing wombat speed/time question (3m)')

# Add missing Q37 (2m, 2024): Time zone travel (Sydney to Rio)
idx_ref, _ = find_q(2024, '36')
new_q37_2024 = {
    'year': 2024, 'marks': 2, 'section': 'II', 'qNum': '37', 'category': 'M1',
    'image': None,
    'q': (
        'Sakura will travel from Sydney (UTC +10) to Rio de Janeiro (UTC −3).\n'
        'The flight from Sydney to Rio de Janeiro will take 20 hours.\n'
        'The flight will arrive in Rio de Janeiro at 3 pm on Wednesday 20 July.\n\n'
        'On what day and at what time will Sakura leave Sydney?'
    ),
    'answer': (
        'Arrival: Wednesday 20 July, 3 pm in Rio (UTC−3)\n'
        'Convert to UTC: 3 pm + 3 h = 6 pm UTC, Wednesday 20 July\n'
        'Convert to Sydney (UTC+10): 6 pm + 10 h = 4 am, Thursday 21 July (Sydney time)\n'
        'Departure from Sydney = arrival time in Sydney − flight duration\n'
        '= 4 am Thursday − 20 hours = 8 am Wednesday 20 July'
    ),
    'keywords': ['8 am', '8:00 am', 'Wednesday', '20 July', 'UTC', '+10', '-3', '13 hours', '8 am Wednesday'],
    'minKeywords': 1,
    'bandDescriptors': {
        '1': 'Correctly converts arrival time to Sydney time.',
        '2': 'Correctly subtracts flight duration to find departure time (8 am Wednesday 20 July).'
    }
}
insert_after(2024, '36', new_q37_2024)
changes.append('2024 Q37: added missing time zone travel question (2m)')


# ─────────────────────────────────────────────
# Write back
# ─────────────────────────────────────────────
with open(JSON, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# Summary
total_2022 = len([q for q in written if q.get('year') == 2022])
total_2023 = len([q for q in written if q.get('year') == 2023])
total_2024 = len([q for q in written if q.get('year') == 2024])
print(f'Done. Changes ({len(changes)}):\n')
for c in changes:
    print(f'  {c}')
print(f'\nwrittenQuestions total: {len(written)}')
print(f'  2022: {total_2022}, 2023: {total_2023}, 2024: {total_2024}')
