// One-off script: appends the N3 Critical Path Analysis studyNotes
// topic to subjects/mathematics-standard-2.json (twelfth Maths Study
// Mode topic). Purely additive — appends to the existing studyNotes
// array. Note: N3's MC bank is thin (2 questions) but the written bank
// is substantial (7 questions) and was used to ground this content.
// Run once: node scripts/archive/add_maths_n3_study_notes.cjs
const fs = require('fs');
const path = require('path');

const filePath = path.join(__dirname, '..', '..', 'subjects', 'mathematics-standard-2.json');
const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));

if (!Array.isArray(data.studyNotes)) {
  console.log('studyNotes array missing — aborting.');
  process.exit(1);
}
if (data.studyNotes.some(t => t.id === 'n3-critical-path-analysis')) {
  console.log('n3-critical-path-analysis already exists — aborting to avoid duplicate.');
  process.exit(1);
}

const n3 = {
  id: 'n3-critical-path-analysis',
  icon: '🗓️',
  title: 'N3 — Critical Path Analysis',
  accentColor: '#C17D3C',
  blocks: [
    {
      type: 'noteGrid',
      boxes: [
        {
          heading: 'Activity networks & the critical path',
          html: '<ul>\n<li>Nodes represent milestones; <b>directed edges (arrows)</b> represent activities/tasks, each with a duration</li>\n<li>The project\'s <b>minimum completion time</b> is the length of its <b>longest</b> path from start to finish — this is the <b>critical path</b></li>\n<li>To find it: list every path from start to finish, add up each path\'s durations, and take the longest total</li>\n</ul>'
        },
        {
          heading: 'Float (slack) time',
          html: '<ul>\n<li>An activity <b>not</b> on the critical path has <b>float</b> — spare time it can be delayed without pushing back the whole project</li>\n<li>Every activity <b>on</b> the critical path has <b>zero float</b> — any delay there delays the entire project</li>\n</ul>'
        }
      ]
    },
    {
      type: 'noteGrid',
      boxes: [
        {
          heading: 'EST — earliest start time',
          html: '<ul>\n<li>The <b>earliest</b> an activity/node can start, based on the <b>longest</b> path of activities that must finish before it</li>\n<li>Worked <b>forward</b> from the start of the project</li>\n</ul>'
        },
        {
          heading: 'LST — latest start time',
          html: '<ul>\n<li>The <b>latest</b> an activity/node can start <b>without delaying</b> the whole project\'s finish</li>\n<li>Worked <b>backward</b> from the required project finish time</li>\n<li>A node where <b>EST = LST</b> lies on the critical path — there\'s no room to delay it</li>\n</ul>'
        }
      ]
    },
    {
      type: 'table',
      caption: 'Critical path analysis at a glance',
      headers: ['Concept', 'What it means'],
      rows: [
        [ { label: 'Concept', html: '<b>Critical path</b>' }, { label: 'What it means', html: 'Longest path from start to finish; sets the minimum project duration' } ],
        [ { label: 'Concept', html: '<b>Float</b>' }, { label: 'What it means', html: 'Spare time an activity can be delayed without affecting the finish — zero on the critical path' } ],
        [ { label: 'Concept', html: '<b>EST</b>' }, { label: 'What it means', html: 'Earliest an activity/node can start, given everything before it' } ],
        [ { label: 'Concept', html: '<b>LST</b>' }, { label: 'What it means', html: 'Latest an activity/node can start without delaying the whole project' } ]
      ]
    },
    {
      type: 'noteGrid',
      boxes: [
        {
          heading: 'Maximum flow & minimum cut',
          html: '<ul>\n<li>The <b>maximum flow</b> is the greatest amount that can travel from a source to a sink, limited by the capacities of the edges (pipes/paths) along each route</li>\n<li>A <b>cut</b> is a set of edges that, if removed, completely separates the source from the sink — its capacity is the sum of the capacities of the edges it contains</li>\n</ul>'
        },
        {
          heading: 'The max-flow-min-cut theorem',
          html: '<ul>\n<li>The maximum possible flow can <b>never exceed</b> the capacity of <b>any</b> cut — so a cut of capacity 30 means the maximum flow is <b>at most 30</b> ("30 or less")</li>\n<li>The <b>true</b> maximum flow equals the <b>smallest (minimum)</b> cut capacity found anywhere in the network</li>\n</ul>'
        }
      ]
    },
    {
      type: 'examTip',
      label: 'Whole paths and upper bounds, not single numbers',
      html: '<p>For critical path questions, always total up the <b>whole path</b>, not just one activity\'s time — the critical path is about which route has the greatest total duration. For flow questions, remember a given cut only sets an <b>upper bound</b> on the max flow (max flow ≤ cut capacity) — never assume the cut shown is automatically the minimum one unless the question confirms it.</p>'
    },
    {
      type: 'linkIt',
      html: '<p>This topic builds directly on the vertex/edge language from <b>N2 — Network Concepts</b>, applied to directed, time-weighted (or capacity-weighted) networks.</p>'
    }
  ],
  revisionQuestions: [
    {
      q: 'A project has two possible paths from start to finish: Path 1 takes 5 + 8 + 3 = 16 days, Path 2 takes 6 + 4 + 9 = 19 days. Determine the minimum time to complete the project and identify the critical path.',
      a: 'The critical path is the longest path — Path 2, totalling <b>19 days</b>. The minimum time to complete the whole project is <b>19 days</b>.'
    },
    {
      q: 'An activity has an EST of 12 and an LST of 12. Explain what this tells you about that activity.',
      a: 'Since EST equals LST, the activity has zero float — it must start exactly on time or the whole project will be delayed. This means the activity lies on the critical path.'
    },
    {
      q: 'An activity is not on the critical path and has a float of 4 days. Explain what this means for scheduling that activity.',
      a: 'The activity can be delayed by up to 4 days (or take up to 4 days longer than planned) without affecting the overall project completion time, since it has 4 days of spare time before it would start delaying the critical path.'
    },
    {
      q: 'A cut in a flow network has a total capacity of 45. Explain what the max-flow-min-cut theorem tells you about the maximum possible flow through this network.',
      a: 'The theorem states the maximum flow can never exceed the capacity of any cut, so the maximum flow through this network is <b>at most 45</b>. The true maximum flow equals the smallest cut capacity found anywhere in the network — 45 is only the actual maximum if no smaller cut exists elsewhere.'
    },
    {
      q: 'Explain the difference between EST and LST for an activity in a project network.',
      a: 'EST (earliest start time) is the earliest an activity can begin, based on the longest path of activities that must be completed before it. LST (latest start time) is the latest an activity can begin without delaying the whole project\'s completion, worked backward from the required finish time.'
    },
    {
      q: 'A project network has four possible start-to-finish paths, of total length 14, 17, 21 and 19 days. State the minimum project completion time and explain your reasoning.',
      a: 'The minimum completion time is <b>21 days</b>, since the project cannot finish until every activity — including those on the longest path — is complete. The longest path (21 days) is the critical path and determines the overall minimum duration.'
    }
  ]
};

data.studyNotes.push(n3);

fs.writeFileSync(filePath, JSON.stringify(data, null, 2) + '\n', 'utf8');
console.log('studyNotes appended: N3 — Critical Path Analysis, ' + n3.revisionQuestions.length + ' revision questions. Total topics now: ' + data.studyNotes.length);
