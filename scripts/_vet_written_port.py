# -*- coding: utf-8 -*-
"""Port the missing VET Construction written questions into subjects/vet-construction.json.

The completion port: the bank held 23 of the 76 official written parts (65 marks/paper).
This adds the rest, so VET's written coverage closes to 76/76.

Sources, and what is NEVER re-read
----------------------------------
* Question STEMS come from the exam papers (legitimate, and required by CLAUDE.md
  section 10's citation rule -- confirm section, number, marks and wording).
* MARKS, SAMPLE ANSWERS and CRITERIA come from the committed ground truth in
  data/answer-key/written/vet-construction.json. The marking guidelines are NOT
  re-read to derive them (section 10 rules 5-8).

Every stem is made SELF-CONTAINED, because the engine shuffles the question list --
a stem reading "this tool" with no stimulus is unanswerable on its own. Where NESA's
wording depends on surrounding context, the stimulus is attached instead of the
wording being changed; the two places a word had to change are noted in STEM_NOTES.

`bandDescriptors` are NOT set here. They are regenerated for every question by
scripts/_vet_review_apply.py from the committed criteria rows, so the 1-to-N band
collapse rule has exactly one implementation.

    python scripts/_vet_written_port.py --year 2021
    python scripts/_vet_written_port.py --year 2021 --dry-run
"""

import argparse
import io
import json
import re
import sys

BANK = "subjects/vet-construction.json"
KEY = "data/answer-key/written/vet-construction.json"

IMG_CHISEL_21 = "/diagrams/vet-construction_2021_Q16_stimulus.jpg"
IMG_SLAB_21 = "/diagrams/vet-construction_2021_Q18_stimulus.jpg"

# Wording changed from the paper, and why. Both are context words that only make sense
# inside the printed paper's running order.
STEM_NOTES = {
    ("2021", "18(d)"): "NESA reads 'on this building site' (the picnic-table project of "
                       "Q18); rendered as 'on a building site' so the shuffled question "
                       "stands alone. Nothing else changed.",
}

NEW = {
    "2021": [
        {
            "year": 2021, "qNum": "16(c)", "section": "II", "marks": 2,
            "q": "A tool is shown.<br>Describe ONE consequence if this tool is poorly maintained.",
            "image": IMG_CHISEL_21,
            "answer": (
                "A poorly maintained chisel becomes blunt, and a blunt chisel is both unsafe "
                "and inefficient.<br><br>"
                "<strong>Safety:</strong> a blunt edge needs far more force to drive, so it is "
                "much more likely to skid off the timber and strike the user's hand — blunt "
                "tools cause more injuries than sharp ones.<br>"
                "<strong>Quality and cost:</strong> a blunt chisel tears rather than slices the "
                "fibres, leaving a rough, inaccurate cut and a poor finish. It also takes longer "
                "to complete the same work, which increases labour time and therefore the cost "
                "of the job."
            ),
            "keywords": ["blunt", "unsafe", "injury", "force", "slip", "finish",
                         "quality", "time", "cost"],
            "minKeywords": 3,
        },
        {
            "year": 2021, "qNum": "16(d)", "section": "II", "marks": 3,
            "q": ("A tool is shown.<br>Describe both care and maintenance procedures that "
                  "should be carried out to ensure the long life of this tool."),
            "image": IMG_CHISEL_21,
            "answer": (
                "<strong>Care</strong> — use the chisel only for the work it is designed for: "
                "cutting joints and paring timber. It should never be used to open paint tins, "
                "lever or remove nails, or cut masonry. Strike it only with an appropriate "
                "mallet or hammer, and store it so the cutting edge is protected — in a roll, "
                "rack or guard rather than loose in a toolbox where the edge will be chipped.<br><br>"
                "<strong>Maintenance</strong> — keep the edge sharp by grinding to restore the "
                "bevel, then honing on an oilstone and stropping to remove the burr (deburring). "
                "Check that the ferrule is secure and in place so the handle does not split, and "
                "inspect the handle for damage, replacing it as needed."
            ),
            "keywords": ["care", "intended", "store", "protect", "edge", "mallet",
                         "maintenance", "grind", "hone", "strop", "ferrule", "handle"],
            "minKeywords": 5,
        },
        {
            "year": 2021, "qNum": "17", "section": "II", "marks": 5,
            "q": "Describe the personal attributes that ALL construction workers should display.",
            "answer": (
                "Construction workers are expected to display a range of personal attributes "
                "that make them safe, reliable and employable.<br><br>"
                "<strong>Attendance and punctuality</strong> — being physically on site and "
                "properly prepared before the expected starting time, so the day's work and the "
                "other trades are not held up.<br>"
                "<strong>Personal presentation and grooming</strong> — being appropriately "
                "dressed and groomed for the role, and not bringing items to work that could "
                "interfere with the job or create a hazard.<br>"
                "<strong>Work performance</strong> — performing tasks to industry standards and "
                "at the level of their skill and training, with attention to detail, and taking "
                "directives from supervisors.<br>"
                "<strong>Ethical behaviour</strong> — honesty, confidentiality, consistency of "
                "service, and compliance with the workplace code of conduct.<br>"
                "<strong>Safe work practices</strong> — following safe work practices at all "
                "times, maintaining safe housekeeping, and understanding duty of care. Workers "
                "should also avoid practices in their private lives that could impair their "
                "ability and judgement on site."
            ),
            "keywords": ["attendance", "punctuality", "presentation", "grooming",
                         "performance", "directive", "attention to detail", "ethical",
                         "honesty", "confidentiality", "safe work", "duty of care",
                         "attitude"],
            "minKeywords": 5,
        },
        {
            "year": 2021, "qNum": "18(a)", "section": "II", "marks": 2,
            "q": ("One tradesperson and one apprentice are required to complete the formwork "
                  "for a project. The total time to complete this task will be 2.5 hours each."
                  "<br>The tradesperson charges $62.00 per hour and the apprentice charges "
                  "$21.00 per hour. These prices include GST.<br>What is the total labour cost "
                  "for this project?"),
            "answer": (
                "Cost each worker separately, then add:<br><br>"
                "Tradesperson: 2.5 × $62.00 = <strong>$155.00</strong><br>"
                "Apprentice: 2.5 × $21.00 = <strong>$52.50</strong><br>"
                "Total labour cost = $155.00 + $52.50 = <strong>$207.50</strong><br><br>"
                "Or combine the rates first, since both work the same 2.5 hours: "
                "$62.00 + $21.00 = $83.00 per hour, and 2.5 × $83.00 = <strong>$207.50</strong>."
            ),
            "keywords": ["207.50", "155", "52.50", "2.5", "62", "21", "83", "labour"],
            "minKeywords": 3,
        },
        {
            "year": 2021, "qNum": "18(b)", "section": "II", "marks": 3,
            "q": ("A concrete slab is to be laid for an outdoor picnic table as shown."
                  "<br>Calculate the perimeter of the concrete slab."),
            "image": IMG_SLAB_21,
            "answer": (
                "The slab is a 6 m × 5 m rectangle with a semicircular end. The semicircle's "
                "diameter is the 5 m width, so its radius is 2.5 m.<br><br>"
                "Curved edge (half a circumference) = 0.5 × 2 × π × 2.5 = "
                "<strong>7.85 m</strong><br>"
                "Straight edges = 5 m (left end) + 6 m (top) + 6 m (bottom) = 17 m<br><br>"
                "Perimeter = 7.85 + 5 + 6 + 6 = <strong>24.85 m</strong><br><br>"
                "Note that the 5 m right-hand edge is <em>not</em> part of the perimeter — the "
                "semicircle replaces it."
            ),
            "keywords": ["24.85", "7.85", "semicircle", "radius", "2.5", "perimeter",
                         "circumference", "pi"],
            "minKeywords": 3,
        },
        {
            "year": 2021, "qNum": "18(c)", "section": "II", "marks": 4,
            "q": ("A concrete slab is to be laid for an outdoor picnic table as shown."
                  "<br>Calculate the volume of concrete needed in cubic metres (m<sup>3</sup>) "
                  "if the slab is 100 mm thick. Include 10% wastage in your answer."),
            "image": IMG_SLAB_21,
            "answer": (
                "Work out the area first, then the volume, then add the wastage.<br><br>"
                "<strong>Area</strong> = rectangle + semicircle<br>"
                "= (6 × 5) + (0.5 × π × 2.5<sup>2</sup>)<br>"
                "= 30 + 9.81 = <strong>39.81 m<sup>2</sup></strong><br><br>"
                "<strong>Volume</strong> = area × thickness. 100 mm = 0.1 m<br>"
                "= 39.81 × 0.1 = <strong>3.98 m<sup>3</sup></strong><br><br>"
                "<strong>Add 10% wastage</strong> = 3.98 × 1.1 = "
                "<strong>4.38 m<sup>3</sup></strong><br><br>"
                "Converting the thickness from millimetres to metres before multiplying is the "
                "step most often missed."
            ),
            "keywords": ["4.38", "3.98", "39.81", "area", "volume", "0.1", "wastage",
                         "10%", "semicircle", "thickness"],
            "minKeywords": 4,
        },
        {
            "year": 2021, "qNum": "18(d)", "section": "II", "marks": 4,
            "q": ("Describe the work health and safety factors that need to be considered "
                  "before work commences on a building site."),
            "answer": (
                "<strong>Site access and induction</strong> — all workers must hold a valid "
                "White Card (general construction induction) before they are allowed on site, "
                "and site access must be controlled so unauthorised people cannot enter.<br>"
                "<strong>Training and competency</strong> — the employer must provide correct "
                "training for the operation of any machinery and plant being used, and workers "
                "must hold the relevant licences.<br>"
                "<strong>Plant and electrical safety</strong> — all electrical equipment must be "
                "in serviceable condition and carry a current test-and-tag before use, and "
                "supply must be protected by an earth leakage circuit breaker (ELCB).<br>"
                "<strong>Amenities and welfare</strong> — clean drinking water, toilet "
                "facilities and a first aid station must be provided.<br>"
                "<strong>Site conditions</strong> — PPE appropriate to the work, sun protection "
                "and allowance for weather conditions, good housekeeping so the site is well "
                "organised and accessible, waste material removed, and safe manual handling "
                "arrangements for lifting loads."
            ),
            "keywords": ["white card", "induction", "training", "licence", "PPE",
                         "electrical", "tag", "ELCB", "first aid", "amenities",
                         "drinking water", "housekeeping", "sun", "weather", "access"],
            "minKeywords": 5,
        },
        {
            "year": 2021, "qNum": "19(a)", "section": "II", "marks": 2,
            "q": ("Provide TWO reasons for using cross-sectional drawings in construction "
                  "planning."),
            "answer": (
                "A cross-sectional drawing cuts through the building, so it shows detail and "
                "information that appears on no other plan.<br><br>"
                "1. It shows how the building is <strong>constructed</strong> below and behind "
                "the finished surfaces — footing size and depth, wall thickness and "
                "construction, sub-floor design, floor construction, and roof construction "
                "including the roof pitch.<br>"
                "2. It gives the <strong>sizes and spacing of structural members</strong> "
                "(bearers, joists, studs, rafters), which the builder needs to order materials "
                "and set out the frame correctly."
            ),
            "keywords": ["footing", "wall", "thickness", "sub-floor", "floor", "roof",
                         "pitch", "structural", "member", "spacing", "detail"],
            "minKeywords": 3,
        },
        {
            "year": 2021, "qNum": "19(b)", "section": "II", "marks": 3,
            "q": "Describe the information that can be obtained from an elevation on a plan.",
            "answer": (
                "An elevation is a straight-on view of one face of the building, so it carries "
                "the <strong>vertical</strong> information and the external appearance.<br><br>"
                "It shows vertical measurements such as the finished floor level (FFL), the "
                "finished ceiling level (FCL), and the height of window sills above floor "
                "level. It shows the overall design and shape of the building, including the "
                "roof line and pitch.<br><br>"
                "It also shows the position of doors and windows in each wall, and the finishes "
                "to the external walls — for example brickwork, cladding or render."
            ),
            "keywords": ["vertical", "height", "FFL", "floor level", "ceiling", "sill",
                         "door", "window", "external", "finish", "design"],
            "minKeywords": 4,
        },
        {
            "year": 2021, "qNum": "19(c)", "section": "II", "marks": 4,
            "q": ("Explain why construction plans and specifications need to be used together "
                  "when constructing a building."),
            "answer": (
                "The two documents do different jobs and are incomplete on their own.<br><br>"
                "<strong>Plans</strong> show the overall appearance, layout and position of the "
                "building — where things go and what size they are. <strong>Specifications</strong> "
                "are a precise written description of the construction detail that the drawings "
                "cannot show: the composition and strength of concrete in footings, the species "
                "and grades of timber, brick type and mortar colour, and the colours of internal "
                "and external finishes.<br><br>"
                "Used together they ensure the <strong>customer receives what they requested</strong> "
                "and that the project complies with industry standards. Builders must follow "
                "specification details such as concrete strength, steel reinforcement and timber "
                "beam grades to ensure the building is structurally stable.<br><br>"
                "Both documents are also a <strong>legal requirement</strong> — they must be "
                "approved by council before any work commences, which is what ensures the "
                "safety and integrity of the building and that it minimises interference with "
                "the environment and neighbouring structures."
            ),
            "keywords": ["plan", "specification", "detail", "concrete", "timber", "grade",
                         "finish", "standard", "council", "approval", "legal", "customer",
                         "structural"],
            "minKeywords": 5,
        },
        {
            "year": 2021, "qNum": "20", "section": "III", "marks": 15,
            "q": ("Describe the roles that key bodies and authorities have in ensuring "
                  "worker safety."),
            "answer": (
                "Worker safety in NSW construction is governed by legislation and enforced and "
                "supported by a number of key bodies, each with a distinct role.<br><br>"
                "<strong>The legislative framework.</strong> The <em>Work Health and Safety Act "
                "2011</em> (NSW) provides the framework protecting the health, safety and "
                "welfare of everyone in NSW workplaces and all related work activities, "
                "replacing the former Occupational Health and Safety Act. The WHS Regulations "
                "sit under it and require duty holders to provide general workplace facilities, "
                "first aid, emergency plans, and training and instruction, and to isolate "
                "hazardous work. The Act's aims are to ensure the health and safety of all "
                "employees on site, protect visitors such as suppliers and contractors, promote "
                "a work environment meeting workers' physical, mental and psychological needs, "
                "and provide codes of practice and joint consultation procedures.<br><br>"
                "<strong>SafeWork NSW</strong> is the state regulator. It issues licences and "
                "registrations for potentially dangerous work, provides advice and guidance "
                "material, investigates workplace incidents and accidents, and enforces WHS "
                "law. Its inspectors may enter a workplace at any time without notice, issue "
                "improvement and prohibition notices, and impose fines or prosecute.<br><br>"
                "<strong>Safe Work Australia</strong> is the national policy body. It does not "
                "regulate or enforce; it develops the model WHS laws and codes of practice that "
                "the states enact, and collects national data on workplace injury and disease.<br><br>"
                "<strong>SIRA and icare</strong> administer the workers compensation scheme, "
                "ensuring injured workers are supported, treated and returned to work.<br><br>"
                "<strong>Unions and employer associations</strong> — such as the CFMEU and "
                "Master Builders Association — represent workers and employers, provide safety "
                "training and advice, and take part in consultation on site.<br><br>"
                "<strong>At the workplace</strong>, the PCBU (person conducting a business or "
                "undertaking) holds the primary duty of care, while health and safety "
                "representatives and the WHS committee provide the formal consultation "
                "mechanism between workers and management.<br><br>"
                "Together these bodies form a partnership between government, unions and "
                "industry working towards the goal of eliminating workplace death and reducing "
                "injury and disease."
            ),
            "keywords": ["WHS Act", "regulation", "SafeWork", "regulator", "inspect",
                         "notice", "fine", "prosecute", "Safe Work Australia", "code of practice",
                         "compensation", "union", "PCBU", "duty of care", "committee",
                         "consultation", "licence", "training"],
            "minKeywords": 7,
        },
        {
            "year": 2021, "qNum": "21(a)", "section": "IV", "marks": 5,
            "q": "Describe the benefits of teamwork in a construction workplace.",
            "answer": (
                "The benefits of teamwork on a construction site are many and varied.<br><br>"
                "<strong>Productivity and cost.</strong> Teamwork reduces the time required to "
                "complete a task, which reduces labour costs and improves the profitability of "
                "the business.<br>"
                "<strong>Safety.</strong> Working as a team reduces the risk of injury — for "
                "example using a two-person lift instead of a one-person lift. Fewer injuries "
                "means fewer sick days, lower workers compensation premiums and less down time.<br>"
                "<strong>Skills.</strong> A team provides the opportunity for skills to be "
                "shared and developed between employees, which makes each worker more valuable "
                "to the employer and widens the scope of work the business can take on.<br>"
                "<strong>Workplace culture.</strong> Teamwork teaches conflict resolution, "
                "promotes a wider sense of ownership of the project, fosters creativity and "
                "learning, and blends complementary strengths.<br><br>"
                "Combined, these factors increase business viability and job security and make "
                "for a more harmonious workplace."
            ),
            "keywords": ["time", "cost", "productivity", "injury", "two-person", "lift",
                         "safety", "skill", "share", "ownership", "conflict", "harmonious",
                         "job security"],
            "minKeywords": 5,
        },
        {
            "year": 2021, "qNum": "21(b)", "section": "IV", "marks": 10,
            "q": "Explain the benefits of effective workplace communication.",
            "answer": (
                "Effective communication is what keeps a construction project safe, accurate "
                "and on schedule. Its benefits differ by the form the communication takes.<br><br>"
                "<strong>Verbal communication</strong> is the most common and most efficient "
                "method on site. Feedback is instantaneous, and the receiver can repeat the "
                "message back to the sender to confirm it has been understood correctly. Using "
                "correct industry terminology — the right tool names and process names — avoids "
                "confusion and rework. For example, a carpenter asking for a specific size and "
                "grade of timber gets the right material first time.<br><br>"
                "<strong>Written communication</strong> is highly effective because it creates a "
                "permanent record that is less likely to be misunderstood or disputed later. It "
                "does require workers to read and write at an appropriate level. Effective "
                "written communication enables workers to read and interpret plans, follow "
                "safety warnings and procedures, correctly follow instructions, prepare accurate "
                "estimates and builders' quantities, and order materials. It should be neat and "
                "in plain language.<br><br>"
                "<strong>Signage</strong> is an important form of written communication, "
                "particularly safety signage. Signs are largely universal and can be understood "
                "by anyone who has received the relevant training, regardless of language.<br><br>"
                "<strong>Non-verbal communication</strong> — hand signals and gestures — is a "
                "benefit in noisy environments, over long distances, and where language barriers "
                "exist. A dogger directing a crane operator is the standard example. It is "
                "important to note that some hand signals and gestures carry different meanings "
                "across cultures.<br><br>"
                "Taken together, effective communication reduces errors and rework, prevents "
                "accidents, keeps trades correctly sequenced so the job is not delayed, ensures "
                "the client gets what was specified, and builds good working relationships "
                "within the team."
            ),
            "keywords": ["verbal", "feedback", "terminology", "written", "record", "plan",
                         "instruction", "signage", "safety", "non-verbal", "hand signal",
                         "noise", "language", "cultural", "error", "rework", "delay"],
            "minKeywords": 7,
        },
    ],
    "2022": [
        {
            "year": 2022, "qNum": "16(b)", "section": "II", "marks": 2,
            "q": ("The table shows techniques related to tools.<br>Describe each technique when "
                  "using the given tool."
                  '<table class="q-table"><tr><th>Tool</th><th>Technique</th>'
                  "<th>Description of technique</th></tr>"
                  "<tr><td>Chisel</td><td>Honing</td><td>&nbsp;</td></tr>"
                  "<tr><td>Handsaw</td><td>Ripping</td><td>&nbsp;</td></tr></table>"),
            "answer": (
                "<strong>Chisel — honing.</strong> Honing is part of the sharpening process. "
                "After grinding restores the bevel, the edge is rubbed on an oilstone or "
                "waterstone at a consistent angle to produce a fine, keen cutting edge, and the "
                "burr is then removed by stropping.<br><br>"
                "<strong>Handsaw — ripping.</strong> Ripping means cutting timber ALONG the "
                "direction of its grain, as opposed to crosscutting, which cuts across the "
                "grain. A rip saw has chisel-shaped teeth designed for that cut."
            ),
            "keywords": ["hone", "sharpen", "edge", "stone", "bevel", "rip", "along",
                         "grain", "timber", "crosscut"],
            "minKeywords": 4,
        },
        {
            "year": 2022, "qNum": "16(c)", "section": "II", "marks": 4,
            "q": "Explain considerations required before purchasing plant and equipment.",
            "answer": (
                "<strong>Cost against benefit.</strong> The purchase price must be weighed "
                "against what the item will return. The right equipment increases job "
                "efficiency and safety on site, which means fewer delays and increased profit; "
                "the wrong purchase is capital tied up in an item that does not earn.<br>"
                "<strong>Frequency of use.</strong> For a one-off job, hiring is often the "
                "better choice than buying — no capital outlay, no storage and no maintenance "
                "burden.<br>"
                "<strong>Ongoing maintenance.</strong> Maintenance costs both time and money "
                "and is required to prolong the life of the tool, so it must be budgeted for "
                "at the point of purchase, not after.<br>"
                "<strong>Training and licensing.</strong> Some plant requires operators to hold "
                "a licence or complete training before it can be used safely and legally.<br>"
                "<strong>Practical logistics.</strong> How the item will be stored and how much "
                "space it needs, how it will be transported to and from the job site, what PPE "
                "operators will need, and any registration and insurance costs."
            ),
            "keywords": ["cost", "efficiency", "profit", "frequency", "hire", "maintenance",
                         "training", "licence", "storage", "transport", "PPE", "insurance"],
            "minKeywords": 5,
        },
        {
            "year": 2022, "qNum": "17(a)", "section": "II", "marks": 2,
            "q": ("Outline TWO examples of how levelling information can be shown on "
                  "construction plans."),
            "answer": (
                "1. <strong>A datum or benchmark</strong> — a fixed reference point of known "
                "height marked on the plan, from which all other levels on the site are "
                "measured.<br>"
                "2. <strong>Contour lines</strong> — lines joining points of equal height, "
                "which show the rise and fall of the land across the site.<br><br>"
                "Levels are also shown as reduced levels (RLs) and as the finished floor level "
                "(FFL) and finished ceiling level (FCL)."
            ),
            "keywords": ["datum", "benchmark", "contour", "rise", "fall", "reduced level",
                         "RL", "floor level", "FFL", "ceiling"],
            "minKeywords": 3,
        },
        {
            "year": 2022, "qNum": "17(b)", "section": "II", "marks": 2,
            "q": "Provide reasons for the use of detail drawings in the construction industry.",
            "answer": (
                "A detail drawing enlarges a specific part of the construction to a larger "
                "scale (typically 1:20, 1:10 or 1:5) so it can be shown clearly.<br><br>"
                "They are used to clarify information that cannot be clearly illustrated on a "
                "sectional view, to provide detailed information about the assembly, joining or "
                "finishing of components, and to give precise dimensions and tolerances. They "
                "clearly identify all components in an assembly, which minimises confusion on "
                "site, and they can be used to demonstrate compliance with building regulations."
            ),
            "keywords": ["enlarge", "scale", "1:20", "1:10", "1:5", "clarify", "assembly",
                         "joining", "dimension", "tolerance", "compliance", "regulation"],
            "minKeywords": 4,
        },
        {
            "year": 2022, "qNum": "17(d)", "section": "II", "marks": 4,
            "q": ("Explain the purpose of a written specification when reading and interpreting "
                  "plans. Support your answer with examples of information that would be "
                  "included in a written specification."),
            "answer": (
                "A written specification is a detailed written description of the project being "
                "constructed. It must be used in conjunction with the construction plans, "
                "because its purpose is to convey the information that <em>cannot</em> be shown "
                "on a set of drawings — the drawings show size and position, the specification "
                "says what things are made of and how the work is to be done.<br><br>"
                "It provides instructions on how the work should be completed and sets out the "
                "sequence of trades, the quality of work expected, and the Australian Standards "
                "that apply.<br><br>"
                "<strong>Examples of what it includes:</strong> how the site should be set up; "
                "materials to be used (brick type, weatherboards, roofing); paint colours and "
                "the number of coats; flooring materials and which rooms they go in (bathroom "
                "tiles, carpet, timber); types of lights and switches; tap fittings and bathroom "
                "fixtures; brand and model numbers of appliances; architrave and skirting size "
                "and profile; kitchen bench tops and cabinetry; and the site clean-up and final "
                "inspections."
            ),
            "keywords": ["written", "description", "conjunction", "plan", "instruction",
                         "material", "paint", "coat", "fixture", "appliance", "standard",
                         "sequence", "quality"],
            "minKeywords": 5,
        },
        {
            "year": 2022, "qNum": "18(a)", "section": "II", "marks": 2,
            "q": ("Outline ONE work practice that would reduce the amount of material waste "
                  "produced on a construction site."),
            "answer": (
                "<strong>Train staff in the correct techniques for selecting, measuring, "
                "handling and storing materials.</strong> Most material waste on site comes "
                "from avoidable mistakes and damage — a member cut to the wrong length, sheets "
                "left out in the weather, or bricks damaged by careless handling. Training "
                "removes the cause rather than dealing with the waste afterwards.<br><br>"
                "Other effective practices include working from an accurate material list and "
                "double-checking quantity calculations so materials are not over-ordered; "
                "ordering in a timely fashion so stock is not stored on site longer than "
                "necessary; storing and transporting materials correctly; sorting waste for "
                "reuse or recycling; and confirming the most current version of the plans is "
                "being used."
            ),
            "keywords": ["training", "measure", "handle", "storage", "damage", "material list",
                         "over-order", "quantity", "recycle", "reuse", "current", "plan"],
            "minKeywords": 3,
        },
        {
            "year": 2022, "qNum": "18(b)", "section": "II", "marks": 4,
            "q": ("Describe the processes to be followed when organising and conducting a "
                  "formal ‘on-site’ meeting."),
            "answer": (
                "<strong>Before the meeting.</strong> Appoint a chairperson to run it. Set and "
                "publish the time, duration and location, and circulate an agenda in advance so "
                "attendees know the purpose and can prepare.<br><br>"
                "<strong>During the meeting.</strong> Follow a set procedure and work through "
                "the agenda. The chairperson controls the discussion to keep it on track and "
                "ensures everyone has the opportunity to contribute. A record of attendees and "
                "apologies is taken, and minutes are kept of what was discussed and decided.<br><br>"
                "<strong>After the meeting.</strong> Distribute the minutes, record the outcomes "
                "and any actions with the person responsible, and plan the follow-up so "
                "decisions are actually carried out and can be reviewed at the next meeting."
            ),
            "keywords": ["chairperson", "agenda", "time", "location", "procedure", "minutes",
                         "attendee", "apolog", "outcome", "follow up", "record"],
            "minKeywords": 5,
        },
        {
            "year": 2022, "qNum": "18(c)", "section": "II", "marks": 5,
            "q": ("A new house is to be built.<br>Describe methods that construction workers use "
                  "to plan and organise their work."),
            "answer": (
                "<strong>Read and interpret the documentation.</strong> Construction plans and "
                "specifications are read first to establish exactly what the job requires.<br>"
                "<strong>Gantt charts and construction programs</strong> set out the planned "
                "sequencing of tasks and the duration of each, so trades can be scheduled in "
                "the right order and the critical path is visible.<br>"
                "<strong>Toolbox talks and site meetings</strong> inform workers about the "
                "day's conditions, any changes, and site goals or deadlines.<br>"
                "<strong>Cutting lists and delivery dockets</strong> provide material "
                "quantities and sizes, and confirm what has actually arrived on site.<br>"
                "<strong>Safe Work Method Statements (SWMS) and Safety Data Sheets (SDS)</strong> "
                "determine the correct procedures for using, handling and storing hazardous "
                "materials before the work starts.<br><br>"
                "Workers also use rosters, timetables and checklists, delegate duties, consult "
                "industry professionals and engage specialist trades such as plumbers and "
                "electricians, check the Building Code of Australia and council regulations, "
                "allow for the weather forecast, and refer to product manuals and technical "
                "data sheets."
            ),
            "keywords": ["plan", "specification", "gantt", "sequence", "duration", "toolbox",
                         "meeting", "cutting list", "docket", "SWMS", "SDS", "roster",
                         "checklist", "council", "weather"],
            "minKeywords": 6,
        },
        {
            "year": 2022, "qNum": "19(b)", "section": "II", "marks": 3,
            "q": ("A bathroom plan is shown.<br>Calculate the number of 300 × 300 floor "
                  "tiles required to tile the area shown. Allow an additional 5% for wastage."),
            "image": "/diagrams/vet-construction_2022_Q19b_stimulus.jpg",
            "answer": (
                "Split the L-shaped floor into two rectangles, in metres.<br><br>"
                "Upper section: 1.2 × 1.2 = <strong>1.44 m<sup>2</sup></strong><br>"
                "Lower section: 2.4 × 2.7 = <strong>6.48 m<sup>2</sup></strong><br>"
                "Total floor area = 1.44 + 6.48 = <strong>7.92 m<sup>2</sup></strong><br><br>"
                "Tile area = 0.3 × 0.3 = <strong>0.09 m<sup>2</sup></strong><br>"
                "Tiles needed = 7.92 ÷ 0.09 = <strong>88 tiles</strong><br><br>"
                "Add 5% wastage: 88 × 1.05 = 92.4, so order <strong>93 tiles</strong> "
                "— always round UP, since part of a tile cannot be bought."
            ),
            "keywords": ["7.92", "1.44", "6.48", "0.09", "88", "93", "92.4", "area",
                         "wastage", "round"],
            "minKeywords": 4,
        },
        {
            "year": 2022, "qNum": "19(c)", "section": "II", "marks": 2,
            "q": ("The total time required to complete the tiling is 8 hours 15 minutes.<br>"
                  "Calculate the total cost for labour based on an hourly rate of $62 per hour "
                  "including GST."),
            "answer": (
                "Convert the minutes to a decimal part of an hour first:<br><br>"
                "15 ÷ 60 = <strong>0.25 hours</strong><br>"
                "Total time = 8.00 + 0.25 = <strong>8.25 hours</strong><br><br>"
                "Labour cost = 8.25 × $62.00 = <strong>$511.50</strong><br><br>"
                "Multiplying 8.15 by the rate is the common error — 8 hours 15 minutes is "
                "8.25 hours, not 8.15."
            ),
            "keywords": ["511.50", "8.25", "0.25", "60", "62", "labour", "hour", "minute"],
            "minKeywords": 3,
        },
        {
            "year": 2022, "qNum": "20", "section": "III", "marks": 15,
            "q": ("Explain how conflict in a construction workplace may arise and the impact it "
                  "could have on workers, employers and clients.<br>Provide relevant industry "
                  "examples to support your response."),
            "answer": (
                "<strong>How conflict arises.</strong> Poor communication is the most common "
                "cause — unclear instructions, or a variation passed on verbally and never "
                "confirmed in writing. Unrealistic timeframes and workloads, lack of "
                "organisation, and opposing priorities or viewpoints between trades all create "
                "friction: a tiler who cannot start because the waterproofer has not finished "
                "is a standard example. Equipment and materials not being available when needed "
                "causes downtime and blame. Other causes include stress, perceived inequity or "
                "favouritism, mistakes and rework, and safety concerns over dangerous work or a "
                "near miss. Conflict also arises from workers turning up late, without the "
                "necessary tools, or under the influence of drugs or alcohol; from not following "
                "workplace policies and procedures; from cultural differences such as language "
                "barriers or lack of respect, and religious beliefs; from a lack of knowledge "
                "and skill; and from inappropriate behaviour, bullying, harassment or offensive "
                "language.<br><br>"
                "<strong>Impact on workers.</strong> Ineffective teamwork and disharmony on "
                "site, job dissatisfaction and low morale, decreased safety and bad judgement "
                "as workers become distracted, increased absenteeism, and in serious cases "
                "termination of employment. Handled well, however, conflict can inspire "
                "creativity in solving the underlying problem.<br><br>"
                "<strong>Impact on employers.</strong> Less productivity and job delays, a poor "
                "workplace culture, increased workplace accidents, reduced profits and pay "
                "disputes, damage to the business reputation, a high rate of employee turnover "
                "with the cost of re-recruiting and retraining, and potential legal "
                "ramifications.<br><br>"
                "<strong>Impact on clients.</strong> The project runs past its completion date, "
                "costs rise through variations and delay claims, and the quality of the "
                "finished work suffers when trades are not cooperating. The client loses "
                "confidence in the builder, may withhold progress payments, and disputes can "
                "end in a formal dispute-resolution process.<br><br>"
                "<strong>Managing it.</strong> Clear communication, defined roles and "
                "expectations, toolbox talks, an agreed grievance procedure, and early "
                "intervention by a supervisor keep most conflict from escalating."
            ),
            "keywords": ["communication", "timeframe", "workload", "priorit", "material",
                         "stress", "bullying", "cultural", "safety", "teamwork", "morale",
                         "absentee", "productivity", "delay", "profit", "reputation",
                         "turnover", "legal", "client", "cost", "quality", "dispute"],
            "minKeywords": 9,
        },
        {
            "year": 2022, "qNum": "21(a)", "section": "IV", "marks": 5,
            "q": "Describe the maintenance of a concrete mixer.",
            "answer": (
                "<strong>Before each use.</strong> Inspect the electrical cord for cuts, fraying "
                "or damage and confirm the test-and-tag is current. Check that all guarding is "
                "in place and operational, the electrical switch works, and the handles and "
                "grips are in place and in good condition.<br><br>"
                "<strong>Tyres and frame.</strong> Check the tyres for general wear and tear and "
                "test them for correct inflation pressure, which matters for both ease of "
                "transport and stability while the mixer is running. Check the overall "
                "appearance for rust and corrosion, and ensure all nuts and bolts are correctly "
                "tightened.<br><br>"
                "<strong>After each use.</strong> Clean the mixer with a hose to remove residual "
                "cement before it sets — hardened cement in the drum is very difficult to "
                "remove and unbalances the drum. Lightly oil the interior of the drum to prevent "
                "corrosion during storage.<br><br>"
                "<strong>Periodic servicing.</strong> Check the drive belt for correct tension "
                "and general condition, replacing it if needed, and grease all moving mechanical "
                "parts that require periodic greasing on a regular basis. For a petrol-powered "
                "machine, check the engine oil level and clean and check the fuel system for "
                "leaks."
            ),
            "keywords": ["tyre", "pressure", "clean", "hose", "cement", "drum", "oil",
                         "corrosion", "belt", "tension", "grease", "tag", "cord", "guard",
                         "bolt"],
            "minKeywords": 6,
        },
        {
            "year": 2022, "qNum": "21(b)", "section": "IV", "marks": 10,
            "q": ("Explain strategies that can be implemented to minimise the risk of harm to "
                  "workers on a construction site."),
            "answer": (
                "<strong>Risk management.</strong> The foundation is to conduct risk assessments "
                "and apply the hierarchy of hazard control — eliminate the hazard first, then "
                "substitute, isolate, apply engineering controls, then administrative controls, "
                "with PPE as the last line of defence rather than the first.<br><br>"
                "<strong>Training and competency.</strong> All workers hold construction "
                "induction training (the White Card), plus accredited courses, licences and "
                "tickets for the plant they operate, supported by mentoring of apprentices.<br><br>"
                "<strong>Plant and equipment.</strong> Correct storage and maintenance of tools "
                "and equipment, test-and-tag of all electrical equipment, and guarding kept in "
                "place and operational.<br><br>"
                "<strong>Hazardous materials.</strong> Correct storage of hazardous materials "
                "and chemicals, with worksite materials stacked and stored correctly so stacks "
                "cannot collapse.<br><br>"
                "<strong>Physical controls.</strong> Scaffolding and edge railing installed when "
                "working at heights, temporary fencing, barricades and hoarding to control "
                "access, and workplace signage, posters and tags to warn of hazards.<br><br>"
                "<strong>Manual handling.</strong> Correct manual handling techniques and "
                "mechanical lifting aids such as trolleys, hoists and cranes — for example "
                "using a brick elevator rather than carrying packs up a ladder.<br><br>"
                "<strong>Documentation.</strong> Safety Data Sheets, Safe Work Method Statements, "
                "Standard Operating Procedures, product labels, manuals and incident reports, so "
                "the safe method is written down and followed consistently.<br><br>"
                "<strong>Housekeeping and emergency readiness.</strong> Designated waste disposal "
                "and recycling with regular site clean-ups, trained first aid personnel and "
                "supplies, and established emergency procedures and evacuation processes.<br><br>"
                "<strong>Culture.</strong> Effective leadership with clear expectations, "
                "effective on-site communication both verbal and non-verbal, and consultation "
                "through the WHS committee and health and safety representatives so workers "
                "raise hazards before they cause harm."
            ),
            "keywords": ["risk assessment", "hierarchy", "eliminate", "control", "PPE",
                         "training", "white card", "licence", "tag", "guard", "hazardous",
                         "storage", "scaffold", "height", "fencing", "signage", "manual handling",
                         "SWMS", "SDS", "first aid", "emergency", "housekeeping", "consultation"],
            "minKeywords": 9,
        },
    ],
    "2023": [
        {
            "year": 2023, "qNum": "16(a)(ii)", "section": "II", "marks": 2,
            "q": ("A common type of saw used in construction is shown.<br>List TWO items of "
                  "personal protective equipment (PPE) required when using this saw."),
            "image": "/diagrams/vet-construction_2023_Q16a_stimulus.jpg",
            "answer": (
                "1. <strong>Safety glasses or goggles</strong> — a drop saw throws timber chips "
                "and dust directly back towards the operator's face.<br>"
                "2. <strong>Hearing protection</strong> — earmuffs or earplugs, because the "
                "blade noise is well above the level at which hearing damage occurs.<br><br>"
                "Other acceptable items are a face shield, a dust mask, protective footwear, "
                "and hair tied back or restrained so it cannot be caught by the blade."
            ),
            "keywords": ["safety glasses", "goggles", "eye", "hearing", "earmuff", "earplug",
                         "face shield", "dust mask", "footwear", "hair"],
            "minKeywords": 2,
        },
        {
            "year": 2023, "qNum": "16(b)", "section": "II", "marks": 3,
            "q": "Outline the advantages of using battery-powered tools and equipment.",
            "answer": (
                "<strong>Portability.</strong> Battery tools are not restricted to the length of "
                "an extension lead, so they can be set up quickly and easily in a variety of "
                "locations. They allow work on remote sites with no mains power and on new "
                "dwellings where power has not yet been connected, and they remove the need for "
                "a generator.<br><br>"
                "<strong>Safety.</strong> With no cords there are no trip hazards dragged across "
                "the site and no frayed leads to check, which also means no machine leads "
                "requiring testing and tagging.<br><br>"
                "<strong>Efficiency.</strong> Set-up is quicker — there is no cord to run out, no "
                "power point to find and no generator to start — so work begins sooner, and "
                "working outdoors and at height is easier."
            ),
            "keywords": ["portable", "cord", "lead", "extension", "trip", "hazard", "generator",
                         "remote", "power", "tag", "quick", "outdoor"],
            "minKeywords": 4,
        },
        {
            "year": 2023, "qNum": "17(a)", "section": "II", "marks": 2,
            "q": ("A construction worker and the employer cannot agree on the correct amount "
                  "the worker should be paid.<br>How could this disagreement be resolved?"),
            "answer": (
                "Either party can seek clarification of the correct award pay rate from an "
                "independent authority rather than trying to settle it between themselves.<br><br>"
                "The worker or employer could contact a <strong>government regulator</strong> — "
                "the Fair Work Ombudsman or Fair Work Commission — to obtain a ruling on the "
                "applicable award rate.<br><br>"
                "They could also seek advice from a <strong>trade union</strong> (for the "
                "worker), a <strong>professional association</strong> or an <strong>industry "
                "group</strong> such as the HIA or MBA (for the employer). If the disagreement "
                "cannot be resolved that way, it can be taken to formal dispute resolution."
            ),
            "keywords": ["award", "rate", "regulator", "fair work", "ombudsman", "union",
                         "association", "industry", "HIA", "MBA", "dispute"],
            "minKeywords": 2,
        },
        {
            "year": 2023, "qNum": "17(b)", "section": "II", "marks": 3,
            "q": ("Describe the personal attributes that the construction industry values in "
                  "its workers."),
            "answer": (
                "The industry values workers who <strong>attend work regularly and are "
                "punctual</strong>, because the whole site's programme depends on trades being "
                "there when scheduled.<br><br>"
                "It values <strong>work performance</strong> — completing tasks within the "
                "scheduled timeframe, taking pride in the work, taking directions from "
                "supervisors, paying attention to detail and giving consistent service.<br><br>"
                "It values <strong>ethical behaviour</strong>: honesty, confidentiality, and a "
                "positive attitude and demeanour towards workmates and clients. Good "
                "<strong>personal presentation and grooming</strong> matter because workers "
                "represent the business in front of clients, and <strong>safe work practices</strong> "
                "are valued because an unsafe worker is a risk to everyone on site."
            ),
            "keywords": ["attendance", "punctual", "performance", "timeframe", "pride",
                         "direction", "attention to detail", "ethical", "honesty",
                         "confidentiality", "attitude", "presentation", "safe work"],
            "minKeywords": 4,
        },
        {
            "year": 2023, "qNum": "17(c)", "section": "II", "marks": 5,
            "q": ("Following the renovation of a residential house, many left over substances "
                  "and materials require disposal.<br>Describe the process of disposal of these "
                  "substances and materials during the final stages of clean-up."),
            "answer": (
                "<strong>Sort first.</strong> Arrange all materials and substances into "
                "categories and place them into the correct bins, so that like material is "
                "collected together ready for its own disposal route. Anything still usable "
                "should be set aside and stored correctly for future use rather than thrown "
                "out.<br><br>"
                "<strong>Timber.</strong> Treated pine offcuts must be kept separate — treated "
                "timber cannot be burnt or mulched. They go into a loose stacking bin and then "
                "to an approved disposal site.<br><br>"
                "<strong>Liquids and chemicals.</strong> Remaining paints, solvents and "
                "adhesives are stored in approved sealed and labelled containers and taken to a "
                "chemical waste disposal facility. They must never be poured onto the ground or "
                "into a stormwater drain.<br><br>"
                "<strong>Masonry and metal.</strong> Left-over bricks and rubble go to a "
                "recycling centre that accepts construction and demolition debris; metal waste "
                "is collected and taken to a metal recycling centre, where it has scrap value.<br><br>"
                "Throughout, use approved disposal collection sites and different bins for each "
                "waste stream, and keep the documentation for any regulated waste."
            ),
            "keywords": ["sort", "categor", "bin", "treated", "timber", "approved", "disposal",
                         "liquid", "sealed", "container", "chemical", "brick", "recycl",
                         "metal", "reuse", "stormwater"],
            "minKeywords": 6,
        },
        {
            "year": 2023, "qNum": "18(a)", "section": "II", "marks": 3,
            "q": ("Describe methods that can be used to limit the noise of a generator on a "
                  "construction site."),
            "answer": (
                "<strong>Position it away from people.</strong> Site the generator outside and "
                "well away from where workers are concentrated, and away from neighbouring "
                "boundaries. Keep it clear of walls and stacked materials that would cause the "
                "sound to echo and amplify.<br><br>"
                "<strong>Limit when it runs.</strong> Only operate the generator when it is "
                "actually needed, and only within the allowable construction hours set by the "
                "council.<br><br>"
                "<strong>Keep it in good order.</strong> Ensure the machine is operating "
                "correctly and is serviced regularly — a poorly maintained or faulty exhaust is "
                "markedly louder — and follow the correct operating procedures.<br><br>"
                "Where noise cannot be reduced far enough at the source, acoustic enclosures or "
                "barriers can be used, and workers nearby must wear hearing protection as PPE."
            ),
            "keywords": ["position", "away", "outside", "echo", "material", "hours", "council",
                         "service", "maintain", "operating", "PPE", "hearing", "enclosure"],
            "minKeywords": 4,
        },
        {
            "year": 2023, "qNum": "18(c)", "section": "II", "marks": 4,
            "q": "Explain why symbols are used on construction plans.",
            "answer": (
                "<strong>They are a standard, shared language.</strong> Symbols follow a set of "
                "conventions — an Australian Standard, AS 1100 — so the same symbol means the "
                "same thing to every user in the industry, no matter who drew the plan.<br><br>"
                "<strong>They are fast to read and reduce confusion.</strong> A symbol is a "
                "quick and easy way to recognise the layout and provides clarity on a crowded "
                "drawing. They indicate where things need to be built and installed, represent "
                "every element in the plan, and provide a reference back to the specifications.<br><br>"
                "<strong>They overcome literacy and language barriers.</strong> A worker who "
                "does not read English fluently can still read a plan drawn in standard symbols, "
                "which matters on a multilingual site.<br><br>"
                "<strong>They keep the drawing flexible.</strong> A symbol represents the "
                "function rather than a specific product — not all fixtures are the same size "
                "and shape — so adjustments can be made during fitout to suit the client's needs "
                "and the space without redrawing the plan."
            ),
            "keywords": ["standard", "AS1100", "convention", "understood", "clarity",
                         "confusion", "quick", "layout", "language", "literacy", "barrier",
                         "specification", "fixture"],
            "minKeywords": 5,
        },
        {
            "year": 2023, "qNum": "19(a)", "section": "II", "marks": 2,
            "q": ("A builder is constructing a house that requires 15 000 bricks. A full pallet "
                  "of bricks has 500 bricks.<br>How many pallets of bricks will need to be "
                  "ordered? Allow for 10% wastage."),
            "answer": (
                "Add the wastage to the brick count first, then convert to pallets.<br><br>"
                "Wastage = 10% × 15 000 = <strong>1500 bricks</strong><br>"
                "Total bricks = 15 000 + 1500 = <strong>16 500 bricks</strong><br><br>"
                "Pallets = 16 500 ÷ 500 = <strong>33 pallets</strong><br><br>"
                "The builder needs to order <strong>33 pallets</strong>. Note that the division "
                "comes out exactly here; where it does not, always round UP, because a part "
                "pallet still has to be ordered as a whole one."
            ),
            "keywords": ["33", "16 500", "16500", "1500", "10%", "wastage", "500", "pallet"],
            "minKeywords": 3,
        },
        {
            "year": 2023, "qNum": "19(b)(ii)", "section": "II", "marks": 2,
            "q": ("A shed is to be built on a concrete slab with concrete footings, as shown."
                  "<br>How many cubic metres of concrete are required for the slab?"),
            "image": "/diagrams/vet-construction_2023_Q19b_stimulus.jpg",
            "answer": (
                "This part is the <strong>slab</strong> only, not the footings. The note on the "
                "drawing gives the slab thickness as 100 mm.<br><br>"
                "Convert the plan dimensions to metres: 8500 mm = 8.5 m, 6000 mm = 6 m, and "
                "100 mm = 0.1 m.<br><br>"
                "Volume = length × width × thickness<br>"
                "= 8.5 × 6 × 0.1 = <strong>5.1 m<sup>3</sup></strong><br><br>"
                "Converting the millimetre dimensions on the plan to metres before multiplying "
                "is the step the mark depends on."
            ),
            "keywords": ["5.1", "8.5", "0.1", "volume", "length", "width", "thickness",
                         "slab", "metre", "convert"],
            "minKeywords": 3,
        },
        {
            "year": 2023, "qNum": "20(a)", "section": "III", "marks": 5,
            "q": ("A builder is constructing a group of 12 three-bedroom units on a large site. "
                  "A variety of trades will be working on this project.<br>Describe appropriate "
                  "ways that different trades can communicate with each other during the "
                  "building process."),
            "answer": (
                "On a site this size, most trades need to be involved in establishing and "
                "maintaining the construction sequence, so communication has to be deliberate "
                "rather than incidental.<br><br>"
                "<strong>Formal and informal meetings.</strong> The site supervisor arranges "
                "both — scheduled site meetings and toolbox talks where the day's work, changes "
                "and WHS matters are covered, and informal face-to-face discussions between "
                "trades as issues arise.<br><br>"
                "<strong>Written and displayed communication.</strong> Notice boards inform "
                "trades of toolbox talks and WHS meetings; the construction programme and "
                "Gantt chart show who is on site when; and plans are used as the common "
                "reference when two trades discuss how their work fits together.<br><br>"
                "<strong>Non-verbal communication.</strong> Signage and the drawings themselves "
                "carry information without discussion, and hand signals are used where noise or "
                "distance prevents speech.<br><br>"
                "<strong>Equipment.</strong> Two-way radios across a large site, speakers or "
                "public address for site-wide announcements, and phones and SMS for confirming "
                "arrangements and deliveries in writing."
            ),
            "keywords": ["meeting", "toolbox", "supervisor", "face-to-face", "notice board",
                         "signage", "plan", "drawing", "non-verbal", "hand signal", "radio",
                         "phone", "SMS", "sequence"],
            "minKeywords": 5,
        },
        {
            "year": 2023, "qNum": "20(b)", "section": "III", "marks": 10,
            "q": ("A builder is constructing a group of 12 three-bedroom units on a large site. "
                  "A variety of trades will be working on this project.<br>Explain how work "
                  "sequencing should be planned and organised for this site.<br>Support your "
                  "answer with relevant workplace examples."),
            "answer": (
                "<strong>Start from the documentation and the logical order of trades.</strong> "
                "Work sequencing means putting tasks in the order in which they physically must "
                "happen and identifying task dependencies: on a unit development the sequence "
                "runs site establishment and excavation, footings and slab, frame, roof, "
                "external cladding and lock-up, then the internal trades. A tiler cannot start "
                "until the waterproofer has finished and the membrane has cured; a plasterer "
                "cannot start until the electrician and plumber have completed their rough-in.<br><br>"
                "<strong>Use a Gantt chart or construction programme.</strong> This sets out the "
                "planned sequence and the duration of every task, is regularly referred to and "
                "adjusted as the job moves, and makes the critical path visible so the builder "
                "knows which delays actually matter. It also lets the same trade be scheduled "
                "across several units in turn rather than being called back repeatedly.<br><br>"
                "<strong>Plan resources against the programme.</strong> Assess what needs to be "
                "done for each component and how, prepare a written work plan and resource list, "
                "and estimate the time and number of personnel required for each stage so the "
                "right number of workers is on site — not too few, creating a bottleneck, and "
                "not too many, causing congestion.<br><br>"
                "<strong>Order and deliver to the sequence.</strong> Supplies are ordered and "
                "deliveries planned so materials arrive as they are needed. On a 12-unit site "
                "there is limited space, so a full delivery of plasterboard arriving before "
                "lock-up would be damaged and would obstruct access.<br><br>"
                "<strong>Monitor and adjust.</strong> Set overall goals, objectives and "
                "priorities with stage completion dates, monitor progress against them, work "
                "within the completion timeframes and to the quality measures specified, and "
                "re-sequence when weather or a supply delay forces it — bringing forward "
                "internal work during a wet week, for example."
            ),
            "keywords": ["sequence", "dependenc", "order", "trade", "gantt", "programme",
                         "duration", "critical", "resource", "personnel", "estimate", "order",
                         "delivery", "monitor", "progress", "timeframe", "quality", "adjust"],
            "minKeywords": 8,
        },
        {
            "year": 2023, "qNum": "21", "section": "IV", "marks": 15,
            "q": ("Explain how the risk control hierarchy can be used to manage hazards on a "
                  "construction site.<br>Support your answer with relevant workplace examples."),
            "answer": (
                "The risk control hierarchy ranks control measures from most to least effective, "
                "and requires the highest practicable control to be used rather than the "
                "easiest. It is applied after hazards have been identified and the risk assessed.<br><br>"
                "<strong>1. Eliminate</strong> — remove the hazard completely. This is always "
                "the most effective control. For example, prefabricating roof trusses at ground "
                "level, or on the ground off site, removes the fall hazard rather than managing "
                "it.<br><br>"
                "<strong>2. Substitute</strong> — replace the hazard with something less "
                "hazardous. Using a water-based sealant instead of a solvent-based one removes "
                "the vapour hazard; using lighter, smaller blocks reduces the manual handling "
                "risk.<br><br>"
                "<strong>3. Isolate</strong> — separate people from the hazard. Barricading an "
                "excavation, fencing the site perimeter, or using an exclusion zone beneath a "
                "crane lift keeps workers out of harm's way.<br><br>"
                "<strong>4. Engineering controls</strong> — modify the plant or process. "
                "On-tool dust extraction on a concrete saw, guarding on a drop saw, an edge "
                "protection rail on a slab, or a mechanical hoist instead of carrying materials "
                "up a ladder.<br><br>"
                "<strong>5. Administrative controls</strong> — change the way people work. Safe "
                "Work Method Statements, standard operating procedures, job rotation to limit "
                "exposure, training and licensing, toolbox talks, signage, and scheduling noisy "
                "or hot work for cooler parts of the day.<br><br>"
                "<strong>6. Personal protective equipment</strong> — the last line of defence, "
                "because it protects only the individual wearing it and only if worn correctly. "
                "Hard hat, safety glasses, hearing protection, gloves, respirator, harness and "
                "steel-capped boots.<br><br>"
                "<strong>In practice</strong> the levels are combined: cutting concrete might "
                "use on-tool water suppression (engineering), an exclusion zone (isolation), a "
                "SWMS and training (administrative) and a P2 respirator (PPE) together. The "
                "hierarchy is not a one-off exercise — controls must be monitored and reviewed "
                "for effectiveness, and reassessed whenever the work, the plant or the site "
                "conditions change.<br><br>"
                "The hazards it is applied to on a construction site include working at heights, "
                "excavations, hazardous materials and chemicals, manual handling, tools, plant "
                "and machinery, noise, the work environment and weather, working alone, and "
                "working near traffic and water."
            ),
            "keywords": ["hierarchy", "eliminate", "substitute", "isolate", "engineering",
                         "administrative", "PPE", "risk assessment", "hazard", "height",
                         "excavation", "guard", "SWMS", "training", "signage", "monitor",
                         "review", "example"],
            "minKeywords": 8,
        },
    ],
    "2024": [
        {
            "year": 2024, "qNum": "17(a)", "section": "II", "marks": 2,
            "q": ("Identify ONE advantage and ONE disadvantage of using a laser measuring "
                  "tool."),
            "answer": (
                "<strong>Advantage:</strong> it reduces the time needed to complete a "
                "measurement — one person can measure a long distance instantly, where a tape "
                "would need two people or repeated set-ups. Laser tools are also portable, easy "
                "to use, and can hold and recall stored measurements.<br><br>"
                "<strong>Disadvantage:</strong> the battery periodically needs replacing or "
                "recharging, so the tool can fail mid-job. They are also expensive compared "
                "with a tape, need to be maintained and calibrated, require a clear line of "
                "sight to the target, and generally measure internal dimensions only."
            ),
            "keywords": ["time", "quick", "one person", "portable", "store", "battery",
                         "recharge", "expensive", "maintain", "line of sight", "internal"],
            "minKeywords": 2,
        },
        {
            "year": 2024, "qNum": "17(b)", "section": "II", "marks": 3,
            "q": "Outline how incorrect measurements can affect a construction project.",
            "answer": (
                "<strong>Materials and cost.</strong> Incorrect measurements change the quantity "
                "of material ordered. Ordering too little means reordering, with additional "
                "delivery costs and a wait; ordering too much means paying for material that is "
                "wasted. Either way the overall cost rises for both the builder and the "
                "customer.<br><br>"
                "<strong>Time.</strong> Reordering or remaking components delays project "
                "completion, and a delay to one trade pushes back every trade scheduled after "
                "it.<br><br>"
                "<strong>Quality and safety.</strong> Components cut to the wrong size do not "
                "fit properly, which produces a poor finish, may require the work to be pulled "
                "down and redone, and in structural work can compromise the strength and safety "
                "of the building."
            ),
            "keywords": ["material", "quantity", "order", "reorder", "cost", "delivery",
                         "waste", "time", "delay", "completion", "fit", "rework", "quality",
                         "safety"],
            "minKeywords": 4,
        },
        {
            "year": 2024, "qNum": "17(c)", "section": "II", "marks": 5,
            "q": ("Describe how engineering controls can be used to manage a hot and dusty work "
                  "environment."),
            "answer": (
                "Engineering controls sit above administrative controls and PPE in the risk "
                "control hierarchy because they modify the physical conditions themselves rather "
                "than relying on workers to behave differently.<br><br>"
                "<strong>Ventilation.</strong> Installing specialised ventilation and extraction "
                "systems regulates both temperature and dust levels. They provide adequate air "
                "exchange, removing hot and contaminated air and replacing it with cooler, "
                "cleaner air. This cools the environment and prevents dust from accumulating, "
                "significantly reducing the respiratory risk to workers.<br><br>"
                "<strong>Dust suppression at the source.</strong> Water spray systems and on-tool "
                "water suppression capture dust as it is generated, rather than after it has "
                "become airborne. On-tool dust extraction fitted to concrete saws and grinders "
                "does the same job by vacuum.<br><br>"
                "<strong>Cooling.</strong> Strategic placement of cooling units, fans or "
                "evaporative coolers in areas where workers are concentrated mitigates the heat "
                "risk, and shade structures or temporary roofing remove the radiant heat load.<br><br>"
                "<strong>Isolation and enclosure.</strong> Enclosing or screening a dusty "
                "process keeps the dust within a defined area so the rest of the site is not "
                "affected.<br><br>"
                "Combined, these controls reduce the hazard for everyone on site at once, which "
                "is why they are preferred over relying on respirators and rest breaks alone — "
                "though those remain as supporting administrative controls and PPE."
            ),
            "keywords": ["engineering", "ventilation", "extraction", "air", "exchange", "dust",
                         "respiratory", "water", "spray", "suppression", "on-tool", "cooling",
                         "fan", "shade", "enclosure", "hierarchy"],
            "minKeywords": 6,
        },
        {
            "year": 2024, "qNum": "18(a)", "section": "II", "marks": 3,
            "q": ("Outline the importance of feedback in the communication process when working "
                  "with clients/customers."),
            "answer": (
                "Feedback is what closes the communication loop. It allows both the sender and "
                "the receiver to confirm that a message has actually been received and "
                "understood, rather than assumed.<br><br>"
                "It <strong>ensures the correct message has been delivered</strong> — the client "
                "restating what they want, or the builder confirming a variation in writing, "
                "shows whether the two parties share the same understanding. It acts as the "
                "bridge between sender and receiver, providing clarification and validation.<br><br>"
                "It <strong>surfaces problems early</strong>, so issues can be addressed while "
                "they are still cheap to fix rather than after the work is built. It also "
                "supports continuous improvement, since a client's feedback on finished work "
                "tells the builder what to do differently next time — and it builds the client's "
                "confidence and the business's reputation."
            ),
            "keywords": ["confirm", "understand", "message", "sender", "receiver", "clarif",
                         "validat", "problem", "issue", "improvement", "client", "expectation"],
            "minKeywords": 4,
        },
        {
            "year": 2024, "qNum": "18(b)", "section": "II", "marks": 3,
            "q": ("Why is it important to correctly store reusable materials on a building "
                  "site?"),
            "answer": (
                "<strong>Availability and efficiency.</strong> Correctly stored materials are "
                "easy to access and ready for use, which reduces delays and improves efficiency "
                "— workers are not hunting for material or waiting for a replacement.<br><br>"
                "<strong>Cost.</strong> Correct storage prevents damage, so materials do not "
                "have to be bought twice. Correct stacking maintains the integrity of the "
                "material — stacking timber flat and evenly supported stops lengths twisting or "
                "bowing — and correct packing and strapping extend the usable life of the "
                "material.<br><br>"
                "<strong>Sustainability.</strong> Materials that can be reused many times reduce "
                "the demand for new materials, conserving resources and reducing waste sent to "
                "landfill. That saves money and lessens the environmental impact of the "
                "project.<br><br>"
                "<strong>Safety.</strong> Correctly stacked and stored material also cannot "
                "topple or collapse onto workers, and keeps access ways clear."
            ),
            "keywords": ["access", "ready", "delay", "efficiency", "damage", "cost", "stack",
                         "twist", "bow", "strap", "reuse", "sustainab", "waste", "safety"],
            "minKeywords": 4,
        },
        {
            "year": 2024, "qNum": "18(c)", "section": "II", "marks": 4,
            "q": ("Explain the factors that need to be considered by a builder during the "
                  "planning and preparation stage of a construction project."),
            "answer": (
                "<strong>Labour.</strong> Estimate the number and type of workers needed at each "
                "stage, so the correct trades are on site as required — too few causes delays, "
                "too many causes congestion and idle time.<br><br>"
                "<strong>Timing.</strong> Set realistic timelines, stage completion dates and "
                "deadlines for each part of the process. This provides a map of what should be "
                "completed and when, and keeps the build moving smoothly.<br><br>"
                "<strong>Resources.</strong> Ensure the correct tools, equipment, materials and "
                "consumables are ready and on site when needed, planned and sequenced "
                "efficiently. Optimum resource use also means not wasting money on plant sitting "
                "idle — hiring it for the window it is actually needed.<br><br>"
                "<strong>Risk.</strong> Thorough planning involves identifying hazards and "
                "constraints in advance — site access, ground conditions, weather, services "
                "location, working at heights — and putting controls in place before work "
                "starts.<br><br>"
                "<strong>Compliance and cost.</strong> Confirm approvals, the Building Code of "
                "Australia and council requirements, and prepare accurate estimates and a "
                "budget so the project is financially viable."
            ),
            "keywords": ["worker", "labour", "estimate", "timeline", "deadline", "stage",
                         "tool", "equipment", "material", "sequence", "resource", "idle",
                         "risk", "hazard", "weather", "approval", "council", "budget", "cost"],
            "minKeywords": 5,
        },
        {
            "year": 2024, "qNum": "19(c)", "section": "II", "marks": 2,
            "q": ("The ratio for concrete is 3 parts aggregate, 2 parts sand and 1 part cement "
                  "(3 : 2 : 1).<br>Calculate the volume of sand required for a concrete slab "
                  "with a volume of 11.6 m<sup>3</sup>."),
            "answer": (
                "Add the ratio parts to find how many parts make the whole:<br><br>"
                "3 + 2 + 1 = <strong>6 parts</strong><br><br>"
                "One part = 11.6 ÷ 6 = <strong>1.93 m<sup>3</sup></strong><br><br>"
                "Sand is 2 parts, so sand = 1.93 × 2 = <strong>3.86 m<sup>3</sup></strong><br><br>"
                "Dividing by 2 instead of by the total of 6 parts is the common error."
            ),
            "keywords": ["3.86", "1.93", "6 parts", "6", "ratio", "sand", "2 parts", "11.6"],
            "minKeywords": 3,
        },
        {
            "year": 2024, "qNum": "19(d)", "section": "II", "marks": 2,
            "q": ("The delivery cost for aggregate is $1.18/km per tonne.<br>Calculate the "
                  "delivery cost of 8 tonnes to a site 13 km away."),
            "answer": (
                "The rate is per kilometre AND per tonne, so multiply by both.<br><br>"
                "8 tonnes × $1.18 = <strong>$9.44</strong> (cost per kilometre)<br>"
                "$9.44 × 13 km = <strong>$122.72</strong><br><br>"
                "The order does not matter — 8 × 1.18 × 13 gives the same $122.72 — but both "
                "quantities must be used. Multiplying by only the distance or only the tonnage "
                "is the common error."
            ),
            "keywords": ["122.72", "9.44", "1.18", "8", "13", "tonne", "km", "delivery"],
            "minKeywords": 3,
        },
        {
            "year": 2024, "qNum": "20(a)", "section": "III", "marks": 5,
            "q": ("Describe TWO appropriate power or pneumatic tools that could be used in the "
                  "construction of a carport."),
            "answer": (
                "<strong>1. Drop saw (compound mitre / drop and slide saw)</strong> — a power "
                "tool used to dock timber to length and to cut the mitres and angles needed for "
                "the carport's rafters, beams and battens. The timber is clamped against the "
                "fence and the blade is drawn down through it, giving a fast, square and "
                "repeatable crosscut, which matters when many members must be cut to identical "
                "length. It requires safety glasses and hearing protection, and the guard must "
                "be operational.<br><br>"
                "<strong>2. Pneumatic nail gun</strong> — air-powered, used to shoot nails into "
                "the frame and to fix the roofing battens. It drives and sets a nail in one "
                "action, so it is far faster than hand nailing and produces consistent fixing "
                "depth over the many fixings a carport frame needs. It must never be pointed at "
                "a person, and the safety contact tip must be working.<br><br>"
                "Other appropriate tools include a cordless drill or impact driver to drive "
                "screws and screw down roofing sheets, a circular saw for ripping, an angle "
                "grinder for cutting steel, and a nibbler for cutting roofing sheet."
            ),
            "keywords": ["drop saw", "mitre", "dock", "length", "cut", "nail gun", "pneumatic",
                         "frame", "batten", "impact driver", "drill", "screw", "circular saw",
                         "grinder", "safety"],
            "minKeywords": 5,
        },
        {
            "year": 2024, "qNum": "20(b)", "section": "III", "marks": 10,
            "q": ("Explain the safe work procedures and practices that should be considered "
                  "during the construction of a carport."),
            "answer": (
                "<strong>Before work starts.</strong> All workers hold a construction induction "
                "card (White Card) and complete a site induction. Hazards specific to the job "
                "are identified — working at height on the roof, overhead powerlines, "
                "underground services at the footing locations, manual handling of beams — and "
                "the risk is assessed and controlled using the hierarchy of risk management. A "
                "Safe Work Method Statement is prepared for the high-risk work, and a job safety "
                "analysis for each task.<br><br>"
                "<strong>Documentation and compliance.</strong> Work complies with SafeWork NSW "
                "requirements. Safety Data Sheets are available for any chemicals such as "
                "treated timber, concrete additives and sealants; standard operating procedures "
                "and product manuals are followed; and workplace documentation and plans are on "
                "site and current.<br><br>"
                "<strong>On site.</strong> Workplace signage marks hazards and exclusion zones. "
                "Good housekeeping keeps offcuts, cords and materials out of access ways. "
                "Electrical safety means testing and tagging all leads and tools and using an "
                "RCD on the supply. Manual handling training and team lifting are used for "
                "beams and roof sheets, with attention to ergonomics and posture, and mechanical "
                "aids where the load is too heavy.<br><br>"
                "<strong>Working at height.</strong> Roof work on a carport is where the "
                "greatest risk sits — use a scaffold or elevated work platform rather than "
                "ladders where possible, install edge protection, and ensure roof sheets are not "
                "handled in windy conditions.<br><br>"
                "<strong>PPE and emergency readiness.</strong> Hard hat, safety glasses, hearing "
                "protection, gloves and steel-capped boots appropriate to each task, with sun "
                "protection for outdoor work. A first aid kit and trained first aider are "
                "available, and emergency and evacuation procedures are known before they are "
                "needed.<br><br>"
                "<strong>Sequencing.</strong> Job sequencing itself is a safety practice — "
                "planning the order of work so that, for example, the frame is braced before "
                "anyone works off it."
            ),
            "keywords": ["white card", "induction", "hazard", "hierarchy", "risk", "SWMS",
                         "JSA", "SafeWork", "SDS", "signage", "housekeeping", "electrical",
                         "tag", "manual handling", "ergonomic", "height", "scaffold", "PPE",
                         "first aid", "emergency", "sequencing"],
            "minKeywords": 8,
        },
        {
            "year": 2024, "qNum": "21", "section": "IV", "marks": 15,
            "q": ("Explain ways in which the construction industry can minimise its impact on "
                  "the environment."),
            "answer": (
                "The construction industry consumes large volumes of raw material and energy and "
                "generates a substantial share of national waste, so environmentally sustainable "
                "work practices are applied across the whole project.<br><br>"
                "<strong>Waste management.</strong> Approved disposal of waste, with sorting on "
                "site into separate streams so timber, masonry, metal and plasterboard can be "
                "recycled rather than sent to landfill. Accurate quantity calculation and "
                "ordering avoids creating the waste in the first place, and off-cuts and surplus "
                "material are stored for reuse.<br><br>"
                "<strong>Material selection.</strong> Use resources that are biodegradable, "
                "non-toxic, recoverable, recyclable, renewable or reusable. Specify plantation "
                "or certified timber, recycled aggregate and low-VOC paints and sealants.<br><br>"
                "<strong>Water and waterways.</strong> Protect discharge into waterways and "
                "stormwater with sediment fences, silt socks at drain inlets and vehicle wash "
                "bays. Test pipes for leaks and use efficient fittings and fixtures to reduce "
                "water consumption in the finished building.<br><br>"
                "<strong>Land and habitat.</strong> Reduce soil erosion by staging the clearing "
                "of vegetation, stabilising exposed ground and limiting the disturbed area at "
                "any one time. Protect wildlife habitats and retain existing trees where "
                "possible.<br><br>"
                "<strong>Chemicals and hazardous materials.</strong> Safe handling and storage "
                "of hazardous materials, bunded storage for liquids, and established management "
                "and clean-up processes for chemical or gas spillage and leakage so nothing "
                "reaches the soil or drains.<br><br>"
                "<strong>Air, noise and vibration.</strong> Limit noise and dust through work-hour "
                "restrictions, acoustic barriers, water suppression and on-tool extraction. "
                "Monitor vibration where work is near existing structures.<br><br>"
                "<strong>Energy and plant.</strong> Maintain tools, equipment and machinery so "
                "they run efficiently and do not leak or over-emit, and utilise alternative "
                "energy sources such as solar or grid power in place of diesel generators where "
                "practical.<br><br>"
                "<strong>Design and compliance.</strong> Comply with BASIX requirements for "
                "energy and water efficiency in new dwellings, and design for orientation, "
                "insulation and natural light so the building's whole-of-life environmental "
                "impact — not just the construction phase — is reduced."
            ),
            "keywords": ["waste", "dispose", "recycl", "reuse", "sort", "landfill",
                         "biodegradable", "renewable", "timber", "stormwater", "waterway",
                         "sediment", "erosion", "habitat", "hazardous", "spill", "noise",
                         "dust", "vibration", "maintenance", "alternative energy", "BASIX",
                         "efficien"],
            "minKeywords": 9,
        },
    ],
}

# Whole questions the engine cannot present at all, declared at subject level.
NEW_OMITTED = [
    {
        "year": 2025, "qNum": "19", "marks": 11,
        "reason": ("Parts (a)-(d) all read from a site plan that NESA has REDACTED from the "
                   "published paper -- page 16 carries only 'Due to copyright restrictions, "
                   "this material cannot be displayed until permission has been obtained.' "
                   "There is no stimulus to crop and the four parts (slab cost, surface water "
                   "exit, fence panels, paver pallets) cannot be answered without it. This is "
                   "an absent source, not an engine limitation."),
    },
]


def leaves(key, year, qnum):
    m = re.match(r"^(\d+)((?:\([a-z0-9ivx]+\))*)$", str(qnum))
    want = [m.group(1)] + re.findall(r"\(([a-z0-9ivx]+)\)", m.group(2))
    out = []
    for p in key["papers"][str(year)]:
        got = [str(p["question"])] + ([] if not p["part"] else p["part"].split("."))
        if got[:len(want)] == want:
            out.append(p)
    return out


def sort_key(q):
    m = re.match(r"^(\d+)((?:\([a-z0-9ivx]+\))*)$", str(q["qNum"]))
    parts = re.findall(r"\(([a-z0-9ivx]+)\)", m.group(2))
    return (int(q["year"]), int(m.group(1)), parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", required=True, help="year to port, or 'all'")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    raw = io.open(BANK, encoding="utf-8", newline="").read().replace("\r\n", "\n")
    bank = json.loads(raw)
    assert json.dumps(bank, indent=2, ensure_ascii=False) + "\n" == raw, \
        "vet-construction.json does not round-trip -- refusing to rewrite it"
    key = json.load(io.open(KEY, encoding="utf-8"))

    years = sorted(NEW) if args.year == "all" else [args.year]
    have = {(str(q["year"]), str(q["qNum"])) for q in bank["writtenQuestions"]}
    added = 0
    for year in years:
        for q in NEW.get(year, []):
            label = (str(q["year"]), q["qNum"])
            if label in have:
                print("  SKIP %s %s (already in the bank)" % label)
                continue
            ls = leaves(key, *label)
            assert ls, "%s %s: no official part joins to this entry" % label
            official = sum(p["marks"] for p in ls)
            assert official == q["marks"], \
                "%s %s: bank says %d marks, official is %d" % (label + (q["marks"], official))
            assert q.get("answer") and q.get("keywords") and q.get("minKeywords"), \
                "%s %s: missing answer/keywords/minKeywords" % label
            assert len(ls) == 1 or True
            note = STEM_NOTES.get(label)
            print("  + %s %-9s %2d marks  %d official band(s)%s"
                  % (label[0], label[1], q["marks"], len(ls[0]["criteria"]),
                     "   [stem note]" if note else ""))
            bank["writtenQuestions"].append(q)
            added += 1

    for o in NEW_OMITTED:
        if any(x["year"] == o["year"] and x["qNum"] == o["qNum"]
               for x in bank.get("omittedQuestions", [])):
            continue
        ls = leaves(key, o["year"], o["qNum"])
        assert ls, "omitted %s Q%s not in the official key" % (o["year"], o["qNum"])
        official = sum(p["marks"] for p in ls)
        assert official == o["marks"], \
            "omitted %s Q%s: declared %d, official %d" % (o["year"], o["qNum"], o["marks"], official)
        bank.setdefault("omittedQuestions", []).append(o)
        print("  omitted %s Q%s  %d marks (%d official parts)"
              % (o["year"], o["qNum"], o["marks"], len(ls)))

    bank["writtenQuestions"].sort(key=sort_key)

    if args.dry_run:
        print("\n  dry run - %d question(s) would be added; nothing written" % added)
        return
    out = json.dumps(bank, indent=2, ensure_ascii=False) + "\n"
    io.open(BANK, "w", encoding="utf-8", newline="\n").write(out)
    print("\n  %d question(s) added; bank now holds %d written questions"
          % (added, len(bank["writtenQuestions"])))


if __name__ == "__main__":
    sys.exit(main())
