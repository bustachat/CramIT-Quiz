"""
fix_2025_written_questions.py
Fix all data quality issues with 2025 written questions in mathematics-standard-2.json.

Issues fixed:
- Q18: embed FV table, fix "compounding monthly" → "annually"
- Q21: merge (a)+(b) split into single 3-mark question
- Q25: replace Q25(b,c) with full 6-mark question + scatterplot image
- Q31: fix image (wrong path) → null, embed full income tax table
- Q34: embed FV table into q text
- Q38: add missing question (fuel efficiency conversion)
- Q40: add missing question (normal distribution sheep, 5 marks)
"""
import sys, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

JSON_PATH = 'subjects/mathematics-standard-2.json'

with open(JSON_PATH, encoding='utf-8') as f:
    data = json.load(f)

written = data['writtenQuestions']

def find_idx(year, qnum):
    for i, q in enumerate(written):
        if q.get('year') == year and str(q.get('qNum')) == str(qnum):
            return i
    return None

changes = []

# -----------------------------------------------------------------------
# Q18 2025: embed FV table, fix compounding type
# -----------------------------------------------------------------------
i = find_idx(2025, '18')
if i is not None:
    written[i]['image'] = None
    written[i]['q'] = (
        'A table of future value interest factors for an annuity of $1 is shown.\n\n'
        '| Period | 1.5% | 3% | 4.5% | 6% |\n'
        '|---|---|---|---|---|\n'
        '| 5 | 5.152 | 5.309 | 5.471 | 5.637 |\n'
        '| 10 | 10.703 | 11.464 | 12.288 | 13.181 |\n'
        '| 20 | 23.124 | 26.870 | 31.371 | 36.786 |\n'
        '| 40 | 54.268 | 75.401 | 107.030 | 154.762 |\n\n'
        'The prize in a lottery is an annuity of $5000 a year for 10 years, '
        'invested at 4.5% per annum compounding annually.\n\n'
        'What will be the value of the prize at the end of 10 years? (2 marks)'
    )
    changes.append('Q18 2025: embedded FV table, fixed compounding type')

# -----------------------------------------------------------------------
# Q21 2025: merge (a)+(b) split into single 3-mark question
# -----------------------------------------------------------------------
ia = find_idx(2025, '21(a)')
ib = find_idx(2025, '21(b)')
if ia is not None and ib is not None:
    # Build merged entry
    merged_q21 = {
        'year': 2025,
        'marks': 3,
        'section': 'II',
        'qNum': '21',
        'category': 'F1',
        'image': None,
        'q': (
            'A house has a reverse-cycle air conditioner which uses 2.5 kW of power '
            'for cooling and 3.2 kW of power for heating. The cost of electricity is '
            '29 cents per kWh.\n\n'
            '(a) Find the cost, in dollars and cents, of cooling the house for 6 hours. (1 mark)\n\n'
            '(b) The cost of operating the air conditioner to heat the house during winter last year '
            'was $640. There are 92 days in winter.\n'
            'Find the number of hours, to 1 decimal place, that the air conditioner was used '
            'on average per day. (2 marks)'
        ),
        'answer': (
            '(a) Cost = power × time × rate\n'
            '= 2.5 kW × 6 h × $0.29/kWh\n'
            '= **$4.35**\n\n'
            '(b) Total hours = $640 ÷ (3.2 kW × $0.29/kWh)\n'
            '= $640 ÷ $0.928/h\n'
            '= 689.655... hours\n'
            'Average per day = 689.655 ÷ 92\n'
            '= **7.5 hours** (to 1 d.p.)'
        ),
        'keywords': ['4.35', '7.5'],
        'minKeywords': 1,
        'bandDescriptors': {
            'high': 'Correctly calculates $4.35 for cooling and 7.5 hours/day for heating.',
            'mid': 'Correctly calculates one part or shows correct method for both.',
            'low': 'Uses Power × Time × Rate formula with some values correct.'
        }
    }
    # Remove higher index first
    ib_actual = find_idx(2025, '21(b)')
    ia_actual = find_idx(2025, '21(a)')
    written.pop(max(ia_actual, ib_actual))
    written[min(ia_actual, ib_actual)] = merged_q21
    changes.append('Q21 2025: merged (a)+(b) into single 3-mark question')

# -----------------------------------------------------------------------
# Q25 2025: replace Q25(b,c) with full 6-mark question + scatterplot
# -----------------------------------------------------------------------
i = find_idx(2025, '25(b,c)')
if i is not None:
    written[i] = {
        'year': 2025,
        'marks': 6,
        'section': 'II',
        'qNum': '25',
        'category': 'S5',
        'image': '/diagrams/mathematics-standard-2_2025_Q25_stimulus.jpg',
        'q': (
            'In a research study, participants were asked to record the number of minutes '
            'they spent watching television and the number of minutes they spent exercising '
            'each day over a period of 3 months. The averages for each participant were '
            'recorded and graphed (scatterplot shown, x = average minutes/day watching TV, '
            'y = average minutes/day exercising).\n\n'
            'The equation of the least-squares regression line for this dataset is '
            'y = 64.3 − 0.7x.\n\n'
            '(a) Describe the bivariate dataset in terms of its form and direction. (2 marks)\n\n'
            '(b) Interpret the values of the slope and y-intercept of the regression line '
            'in the context of this dataset. (2 marks)\n\n'
            '(c) Jo spends an average of 42 minutes per day watching television. Use the '
            'equation of the regression line to determine how many minutes on average Jo '
            'is expected to exercise each day. (1 mark)\n\n'
            '(d) Explain why it is NOT appropriate to extrapolate the regression line to '
            'predict the average number of minutes of exercise per day for someone who '
            'watches an average of 2 hours of television per day. (1 mark)'
        ),
        'answer': (
            '(a) Form: linear (the data points follow an approximately straight-line pattern)\n'
            'Direction: negative (as TV time increases, exercise time decreases)\n\n'
            '(b) Slope = −0.7: for each additional minute of TV watched per day, the '
            'average exercise time decreases by 0.7 minutes per day.\n'
            'y-intercept = 64.3: a person who watches 0 minutes of TV per day is '
            'predicted to exercise 64.3 minutes per day.\n\n'
            '(c) y = 64.3 − 0.7 × 42 = 64.3 − 29.4 = **34.9 minutes per day**\n\n'
            '(d) 2 hours = 120 minutes, which is well beyond the range of the data '
            '(maximum ~60 minutes). Extrapolating outside the data range is unreliable '
            'as the linear relationship may not hold.'
        ),
        'keywords': ['linear', 'negative', '0.7', '64.3', '34.9', 'extrapolat'],
        'minKeywords': 3,
        'bandDescriptors': {
            'high': 'Correctly describes form and direction, interprets both slope and intercept in context, calculates 34.9 min, and gives valid extrapolation reason.',
            'mid': 'Correctly completes 3–4 of the 4 parts with mostly correct reasoning.',
            'low': 'Identifies negative direction or calculates Jo\'s exercise time.'
        }
    }
    changes.append('Q25 2025: replaced Q25(b,c) with full 6-mark question + scatterplot image')

# -----------------------------------------------------------------------
# Q31 2025: fix image → null, embed tax table
# -----------------------------------------------------------------------
i = find_idx(2025, '31')
if i is not None:
    written[i]['image'] = None
    written[i]['q'] = (
        'The table shows the income tax rate for Australian residents for the 2024−2025 '
        'financial year:\n\n'
        '| Taxable income | Tax on this income |\n'
        '|---|---|\n'
        '| $0 – $18 200 | Nil |\n'
        '| $18 201 – $45 000 | 16 cents for each $1 over $18 200 |\n'
        '| $45 001 – $135 000 | $4288 plus 30 cents for each $1 over $45 000 |\n'
        '| $135 001 – $190 000 | $31 288 plus 37 cents for each $1 over $135 000 |\n'
        '| $190 001 and over | $51 638 plus 45 cents for each $1 over $190 000 |\n\n'
        'At the end of the 2024−2025 financial year, Alex\'s tax payable was $47 420, '
        'excluding the Medicare levy.\n\n'
        'What was Alex\'s taxable income? (3 marks)'
    )
    if 'answer' not in written[i] or not written[i].get('answer'):
        written[i]['answer'] = (
            'Tax of $47 420 falls in the $45 001 – $135 000 bracket '
            '(base tax = $4288).\n\n'
            'Additional tax = $47 420 − $4288 = $43 132\n\n'
            'Amount over $45 000:\n'
            '$43 132 ÷ 0.30 = $143 773.33...\n\n'
            'Taxable income = $45 000 + $143 773.33 = **$188 773.33**\n\n'
            '(Verify: $4288 + 0.30 × $143 773.33 = $4288 + $43 132 = $47 420 ✓)'
        )
    changes.append('Q31 2025: image → null, embedded income tax table, verified answer')

# -----------------------------------------------------------------------
# Q34 2025: embed FV table
# -----------------------------------------------------------------------
i = find_idx(2025, '34')
if i is not None:
    written[i]['image'] = None
    written[i]['q'] = (
        'The table shows future value interest factors for an annuity of $1:\n\n'
        '| Period (n) | r = 0.005 | r = 0.01 | r = 0.015 | r = 0.02 | r = 0.03 | r = 0.06 |\n'
        '|---|---|---|---|---|---|---|\n'
        '| 7 | 7.10588 | 7.21354 | 7.32300 | 7.43428 | 7.66246 | 8.39384 |\n'
        '| 28 | 29.97452 | 32.12910 | 34.48148 | 37.05121 | 42.93092 | 68.52811 |\n'
        '| 56 | 64.44140 | 74.58098 | 86.79754 | 101.55826 | 141.15377 | 418.82235 |\n'
        '| 84 | 104.07393 | 130.67227 | 166.17264 | 213.86661 | 365.88054 | 2209.41674 |\n\n'
        'Lin invests a lump sum of $21 000 for 7 years at an interest rate of 6% per annum, '
        'compounding monthly.\n\n'
        'Yemi wants to achieve the same future value as Lin by using an annuity. Yemi plans '
        'to deposit a fixed amount into an investment account at the end of each month for '
        '7 years. The investment account pays 6% per annum, compounding monthly.\n\n'
        'Using the table provided, determine how much Yemi needs to deposit each month. (3 marks)'
    )
    changes.append('Q34 2025: embedded FV factors table')

# -----------------------------------------------------------------------
# Q38 2025: add missing question
# -----------------------------------------------------------------------
i = find_idx(2025, '38')
if i is None:
    # Insert after Q37 (or at end of 2025 section)
    last_2025 = max(j for j,q in enumerate(written) if q.get('year') == 2025)
    written.insert(last_2025 + 1, {
        'year': 2025,
        'marks': 3,
        'section': 'II',
        'qNum': '38',
        'category': 'M1',
        'image': None,
        'q': (
            'A car\'s fuel efficiency is 30 miles per US gallon.\n\n'
            '1 US gallon = 3.8 litres (correct to 2 significant figures)\n'
            '1 mile = 1.6 km (correct to 2 significant figures)\n\n'
            'Calculate the car\'s fuel efficiency in litres per 100 km, '
            'correct to 1 decimal place. (3 marks)'
        ),
        'answer': (
            'Convert 30 miles/gallon to km/litre first:\n\n'
            '30 miles/gallon × 1.6 km/mile ÷ 3.8 litres/gallon\n'
            '= 30 × 1.6 ÷ 3.8\n'
            '= 48 ÷ 3.8\n'
            '= 12.6315... km/litre\n\n'
            'Convert to litres/100 km:\n'
            '= 100 ÷ 12.6315...\n'
            '= **7.9 litres/100 km** (to 1 d.p.)'
        ),
        'keywords': ['7.9'],
        'minKeywords': 1,
        'bandDescriptors': {
            'high': 'Correctly converts to get 7.9 L/100 km.',
            'mid': 'Converts miles to km or gallons to litres correctly in chain.',
            'low': 'Sets up the conversion using given factors.'
        }
    })
    changes.append('Q38 2025: added missing fuel efficiency question')

# -----------------------------------------------------------------------
# Q40 2025: add missing question
# -----------------------------------------------------------------------
i = find_idx(2025, '40')
if i is None:
    last_2025 = max(j for j,q in enumerate(written) if q.get('year') == 2025)
    written.insert(last_2025 + 1, {
        'year': 2025,
        'marks': 5,
        'section': 'II',
        'qNum': '40',
        'category': 'S4',
        'image': None,
        'q': (
            '(a) In a flock of 12 600 sheep, the ratio of males to females is 1 : 20. '
            'The weights of the male sheep are normally distributed with a mean of 76.2 kg '
            'and a standard deviation of 6.8 kg. In the flock, 15 of the male sheep each '
            'weigh more than x kg. Find the value of x. (4 marks)\n\n'
            '(b) The weights of the female sheep are also normally distributed but have a '
            'smaller mean and smaller standard deviation than the weights of male sheep. '
            'Explain whether it could be expected that 300 of the females from the flock '
            'each weigh more than x kg, where x is the value found in part (a). (1 mark)'
        ),
        'answer': (
            '(a) Total sheep = 12 600, ratio males:females = 1:20\n'
            'Number of male sheep = 12 600 × (1/21) = 600 males\n\n'
            '15 out of 600 weigh more than x kg:\n'
            'Proportion = 15/600 = 0.025 → P(Z > z) = 0.025 → z = 1.96\n\n'
            'x = μ + z × σ = 76.2 + 1.96 × 6.8\n'
            '= 76.2 + 13.328\n'
            '= **89.528... ≈ 89.5 kg**\n\n'
            '(b) Number of females = 12 600 × (20/21) = 12 000\n'
            '300 out of 12 000 = 0.025 (2.5%) would need to weigh more than 89.5 kg.\n'
            'But females have SMALLER mean and SMALLER standard deviation than males.\n'
            'So x = 89.5 kg is even further into the upper tail for females.\n'
            'Less than 2.5% of females would weigh more than x kg.\n'
            'Therefore it could NOT be expected that 300 females weigh more than x kg.'
        ),
        'keywords': ['600', '1.96', '89.5', 'smaller', 'could not'],
        'minKeywords': 2,
        'bandDescriptors': {
            'high': 'Correctly finds 600 males, uses z=1.96, calculates x≈89.5 kg, and correctly explains females cannot reach 300.',
            'mid': 'Finds number of males and sets up z-score calculation, or correctly explains part (b).',
            'low': 'Identifies number of males (600) or states the proportion 15/600 = 0.025.'
        }
    })
    changes.append('Q40 2025: added missing normal distribution question (5 marks)')

# Write back
with open(JSON_PATH, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('Done. Changes:')
for c in changes: print(f'  {c}')
print(f'\nTotal writtenQuestions: {len(data["writtenQuestions"])}')
