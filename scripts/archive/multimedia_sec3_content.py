# -*- coding: utf-8 -*-
"""Stage 4 content for Multimedia Section III (Question 16, 2020-2025).

Stems are NESA's own wording from the exam papers. Model answers are authored
from NESA's committed sample answers in data/answer-key/written/multimedia.json
(the marking guidelines are never re-read - CLAUDE.md s10). Band descriptors are
NOT written here: they are generated verbatim from that same key's criteria rows
by the build script, using the standing collapse rule.
"""

# label -> dict(prompt, answer, keywords, minKeywords)
CONTENT = {

# ─────────────────────────────────────────────────────────── 2020
2020: dict(
  stem="A multimedia company is considering moving to a new location.",
  parts=[
    dict(
      label="(a)", marks=5,
      q="Describe environmental factors the company needs to consider when selecting a new site.",
      answer=(
        "Several environmental factors affect the choice of a new site.<br><br>"
        "<strong>Impact on the natural environment.</strong> An environmental impact statement may be "
        "required before approval is given. If it shows the site would harm endangered species or a "
        "sensitive habitat, the company may need to select a different location or adopt strategies "
        "that reduce that impact.<br><br>"
        "<strong>Transportation facilities.</strong> Receiving raw materials and distributing finished "
        "products requires access to arterial roads, rail and air or sea ports. Locating close to these "
        "distribution networks shortens journeys and so lowers fuel use and emissions. Public transport "
        "access for the workforce matters for the same reason - fewer cars on the road means fewer "
        "emissions.<br><br>"
        "<strong>Resource availability.</strong> The site must give reliable access to the power, "
        "materials and processes the company needs, and ideally support alternative resources such as "
        "solar generation.<br><br>"
        "<strong>Waste management and pollution.</strong> The site must allow waste to be stored, "
        "collected and recycled properly, and must limit the noise, light and air pollution affecting "
        "the surrounding population.<br><br>"
        "<strong>Legislative requirements.</strong> Local council, state and federal regulations govern "
        "land use, emissions and waste disposal, and the site must comply with all three.<br><br>"
        "<strong>Land and geographical factors.</strong> Land costs and availability, drainage, flooding "
        "risk and climate all affect suitability, as does the rehabilitation of a previously used "
        "commercial site."
      ),
      keywords=[
        "environmental impact statement", "endangered species", "habitat", "transportation facilities",
        "arterial roads", "emissions", "workforce", "public transport", "resource availability",
        "alternative resources", "waste management", "pollution", "surrounding population",
        "legislative requirements", "land costs", "geographical", "rehabilitation", "recycled",
      ],
      minKeywords=7,
    ),
    dict(
      label="(b)", marks=10,
      q="Discuss strategies the company could implement to minimise its continuing environmental impact.",
      answer=(
        "A range of strategies can reduce the company's ongoing environmental impact, and each carries "
        "trade-offs.<br><br>"
        "<strong>Energy.</strong> Switching to green energy such as solar generation, storing surplus in "
        "batteries for night use, and shifting heavy processing to off peak electricity all cut the "
        "carbon footprint. Replacing equipment with better energy rating alternatives - LED lighting, "
        "motion sensing controls and LED monitors - lowers consumption further. Against this, the initial "
        "investment is high, although running costs fall over time.<br><br>"
        "<strong>Materials and waste.</strong> Recycling and reusing consumables, moving to a paperless "
        "office, and providing recycling bins reduce landfill. A metal buy back or take-back scheme lets "
        "old products be collected and reprocessed. The drawback is that sorting and collection require "
        "staff time and space.<br><br>"
        "<strong>Transport.</strong> Planning delivery routes efficiently, maintaining vehicles, limiting "
        "night operations near communities and using fuel saving measures reduce both emissions and "
        "noise. Some of these constrain scheduling flexibility.<br><br>"
        "<strong>Policy and compliance.</strong> The company should develop an environmental policy "
        "showing its commitment to the relevant regulations and laws. Environmental policy affects the "
        "business because legislation compels organisations to change operational procedures and "
        "equipment, which costs money in the short term but reduces the risk of penalties and improves "
        "the company's public reputation.<br><br>"
        "On balance, the measures with the strongest long-term effect - renewable energy and equipment "
        "replacement - are the most expensive to start, while low-cost measures such as recycling and "
        "a paperless office deliver smaller but immediate gains, so a staged combination is the most "
        "practical approach."
      ),
      keywords=[
        "green energy", "solar", "batteries", "off peak electricity", "energy rating", "led",
        "motion sensing", "recycling", "reusing", "paperless office", "buy back", "landfill",
        "routes", "fuel saving", "emissions", "noise", "environmental policy", "regulations",
        "legislation", "carbon footprint", "penalties", "reputation",
      ],
      minKeywords=9,
    ),
  ],
  band=dict(
    full="Describes a range of environmental factors relevant to selecting a new site, and discusses strategies for reducing the company's continuing impact with points for and/or against each.",
    partial="Covers both parts but with uneven depth - typically several site factors described soundly and strategies listed without weighing them, or strategies discussed well from a limited set of site factors.",
    minimal="Provides some relevant information about environmental factors or strategies without describing or discussing them in the terms the question asks for.",
  ),
),

# ─────────────────────────────────────────────────────────── 2021
2021: dict(
  stem=("A company has experienced a significant change in demand for its products. Consequently, "
        "it is modifying operations to adapt to these changes."),
  parts=[
    dict(
      label="(a)", marks=5,
      q="Describe the Industrial Relations issues that could occur as a result of these modifications.",
      answer=(
        "Modifying operations raises a number of industrial relations issues.<br><br>"
        "<strong>If the company downsizes,</strong> the change can lead to job losses and retrenchments. "
        "These require redundancy packages and union negotiation over individual contracts and group "
        "negotiated contracts. The retrenchment process must be conducted in an equitable fashion and in "
        "accordance with government legislation and policies that protect employees' rights and job "
        "security.<br><br>"
        "<strong>If the company expands,</strong> recruitment of new staff becomes necessary. Existing "
        "staff may be retained and upskilled rather than replaced, which raises questions about pay "
        "rates, classifications and multi-skilling.<br><br>"
        "<strong>Across both cases,</strong> unions play a major role in negotiating wages and "
        "conditions, and equal employment opportunity legislation applies both to hiring new employees "
        "and to the promotion of existing staff. Consultation with the workforce about changes to rosters, "
        "duties and work practices is also an industrial relations obligation rather than a courtesy."
      ),
      keywords=[
        "downsize", "job losses", "retrenchments", "redundancy", "union", "individual contracts",
        "group negotiated contracts", "equitable", "legislation", "employees' rights", "recruitment",
        "upskilled", "multi-skilling", "equal employment opportunity", "promotion", "consultation",
        "work practices",
      ],
      minKeywords=7,
    ),
    dict(
      label="(b)", marks=10,
      q="Explain career and training opportunities that could be available as a result of these modifications.",
      answer=(
        "The change in demand creates opportunities for employees, and the form they take depends on "
        "whether the company expands or downsizes.<br><br>"
        "<strong>If the company expands.</strong> Employees gain opportunities to train and further "
        "develop their knowledge and skills in the industry they work in. Where new machinery or "
        "technology is introduced, the company must ensure all affected employees are trained to use it "
        "safely and effectively, so the change itself generates training. Training may be delivered "
        "through TAFE or university courses, through outside agencies, through in-house training, or as "
        "on the job training while employees continue working. Multi-skilling lets staff move between "
        "roles as demand shifts, which benefits the employee's prospects and the company's flexibility. "
        "Expansion also opens management opportunities, leadership roles, internships and traineeships, "
        "and the recruitment of new staff to meet demand.<br><br>"
        "<strong>If the company downsizes.</strong> Employees can be retrained into roles the company "
        "still needs, reducing the number of forced redundancies. Voluntary redundancies may be offered. "
        "Employees who regularly undertake training in new courses are less likely to be made redundant "
        "because they are useful across more of the business. Part time or casual work and a change of "
        "management structure can preserve employment where full-time roles cannot be sustained, and "
        "government subsidy may support retraining.<br><br>"
        "In both cases the link is the same: training raises an employee's value to the business, which "
        "improves job security and widens career paths."
      ),
      keywords=[
        "train", "knowledge and skills", "new machinery", "tafe", "university", "outside agencies",
        "in-house training", "on the job training", "multi-skilling", "management opportunities",
        "leadership", "traineeships", "recruitment", "retrained", "voluntary redundancies",
        "part time", "casual", "government subsidy", "management structure", "job security",
        "career paths",
      ],
      minKeywords=9,
    ),
  ],
  band=dict(
    full="Describes the industrial relations issues arising from the modified operations, and explains the career and training opportunities they create, linking each strategy to its outcome for the employee or the business.",
    partial="Covers both parts but unevenly - typically industrial relations issues identified rather than described, or training opportunities listed without explaining what each achieves.",
    minimal="Provides some relevant information about industrial relations or training without connecting it to the company's change in operations.",
  ),
),

# ─────────────────────────────────────────────────────────── 2022
2022: dict(
  stem="A company has identified safety issues as a potential area of concern.",
  parts=[
    dict(
      label="(a)", marks=5,
      q="Describe the role of work health and safety (WHS) legislation in a multimedia workplace.",
      answer=(
        "Work health and safety legislation places a legal duty on the workplace to ensure the safety of "
        "its employees. The law exists to protect the welfare of employees, and failure to comply with "
        "these legal requirements may result in penalties or prosecution.<br><br>"
        "In a multimedia workplace the legislation requires the employer to provide safety training so "
        "staff know how to work safely, to supply safe equipment and maintain it, to carry out safety "
        "inspection of the workplace, to establish evacuation procedures, to display safety signage, and "
        "to form safety committees through which workers are consulted about hazards.<br><br>"
        "It also requires risk assessment of the specific hazards a multimedia environment presents - "
        "prolonged screen work and the ergonomic injuries it causes, manual handling of equipment, "
        "trailing cables, and electrical safety around editing and lighting rigs. Employees in turn have "
        "a duty to follow the procedures provided and to report hazards, so the legislation places "
        "obligations on both parties rather than the employer alone."
      ),
      keywords=[
        "legislation", "duty", "welfare", "penalties", "prosecution", "safety training", "safe equipment",
        "safety inspection", "evacuation procedures", "safety signage", "safety committees", "consulted",
        "risk assessment", "ergonomic", "manual handling", "electrical safety", "report hazards",
      ],
      minKeywords=7,
    ),
    dict(
      label="(b)", marks=10,
      q="Explain strategies that could be implemented to improve safety in a multimedia workplace.",
      answer=(
        "A multimedia workplace can improve safety through a combination of procedural, training and "
        "equipment strategies.<br><br>"
        "<strong>Applying the hierarchy of control.</strong> Hazards should first be eliminated, then "
        "substituted, isolated or controlled by engineering means, with administrative controls and "
        "personal protective equipment used last. Working through the hierarchy in order matters because "
        "it removes a hazard rather than relying on people to avoid it.<br><br>"
        "<strong>Training and consultation.</strong> Employee training ensures staff can identify hazards "
        "and use equipment correctly. Regular WHS meetings and discussions give workers a way to raise "
        "problems early, and an accident log review turns incidents that have already happened into "
        "changes that prevent the next one.<br><br>"
        "<strong>Equipment and maintenance.</strong> Tagging and testing of electrical leads and regular "
        "equipment inspections catch faults before they cause injury. RCD electrical safety devices cut "
        "power fast enough to prevent electrocution. Fire safety equipment and access to first aid limit "
        "the harm when something does go wrong.<br><br>"
        "<strong>The work environment.</strong> Ergonomic workstations with adjustable chairs, correct "
        "monitor height and appropriate lighting reduce the strain injuries that long editing sessions "
        "cause, and taking regular breaks addresses the same risk. Manual handling techniques and lifting "
        "equipment protect staff moving heavy gear on location. WHS signage marks hazards and exits, and "
        "chemical signage and storage cover printing and cleaning products.<br><br>"
        "These strategies reinforce one another: equipment controls fail if staff are untrained, and "
        "training achieves little if the equipment itself is unsafe."
      ),
      keywords=[
        "hierarchy of control", "eliminated", "substituted", "isolated", "administrative controls",
        "personal protective equipment", "employee training", "whs meetings", "accident log",
        "tagging and testing", "equipment inspections", "rcd", "fire safety equipment", "first aid",
        "ergonomic workstations", "regular breaks", "manual handling", "signage", "chemical",
        "storage",
      ],
      minKeywords=9,
    ),
  ],
  band=dict(
    full="Describes the role WHS legislation plays in the workplace and explains a range of strategies for improving safety, showing how each strategy addresses a specific hazard.",
    partial="Covers both parts but unevenly - typically the role of legislation described soundly with strategies listed rather than explained, or strategies explained well from a limited account of the legislation.",
    minimal="Provides some relevant information about WHS or workplace safety without describing the role of legislation or explaining how a strategy works.",
  ),
),

# ─────────────────────────────────────────────────────────── 2023
2023: dict(
  stem=None,
  parts=[
    dict(
      label="(a)", marks=3,
      q="Describe how ONE new technology is being used to improve the multimedia industry.",
      answer=(
        "Virtual reality is a simulated 3D environment. In the multimedia industry one purpose of virtual "
        "reality is to allow users to explore and interact with a virtual surrounding in a way that "
        "approximates reality, such as in games, training simulations and architectural walkthroughs. As "
        "a result a more immersive experience is created for the user, and clients can be shown a space "
        "or product before it physically exists.<br><br>"
        "Other new technologies that could be described include augmented reality, which overlays digital "
        "content onto a live view of the real world; 3D printing, used to produce physical models and "
        "props from digital files; laser cutting; and robotics used in automated production."
      ),
      keywords=[
        "virtual reality", "simulated", "3d", "interact", "immersive", "games",
        "augmented reality", "3d printing", "laser cutting", "robotics",
      ],
      minKeywords=3,
    ),
    dict(
      label="(b)", marks=12,
      q=("Discuss the impact of mass production and automation on the multimedia industry. "
         "Support your answer with relevant industry examples."),
      answer=(
        "Mass production and automation have reshaped how multimedia products are made, with significant "
        "advantages and real costs.<br><br>"
        "<strong>Advantages.</strong> Automation increases efficiency and therefore production rates, so "
        "more products can be produced in a shorter amount of time, leading to increased profits. It "
        "delivers consistency across products and the minimisation of errors, because an automated "
        "process repeats the same operation identically. Automated machines incur less costs in the long "
        "term, which allows the meeting of consumer demands at a lower cost through reduced labour costs "
        "and lower product prices. In practice this is visible in batch rendering farms that output "
        "thousands of video frames overnight, automated DVD and disc replication, template-driven web "
        "publishing where one design populates hundreds of pages, and automated video encoding that "
        "produces every streaming resolution from a single master file.<br><br>"
        "<strong>Disadvantages.</strong> Standardised processes do not allow customisation, so work that "
        "needs a bespoke creative treatment fits poorly. There can be a negative impact on the "
        "environment through energy use and electronic waste. The high initial investment in equipment "
        "is a barrier for smaller studios. Decreased quality can result where a generic template replaces "
        "considered design. Most significantly there is a loss of jobs as machinery and automated "
        "processes take over tasks previously done by hand, and the remaining staff need training to "
        "operate new machinery, which is a cost in both time and money.<br><br>"
        "<strong>Overall.</strong> Automation has benefited high-volume, repetitive multimedia work most "
        "and specialised creative work least. The industry has not simply shed jobs but shifted them - "
        "away from repetitive production tasks and towards roles that supervise, configure and "
        "creatively direct the automated systems."
      ),
      keywords=[
        "efficiency", "production rates", "shorter amount of time", "increased profits", "consistency",
        "minimisation of errors", "less costs", "consumer demands", "labour costs", "lower product prices",
        "rendering", "replication", "template", "encoding", "customisation", "environment",
        "initial investment", "decreased quality", "loss of jobs", "training",
    ],
      minKeywords=9,
    ),
  ],
  band=dict(
    full="Describes how one new technology is improving the industry, and discusses the impact of mass production and automation with points for and against, integrating relevant industry examples throughout.",
    partial="Covers both parts but unevenly - typically a sound description of a new technology with a one-sided or thinly exemplified discussion of automation, or a strong discussion with a limited description.",
    minimal="Provides some relevant information about a technology or about automation without describing or discussing it in the terms the question asks for.",
  ),
),

# ─────────────────────────────────────────────────────────── 2024
2024: dict(
  stem=("Use the following information to answer parts (a) and (b).<br><br>"
        "Organisation <em>A</em> is a partnership-owned firm with a hierarchical structure. "
        "Organisation <em>B</em> is a sole trader-owned firm with a flat management structure. "
        "Both organisations are committed to excellence and offer unique solutions tailored to "
        "diverse client needs."),
  parts=[
    dict(
      label="(a)", marks=5,
      q="Compare how marketing and advertising may be approached differently by each of these firms.",
      answer=(
        "Organisation A, a partnership-owned firm with a hierarchical structure, tends to take a formal "
        "approach to marketing and advertising. Decisions about how to promote its products or services "
        "pass through different levels of management before being put into action, and each partner may "
        "have a say, which takes time. The firm is more likely to have specialised teams for separate "
        "marketing tasks such as market research, branding and campaign design, and to run larger, "
        "planned campaigns with a formal budget.<br><br>"
        "Organisation B, a sole trader-owned firm with a flat management structure, takes a more flexible "
        "approach. Marketing decisions are made more quickly because there are fewer levels of "
        "management and the owner can decide alone. A small team might handle marketing directly, "
        "allowing faster reactions to changes in market conditions, and lower-cost channels such as "
        "social media and word of mouth are more likely to be used.<br><br>"
        "The key difference is therefore one of speed and consistency against scale and specialisation: "
        "Organisation B can respond faster and more personally, while Organisation A can sustain a "
        "larger, more consistent and more professionally produced campaign."
      ),
      keywords=[
        "partnership", "hierarchical", "formal", "levels of management", "each partner",
        "specialised teams", "market research", "branding", "budget", "sole trader", "flat",
        "flexible", "more quickly", "small team", "market conditions", "social media",
        "word of mouth", "speed", "specialisation",
      ],
      minKeywords=8,
    ),
    dict(
      label="(b)", marks=10,
      q="Analyse how the organisational structures of the two firms influence their approaches to production and efficiency.",
      answer=(
        "The two structures shape production and efficiency in opposite ways, and each has strengths.<br><br>"
        "<strong>Decision-making speed.</strong> Hierarchical structures such as Organisation A may "
        "experience slower decision-making because of the various levels of approval required. Flat "
        "structures such as Organisation B typically allow quicker decisions due to fewer layers of "
        "management, so a job can move into production sooner.<br><br>"
        "<strong>Responsiveness to change.</strong> Organisation A may be less responsive to change "
        "because its many tiers of management slow the implementation of new ideas. Organisation B is "
        "likely to be more agile and can adapt quickly due to its simpler structure.<br><br>"
        "<strong>Quality control.</strong> In a hierarchical structure quality control can be more "
        "standardised and rigorous, although potentially slower, because work is checked at defined "
        "stages. Flat structures may have more flexible quality control, allowing quicker adjustments "
        "but possibly less consistency between jobs.<br><br>"
        "<strong>Resource allocation and overhead.</strong> Hierarchical firms may have more complex "
        "resource allocation processes and higher management overhead, which can lead to inefficiencies. "
        "Flat structures can allocate resources more dynamically and efficiently due to less bureaucracy, "
        "giving better cost efficiency on small jobs.<br><br>"
        "<strong>Communication, autonomy and risk.</strong> Communication in Organisation A follows "
        "defined reporting lines, which is reliable but slow; in Organisation B it is direct. Greater "
        "employee autonomy in the flat structure supports innovation but concentrates risk management on "
        "one person, since the sole trader carries decisions that a partnership would share.<br><br>"
        "Overall, Organisation A's structure suits large, repeatable projects where consistency and "
        "capacity matter, while Organisation B's suits small, fast-turnaround work where responsiveness "
        "matters more than scale."
      ),
      keywords=[
        "decision-making", "levels of approval", "layers of management", "responsiveness", "tiers",
        "agile", "adapt quickly", "quality control", "standardised", "rigorous", "consistency",
        "resource allocation", "overhead", "inefficiencies", "bureaucracy", "cost efficiency",
        "communication", "autonomy", "innovation", "risk management",
      ],
      minKeywords=9,
    ),
  ],
  band=dict(
    full="Compares the two firms' marketing and advertising approaches and analyses how each organisational structure influences production and efficiency, drawing out the trade-offs rather than describing the firms separately.",
    partial="Covers both parts but unevenly - typically the two firms described side by side without a genuine comparison, or a sound analysis of structure supported by a limited comparison of marketing.",
    minimal="Provides some relevant information about marketing or organisational structure without comparing the firms or analysing the effect on production.",
  ),
),

# ─────────────────────────────────────────────────────────── 2025
2025: dict(
  stem=None,
  parts=[
    dict(
      label="(a)", marks=5,
      q=("Describe the effects of legislative requirements on the sustainable practices and "
         "environmental impacts of the multimedia industry."),
      answer=(
        "Legislation mandates that electronic waste, including multimedia equipment, must be collected "
        "and recycled responsibly. This has led to a reduction in the amount of e-waste being sent to "
        "landfill, and so has minimised the environmental footprint of the industry.<br><br>"
        "Because of these requirements, companies are now more committed to designing products that are "
        "easier to recycle and that contain fewer hazardous materials. Many multimedia companies have "
        "started using recyclable materials in their products and have set up take-back programs to "
        "ensure proper recycling at end of life.<br><br>"
        "Legislation operates at local, state and federal levels and also covers energy efficiency "
        "standards for equipment, the safe disposal of batteries and printer consumables, and the "
        "reporting of emissions. Meeting these obligations imposes compliance costs and requires "
        "companies to document their processes, but it has significantly improved the industry's "
        "sustainable practices by promoting responsible disposal and recycling of electronic waste."
      ),
      keywords=[
        "legislation", "electronic waste", "recycled", "landfill", "environmental footprint",
        "hazardous materials", "recyclable materials", "take-back", "local", "state", "federal",
        "energy efficiency", "batteries", "emissions", "compliance costs", "sustainable practices",
        "responsible disposal",
      ],
      minKeywords=7,
    ),
    dict(
      label="(b)", marks=10,
      q=("Analyse how historical developments and advancements in manufacturing processes have "
         "affected the multimedia industry. Support your answer with relevant examples."),
      answer=(
        "The multimedia industry has been shaped by successive advances in manufacturing.<br><br>"
        "<strong>Mechanisation and mass production.</strong> Early mechanisation and mass production "
        "methods increased efficiency and reduced labour costs, which made equipment affordable and gave "
        "wider accessibility to products that had previously been specialist.<br><br>"
        "<strong>The analogue to digital shift.</strong> During the late 20th century the introduction of "
        "digital technology revolutionised the production and distribution of multimedia content. Moving "
        "from analogue to digital allowed higher quality production, easier editing and faster "
        "distribution, because a digital file can be copied and revised without generational loss.<br><br>"
        "<strong>Microprocessors and miniaturisation.</strong> In the 21st century advances in "
        "microprocessor technology produced more powerful and compact devices such as smartphones and "
        "tablets, which have become primary tools for both creating and consuming multimedia. The "
        "miniaturisation of components allowed multiple functions to be integrated into a single device, "
        "improving portability and material efficiency.<br><br>"
        "<strong>Computer-aided processes.</strong> CAD, CAM and authoring software, together with "
        "robotics and CNC systems, improved precision, consistency and design flexibility while reducing "
        "waste and errors. Standardisation of materials and components ensured quality control and "
        "interoperability between systems.<br><br>"
        "<strong>Cloud computing.</strong> Cloud technology enables the storage and streaming of vast "
        "amounts of content, making it accessible worldwide. This produced streaming services such as "
        "Netflix and Spotify, which changed how multimedia content is consumed and distributed, and "
        "on-demand production which minimises material waste.<br><br>"
        "<strong>Sustainability.</strong> More recently, sustainable manufacturing, recycled and "
        "biodegradable materials, energy-efficient production and circular economy principles have "
        "reduced the industry's environmental cost.<br><br>"
        "Analysed together, these developments moved the industry from a physical, capital-intensive "
        "manufacturing model to a largely digital and distributed one - raising efficiency, "
        "accessibility and quality, while shifting employment away from production and towards content "
        "creation and systems management."
      ),
      keywords=[
        "mechanisation", "mass production", "labour costs", "accessibility", "digital technology",
        "analogue", "editing", "distribution", "microprocessor", "smartphones", "miniaturisation",
        "portability", "cad", "cam", "authoring software", "robotics", "cnc", "precision",
        "standardisation", "interoperability", "cloud", "streaming", "netflix", "on-demand",
        "biodegradable", "circular economy",
      ],
      minKeywords=11,
    ),
  ],
  band=dict(
    full="Describes in detail how legislative requirements have affected sustainable practices, and analyses how historical developments in manufacturing have affected the industry, integrating relevant examples throughout.",
    partial="Covers both parts but unevenly - typically legislation described soundly with a largely chronological account of developments rather than an analysis of their effects, or the reverse.",
    minimal="Provides some relevant information about legislation or about past developments without describing their effects or analysing their impact on the industry.",
  ),
),

}
