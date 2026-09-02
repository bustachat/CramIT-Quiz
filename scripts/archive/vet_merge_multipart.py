# -*- coding: utf-8 -*-
"""One-off: merge VET Construction's split Section II multi-part written questions
into one bank entry per NESA question, matching Mathematics Advanced/Standard 2's
established convention (one entry per question, inline <img>, no top-level `image`
field on written questions). Not run in CI; run once, then delete.

Scope: Section II (Q16-19) only. Section III/IV (Q20/Q21) split into (a)/(b) bank
entries too, but NESA explicitly directs those to be answered in SEPARATE writing
booklets -- genuinely independent responses, not a shared short-answer sequence --
so they are left untouched.

Usage: python scripts/_vet_merge_multipart.py [--write]
Without --write, prints a dry-run report (marks reconciliation) and does not touch
the bank.
"""

import io
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BANK_PATH = os.path.join(REPO, "subjects", "vet-construction.json")
KEY_PATH = os.path.join(REPO, "data", "answer-key", "written", "vet-construction.json")

IMG_STYLE = 'style="max-width:100%;height:auto;display:block;margin:14px auto"'


def img(src, alt):
    return '<img src="%s" alt="%s" %s>' % (src, alt, IMG_STYLE)


def uniq(*lists):
    seen = []
    for lst in lists:
        for k in lst:
            if k not in seen:
                seen.append(k)
    return seen


# Each merged group: (year, base_qnum) -> new combined entry (qNum stays a bare int).
MERGES = {}


def add(year, qnum, marks, q, answer, keywords, band, image=None):
    # qNum stored as a string, matching every other VET bank entry's convention
    # (single-part questions are already "17", "20", "21(a)", never a bare int).
    MERGES[(year, qnum)] = {
        "year": year,
        "marks": marks,
        "section": "II",
        "qNum": str(qnum),
        "q": q,
        "answer": answer,
        "keywords": keywords,
        "bandDescriptors": band,
    }


# ============================================================ 2021 ==============

add(2021, 16, 8,
    q=("A tool is shown." + img("/diagrams/vet-construction_2021_Q16_stimulus.jpg",
        "A chisel with a bevelled cutting edge and wooden handle") +
       "<br><br>(a) Name the tool shown. <strong>(1 mark)</strong>"
       "<br><br>(b) Describe TWO suitable uses for this tool. <strong>(2 marks)</strong>"
       "<br><br>(c) Describe ONE consequence if this tool is poorly maintained. <strong>(2 marks)</strong>"
       "<br><br>(d) Describe both care and maintenance procedures that should be carried out "
       "to ensure the long life of this tool. <strong>(3 marks)</strong>"),
    answer=(
        "(a) Chisel (Firmer chisel, Bevelled-edge chisel, or Mortice chisel are all acceptable answers)."
        "<br><br>(b) A chisel can be used to: (1) Cut joints such as rebates, housings, mortices and "
        "dovetails by paring or chopping timber with a mallet. (2) Clean out recesses for hinges, locks "
        "and strike plates to ensure they sit flush with the timber surface. Other acceptable uses "
        "include: fitting and trimming joints in timber framing, removing glue squeeze-out from joints, "
        "or paring end grain for a clean fit."
        "<br><br>(c) A poorly maintained chisel becomes blunt, and a blunt chisel is both unsafe and "
        "inefficient.<br><strong>Safety:</strong> a blunt edge needs far more force to drive, so it is "
        "much more likely to skid off the timber and strike the user's hand — blunt tools cause more "
        "injuries than sharp ones.<br><strong>Quality and cost:</strong> a blunt chisel tears rather "
        "than slices the fibres, leaving a rough, inaccurate cut and a poor finish. It also takes "
        "longer to complete the same work, which increases labour time and therefore the cost of the job."
        "<br><br>(d) <strong>Care</strong> — use the chisel only for the work it is designed for: "
        "cutting joints and paring timber. It should never be used to open paint tins, lever or remove "
        "nails, or cut masonry. Strike it only with an appropriate mallet or hammer, and store it so the "
        "cutting edge is protected — in a roll, rack or guard rather than loose in a toolbox where the "
        "edge will be chipped.<br><strong>Maintenance</strong> — keep the edge sharp by grinding to "
        "restore the bevel, then honing on an oilstone and stropping to remove the burr (deburring). "
        "Check that the ferrule is secure and in place so the handle does not split, and inspect the "
        "handle for damage, replacing it as needed."
    ),
    keywords=uniq(
        ["chisel", "firmer", "bevelled", "mortice", "mortise"],
        ["joint", "rebate", "housing", "hinge", "lock", "pare", "trim", "cut", "timber"],
        ["blunt", "unsafe", "injury", "force", "slip", "finish", "quality", "time", "cost"],
        ["care", "intended", "store", "protect", "edge", "mallet", "maintenance", "grind",
         "hone", "strop", "ferrule", "handle"],
    ),
    band={
        "full": "Correctly identifies the chisel, describes TWO suitable uses, ONE consequence of "
                "poor maintenance, and both care and maintenance procedures in detail",
        "partial": "Identifies the chisel and describes uses, a consequence and care/maintenance "
                   "with reasonable but incomplete detail",
        "minimal": "Provides limited relevant information addressing one or two parts of the question",
    })

add(2021, 18, 13,
    q=("A concrete slab is to be laid for an outdoor picnic table as shown." +
       img("/diagrams/vet-construction_2021_Q18_stimulus.jpg",
           "A rectangular concrete slab with a semicircular end, dimensioned 6 m by 5 m") +
       "<br><br>(a) One tradesperson and one apprentice are required to complete the formwork for "
       "this project. The total time to complete this task will be 2.5 hours each.<br>The "
       "tradesperson charges $62.00 per hour and the apprentice charges $21.00 per hour. These "
       "prices include GST.<br>What is the total labour cost for this project? <strong>(2 marks)</strong>"
       "<br><br>(b) Calculate the perimeter of the concrete slab. <strong>(3 marks)</strong>"
       "<br><br>(c) Calculate the volume of concrete needed in cubic metres (m<sup>3</sup>) if the "
       "slab is 100 mm thick. Include 10% wastage in your answer. <strong>(4 marks)</strong>"
       "<br><br>(d) Describe the work health and safety factors that need to be considered before "
       "work commences on this building site. <strong>(4 marks)</strong>"),
    answer=(
        "(a) Cost each worker separately, then add:<br><br>Tradesperson: 2.5 × $62.00 = "
        "<strong>$155.00</strong><br>Apprentice: 2.5 × $21.00 = <strong>$52.50</strong><br>Total "
        "labour cost = $155.00 + $52.50 = <strong>$207.50</strong><br><br>Or combine the rates "
        "first, since both work the same 2.5 hours: $62.00 + $21.00 = $83.00 per hour, and 2.5 × "
        "$83.00 = <strong>$207.50</strong>."
        "<br><br>(b) The slab is a 6 m × 5 m rectangle with a semicircular end. The semicircle's "
        "diameter is the 5 m width, so its radius is 2.5 m.<br><br>Curved edge (half a "
        "circumference) = 0.5 × 2 × π × 2.5 = <strong>7.85 m</strong><br>Straight edges = 5 m "
        "(left end) + 6 m (top) + 6 m (bottom) = 17 m<br><br>Perimeter = 7.85 + 5 + 6 + 6 = "
        "<strong>24.85 m</strong><br><br>Note that the 5 m right-hand edge is <em>not</em> part of "
        "the perimeter — the semicircle replaces it."
        "<br><br>(c) Work out the area first, then the volume, then add the wastage.<br><br>"
        "<strong>Area</strong> = rectangle + semicircle<br>= (6 × 5) + (0.5 × π × 2.5<sup>2</sup>)"
        "<br>= 30 + 9.81 = <strong>39.81 m<sup>2</sup></strong><br><br><strong>Volume</strong> = "
        "area × thickness. 100 mm = 0.1 m<br>= 39.81 × 0.1 = <strong>3.98 m<sup>3</sup></strong>"
        "<br><br><strong>Add 10% wastage</strong> = 3.98 × 1.1 = <strong>4.38 m<sup>3</sup></strong>"
        "<br><br>Converting the thickness from millimetres to metres before multiplying is the "
        "step most often missed."
        "<br><br>(d) <strong>Site access and induction</strong> — all workers must hold a valid "
        "White Card (general construction induction) before they are allowed on site, and site "
        "access must be controlled so unauthorised people cannot enter.<br><strong>Training and "
        "competency</strong> — the employer must provide correct training for the operation of any "
        "machinery and plant being used, and workers must hold the relevant licences."
        "<br><strong>Plant and electrical safety</strong> — all electrical equipment must be in "
        "serviceable condition and carry a current test-and-tag before use, and supply must be "
        "protected by an earth leakage circuit breaker (ELCB).<br><strong>Amenities and "
        "welfare</strong> — clean drinking water, toilet facilities and a first aid station must "
        "be provided.<br><strong>Site conditions</strong> — PPE appropriate to the work, sun "
        "protection and allowance for weather conditions, good housekeeping so the site is well "
        "organised and accessible, waste material removed, and safe manual handling arrangements "
        "for lifting loads."
    ),
    keywords=uniq(
        ["207.50", "155", "52.50", "2.5", "62", "21", "83", "labour"],
        ["24.85", "7.85", "semicircle", "radius", "perimeter", "circumference", "pi"],
        ["4.38", "3.98", "39.81", "area", "volume", "0.1", "wastage", "10%", "thickness"],
        ["white card", "induction", "training", "licence", "PPE", "electrical", "tag", "ELCB",
         "first aid", "amenities", "drinking water", "housekeeping", "sun", "weather", "access"],
    ),
    band={
        "full": "Correctly calculates the labour cost, the perimeter and the volume of concrete "
                "(with 10% wastage), and describes a range of WHS factors in detail",
        "partial": "Shows correct working for some calculations and describes some relevant WHS "
                   "factors, with minor errors or omissions",
        "minimal": "Shows a relevant calculation or identifies a WHS consideration",
    })

add(2021, 19, 9,
    q=("(a) Provide TWO reasons for using cross-sectional drawings in construction planning. "
       "<strong>(2 marks)</strong>"
       "<br><br>(b) Describe the information that can be obtained from an elevation on a plan. "
       "<strong>(3 marks)</strong>"
       "<br><br>(c) Explain why construction plans and specifications need to be used together "
       "when constructing a building. <strong>(4 marks)</strong>"),
    answer=(
        "(a) A cross-sectional drawing cuts through the building, so it shows detail and "
        "information that appears on no other plan.<br><br>1. It shows how the building is "
        "<strong>constructed</strong> below and behind the finished surfaces — footing size and "
        "depth, wall thickness and construction, sub-floor design, floor construction, and roof "
        "construction including the roof pitch.<br>2. It gives the <strong>sizes and spacing of "
        "structural members</strong> (bearers, joists, studs, rafters), which the builder needs to "
        "order materials and set out the frame correctly."
        "<br><br>(b) An elevation is a straight-on view of one face of the building, so it carries "
        "the <strong>vertical</strong> information and the external appearance.<br><br>It shows "
        "vertical measurements such as the finished floor level (FFL), the finished ceiling level "
        "(FCL), and the height of window sills above floor level. It shows the overall design and "
        "shape of the building, including the roof line and pitch.<br><br>It also shows the "
        "position of doors and windows in each wall, and the finishes to the external walls — for "
        "example brickwork, cladding or render."
        "<br><br>(c) The two documents do different jobs and are incomplete on their own."
        "<br><br><strong>Plans</strong> show the overall appearance, layout and position of the "
        "building — where things go and what size they are. <strong>Specifications</strong> are a "
        "precise written description of the construction detail that the drawings cannot show: the "
        "composition and strength of concrete in footings, the species and grades of timber, brick "
        "type and mortar colour, and the colours of internal and external finishes."
        "<br><br>Used together they ensure the <strong>customer receives what they requested</strong> "
        "and that the project complies with industry standards. Builders must follow specification "
        "details such as concrete strength, steel reinforcement and timber beam grades to ensure "
        "the building is structurally stable."
        "<br><br>Both documents are also a <strong>legal requirement</strong> — they must be "
        "approved by council before any work commences, which is what ensures the safety and "
        "integrity of the building and that it minimises interference with the environment and "
        "neighbouring structures."
    ),
    keywords=uniq(
        ["footing", "wall", "thickness", "sub-floor", "floor", "roof", "pitch", "structural",
         "member", "spacing", "detail"],
        ["vertical", "height", "FFL", "floor level", "ceiling", "sill", "door", "window",
         "external", "finish", "design"],
        ["plan", "specification", "concrete", "timber", "grade", "standard", "council",
         "approval", "legal", "customer", "structural"],
    ),
    band={
        "full": "Provides TWO reasons for cross-sectional drawings, describes the features found "
                "on an elevation, and explains why plans and specifications are used together",
        "partial": "Addresses some parts with reasonable detail — for example lists a reason for "
                   "cross-sections, identifies some elevation features, or describes the "
                   "plan/specification relationship",
        "minimal": "Provides some relevant information addressing one part of the question",
    })

# ============================================================ 2022 ==============

add(2022, 16, 8,
    q=("(a) A tool is shown." +
       img("/diagrams/vet-construction_2022_Q16a_stimulus.jpg",
           "A plumb bob: a weighted cone hanging from a string") +
       "<br>Identify the tool and outline its function. <strong>(2 marks)</strong>"
       "<br><br>(b) The table shows techniques related to tools.<br>Describe each technique when "
       "using the given tool. <strong>(2 marks)</strong>"
       "<table class=\"q-table\"><tr><th>Tool</th><th>Technique</th>"
       "<th>Description of technique</th></tr>"
       "<tr><td>Chisel</td><td>Honing</td><td>&nbsp;</td></tr>"
       "<tr><td>Handsaw</td><td>Ripping</td><td>&nbsp;</td></tr></table>"
       "<br>(c) Explain considerations required before purchasing plant and equipment. "
       "<strong>(4 marks)</strong>"),
    answer=(
        "(a) The tool shown is a plumb bob. Its function is to establish a true vertical (plumb) "
        "line from a fixed overhead point. When suspended freely on a line, gravity causes the "
        "weighted bob to hang directly below the attachment point, creating a precise vertical "
        "reference. It is used to transfer vertical datum points, check the plumb of walls and "
        "columns, and set out vertical lines in building construction."
        "<br><br>(b) <strong>Chisel — honing.</strong> Honing is part of the sharpening process. "
        "After grinding restores the bevel, the edge is rubbed on an oilstone or waterstone at a "
        "consistent angle to produce a fine, keen cutting edge, and the burr is then removed by "
        "stropping.<br><br><strong>Handsaw — ripping.</strong> Ripping means cutting timber ALONG "
        "the direction of its grain, as opposed to crosscutting, which cuts across the grain. A "
        "rip saw has chisel-shaped teeth designed for that cut."
        "<br><br>(c) <strong>Cost against benefit.</strong> The purchase price must be weighed "
        "against what the item will return. The right equipment increases job efficiency and "
        "safety on site, which means fewer delays and increased profit; the wrong purchase is "
        "capital tied up in an item that does not earn.<br><strong>Frequency of use.</strong> For "
        "a one-off job, hiring is often the better choice than buying — no capital outlay, no "
        "storage and no maintenance burden.<br><strong>Ongoing maintenance.</strong> Maintenance "
        "costs both time and money and is required to prolong the life of the tool, so it must be "
        "budgeted for at the point of purchase, not after.<br><strong>Training and "
        "licensing.</strong> Some plant requires operators to hold a licence or complete training "
        "before it can be used safely and legally.<br><strong>Practical logistics.</strong> How "
        "the item will be stored and how much space it needs, how it will be transported to and "
        "from the job site, what PPE operators will need, and any registration and insurance costs."
    ),
    keywords=uniq(
        ["plumb", "vertical", "gravity", "bob", "hang", "datum", "line", "check", "wall"],
        ["hone", "sharpen", "edge", "stone", "bevel", "rip", "along", "grain", "timber", "crosscut"],
        ["cost", "efficiency", "profit", "frequency", "hire", "maintenance", "training", "licence",
         "storage", "transport", "PPE", "insurance"],
    ),
    band={
        "full": "Correctly identifies the plumb bob and its function, describes both the honing "
                "and ripping techniques, and explains a range of purchasing considerations",
        "partial": "Addresses some parts with reasonable detail — identifies the tool or its "
                   "function, describes one technique, or outlines some purchasing considerations",
        "minimal": "Provides some relevant information addressing one part of the question",
    })

add(2022, 17, 10,
    q=("(a) Outline TWO examples of how levelling information can be shown on construction plans. "
       "<strong>(2 marks)</strong>"
       "<br><br>(b) Provide reasons for the use of detail drawings in the construction industry. "
       "<strong>(2 marks)</strong>"
       "<br><br>(c) Identify each of the architectural symbols shown." +
       img("/diagrams/vet-construction_2022_Q17c_stimulus.jpg",
           "Two site-plan symbols: a rainwater tank symbol and a tree symbol drawn with a broken outline") +
       " <strong>(2 marks)</strong>"
       "<br><br>(d) Explain the purpose of a written specification when reading and interpreting "
       "plans. Support your answer with examples of information that would be included in a "
       "written specification. <strong>(4 marks)</strong>"),
    answer=(
        "(a) 1. <strong>A datum or benchmark</strong> — a fixed reference point of known height "
        "marked on the plan, from which all other levels on the site are measured.<br>2. "
        "<strong>Contour lines</strong> — lines joining points of equal height, which show the "
        "rise and fall of the land across the site.<br><br>Levels are also shown as reduced levels "
        "(RLs) and as the finished floor level (FFL) and finished ceiling level (FCL)."
        "<br><br>(b) A detail drawing enlarges a specific part of the construction to a larger "
        "scale (typically 1:20, 1:10 or 1:5) so it can be shown clearly.<br><br>They are used to "
        "clarify information that cannot be clearly illustrated on a sectional view, to provide "
        "detailed information about the assembly, joining or finishing of components, and to give "
        "precise dimensions and tolerances. They clearly identify all components in an assembly, "
        "which minimises confusion on site, and they can be used to demonstrate compliance with "
        "building regulations."
        "<br><br>(c) RWT = rainwater tank.<br><br>The second symbol — a broken (dashed) circle "
        "with a small circle at its centre — is a tree to be removed. On a site plan a feature "
        "drawn with a continuous outline is to remain, while a broken outline marks one that is "
        "to be removed or demolished; the small centre circle is the trunk."
        "<br><br>(d) A written specification is a detailed written description of the project "
        "being constructed. It must be used in conjunction with the construction plans, because "
        "its purpose is to convey the information that <em>cannot</em> be shown on a set of "
        "drawings — the drawings show size and position, the specification says what things are "
        "made of and how the work is to be done.<br><br>It provides instructions on how the work "
        "should be completed and sets out the sequence of trades, the quality of work expected, "
        "and the Australian Standards that apply.<br><br><strong>Examples of what it "
        "includes:</strong> how the site should be set up; materials to be used (brick type, "
        "weatherboards, roofing); paint colours and the number of coats; flooring materials and "
        "which rooms they go in (bathroom tiles, carpet, timber); types of lights and switches; "
        "tap fittings and bathroom fixtures; brand and model numbers of appliances; architrave and "
        "skirting size and profile; kitchen bench tops and cabinetry; and the site clean-up and "
        "final inspections."
    ),
    keywords=uniq(
        ["datum", "benchmark", "contour", "rise", "fall", "reduced level", "RL", "floor level",
         "FFL", "ceiling"],
        ["enlarge", "scale", "1:20", "1:10", "1:5", "clarify", "assembly", "joining", "dimension",
         "tolerance", "compliance", "regulation"],
        ["rainwater", "tank", "tree", "removed", "demolished", "broken"],
        ["written", "description", "conjunction", "plan", "instruction", "material", "paint",
         "coat", "fixture", "appliance", "standard", "sequence", "quality"],
    ),
    band={
        "full": "Outlines TWO examples of levelling information, provides reasons for detail "
                "drawings, correctly identifies both symbols, and explains the purpose of a "
                "written specification with examples",
        "partial": "Addresses some parts with reasonable detail — for example lists a type of "
                   "levelling information, outlines the use of detail drawings, or correctly "
                   "labels one symbol",
        "minimal": "Provides some relevant information addressing one part of the question",
    })

add(2022, 18, 11,
    q=("(a) Outline ONE work practice that would reduce the amount of material waste produced on "
       "a construction site. <strong>(2 marks)</strong>"
       "<br><br>(b) Describe the processes to be followed when organising and conducting a formal "
       "'on-site' meeting. <strong>(4 marks)</strong>"
       "<br><br>(c) A new house is to be built.<br>Describe methods that construction workers use "
       "to plan and organise their work. <strong>(5 marks)</strong>"),
    answer=(
        "(a) <strong>Train staff in the correct techniques for selecting, measuring, handling and "
        "storing materials.</strong> Most material waste on site comes from avoidable mistakes and "
        "damage — a member cut to the wrong length, sheets left out in the weather, or bricks "
        "damaged by careless handling. Training removes the cause rather than dealing with the "
        "waste afterwards.<br><br>Other effective practices include working from an accurate "
        "material list and double-checking quantity calculations so materials are not "
        "over-ordered; ordering in a timely fashion so stock is not stored on site longer than "
        "necessary; storing and transporting materials correctly; sorting waste for reuse or "
        "recycling; and confirming the most current version of the plans is being used."
        "<br><br>(b) <strong>Before the meeting.</strong> Appoint a chairperson to run it. Set and "
        "publish the time, duration and location, and circulate an agenda in advance so attendees "
        "know the purpose and can prepare.<br><br><strong>During the meeting.</strong> Follow a "
        "set procedure and work through the agenda. The chairperson controls the discussion to "
        "keep it on track and ensures everyone has the opportunity to contribute. A record of "
        "attendees and apologies is taken, and minutes are kept of what was discussed and "
        "decided.<br><br><strong>After the meeting.</strong> Distribute the minutes, record the "
        "outcomes and any actions with the person responsible, and plan the follow-up so decisions "
        "are actually carried out and can be reviewed at the next meeting."
        "<br><br>(c) <strong>Read and interpret the documentation.</strong> Construction plans and "
        "specifications are read first to establish exactly what the job requires.<br><strong>Gantt "
        "charts and construction programs</strong> set out the planned sequencing of tasks and the "
        "duration of each, so trades can be scheduled in the right order and the critical path is "
        "visible.<br><strong>Toolbox talks and site meetings</strong> inform workers about the "
        "day's conditions, any changes, and site goals or deadlines.<br><strong>Cutting lists and "
        "delivery dockets</strong> provide material quantities and sizes, and confirm what has "
        "actually arrived on site.<br><strong>Safe Work Method Statements (SWMS) and Safety Data "
        "Sheets (SDS)</strong> determine the correct procedures for using, handling and storing "
        "hazardous materials before the work starts.<br><br>Workers also use rosters, timetables "
        "and checklists, delegate duties, consult industry professionals and engage specialist "
        "trades such as plumbers and electricians, check the Building Code of Australia and "
        "council regulations, allow for the weather forecast, and refer to product manuals and "
        "technical data sheets."
    ),
    keywords=uniq(
        ["training", "measure", "handle", "storage", "damage", "material list", "over-order",
         "quantity", "recycle", "reuse", "current", "plan"],
        ["chairperson", "agenda", "time", "location", "procedure", "minutes", "attendee",
         "apolog", "outcome", "follow up", "record"],
        ["specification", "gantt", "sequence", "duration", "toolbox", "meeting", "cutting list",
         "docket", "SWMS", "SDS", "roster", "checklist", "council", "weather"],
    ),
    band={
        "full": "Outlines a work practice that reduces material waste, clearly describes the "
                "steps in running an on-site meeting, and describes a range of methods used to "
                "plan and organise work on a new house",
        "partial": "Addresses some parts with reasonable detail — lists a waste-reduction "
                   "practice, describes part of the meeting process, or outlines some planning "
                   "methods",
        "minimal": "Provides some relevant information addressing one part of the question",
    })

add(2022, 19, 6,
    q=("(a) Using the delivery cost table shown, calculate the cost to deliver 3700 kg of sand "
       "from 54 km away. <strong>(1 mark)</strong>" +
       img("/diagrams/vet-construction_2022_Q19a_stimulus.jpg",
           "A delivery-charge table with weight of sand in tonnes down the rows and distance of "
           "delivery in km across the columns") +
       "<br><br>(b) A bathroom plan is shown." +
       img("/diagrams/vet-construction_2022_Q19b_stimulus.jpg",
           "An L-shaped bathroom floor plan dimensioned 1.2 m by 1.2 m and 2.4 m by 2.7 m") +
       "<br>Calculate the number of 300 × 300 floor tiles required to tile the area shown. Allow "
       "an additional 5% for wastage. <strong>(3 marks)</strong>"
       "<br><br>(c) The total time required to complete the tiling is 8 hours 15 minutes."
       "<br>Calculate the total cost for labour based on an hourly rate of $62 per hour including "
       "GST. <strong>(2 marks)</strong>"),
    answer=(
        "(a) $450. Convert the load to the units the table uses: 3700 kg = 3.7 tonnes, which "
        "falls in the <em>3.00–4.99</em> tonne row. 54 km falls in the <em>51–70</em> km column. "
        "Reading across to that column gives a delivery cost of $450."
        "<br><br>(b) Split the L-shaped floor into two rectangles, in metres.<br><br>Upper "
        "section: 1.2 × 1.2 = <strong>1.44 m<sup>2</sup></strong><br>Lower section: 2.4 × 2.7 = "
        "<strong>6.48 m<sup>2</sup></strong><br>Total floor area = 1.44 + 6.48 = <strong>7.92 "
        "m<sup>2</sup></strong><br><br>Tile area = 0.3 × 0.3 = <strong>0.09 m<sup>2</sup></strong>"
        "<br>Tiles needed = 7.92 ÷ 0.09 = <strong>88 tiles</strong><br><br>Add 5% wastage: 88 × "
        "1.05 = 92.4, so order <strong>93 tiles</strong> — always round UP, since part of a tile "
        "cannot be bought."
        "<br><br>(c) Convert the minutes to a decimal part of an hour first:<br><br>15 ÷ 60 = "
        "<strong>0.25 hours</strong><br>Total time = 8.00 + 0.25 = <strong>8.25 hours</strong>"
        "<br><br>Labour cost = 8.25 × $62.00 = <strong>$511.50</strong><br><br>Multiplying 8.15 by "
        "the rate is the common error — 8 hours 15 minutes is 8.25 hours, not 8.15."
    ),
    keywords=uniq(
        ["450", "tonne", "3.00–4.99", "51–70", "table"],
        ["7.92", "1.44", "6.48", "0.09", "88", "93", "92.4", "area", "wastage", "round"],
        ["511.50", "8.25", "0.25", "60", "62", "labour", "hour", "minute"],
    ),
    band={
        "full": "Correctly reads the delivery table, calculates the number of tiles including "
                "wastage, and calculates the total labour cost",
        "partial": "Correctly completes two of the three calculations, or shows correct working "
                   "with minor errors",
        "minimal": "Shows a relevant calculation for one part of the question",
    })

# ============================================================ 2023 ==============

add(2023, 16, 6,
    q=("(a) A common type of saw used in construction is shown." +
       img("/diagrams/vet-construction_2023_Q16a_stimulus.jpg",
           "A drop saw (compound mitre saw) mounted on a pivot arm") +
       "<br>(i) What type of saw is this? <strong>(1 mark)</strong>"
       "<br><br>(ii) List TWO items of personal protective equipment (PPE) required when using "
       "this saw. <strong>(2 marks)</strong>"
       "<br><br>(b) Outline the advantages of using battery-powered tools and equipment. "
       "<strong>(3 marks)</strong>"),
    answer=(
        "(a)(i) Drop saw (also acceptable: mitre saw, compound mitre saw, cut-off saw). A drop "
        "saw is a power saw mounted on a pivot arm that drops down to make precise cross cuts and "
        "mitre cuts in timber."
        "<br><br>(a)(ii) 1. <strong>Safety glasses or goggles</strong> — a drop saw throws timber "
        "chips and dust directly back towards the operator's face.<br>2. <strong>Hearing "
        "protection</strong> — earmuffs or earplugs, because the blade noise is well above the "
        "level at which hearing damage occurs.<br><br>Other acceptable items are a face shield, a "
        "dust mask, protective footwear, and hair tied back or restrained so it cannot be caught "
        "by the blade."
        "<br><br>(b) <strong>Portability.</strong> Battery tools are not restricted to the length "
        "of an extension lead, so they can be set up quickly and easily in a variety of locations. "
        "They allow work on remote sites with no mains power and on new dwellings where power has "
        "not yet been connected, and they remove the need for a generator.<br><br><strong>Safety."
        "</strong> With no cords there are no trip hazards dragged across the site and no frayed "
        "leads to check, which also means no machine leads requiring testing and tagging."
        "<br><br><strong>Efficiency.</strong> Set-up is quicker — there is no cord to run out, no "
        "power point to find and no generator to start — so work begins sooner, and working "
        "outdoors and at height is easier."
    ),
    keywords=uniq(
        ["drop saw", "mitre", "compound", "sliding", "cut-off", "chop saw"],
        ["safety glasses", "goggles", "eye", "hearing", "earmuff", "earplug", "face shield",
         "dust mask", "footwear", "hair"],
        ["portable", "cord", "lead", "extension", "trip", "hazard", "generator", "remote", "power",
         "tag", "quick", "outdoor"],
    ),
    band={
        "full": "Correctly names the saw, lists TWO items of PPE required, and outlines the "
                "advantages of battery-powered tools",
        "partial": "Addresses some parts with reasonable detail — names the saw or one PPE item, "
                   "and lists some advantages",
        "minimal": "Provides some relevant information addressing one part of the question",
    })

add(2023, 17, 10,
    q=("(a) A construction worker and the employer cannot agree on the correct amount the worker "
       "should be paid.<br>How could this disagreement be resolved? <strong>(2 marks)</strong>"
       "<br><br>(b) Describe the personal attributes that the construction industry values in its "
       "workers. <strong>(3 marks)</strong>"
       "<br><br>(c) Following the renovation of a residential house, many left over substances and "
       "materials require disposal.<br>Describe the process of disposal of these substances and "
       "materials during the final stages of clean-up. <strong>(5 marks)</strong>"),
    answer=(
        "(a) Either party can seek clarification of the correct award pay rate from an "
        "independent authority rather than trying to settle it between themselves.<br><br>The "
        "worker or employer could contact a <strong>government regulator</strong> — the Fair Work "
        "Ombudsman or Fair Work Commission — to obtain a ruling on the applicable award rate."
        "<br><br>They could also seek advice from a <strong>trade union</strong> (for the worker), "
        "a <strong>professional association</strong> or an <strong>industry group</strong> such as "
        "the HIA or MBA (for the employer). If the disagreement cannot be resolved that way, it "
        "can be taken to formal dispute resolution."
        "<br><br>(b) The industry values workers who <strong>attend work regularly and are "
        "punctual</strong>, because the whole site's programme depends on trades being there when "
        "scheduled.<br><br>It values <strong>work performance</strong> — completing tasks within "
        "the scheduled timeframe, taking pride in the work, taking directions from supervisors, "
        "paying attention to detail and giving consistent service.<br><br>It values <strong>ethical "
        "behaviour</strong>: honesty, confidentiality, and a positive attitude and demeanour "
        "towards workmates and clients. Good <strong>personal presentation and grooming</strong> "
        "matter because workers represent the business in front of clients, and <strong>safe work "
        "practices</strong> are valued because an unsafe worker is a risk to everyone on site."
        "<br><br>(c) <strong>Sort first.</strong> Arrange all materials and substances into "
        "categories and place them into the correct bins, so that like material is collected "
        "together ready for its own disposal route. Anything still usable should be set aside and "
        "stored correctly for future use rather than thrown out.<br><br><strong>Timber.</strong> "
        "Treated pine offcuts must be kept separate — treated timber cannot be burnt or mulched. "
        "They go into a loose stacking bin and then to an approved disposal site."
        "<br><br><strong>Liquids and chemicals.</strong> Remaining paints, solvents and adhesives "
        "are stored in approved sealed and labelled containers and taken to a chemical waste "
        "disposal facility. They must never be poured onto the ground or into a stormwater drain."
        "<br><br><strong>Masonry and metal.</strong> Left-over bricks and rubble go to a recycling "
        "centre that accepts construction and demolition debris; metal waste is collected and "
        "taken to a metal recycling centre, where it has scrap value.<br><br>Throughout, use "
        "approved disposal collection sites and different bins for each waste stream, and keep the "
        "documentation for any regulated waste."
    ),
    keywords=uniq(
        ["award", "rate", "regulator", "fair work", "ombudsman", "union", "association",
         "industry", "HIA", "MBA", "dispute"],
        ["attendance", "punctual", "performance", "timeframe", "pride", "direction",
         "attention to detail", "ethical", "honesty", "confidentiality", "attitude",
         "presentation", "safe work"],
        ["sort", "categor", "bin", "treated", "timber", "approved", "disposal", "liquid",
         "sealed", "container", "chemical", "brick", "recycl", "metal", "reuse", "stormwater"],
    ),
    band={
        "full": "Outlines a method of resolving a pay dispute, describes the personal attributes "
                "valued in the industry, and accurately describes clean-up processes for a range "
                "of substances and materials",
        "partial": "Addresses some parts with reasonable detail — outlines a resolution method, "
                   "some valued attributes, or some disposal processes",
        "minimal": "Provides some relevant information addressing one part of the question",
    })

add(2023, 18, 10,
    q=("(a) Describe methods that can be used to limit the noise of a generator on a construction "
       "site. <strong>(3 marks)</strong>"
       "<br><br>(b) The drawing shows the plan of a house. Some features have been numbered." +
       img("/diagrams/vet-construction_2023_Q18b_stimulus.jpg",
           "A floor plan with five numbered features: a window, a sink, a stove, a toilet and a "
           "sliding door") +
       "<br>Complete the table by identifying the numbered features. <strong>(3 marks)</strong>"
       "<br><br>(c) Explain why symbols are used on construction plans. <strong>(4 marks)</strong>"),
    answer=(
        "(a) <strong>Position it away from people.</strong> Site the generator outside and well "
        "away from where workers are concentrated, and away from neighbouring boundaries. Keep it "
        "clear of walls and stacked materials that would cause the sound to echo and amplify."
        "<br><br><strong>Limit when it runs.</strong> Only operate the generator when it is "
        "actually needed, and only within the allowable construction hours set by the council."
        "<br><br><strong>Keep it in good order.</strong> Ensure the machine is operating correctly "
        "and is serviced regularly — a poorly maintained or faulty exhaust is markedly louder — "
        "and follow the correct operating procedures.<br><br>Where noise cannot be reduced far "
        "enough at the source, acoustic enclosures or barriers can be used, and workers nearby "
        "must wear hearing protection as PPE."
        "<br><br>(b) 1. Window (shown by a break in the wall with a line through it)\n2. Sink "
        "(shown by a rectangular symbol with a circle or oval)\n3. Stove/Cooktop (shown by a "
        "rectangular symbol with burner circles)\n4. Toilet (shown by a D-shape or oval attached "
        "to the wall)\n5. Sliding door (shown by a line with a track symbol parallel to the wall)"
        "<br><br>(c) <strong>They are a standard, shared language.</strong> Symbols follow a set "
        "of conventions — an Australian Standard, AS 1100 — so the same symbol means the same "
        "thing to every user in the industry, no matter who drew the plan.<br><br><strong>They "
        "are fast to read and reduce confusion.</strong> A symbol is a quick and easy way to "
        "recognise the layout and provides clarity on a crowded drawing. They indicate where "
        "things need to be built and installed, represent every element in the plan, and provide "
        "a reference back to the specifications.<br><br><strong>They overcome literacy and "
        "language barriers.</strong> A worker who does not read English fluently can still read a "
        "plan drawn in standard symbols, which matters on a multilingual site.<br><br><strong>They "
        "keep the drawing flexible.</strong> A symbol represents the function rather than a "
        "specific product — not all fixtures are the same size and shape — so adjustments can be "
        "made during fitout to suit the client's needs and the space without redrawing the plan."
    ),
    keywords=uniq(
        ["position", "away", "outside", "echo", "material", "hours", "council", "service",
         "maintain", "operating", "PPE", "hearing", "enclosure"],
        ["window", "sink", "stove", "toilet", "sliding", "door", "cooktop"],
        ["standard", "AS1100", "convention", "understood", "clarity", "confusion", "quick",
         "layout", "language", "literacy", "barrier", "specification", "fixture"],
    ),
    band={
        "full": "Describes methods to limit generator noise, correctly labels ALL five symbols on "
                "the plan, and explains why symbols are used on construction plans",
        "partial": "Addresses some parts with reasonable detail — identifies noise-limiting "
                   "methods, labels some symbols correctly, or describes why symbols are used",
        "minimal": "Provides some relevant information addressing one part of the question",
    })

add(2023, 19, 9,
    q=("(a) A builder is constructing a house that requires 15 000 bricks. A full pallet of "
       "bricks has 500 bricks.<br>How many pallets of bricks will need to be ordered? Allow for "
       "10% wastage. <strong>(2 marks)</strong>"
       "<br><br>(b) A shed is to be built on a concrete slab with concrete footings. The drawing "
       "shows the hidden detail of the edge and centre beams required for the footings of the "
       "shed." +
       img("/diagrams/vet-construction_2023_Q19b_stimulus.jpg",
           "A shed footing plan dimensioned 8500 mm by 6000 mm, showing edge and centre beams "
           "300 mm wide, with a 100 mm thick slab noted") +
       "<br>(i) Calculate how many cubic metres of concrete are required for the footings. "
       "<strong>(5 marks)</strong>"
       "<br><br>(ii) How many cubic metres of concrete are required for the slab? "
       "<strong>(2 marks)</strong>"),
    answer=(
        "(a) Add the wastage to the brick count first, then convert to pallets.<br><br>Wastage = "
        "10% × 15 000 = <strong>1500 bricks</strong><br>Total bricks = 15 000 + 1500 = <strong>16 "
        "500 bricks</strong><br><br>Pallets = 16 500 ÷ 500 = <strong>33 pallets</strong>"
        "<br><br>The builder needs to order <strong>33 pallets</strong>. Note that the division "
        "comes out exactly here; where it does not, always round UP, because a part pallet still "
        "has to be ordered as a whole one."
        "<br><br>(b)(i) The footings are 300 mm × 300 mm, i.e. 0.3 m × 0.3 m in section. The "
        "drawing shows FIVE beams: two running the 8500 length, and THREE running the 6000 width "
        "— the two edge beams and a centre beam.<br><br>Long beams (8500 direction), taken full "
        "length: 2 × 8.5 = 17 m. Volume = 17 × 0.3 × 0.3 = 1.53 m³.<br>Cross beams (6000 "
        "direction): shorten each by the 300 mm width of a long beam at each end so the overlaps "
        "are not counted twice — 6.0 − (2 × 0.3) = 5.4 m each, and 3 × 5.4 = 16.2 m. Volume = 16.2 "
        "× 0.3 × 0.3 = 1.46 m³.<br><br>Total concrete = 1.53 + 1.46 = 2.99 m³.<br><br>The centre "
        "beam is the part most often missed. Working from the outer perimeter alone — 2 × (8.5 + "
        "6) = 29 m, giving 29 × 0.3 × 0.3 = 2.61 m³ — omits it and also double-counts the four "
        "corners, so it is not the required answer."
        "<br><br>(b)(ii) This part is the <strong>slab</strong> only, not the footings. The note "
        "on the drawing gives the slab thickness as 100 mm.<br><br>Convert the plan dimensions to "
        "metres: 8500 mm = 8.5 m, 6000 mm = 6 m, and 100 mm = 0.1 m.<br><br>Volume = length × "
        "width × thickness<br>= 8.5 × 6 × 0.1 = <strong>5.1 m<sup>3</sup></strong><br><br>"
        "Converting the millimetre dimensions on the plan to metres before multiplying is the "
        "step the mark depends on."
    ),
    keywords=uniq(
        ["33", "16 500", "16500", "1500", "10%", "wastage", "500", "pallet"],
        ["2.99", "1.53", "1.46", "5.4", "16.2", "centre beam", "edge beam", "0.3", "volume",
         "footing"],
        ["5.1", "8.5", "0.1", "length", "width", "thickness", "slab", "metre", "convert"],
    ),
    band={
        "full": "Correctly calculates the number of pallets, the concrete for the footings "
                "(including the centre beam), and the concrete for the slab",
        "partial": "Correctly completes two of the three calculations, or shows correct working "
                   "with minor errors",
        "minimal": "Shows a relevant calculation for one part of the question",
    })

# ============================================================ 2024 ==============

add(2024, 16, 6,
    q=("(a) A tool is shown." +
       img("/diagrams/vet-construction_2024_Q16a_stimulus.jpg", "A spirit level with two vials") +
       "<br>Identify this hand tool and outline TWO uses for it. <strong>(3 marks)</strong>"
       "<br><br>(b) A belt sander is shown." +
       img("/diagrams/vet-construction_2024_Q16b_stimulus.jpg",
           "A 240-volt electric belt sander") +
       "<br>Describe the pre-operational safety checks needed before using a 240-volt belt "
       "sander. <strong>(3 marks)</strong>"),
    answer=(
        "(a) The tool is a spirit level. Uses: (1) Checking that horizontal surfaces (floors, "
        "window sills, formwork) are level — the bubble in the horizontal vial sits centred "
        "between the lines when the surface is true level. (2) Checking that vertical elements "
        "(walls, door frames, columns) are plumb — the bubble in the vertical vial sits centred "
        "when the surface is truly vertical. Can also be used as a straight edge for marking "
        "lines across flat surfaces."
        "<br><br>(b) Pre-operation safety checks for a 240V belt sander include: (1) Inspect the "
        "power cord for cuts, fraying, kinking or damage to the insulation — damaged cords must "
        "be removed from service. (2) Check the current test-and-tag label to confirm the tool "
        "has been recently inspected and is electrically safe for use. (3) Ensure all guards are "
        "correctly in place and secure — particularly the belt guard that covers the sanding "
        "belt in motion. (4) Check the sanding belt for correct installation, damage and tension "
        "— an incorrectly fitted belt can break and cause injury. (5) Inspect the dust bag/"
        "extraction port and ensure it is connected and functioning to control dust hazards."
    ),
    keywords=uniq(
        ["spirit level", "level", "plumb", "horizontal", "vertical", "bubble", "wall", "frame",
         "floor"],
        ["cord", "tag", "guard", "belt", "dust", "bag", "inspection", "damage", "safe",
         "electrical"],
    ),
    band={
        "full": "Correctly names the spirit level and outlines TWO uses, and describes a range of "
                "safety checks before using a belt sander",
        "partial": "Names the tool or outlines one use, and outlines some safety checks",
        "minimal": "Provides some relevant information addressing one part of the question",
    })

add(2024, 17, 10,
    q=("(a) Identify ONE advantage and ONE disadvantage of using a laser measuring tool. "
       "<strong>(2 marks)</strong>"
       "<br><br>(b) Outline how incorrect measurements can affect a construction project. "
       "<strong>(3 marks)</strong>"
       "<br><br>(c) Describe how engineering controls can be used to manage a hot and dusty work "
       "environment. <strong>(5 marks)</strong>"),
    answer=(
        "(a) <strong>Advantage:</strong> it reduces the time needed to complete a measurement — "
        "one person can measure a long distance instantly, where a tape would need two people or "
        "repeated set-ups. Laser tools are also portable, easy to use, and can hold and recall "
        "stored measurements.<br><br><strong>Disadvantage:</strong> the battery periodically "
        "needs replacing or recharging, so the tool can fail mid-job. They are also expensive "
        "compared with a tape, need to be maintained and calibrated, require a clear line of "
        "sight to the target, and generally measure internal dimensions only."
        "<br><br>(b) <strong>Materials and cost.</strong> Incorrect measurements change the "
        "quantity of material ordered. Ordering too little means reordering, with additional "
        "delivery costs and a wait; ordering too much means paying for material that is wasted. "
        "Either way the overall cost rises for both the builder and the customer."
        "<br><br><strong>Time.</strong> Reordering or remaking components delays project "
        "completion, and a delay to one trade pushes back every trade scheduled after it."
        "<br><br><strong>Quality and safety.</strong> Components cut to the wrong size do not fit "
        "properly, which produces a poor finish, may require the work to be pulled down and "
        "redone, and in structural work can compromise the strength and safety of the building."
        "<br><br>(c) Engineering controls sit above administrative controls and PPE in the risk "
        "control hierarchy because they modify the physical conditions themselves rather than "
        "relying on workers to behave differently.<br><br><strong>Ventilation.</strong> Installing "
        "specialised ventilation and extraction systems regulates both temperature and dust "
        "levels. They provide adequate air exchange, removing hot and contaminated air and "
        "replacing it with cooler, cleaner air. This cools the environment and prevents dust from "
        "accumulating, significantly reducing the respiratory risk to workers."
        "<br><br><strong>Dust suppression at the source.</strong> Water spray systems and on-tool "
        "water suppression capture dust as it is generated, rather than after it has become "
        "airborne. On-tool dust extraction fitted to concrete saws and grinders does the same job "
        "by vacuum.<br><br><strong>Cooling.</strong> Strategic placement of cooling units, fans or "
        "evaporative coolers in areas where workers are concentrated mitigates the heat risk, and "
        "shade structures or temporary roofing remove the radiant heat load.<br><br>"
        "<strong>Isolation and enclosure.</strong> Enclosing or screening a dusty process keeps "
        "the dust within a defined area so the rest of the site is not affected.<br><br>Combined, "
        "these controls reduce the hazard for everyone on site at once, which is why they are "
        "preferred over relying on respirators and rest breaks alone — though those remain as "
        "supporting administrative controls and PPE."
    ),
    keywords=uniq(
        ["time", "quick", "one person", "portable", "store", "battery", "recharge", "expensive",
         "maintain", "line of sight", "internal"],
        ["material", "quantity", "order", "reorder", "cost", "delivery", "waste", "delay",
         "completion", "fit", "rework", "quality", "safety"],
        ["engineering", "ventilation", "extraction", "air", "exchange", "dust", "respiratory",
         "water", "spray", "suppression", "on-tool", "cooling", "fan", "shade", "enclosure",
         "hierarchy"],
    ),
    band={
        "full": "Identifies an advantage and disadvantage of a laser tool, outlines how incorrect "
                "measurements affect a project, and describes in detail how engineering controls "
                "manage a hot and dusty environment",
        "partial": "Addresses some parts with reasonable detail — identifies an advantage or "
                   "disadvantage, identifies consequences of incorrect measurement, or outlines "
                   "some engineering controls",
        "minimal": "Provides some relevant information addressing one part of the question",
    })

add(2024, 18, 10,
    q=("(a) Outline the importance of feedback in the communication process when working with "
       "clients/customers. <strong>(3 marks)</strong>"
       "<br><br>(b) Why is it important to correctly store reusable materials on a building "
       "site? <strong>(3 marks)</strong>"
       "<br><br>(c) Explain the factors that need to be considered by a builder during the "
       "planning and preparation stage of a construction project. <strong>(4 marks)</strong>"),
    answer=(
        "(a) Feedback is what closes the communication loop. It allows both the sender and the "
        "receiver to confirm that a message has actually been received and understood, rather "
        "than assumed.<br><br>It <strong>ensures the correct message has been delivered</strong> "
        "— the client restating what they want, or the builder confirming a variation in writing, "
        "shows whether the two parties share the same understanding. It acts as the bridge "
        "between sender and receiver, providing clarification and validation.<br><br>It "
        "<strong>surfaces problems early</strong>, so issues can be addressed while they are "
        "still cheap to fix rather than after the work is built. It also supports continuous "
        "improvement, since a client's feedback on finished work tells the builder what to do "
        "differently next time — and it builds the client's confidence and the business's "
        "reputation."
        "<br><br>(b) <strong>Availability and efficiency.</strong> Correctly stored materials are "
        "easy to access and ready for use, which reduces delays and improves efficiency — "
        "workers are not hunting for material or waiting for a replacement.<br><br><strong>Cost."
        "</strong> Correct storage prevents damage, so materials do not have to be bought twice. "
        "Correct stacking maintains the integrity of the material — stacking timber flat and "
        "evenly supported stops lengths twisting or bowing — and correct packing and strapping "
        "extend the usable life of the material.<br><br><strong>Sustainability.</strong> "
        "Materials that can be reused many times reduce the demand for new materials, conserving "
        "resources and reducing waste sent to landfill. That saves money and lessens the "
        "environmental impact of the project.<br><br><strong>Safety.</strong> Correctly stacked "
        "and stored material also cannot topple or collapse onto workers, and keeps access ways "
        "clear."
        "<br><br>(c) <strong>Labour.</strong> Estimate the number and type of workers needed at "
        "each stage, so the correct trades are on site as required — too few causes delays, too "
        "many causes congestion and idle time.<br><br><strong>Timing.</strong> Set realistic "
        "timelines, stage completion dates and deadlines for each part of the process. This "
        "provides a map of what should be completed and when, and keeps the build moving "
        "smoothly.<br><br><strong>Resources.</strong> Ensure the correct tools, equipment, "
        "materials and consumables are ready and on site when needed, planned and sequenced "
        "efficiently. Optimum resource use also means not wasting money on plant sitting idle — "
        "hiring it for the window it is actually needed.<br><br><strong>Risk.</strong> Thorough "
        "planning involves identifying hazards and constraints in advance — site access, ground "
        "conditions, weather, services location, working at heights — and putting controls in "
        "place before work starts.<br><br><strong>Compliance and cost.</strong> Confirm "
        "approvals, the Building Code of Australia and council requirements, and prepare "
        "accurate estimates and a budget so the project is financially viable."
    ),
    keywords=uniq(
        ["confirm", "understand", "message", "sender", "receiver", "clarif", "validat", "problem",
         "issue", "improvement", "client", "expectation"],
        ["access", "ready", "delay", "efficiency", "damage", "cost", "stack", "twist", "bow",
         "strap", "reuse", "sustainab", "waste", "safety"],
        ["worker", "labour", "estimate", "timeline", "deadline", "stage", "tool", "equipment",
         "material", "sequence", "resource", "idle", "risk", "hazard", "weather", "approval",
         "council", "budget", "cost"],
    ),
    band={
        "full": "Outlines the importance of feedback with clients, explains why correct storage "
                "of reusable materials matters, and clearly explains the factors considered "
                "during planning and preparation",
        "partial": "Addresses some parts with reasonable detail — identifies the importance of "
                   "feedback, outlines storage importance, or describes some planning factors",
        "minimal": "Provides some relevant information addressing one part of the question",
    })

add(2024, 19, 9,
    q=("(a) Calculate the perimeter of the shape shown (which includes a right-angle triangle "
       "section)." +
       img("/diagrams/vet-construction_2024_Q19a_stimulus.jpg",
           "An irregular shape dimensioned 8 m, 6 m, 3 m and 4 m, with a right-angle triangle "
           "section, not to scale") +
       " <strong>(2 marks)</strong>"
       "<br><br>(b) A concrete slab with a circular hole in the middle is shown." +
       img("/diagrams/vet-construction_2024_Q19b_stimulus.jpg",
           "A rectangular concrete slab 8 m by 6 m, 150 mm thick, with a circular hole of 1 m "
           "radius in the middle") +
       "<br>Calculate the volume of the concrete slab. <strong>(3 marks)</strong>"
       "<br><br>(c) The ratio for concrete is 3 parts aggregate, 2 parts sand and 1 part cement "
       "(3 : 2 : 1).<br>Calculate the volume of sand required for a concrete slab with a volume "
       "of 11.6 m<sup>3</sup>. <strong>(2 marks)</strong>"
       "<br><br>(d) The delivery cost for aggregate is $1.18/km per tonne.<br>Calculate the "
       "delivery cost of 8 tonnes to a site 13 km away. <strong>(2 marks)</strong>"),
    answer=(
        "(a) Calculate the hypotenuse using Pythagoras: √(3² + 4²) = √(9 + 16) = √25 = 5 m"
        "<br><br>Sum all sides: 8 + 6 + 3 + 4 + 5 = 26 m<br><br>(Dimensions vary with plan — show "
        "all working including Pythagoras theorem)"
        "<br><br>(b) Slab volume = 8 × 6 × 0.15 = 7.2 m³<br><br>Circular hole volume = π × r² × "
        "depth = π × 1² × 0.15 = 0.471 m³<br><br>Net concrete volume = 7.2 − 0.471 = 6.729 m³ ≈ "
        "6.73 m³"
        "<br><br>(c) Add the ratio parts to find how many parts make the whole:<br><br>3 + 2 + 1 "
        "= <strong>6 parts</strong><br><br>One part = 11.6 ÷ 6 = <strong>1.93 m<sup>3</sup></strong>"
        "<br><br>Sand is 2 parts, so sand = 1.93 × 2 = <strong>3.86 m<sup>3</sup></strong>"
        "<br><br>Dividing by 2 instead of by the total of 6 parts is the common error."
        "<br><br>(d) The rate is per kilometre AND per tonne, so multiply by both.<br><br>8 "
        "tonnes × $1.18 = <strong>$9.44</strong> (cost per kilometre)<br>$9.44 × 13 km = "
        "<strong>$122.72</strong><br><br>The order does not matter — 8 × 1.18 × 13 gives the "
        "same $122.72 — but both quantities must be used. Multiplying by only the distance or "
        "only the tonnage is the common error."
    ),
    keywords=uniq(
        ["pythagoras", "26", "hypotenuse", "5", "perimeter", "sides"],
        ["7.2", "0.471", "6.73", "pi", "radius", "circle", "slab", "0.15"],
        ["3.86", "1.93", "6 parts", "6", "ratio", "sand", "2 parts", "11.6"],
        ["122.72", "9.44", "1.18", "8", "13", "tonne", "km", "delivery"],
    ),
    band={
        "full": "Correctly calculates the perimeter, the net slab volume, the sand volume and the "
                "delivery cost",
        "partial": "Correctly completes two or three of the four calculations, or shows correct "
                   "working with minor errors",
        "minimal": "Shows a relevant calculation for one part of the question",
    })

# ============================================================ 2025 ==============

add(2025, 16, 5,
    q=("A tool is shown." +
       img("/diagrams/vet-construction_2025_Q16_stimulus.jpg", "A wood router") +
       "<br><br>(a) Outline a suitable use for this tool. <strong>(2 marks)</strong>"
       "<br><br>(b) Describe TWO settings or adjustments that may be required before using this "
       "tool. <strong>(3 marks)</strong>"),
    answer=(
        "(a) The tool shown is a router. A suitable use for this tool is to create a rebate (a "
        "step-shaped recess) along the edge of a timber board for joint construction, such as a "
        "rebate joint used when making drawers or cabinets. Other suitable uses include: edge "
        "profiling (decorative shaping of timber edges), cutting grooves and housings in timber, "
        "flush/pattern cutting using a template, and mortising."
        "<br><br>(b) Two settings or adjustments required before using a router are:<br><br>1. "
        "Depth of cut: The depth gauge on the router is adjusted to set how deeply the cutter "
        "will enter the timber. This determines the depth of the rebate, groove or profile being "
        "cut and must be set precisely before beginning the cut.<br><br>2. Width of cut: The side "
        "fence (parallel guide) position is adjusted to control the distance from the edge of the "
        "timber to the cutting position, determining the width of the cut. Other acceptable "
        "adjustments include: selecting the appropriate cutter profile/shape for the operation, "
        "and setting the spindle speed (RPM) to suit the material and cutter diameter being used."
    ),
    keywords=uniq(
        ["router", "rebate", "groove", "housing", "edge", "profile", "joint", "mortise",
         "pattern", "timber"],
        ["depth", "gauge", "width", "fence", "speed", "rpm", "cutter", "adjust", "setting"],
    ),
    band={
        "full": "Outlines a suitable use for the router and describes TWO settings or "
                "adjustments required before using it",
        "partial": "Provides some relevant information about the tool's use or a setting",
        "minimal": "Provides some relevant information addressing one part of the question",
    })

add(2025, 17, 10,
    q=("(a) Outline considerations when selecting an abrasive for use with electric sanders. "
       "<strong>(2 marks)</strong>"
       "<br><br>(b) Describe TWO indicators which show that a tool is not performing efficiently, "
       "or has a fault. <strong>(3 marks)</strong>"
       "<br><br>(c) Explain how builders can protect their tools and equipment from theft and "
       "damage on site. <strong>(5 marks)</strong>"),
    answer=(
        "(a) When selecting an abrasive for an electric sander, key considerations include: the "
        "grit size — coarser grits (e.g. 40–80 grit) for initial material removal and fine grits "
        "(e.g. 180–240 grit) for final finishing; the material being sanded — hardwoods require "
        "different abrasives to softwoods; the abrasive type — silicon carbide, aluminium oxide "
        "or garnet each suit different materials and applications; and the backing type — paper, "
        "cloth or Velcro/hook-and-loop backing depending on the sander type and the required "
        "durability of the abrasive sheet."
        "<br><br>(b) Two indicators that a tool is not performing efficiently or has a fault are:"
        "<br><br>1. Smoke or burning smell: If a power tool produces smoke or a burning smell "
        "during operation, this indicates the motor is overloading, overheating, or that there is "
        "an electrical fault. This is a serious safety indicator and the tool must be immediately "
        "switched off and removed from service.<br><br>2. Excessive vibration or unusual noise: A "
        "tool that vibrates more than normal, produces grinding noises, rattles or makes "
        "unfamiliar sounds indicates worn bearings, a loose or damaged component, or an "
        "unbalanced cutting tool. These symptoms indicate a fault that could lead to failure or "
        "injury. Other valid indicators include: slower operation than normal, poor results/"
        "finish quality, failure to start, blockages, or excessive heat."
        "<br><br>(c) Builders can implement a range of strategies to protect their tools and "
        "equipment from both theft and physical damage on site.<br><br>To prevent theft, builders "
        "should use secure, lockable storage such as purpose-built toolboxes, steel job site "
        "boxes or shipping containers with heavy-duty padlocks and hasp-and-staple fixings. A "
        "sign-in/sign-out register should be maintained so tool location is always known. The "
        "site perimeter should be secured with fencing, gates and padlocks to restrict "
        "unauthorised access, and security lighting and CCTV cameras installed to deter theft and "
        "provide evidence if items are stolen. High-value items such as laser levels and power "
        "tools should be engraved with identification numbers or asset tags.<br><br>To prevent "
        "damage, tools should be stored in dedicated racks or cases to prevent them from being "
        "knocked or dropped. Power tools must be stored away from moisture, dust and extreme "
        "temperatures that can damage electronics and motors. Tools should be returned to storage "
        "after each use rather than left lying on site where they can be driven over or stepped "
        "on. Protective covers and blade guards should always be in place during storage and "
        "transport."
    ),
    keywords=uniq(
        ["grit", "coarse", "fine", "material", "timber", "aluminium oxide", "silicon carbide",
         "backing", "cloth", "paper"],
        ["smoke", "vibration", "noise", "overheating", "bearing", "fault", "slow", "poor",
         "heat", "burning"],
        ["lockable", "secure", "container", "sign-in", "fence", "lighting", "camera", "cctv",
         "rack", "cover", "guard", "identify", "register", "storage"],
    ),
    band={
        "full": "Outlines abrasive-selection considerations, describes TWO fault indicators, and "
                "provides a thorough explanation of how builders protect tools from theft and "
                "damage",
        "partial": "Addresses some parts with reasonable detail — outlines a consideration, an "
                   "indicator, or some protection strategies",
        "minimal": "Provides some relevant information addressing one part of the question",
    })

add(2025, 18, 9,
    q=("(a) List the type of information that can be found in a building specification. "
       "<strong>(2 marks)</strong>"
       "<br><br>(b) Identify the meaning of the following symbols or abbreviations that are "
       "found on construction drawings." +
       img("/diagrams/vet-construction_2025_Q18b_stimulus.jpg",
           "A symbol/abbreviation table with HW, RWP and a horizontal sliding window symbol") +
       " <strong>(3 marks)</strong>"
       "<br><br>(c) Describe the range of information that can be found on a floor plan. "
       "<strong>(4 marks)</strong>"),
    answer=(
        "(a) A building specification contains detailed written information that complements the "
        "drawings, including: the species and grade of timber to be used; brick type, mortar mix "
        "ratios and quality; the composition and strength of concrete in footings and slabs; "
        "paint colours, brands and number of coats; PC (Prime Cost) items such as hot water "
        "systems, tapware, baths, appliances and light fittings; floor and wall tile types and "
        "fixing methods; roofing material types and fixing requirements; and waterproofing "
        "membrane specifications."
        "<br><br>(b) HW = Hot Water (refers to the hot water supply pipe or hot water service "
        "connection on plumbing/services drawings)\nRWP = Rainwater Pipe (the vertical downpipe "
        "that carries rainwater from the roof gutters to the stormwater drainage system)\n"
        "Horizontal sliding window symbol (two rectangles with arrows pointing toward each other) "
        "= a window where the sashes slide horizontally past each other to open"
        "<br><br>(c) A floor plan provides a comprehensive range of information about the "
        "internal layout and dimensions of a building. It shows the overall building footprint "
        "and dimensions, including the layout and names of all rooms and spaces (bedrooms, "
        "kitchen, bathroom, living areas). Wall locations and thicknesses are shown, along with "
        "the positions of all doors (and their swing direction) and windows. Structural elements "
        "such as columns and loadbearing walls are identified. Fixed appliances and fixtures are "
        "shown including kitchens (sink, stove, dishwasher), bathrooms (bath, shower, toilet, "
        "vanity) and laundries. Staircase location and direction of travel (with step count) are "
        "indicated. Built-in joinery such as wardrobes, pantries and linen cupboards are shown. "
        "Some floor plans also indicate floor coverings, ceiling heights, roof outline and eaves "
        "overhang, and the locations of downpipes."
    ),
    keywords=uniq(
        ["timber", "concrete", "brick", "mortar", "paint", "pc items", "tapware", "appliance",
         "specification", "material", "colour", "finish"],
        ["hot water", "HW", "rainwater pipe", "RWP", "sliding", "window", "horizontal",
         "downpipe"],
        ["room", "dimension", "wall", "door", "window", "fixture", "toilet", "kitchen", "stair",
         "footprint", "layout", "appliance", "structure"],
    ),
    band={
        "full": "Lists information found in a building specification, correctly identifies THREE "
                "symbols or abbreviations, and describes a range of information found on a floor "
                "plan",
        "partial": "Addresses some parts with reasonable detail — lists some specification "
                   "information, identifies one or two symbols, or outlines some floor-plan "
                   "information",
        "minimal": "Provides some relevant information addressing one part of the question",
    })

print("done, %d groups total" % len(MERGES))


def official_marks(key, year, base):
    parts = key["papers"][str(year)]
    return sum(p["marks"] for p in parts if p["question"] == base)


def main():
    write = "--write" in sys.argv

    bank = json.load(io.open(BANK_PATH, encoding="utf-8"))
    key = json.load(io.open(KEY_PATH, encoding="utf-8"))
    # Read the pre-merge 72-entry snapshot (subjects/vet-construction.json may already
    # have been merged by an earlier run of this script) so re-running is idempotent.
    backup_path = os.path.join(REPO, "vet_bank_dump.json")
    if os.path.exists(backup_path):
        written = json.load(io.open(backup_path, encoding="utf-8"))
    else:
        written = bank["writtenQuestions"]

    # Validate every merge's marks against the official key before touching anything.
    bad = []
    for (year, qnum), entry in sorted(MERGES.items()):
        official = official_marks(key, year, qnum)
        if entry["marks"] != official:
            bad.append("%s Q%s: entry has %d marks, official is %d" %
                       (year, qnum, entry["marks"], official))
    if bad:
        sys.exit("Marks mismatch, aborting:\n  " + "\n  ".join(bad))
    print("All %d merged entries reconcile against the official key." % len(MERGES))

    # Group existing bank entries by (year, base qnum) to find what each merge replaces.
    def base_of(qnum):
        s = str(qnum)
        i = 0
        while i < len(s) and s[i].isdigit():
            i += 1
        return int(s[:i]) if i else None

    groups = {}
    for idx, q in enumerate(written):
        b = base_of(q["qNum"])
        groups.setdefault((q["year"], b), []).append(idx)

    new_written = []
    consumed = set()
    replaced_report = []
    for i, q in enumerate(written):
        if i in consumed:
            continue
        key_tuple = (q["year"], base_of(q["qNum"]))
        if key_tuple in MERGES:
            idxs = groups[key_tuple]
            consumed.update(idxs)
            old_qnums = [written[j]["qNum"] for j in idxs]
            old_marks_sum = sum(written[j]["marks"] for j in idxs)
            replaced_report.append(
                "%s Q%s: %d entries %s (marks %d) -> 1 entry (marks %d)" %
                (key_tuple[0], key_tuple[1], len(idxs), old_qnums, old_marks_sum,
                 MERGES[key_tuple]["marks"]))
            new_written.append(MERGES[key_tuple])
        else:
            new_written.append(q)
            consumed.add(i)

    print("\n".join(replaced_report))
    print("\nBank written count: %d -> %d" % (len(written), len(new_written)))

    if not write:
        print("\nDry run only. Re-run with --write to apply.")
        return

    bank["writtenQuestions"] = new_written
    with io.open(BANK_PATH, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(bank, indent=2, ensure_ascii=False) + "\n")
    print("\nWrote %s" % BANK_PATH)


if __name__ == "__main__":
    main()
