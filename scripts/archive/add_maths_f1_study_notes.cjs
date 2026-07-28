// One-off script: adds the F1 Money Matters studyNotes pilot topic to
// subjects/mathematics-standard-2.json. Purely additive (new top-level
// "studyNotes" key) — does not touch mcQuestions/tips/writtenQuestions.
// Run once: node scripts/add_maths_f1_study_notes.cjs
const fs = require('fs');
const path = require('path');

const filePath = path.join(__dirname, '..', 'subjects', 'mathematics-standard-2.json');
const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));

if (data.studyNotes) {
  console.log('studyNotes already exists — aborting to avoid overwrite. Remove the key manually first if you want to re-run.');
  process.exit(1);
}

const f1 = {
  id: 'f1-money-matters',
  icon: '💰',
  title: 'F1 — Money Matters',
  accentColor: '#C17D3C',
  blocks: [
    {
      type: 'noteGrid',
      boxes: [
        {
          heading: 'Earning an income',
          html: '<ul>\n<li><b>Wage</b> — paid per hour worked; total pay varies week to week with hours (casual/part-time work)</li>\n<li><b>Salary</b> — a fixed annual amount, divided evenly across pay periods (e.g. fortnightly) regardless of the exact hours worked</li>\n<li><b>Piecework</b> — paid per item made or task completed, not per hour</li>\n<li><b>Commission</b> — a percentage of the value of sales made; can be <b>tiered</b> (a different rate applies above a threshold)</li>\n<li><b>Royalty</b> — a percentage of revenue paid to the creator of a work (book, song, patent) each time it is sold/used</li>\n<li><b>Allowance</b> — a flat extra payment for a specific condition (meal, travel, uniform) — added on top of wage, independent of hours worked</li>\n</ul>'
        },
        {
          heading: 'Overtime & leave loading',
          html: '<ul>\n<li><b>Overtime</b> — extra hours beyond a standard week (e.g. 38 hrs), usually paid at a higher rate: <b>time-and-a-half</b> = normal rate × 1.5, <b>double time</b> = normal rate × 2</li>\n<li>Overtime pay = normal hourly rate × multiplier × overtime hours</li>\n<li><b>Annual leave loading</b> — an extra 17.5% paid on top of normal pay while on annual leave (compensates for lost overtime/allowances)</li>\n<li>Leave loading pay = (weekly pay × weeks of leave) + 17.5% × (weekly pay × weeks of leave)</li>\n</ul>'
        }
      ]
    },
    {
      type: 'noteGrid',
      boxes: [
        {
          heading: 'Simple interest',
          html: '<ul>\n<li><b><em>I</em> = <em>P</em> × <em>r</em> × <em>t</em></b> — <em>P</em> = principal, <em>r</em> = annual rate as a <b>decimal</b>, <em>t</em> = time in years</li>\n<li>Interest earned/charged is the <b>same dollar amount every year</b> — no compounding</li>\n<li>Total repaid on a simple-interest loan = <em>P</em> + <em>I</em></li>\n<li>Always convert a percentage rate to a decimal before substituting (3% → 0.03)</li>\n</ul>'
        },
        {
          heading: 'GST & percentage discounts',
          html: '<ul>\n<li><b>GST</b> is 10% of the pre-GST price, so a GST-inclusive price = pre-GST price × 1.1</li>\n<li>To find the GST <b>already included</b> in a GST-inclusive price: GST = price ÷ 11 (since 10/110 = 1/11)</li>\n<li><b>Successive discounts don\'t add up directly</b> — apply each discount to the reduced price in turn, e.g. 30% then 20% off leaves 0.7 × 0.8 = 0.56 of the original, a total discount of <b>44%</b>, not 50%</li>\n</ul>'
        }
      ]
    },
    {
      type: 'table',
      caption: 'Depreciation — two methods compared',
      headers: ['Method', 'Formula', 'When it\'s used'],
      rows: [
        [
          { label: 'Method', html: '<b>Straight-line</b> (linear)' },
          { label: 'Formula', html: '<em>S</em> = <em>V</em>₀ − <em>D</em> × <em>n</em><br><span style="font-size:0.85em;color:var(--muted)"><em>D</em> = loss per period, <em>n</em> = number of periods</span>' },
          { label: 'When it\'s used', html: 'A fixed dollar amount is lost each period (or per km driven) — the same amount every time' }
        ],
        [
          { label: 'Method', html: '<b>Declining-balance</b> (reducing)' },
          { label: 'Formula', html: '<em>S</em> = <em>V</em>₀ × (1 − <em>r</em>)ⁿ<br><span style="font-size:0.85em;color:var(--muted)"><em>r</em> = rate per period as a decimal, <em>n</em> = number of periods</span>' },
          { label: 'When it\'s used', html: 'A fixed <b>percentage of the current value</b> is lost each period — the dollar loss shrinks over time since it\'s a % of a smaller base' }
        ]
      ]
    },
    {
      type: 'noteGrid',
      boxes: [
        {
          heading: 'Income tax & PAYG',
          html: '<ul>\n<li><b>Taxable income</b> = gross income − allowable deductions (e.g. work expenses, union fees)</li>\n<li>Tax payable is worked out from a <b>tax bracket table</b> given in the question — always in the form "base amount + <em>c</em>¢ for each $1 over a threshold"</li>\n<li><b>Medicare levy</b> — usually 2% of taxable income, added on top of income tax</li>\n<li><b>PAYG</b> (Pay As You Go) — tax withheld from each pay by the employer and sent to the ATO progressively through the year, as an estimate of what will be owed</li>\n<li><b>Refund vs. owing</b> — compare total PAYG withheld to actual tax payable: PAYG &gt; tax payable → refund; PAYG &lt; tax payable → the taxpayer owes the shortfall</li>\n</ul>'
        },
        {
          heading: 'Shares & investments',
          html: '<ul>\n<li>Profit/loss = (selling price − buying price) × number of shares − brokerage fees</li>\n<li><b>Brokerage</b> — a fee charged by the broker for handling the transaction, usually charged on both the buy and the sell — it reduces profit, don\'t forget to subtract it</li>\n<li>Shares can also be compared to fixed-rate investments using percentage return over time</li>\n</ul>'
        }
      ]
    },
    {
      type: 'examTip',
      label: 'Reading financial word problems',
      html: '<p>These questions pack a lot into one sentence — before calculating, underline: is the amount <b>weekly or annual</b>? Is a price <b>GST-inclusive or exclusive</b>? Is a rate <b>per annum or per period</b>? Getting one of these wrong flips the whole answer, even if your formula and arithmetic are correct.</p>'
    },
    {
      type: 'linkIt',
      html: '<p>Simple interest and straight-line depreciation are the "flat-rate" versions of ideas that reappear in <b>compound growth</b> — see <b>F4 — Investments &amp; Loans</b> for compound interest (<em>A</em> = <em>P</em>(1 + <em>r</em>/<em>n</em>)ⁿᵗ) and reducing-balance loans, which use the same declining-balance logic as this topic\'s depreciation.</p>'
    }
  ],
  revisionQuestions: [
    {
      q: 'Explain the difference between a wage and a salary.',
      a: 'A wage is paid per hour worked, so total pay can vary week to week depending on hours. A salary is a fixed annual amount, divided evenly into regular pay instalments (e.g. fortnightly) regardless of the exact hours worked in that period.'
    },
    {
      q: 'Calculate the simple interest earned on $4000 invested at 2.5% p.a. for 3 years.',
      a: '<em>I</em> = <em>Prt</em> = 4000 × 0.025 × 3 = $300.'
    },
    {
      q: 'A courier van worth $48 000 new depreciates at $0.18 per km driven, using the straight-line method. Find its value after it has travelled 90 000 km.',
      a: 'Depreciation = 0.18 × 90 000 = $16 200. Value = $48 000 − $16 200 = <b>$31 800</b>.'
    },
    {
      q: 'Describe what determines whether a taxpayer receives a refund or owes money at the end of the financial year.',
      a: 'Throughout the year the employer withholds PAYG tax as an estimate of what will be owed. At tax time, the taxpayer\'s actual tax payable — calculated from their annual taxable income using the tax bracket table — is compared to the total PAYG withheld. If PAYG paid is more than the tax payable, the difference is refunded; if it\'s less, the taxpayer must pay the shortfall.'
    },
    {
      q: 'An item is priced at $253, GST inclusive. Determine the amount of GST included in this price.',
      a: 'The GST-inclusive price is 11/10 of the pre-GST price, so the GST component is 1/11 of the total: GST = 253 ÷ 11 = <b>$23</b>.'
    },
    {
      q: 'A salesperson earns a base salary plus 2% commission on sales up to $500 000 and 3% on any amount above that. Explain how to calculate their total pay for sales of $650 000.',
      a: 'Commission = (2% × $500 000) + (3% × ($650 000 − $500 000)) = $10 000 + $4 500 = $14 500. This is added to the base salary for total pay — the higher 3% rate only applies to the portion of sales above the $500 000 threshold, not the whole sale amount.'
    }
  ]
};

data.studyNotes = [f1];

fs.writeFileSync(filePath, JSON.stringify(data, null, 2) + '\n', 'utf8');
console.log('studyNotes added: 1 topic (F1 — Money Matters), ' + f1.revisionQuestions.length + ' revision questions.');
