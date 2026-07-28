// One-off script: appends the F5 Annuities studyNotes topic to
// subjects/mathematics-standard-2.json (eighth Maths Study Mode topic).
// Purely additive — appends to the existing studyNotes array.
// Run once: node scripts/archive/add_maths_f5_study_notes.cjs
const fs = require('fs');
const path = require('path');

const filePath = path.join(__dirname, '..', '..', 'subjects', 'mathematics-standard-2.json');
const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));

if (!Array.isArray(data.studyNotes)) {
  console.log('studyNotes array missing — aborting.');
  process.exit(1);
}
if (data.studyNotes.some(t => t.id === 'f5-annuities')) {
  console.log('f5-annuities already exists — aborting to avoid duplicate.');
  process.exit(1);
}

const f5 = {
  id: 'f5-annuities',
  icon: '🏦',
  title: 'F5 — Annuities',
  accentColor: '#C17D3C',
  blocks: [
    {
      type: 'noteGrid',
      boxes: [
        {
          heading: 'What is an annuity?',
          html: '<ul>\n<li>A sequence of <b>equal, regular payments</b> into (or out of) an account that earns <b>compound interest</b> each period</li>\n<li>Payments are usually made at the <b>end</b> of each compounding period</li>\n<li>Can work either way: building up savings (regular deposits) or paying off a loan (regular repayments)</li>\n</ul>'
        },
        {
          heading: 'Recurrence relations for annuities',
          html: '<ul>\n<li><b><em>A</em>ₙ = <em>A</em>ₙ₋₁ × (1 + <em>r</em>) ± payment</b> — <em>r</em> is the interest rate per period, <em>A</em>₀ is the starting balance</li>\n<li><b>Add</b> the payment for an investment (regular deposits growing the balance)</li>\n<li><b>Subtract</b> the payment for a loan or a withdrawal (regular amounts drawn down)</li>\n<li>Work through one period at a time — there\'s no shortcut, just repeat the same step</li>\n</ul>'
        }
      ]
    },
    {
      type: 'noteGrid',
      boxes: [
        {
          heading: 'Future value of an annuity (using tables)',
          html: '<ul>\n<li>Exams provide a <b>"future value of an annuity of $1" table</b> — look up the factor for the given rate and number of periods</li>\n<li><b><em>FV</em> = payment × (FV interest factor)</b> — multiply the table value by the actual payment amount</li>\n</ul>'
        },
        {
          heading: 'Present value of an annuity (using tables)',
          html: '<ul>\n<li>Same idea with a <b>"present value of an annuity of $1" table</b></li>\n<li><b><em>PV</em> = payment × (PV interest factor)</b> — used to value a future stream of payments in today\'s dollars, or to connect a loan amount to its repayments</li>\n</ul>'
        }
      ]
    },
    {
      type: 'table',
      caption: 'Reading annuity interest-factor tables',
      headers: ['Situation', 'Formula', 'What the table gives you'],
      rows: [
        [ { label: 'Situation', html: 'Future value of an investment' }, { label: 'Formula', html: '<em>FV</em> = payment × FV factor' }, { label: 'What the table gives you', html: 'The value $1 invested each period grows to by the end' } ],
        [ { label: 'Situation', html: 'Present value of a loan' }, { label: 'Formula', html: 'Loan amount = repayment × PV factor' }, { label: 'What the table gives you', html: 'Today\'s value of $1 to be paid each period' } ],
        [ { label: 'Situation', html: 'Finding the repayment' }, { label: 'Formula', html: 'Repayment = loan amount ÷ PV factor' }, { label: 'What the table gives you', html: 'Same PV factor, rearranged to solve for the unknown repayment' } ]
      ]
    },
    {
      type: 'noteGrid',
      boxes: [
        {
          heading: 'Loans repaid via annuity tables',
          html: '<ul>\n<li>A reducing-balance loan repaid in equal instalments is mathematically an annuity <b>in reverse</b> — the loan amount is the present value of all the future repayments</li>\n<li><b>Repayment = loan amount ÷ PV interest factor</b> — using the factor for the loan\'s rate per period and total number of repayments</li>\n</ul>'
        },
        {
          heading: 'PV vs. FV — which is bigger',
          html: '<ul>\n<li>For any annuity: <b>PV &lt; total of the nominal (face-value) payments &lt; FV</b></li>\n<li>Discounting brings future payments back to a <b>smaller</b> value today (PV); compounding grows the account to <b>more</b> than the sum of the plain contributions (FV)</li>\n</ul>'
        }
      ]
    },
    {
      type: 'examTip',
      label: 'Matching the table to the question',
      html: '<p>Always match the interest factor table\'s rate-per-period and number-of-periods to the question\'s actual compounding frequency — e.g. monthly repayments need the <b>monthly</b> rate and the <b>total number of months</b>, not the annual figures. Reading the wrong row/column of the table is the single most common error in this topic.</p>'
    },
    {
      type: 'linkIt',
      html: '<p>Annuities extend <b>F4 — Investments &amp; Loans</b>\'s single-lump-sum compound interest to a whole <b>series</b> of regular payments — the underlying compounding is identical, just applied repeatedly.</p>'
    }
  ],
  revisionQuestions: [
    {
      q: 'Explain the difference between the future value and the present value of an annuity.',
      a: 'The future value (FV) is the total amount accumulated at the end of the annuity\'s term — every payment plus all the compound interest earned. The present value (PV) is the equivalent single lump sum, invested today, that would grow into (or is needed to fund) that same stream of payments. PV is always smaller than FV, since it hasn\'t yet had the chance to earn interest.'
    },
    {
      q: 'A savings recurrence relation is Aₙ = Aₙ₋₁ × 1.004 − 250, with A₀ = $10 000. Find the balance after the second withdrawal (A₂).',
      a: '<em>A</em>₁ = 10 000 × 1.004 − 250 = 10 040 − 250 = 9790. <em>A</em>₂ = 9790 × 1.004 − 250 = 9829.16 − 250 = <b>$9579.16</b>.'
    },
    {
      q: 'An annuity has a future value interest factor of 12.0061 for 10 yearly payments at a given rate. If each payment is $2000, calculate the future value of the annuity.',
      a: '<em>FV</em> = payment × factor = 2000 × 12.0061 = <b>$24 012.20</b>.'
    },
    {
      q: 'A loan of $180 000 is to be repaid in equal monthly instalments. The present value interest factor for the loan\'s rate and term is 150.30. Calculate the monthly repayment.',
      a: 'Repayment = loan amount ÷ PV factor = 180 000 ÷ 150.30 ≈ <b>$1197.61</b>.'
    },
    {
      q: 'Explain why, for the same regular payment amount, the present value of an annuity is always less than the total of all the nominal (undiscounted) payments.',
      a: 'The present value discounts every future payment back to today\'s value using the interest rate — money received in the future is worth less today, since it hasn\'t yet had the chance to earn interest. So even though the actual dollar payments add up to a certain total, their combined value today (PV) is always less than that simple total.'
    },
    {
      q: 'Describe, in general terms, how a recurrence relation for an annuity differs between an investment (building up savings) and a loan (paying down debt).',
      a: 'In both cases the balance is multiplied by (1 + r) each period to add interest. For an investment, the regular contribution is <b>added</b> each period, so the balance grows from both interest and new deposits. For a loan, the regular repayment is <b>subtracted</b> each period — interest still accrues on the balance (working against the borrower), but the repayment reduces it, so the balance shrinks over time as long as repayments exceed the interest charged.'
    }
  ]
};

data.studyNotes.push(f5);

fs.writeFileSync(filePath, JSON.stringify(data, null, 2) + '\n', 'utf8');
console.log('studyNotes appended: F5 — Annuities, ' + f5.revisionQuestions.length + ' revision questions. Total topics now: ' + data.studyNotes.length);
