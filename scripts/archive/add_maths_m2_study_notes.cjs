// One-off script: appends the M2 Working with Time studyNotes topic to
// subjects/mathematics-standard-2.json (ninth Maths Study Mode topic).
// Purely additive — appends to the existing studyNotes array.
// Run once: node scripts/archive/add_maths_m2_study_notes.cjs
const fs = require('fs');
const path = require('path');

const filePath = path.join(__dirname, '..', '..', 'subjects', 'mathematics-standard-2.json');
const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));

if (!Array.isArray(data.studyNotes)) {
  console.log('studyNotes array missing — aborting.');
  process.exit(1);
}
if (data.studyNotes.some(t => t.id === 'm2-working-with-time')) {
  console.log('m2-working-with-time already exists — aborting to avoid duplicate.');
  process.exit(1);
}

const m2 = {
  id: 'm2-working-with-time',
  icon: '🌍',
  title: 'M2 — Working with Time',
  accentColor: '#C17D3C',
  blocks: [
    {
      type: 'noteGrid',
      boxes: [
        {
          heading: 'Longitude & time zones',
          html: '<ul>\n<li>Earth turns 360° in 24 hours, so <b>15° of longitude = 1 hour</b> of time difference</li>\n<li>Moving <b>east</b> makes the local time <b>later</b> (ahead); moving <b>west</b> makes it <b>earlier</b> (behind) — Earth rotates west to east, so eastern places reach each new hour first</li>\n<li><b>UTC</b> (Coordinated Universal Time) is the reference point — a city at UTC+10 is 10 hours ahead of UTC; a city at UTC−5 is 5 hours behind</li>\n</ul>'
        },
        {
          heading: 'Latitude & north/south position',
          html: '<ul>\n<li>Latitude measures position <b>north or south</b> of the equator (0°), up to 90° at each pole</li>\n<li>Moving "north" from a southern latitude reduces the °S value — moving far enough north can cross the equator into °N (e.g. 20°S + 55° north = 35°N)</li>\n<li>Latitude affects <b>position</b>, not time — a longitude question is what actually determines the time-zone calculation</li>\n</ul>'
        }
      ]
    },
    {
      type: 'noteGrid',
      boxes: [
        {
          heading: 'Calculating the time in another zone',
          html: '<ul>\n<li>Find the <b>difference in UTC offset</b> between the two zones (e.g. UTC+10 vs. UTC−5 → 15 hours apart)</li>\n<li><b>Add</b> that difference to move to a zone further east (ahead); <b>subtract</b> it to move to a zone further west (behind)</li>\n</ul>'
        },
        {
          heading: 'Handling the date',
          html: '<ul>\n<li>If adding or subtracting hours pushes the time past midnight in either direction, the <b>day changes too</b></li>\n<li>Track this carefully — crossing midnight forward means the next day; crossing it backward means the previous day</li>\n</ul>'
        }
      ]
    },
    {
      type: 'table',
      caption: 'Worked example — City A (UTC+10) is 8:00 pm Wed. What\'s the time in City B (UTC−5)?',
      headers: ['Step', 'What to do', 'Result'],
      rows: [
        [ { label: 'Step', html: '1' }, { label: 'What to do', html: 'Find the offset difference: 10 − (−5)' }, { label: 'Result', html: 'City A is 15 hours ahead of City B' } ],
        [ { label: 'Step', html: '2' }, { label: 'What to do', html: 'Subtract 15 hours from City A\'s time (moving to the zone behind)' }, { label: 'Result', html: '8:00 pm Wed − 15 h = <b>5:00 am Wed</b>' } ]
      ]
    },
    {
      type: 'noteGrid',
      boxes: [
        {
          heading: 'Flight duration across time zones',
          html: '<ul>\n<li>The safest method: <b>1)</b> convert the departure local time to UTC (remove the departure zone\'s offset), <b>2)</b> add the flight duration, <b>3)</b> convert that UTC time to the destination zone\'s local time (apply the destination\'s offset)</li>\n<li>Working through UTC avoids sign errors from jumping directly between two local times, especially when the zones have opposite-sign offsets</li>\n</ul>'
        },
        {
          heading: 'Reverse problems',
          html: '<ul>\n<li>If given the <b>arrival</b> time and flight duration, and asked for the departure time: convert arrival local time to UTC, <b>subtract</b> the flight duration, then convert that UTC time to the departure zone\'s local time</li>\n<li>Same method as forward problems, just run in reverse</li>\n</ul>'
        }
      ]
    },
    {
      type: 'examTip',
      label: 'Work through UTC, not zone-to-zone directly',
      html: '<p>Always convert to UTC first, do the arithmetic there, then convert to whichever zone the question asks for — rather than trying to jump directly from one local time to another. This is especially important when the two zones have opposite-sign offsets (one east of UTC, one west).</p>'
    },
    {
      type: 'linkIt',
      html: '<p>Flight-duration problems combine this topic\'s time-zone conversion with the elapsed-time reading covered in <b>M7 — Rates &amp; Ratios</b>\'s speed/distance/time work.</p>'
    }
  ],
  revisionQuestions: [
    {
      q: 'Explain why moving east across time zones makes the local time later, while moving west makes it earlier.',
      a: 'Earth rotates from west to east, so places further east reach sunrise — and each new hour — before places to the west. This means a location east of you is <b>ahead</b> in time (a later clock reading at the same instant), and a location west of you is <b>behind</b> (an earlier clock reading).'
    },
    {
      q: 'A meeting starts at 4:00 pm Tuesday in a city at UTC+8. Determine the time and day in a city at UTC−3 at that same instant.',
      a: 'Offset difference = 8 − (−3) = 11 hours; the UTC+8 city is 11 hours ahead. Subtract 11 hours from 4:00 pm Tuesday: 4:00 pm − 11 h = <b>5:00 am Tuesday</b>.'
    },
    {
      q: 'A flight departs Sydney (UTC+10) at 11:30 pm Monday and takes 14 hours 45 minutes to reach Los Angeles (UTC−8). Determine the arrival time and day in Los Angeles.',
      a: 'Convert departure to UTC: 11:30 pm Mon − 10 h = 1:30 pm Mon UTC. Add flight duration: 1:30 pm Mon + 14 h 45 min = 4:15 am Tue UTC. Convert to LA (UTC−8): 4:15 am Tue − 8 h = <b>8:15 pm Monday</b> in Los Angeles.'
    },
    {
      q: 'City P is at latitude 20°S. City Q is 55° north of City P. State the latitude of City Q.',
      a: 'Moving 55° north from 20°S crosses the equator: 55 − 20 = <b>35°N</b>.'
    },
    {
      q: 'Explain the general method for solving a time-zone problem that involves a long flight duration, to minimise the risk of errors.',
      a: 'Convert the departure local time into UTC by removing the departure city\'s offset. Add the flight\'s duration to that UTC time. Then convert the resulting UTC time into the destination city\'s local time by applying its offset. Working through UTC at every step avoids the confusion of jumping directly between two local times, especially when the offsets have different signs.'
    },
    {
      q: 'A game starts at 6:15 am Saturday in a city at UTC−4. Determine the time and day in a city at UTC+9 at that same instant.',
      a: 'Offset difference = 9 − (−4) = 13 hours ahead. Add 13 hours to 6:15 am Saturday: 6:15 am + 13 h = <b>7:15 pm Saturday</b>.'
    }
  ]
};

data.studyNotes.push(m2);

fs.writeFileSync(filePath, JSON.stringify(data, null, 2) + '\n', 'utf8');
console.log('studyNotes appended: M2 — Working with Time, ' + m2.revisionQuestions.length + ' revision questions. Total topics now: ' + data.studyNotes.length);
