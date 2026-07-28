// One-off script: appends the F4 Investments & Loans studyNotes topic to
// subjects/mathematics-standard-2.json (second Maths Study Mode topic,
// after F1 Money Matters). Purely additive — appends to the existing
// studyNotes array, does not touch mcQuestions/tips/writtenQuestions.
// Run once: node scripts/archive/add_maths_f4_study_notes.cjs
const fs = require('fs');
const path = require('path');

const filePath = path.join(__dirname, '..', '..', 'subjects', 'mathematics-standard-2.json');
const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));

if (!Array.isArray(data.studyNotes)) {
  console.log('studyNotes array missing — expected F1 to already exist. Aborting.');
  process.exit(1);
}
if (data.studyNotes.some(t => t.id === 'f4-investments-loans')) {
  console.log('f4-investments-loans already exists — aborting to avoid duplicate.');
  process.exit(1);
}

const f4 = {
  id: 'f4-investments-loans',
  icon: '📈',
  title: 'F4 — Investments & Loans',
  accentColor: '#C17D3C',
  blocks: [
    {
      type: 'noteGrid',
      boxes: [
        {
          heading: 'Compound interest — future value',
          html: '<ul>\n<li><b><em>A</em> = <em>P</em>(1 + <em>r</em>/<em>n</em>)<sup>nt</sup></b> — <em>P</em> = principal, <em>r</em> = annual rate as a decimal, <em>n</em> = number of times compounded per year, <em>t</em> = time in years</li>\n<li>Unlike simple interest, each period\'s interest is calculated on the <b>current balance</b> (principal + interest already earned), not just the original principal</li>\n<li>Match the rate and the number of periods carefully — e.g. \"8% p.a. compounded quarterly for 6 years\" means <em>r</em> = 0.08, <em>n</em> = 4, <em>t</em> = 6, so <em>nt</em> = 24 periods</li>\n</ul>'
        },
        {
          heading: 'Finding the present value',
          html: '<ul>\n<li><b><em>PV</em> = <em>FV</em> ÷ (1 + <em>r</em>/<em>n</em>)<sup>nt</sup></b> — rearranges the future value formula to answer "how much do I need to invest now?"</li>\n<li>Use this whenever a question gives you a <b>target future amount</b> and asks for the starting investment, rather than the other way around</li>\n<li>The rate, compounding frequency and time work exactly the same way as in the future value formula — only the unknown moves</li>\n</ul>'
        }
      ]
    },
    {
      type: 'noteGrid',
      boxes: [
        {
          heading: 'Shares & dividends',
          html: '<ul>\n<li><b>Dividend yield</b> = (annual dividend per share ÷ share price) × 100% — lets you compare returns between shares of very different prices</li>\n<li>A higher dividend yield means a better return <b>relative to what was paid</b> for the share, even if the dollar dividend or share price alone looks smaller</li>\n<li>Profit/loss on buying and selling shares still follows F1\'s rule: (selling price − buying price) × number of shares − brokerage fees</li>\n</ul>'
        },
        {
          heading: 'Appreciation (growth in value)',
          html: '<ul>\n<li>Some assets (antiques, some property, some collectables) <b>gain</b> value over time instead of depreciating</li>\n<li>Uses the same compound-growth shape as interest: <b>Value after <em>t</em> years = <em>V</em>₀(1 + <em>r</em>)ᵗ</b></li>\n<li>The only difference from compound interest is what\'s growing — dollars in an account vs. the value of an item — the maths is identical</li>\n</ul>'
        }
      ]
    },
    {
      type: 'table',
      caption: 'Compound interest formula — what each symbol means',
      headers: ['Symbol', 'Meaning', 'Example'],
      rows: [
        [ { label: 'Symbol', html: '<em>P</em>' }, { label: 'Meaning', html: 'Principal — the initial amount' }, { label: 'Example', html: '$5000 invested' } ],
        [ { label: 'Symbol', html: '<em>r</em>' }, { label: 'Meaning', html: 'Annual interest rate, as a decimal' }, { label: 'Example', html: '6% p.a. → 0.06' } ],
        [ { label: 'Symbol', html: '<em>n</em>' }, { label: 'Meaning', html: 'Number of times compounded per year' }, { label: 'Example', html: 'Monthly → 12, quarterly → 4, half-yearly → 2' } ],
        [ { label: 'Symbol', html: '<em>t</em>' }, { label: 'Meaning', html: 'Time, in years' }, { label: 'Example', html: '3 years' } ]
      ]
    },
    {
      type: 'noteGrid',
      boxes: [
        {
          heading: 'Declining-balance depreciation',
          html: '<ul>\n<li>Same formula as F1\'s declining-balance method — <b><em>S</em> = <em>V</em>₀(1 − <em>r</em>)ⁿ</b> — but F4 questions often give the rate <b>per half-year or per quarter</b> rather than per year</li>\n<li>Match <em>n</em> to whatever period the rate is given in — "8% per half-year for 5 years" means <em>r</em> = 0.08 and <em>n</em> = 10 (not 5)</li>\n</ul>'
        },
        {
          heading: 'Reducing-balance loans',
          html: '<ul>\n<li>Each repayment is split between <b>interest</b> (charged on the amount currently owed) and paying down the <b>principal</b></li>\n<li>Interest is largest early in the loan, when the balance owing is still close to the original amount — so early repayments reduce the principal only a little</li>\n<li>As the balance falls, less of each fixed repayment is needed for interest, so more goes toward the principal — the loan pays down faster later on</li>\n</ul>'
        }
      ]
    },
    {
      type: 'noteGrid',
      boxes: [
        {
          heading: 'Credit cards',
          html: '<ul>\n<li>Interest usually compounds <b>daily</b> on the amount owing</li>\n<li>Many cards offer an <b>interest-free period</b> (e.g. 45 days) — pay the full balance within it and no interest is charged at all</li>\n<li>If any amount is still owing after the interest-free period, interest starts accruing on the outstanding balance from that point (or from the purchase date, depending on the card\'s terms) until it\'s repaid</li>\n</ul>'
        },
        {
          heading: 'Comparing investment options',
          html: '<ul>\n<li>When a question offers two different schemes (e.g. a lump sum vs. regular deposits, or different compounding frequencies), <b>calculate the future value of each separately</b> using its own method/formula</li>\n<li>Never assume the higher quoted rate or the more frequent compounding automatically wins — compare the actual calculated totals</li>\n</ul>'
        }
      ]
    },
    {
      type: 'examTip',
      label: 'Matching variables to the question',
      html: '<p>Before substituting into any formula on this page, write out what <em>P</em>, <em>r</em>, <em>n</em> and <em>t</em> actually are in the question. The most common error isn\'t the formula — it\'s using the wrong <em>n</em> (e.g. forgetting to convert an annual rate when compounding is quarterly) or mixing up which value is being asked for (future value vs. present value vs. the rate itself).</p>'
    },
    {
      type: 'linkIt',
      html: '<p>These formulas build directly on <b>F1 — Money Matters</b>: compound interest is the "reinvesting" version of F1\'s simple interest, and declining-balance depreciation here uses the exact same formula as F1, just often with a per-period (not per-year) rate.</p>'
    }
  ],
  revisionQuestions: [
    {
      q: 'Explain why compound interest results in a greater final amount than simple interest for the same principal, rate and time.',
      a: 'Simple interest earns the same dollar amount each year, calculated only on the original principal. Compound interest recalculates the interest each period on the current balance — principal plus all interest already earned — so the amount earning interest keeps growing. This compounding effect means compound interest overtakes simple interest for the same rate and time, and the gap grows the longer the investment runs.'
    },
    {
      q: 'Calculate the future value of $5000 invested at 6% p.a. compounded quarterly for 3 years.',
      a: '<em>A</em> = <em>P</em>(1 + <em>r</em>/<em>n</em>)<sup>nt</sup> = 5000(1 + 0.06/4)<sup>4×3</sup> = 5000(1.015)<sup>12</sup> ≈ <b>$5978.09</b>.'
    },
    {
      q: 'A painting bought for $8000 appreciates at 4% p.a. Find its value after 6 years.',
      a: 'Value = <em>V</em>₀(1 + <em>r</em>)ᵗ = 8000(1.04)⁶ ≈ <b>$10 122</b>.'
    },
    {
      q: 'Company A has a share price of $18.20 and pays a dividend of $1.10 per share. Company B has a share price of $6.40 and pays $0.52 per share. Determine which is the better investment based on dividend yield.',
      a: 'Dividend yield = (dividend ÷ share price) × 100%. Company A: (1.10 ÷ 18.20) × 100 ≈ 6.04%. Company B: (0.52 ÷ 6.40) × 100 = 8.125%. Company B has the higher dividend yield, so it gives a better return relative to its price — even though Company A\'s dividend and share price are both larger in dollar terms.'
    },
    {
      q: 'Explain why, in the early years of a reducing-balance loan, a large portion of each repayment goes toward interest rather than reducing the principal.',
      a: 'Interest each period is calculated on the current amount owing. Early in the loan the balance is still close to the original amount borrowed, so the interest charge is largest at that point — meaning most of each fixed repayment covers that interest, leaving only a small remainder to reduce the principal. As the balance falls over time, the interest portion shrinks and more of each repayment goes toward paying down the principal.'
    },
    {
      q: 'A credit card has a 45-day interest-free period and charges 15% p.a. compounded daily after that. Describe what determines whether interest is charged on a purchase.',
      a: 'If the cardholder pays the full balance within the 45-day interest-free period, no interest is charged on that purchase at all. If any amount remains unpaid once the period ends, interest begins compounding daily on the outstanding balance from that point until it is fully repaid.'
    }
  ]
};

data.studyNotes.push(f4);

fs.writeFileSync(filePath, JSON.stringify(data, null, 2) + '\n', 'utf8');
console.log('studyNotes appended: F4 — Investments & Loans, ' + f4.revisionQuestions.length + ' revision questions. Total topics now: ' + data.studyNotes.length);
