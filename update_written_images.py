"""
Update mathematics-standard-2.json:
1. Change 13 image paths from .jpg → .svg (for SVG-replaced diagrams)
2. Set image: null + embed table data for 5 table questions
"""
import sys, json, re
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

JSON_PATH = 'subjects/mathematics-standard-2.json'

with open(JSON_PATH, 'r', encoding='utf-8') as f:
    data = json.load(f)

written = data['writtenQuestions']

# Helper to find question by year+qNum
def find_q(year, qnum):
    for i, q in enumerate(written):
        if q.get('year') == year and str(q.get('qNum')) == str(qnum):
            return i, q
    raise ValueError(f'Not found: {year} Q{qnum}')

changes = []

# ---- SVG path changes ----
svg_changes = [
    (2022, '31'), (2022, '33'),
    (2023, '31'), (2023, '33'), (2023, '35'),
    (2024, '28'), (2024, '32'), (2024, '36'), (2024, '39'), (2024, '40'),
    (2025, '22'), (2025, '35'), (2025, '37'),
]
for year, qnum in svg_changes:
    idx, q = find_q(year, qnum)
    old_img = q.get('image', '')
    if not old_img or not old_img.endswith('.jpg'):
        print(f'SKIP {year} Q{qnum}: image={old_img!r}')
        continue
    new_img = old_img.replace('.jpg', '.svg')
    q['image'] = new_img
    changes.append(f'{year} Q{qnum}: {old_img} → {new_img}')

# ---- Table questions: image → null, embed table in q ----

# 2022 Q20: S/C/Y/B/M distances
idx, q = find_q(2022, '20')
q['image'] = None
q['q'] = (
    'The table shows the distances (in kilometres) between towns '
    'Snowtown (S), Clairville (C), Yuma (Y), Bosten (B), and Morrella (M):\n\n'
    '| | S | C | Y | B | M |\n'
    '|---|---|---|---|---|---|\n'
    '| S | – | – | 280 | 275 | – |\n'
    '| C | – | – | 60 | 150 | – |\n'
    '| Y | 280 | 60 | – | – | 530 |\n'
    '| B | 275 | 150 | – | – | 790 |\n'
    '| M | – | – | 530 | 790 | – |\n\n'
    '(a) Draw a weighted network diagram to represent the information shown in the table, '
    'using the five towns as vertices. (2 marks)\n\n'
    '(b) A tourist wishes to visit each town. '
    'Draw the minimum spanning tree which will allow for this AND determine its length. (3 marks)'
)
changes.append('2022 Q20: image → null, table embedded')

# 2023 Q17: flight distances matrix
idx, q = find_q(2023, '17')
q['image'] = None
q['q'] = (
    'The table shows some of the flight distances (rounded to the nearest 10 km) '
    'between various Australian cities: Adelaide (A), Brisbane (B), Darwin (D), '
    'Hobart (H), Perth (P), Sydney (S).\n\n'
    '| City | A | B | D | H | P | S |\n'
    '|---|---|---|---|---|---|---|\n'
    '| Adelaide (A) | – | – | 1170 | – | 2120 | – |\n'
    '| Brisbane (B) | – | – | 2850 | – | – | 750 |\n'
    '| Darwin (D) | 1170 | 2850 | – | – | 2650 | 3150 |\n'
    '| Hobart (H) | – | – | – | – | – | 1040 |\n'
    '| Perth (P) | 2120 | – | 2650 | – | – | 3270 |\n'
    '| Sydney (S) | – | 750 | 3150 | 1040 | 3270 | – |\n\n'
    '(a) Use the information in the table to complete the network diagram where the '
    'edges are labelled with distances. The network has nodes A, B, D, H, P, S with '
    'edge D–P = 2650 already shown. Add all remaining edges from the table. (2 marks)\n\n'
    '(b) Mahsa wants to travel from Hobart to Darwin. She wants to change planes only once. '
    'Using the network diagram, calculate how many kilometres she will travel by plane. (1 mark)'
)
changes.append('2023 Q17: image → null, flight distance table embedded')

# 2023 Q29: monthly repayment table
idx, q = find_q(2023, '29')
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
    '(a) A couple borrows $520 000 to buy a house at 8% per annum over 25 years. '
    'How much does the couple repay in total for this loan? (3 marks)\n\n'
    '(b) Chris borrows some money at 7% per annum. Chris will repay the loan over '
    '15 years, paying $3596 per month. How much money does Chris borrow? (1 mark)'
)
changes.append('2023 Q29: image → null, repayment table embedded')

# 2023 Q37: table data already in q text — just null the image
idx, q = find_q(2023, '37')
q['image'] = None
changes.append('2023 Q37: image → null (table data already in q text)')

# 2024 Q41: PV interest factors table
idx, q = find_q(2024, '41')
q['image'] = None
q['q'] = (
    'Twenty-five years ago, Phoenix deposited a single sum of money into a new bank account, '
    'earning 2.4% interest per annum compounding monthly.\n\n'
    'Present value interest factors for an annuity of $1 for various interest rates (r) '
    'and numbers of periods (n):\n\n'
    '| n \\ r | 0.001 | 0.002 | 0.003 | 0.004 |\n'
    '|---|---|---|---|---|\n'
    '| 60 | 58.207 | 56.487 | 54.835 | 53.249 |\n'
    '| 120 | 113.026 | 106.592 | 100.649 | 95.156 |\n'
    '| 180 | 164.655 | 151.036 | 138.927 | 128.137 |\n'
    '| 240 | 213.278 | 190.460 | 170.908 | 154.093 |\n'
    '| 300 | 259.071 | 225.430 | 197.627 | 174.521 |\n\n'
    'Phoenix made the following withdrawals:\n'
    '• $2000 at the end of each month for the first 15 years (starting end of month 1)\n'
    '• $1200 at the end of each month for the next 10 years (starting end of month 181)\n\n'
    'Calculate the minimum sum that Phoenix could have deposited in order to make these withdrawals. (4 marks)'
)
changes.append('2024 Q41: image → null, PV factors table embedded')

# Write back
with open(JSON_PATH, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('Done. Changes made:')
for c in changes:
    print(f'  {c}')
print(f'\nTotal: {len(changes)} changes')
