"""
FDA meeting types and tracker logic.
"""

from dataclasses import dataclass

MEETING_TYPES = {
    "Type A": {
        "description": (
            "Meetings for programs with a clinical hold, dispute resolution, or special protocol assessment "
            "(SPA). Highest priority — FDA aims to schedule within 30 days of request."
        ),
        "timeline": "30 days from request to meeting",
        "when_to_use": "Clinical hold response, formal dispute resolution, SPA discussion",
        "relevant_for_restinguo": False,
    },
    "Type B": {
        "description": (
            "Pre-IND meetings, end-of-Phase-1, end-of-Phase-2, and pre-BLA/NDA meetings. "
            "Most important meeting type for Restinguo. FDA aims to schedule within 60-90 days."
        ),
        "timeline": "60–90 days from request to meeting (written response within 30 days if meeting denied)",
        "when_to_use": "Pre-IND consultation, end-of-phase meetings, pre-submission meetings",
        "relevant_for_restinguo": True,
    },
    "Type C": {
        "description": (
            "All other FDA meetings — advice on development, protocol design, manufacturing, labeling. "
            "FDA aims to schedule within 90 days."
        ),
        "timeline": "90 days from request to meeting",
        "when_to_use": "General development guidance, manufacturing questions, labeling discussions",
        "relevant_for_restinguo": True,
    },
}

MEETING_STATUSES = ["Planning", "Request Drafted", "Request Submitted", "Scheduled", "Completed", "Cancelled"]

PRE_IND_AGENDA_TEMPLATE = """
PRE-IND MEETING AGENDA
Restinguo — COPA Syndrome IFNAR Antagonist Program
[Date TBD] | [Time TBD] | [Location/Teleconference]

---
ATTENDEES
Restinguo: [CEO], [CMO/CSO], [Regulatory Affairs Lead], [Nonclinical Lead], [CMC Lead]
FDA: [Division Director], [Medical Officer], [Pharmacologist], [CMC Reviewer]

---
AGENDA

1. Introduction and Meeting Objectives (5 min)
   - Overview of Restinguo and the COPA syndrome program
   - Meeting objectives and key questions

2. Disease Background: COPA Syndrome (10 min)
   - Disease mechanism: COPA mutation → STING accumulation → constitutive type I IFN signaling
   - Epidemiology: <500 patients diagnosed worldwide; orphan disease
   - Clinical presentation: ILD, arthritis, nephritis; pediatric onset
   - Unmet need: no approved therapy; off-label JAK inhibitors are inadequate
   - Natural history data

3. Therapeutic Hypothesis and Rationale (10 min)
   - IFNAR blockade MOA: downstream interruption of pathological IFN signaling
   - Regulatory analog: anifrolumab (approved for SLE, same IFNAR1 target)
   - Lead compound overview: [compound type, mechanism, differentiation from anifrolumab]
   - Preclinical summary

4. Nonclinical Program Discussion — Key FDA Questions (20 min)
   Q1: Animal Model Acceptability
       - COPA syndrome: no validated animal model
       - Proposed approach: [Copa KI mouse / SAVI mouse / other]
       - FDA Question: Will FDA accept [model] for IND-enabling toxicology and efficacy studies?

   Q2: Tox Species Selection
       - [Compound] cross-reacts with [species]
       - FDA Question: Is [species pair] acceptable for GLP tox studies?

   Q3: Nonclinical Package Completeness
       - FDA Question: Is the proposed nonclinical package (28-day tox, safety pharm, genotox)
         sufficient to support Phase 1 SAD/MAD in adults?

5. Clinical Program Discussion — Key FDA Questions (20 min)
   Q4: Phase 1 Design
       - Proposed: SAD/MAD in healthy volunteers vs. COPA patients
       - FDA Question: Given ultra-rare population, is a combined Phase 1/2 in COPA patients acceptable?

   Q5: Pharmacodynamic Endpoints
       - Proposed PD biomarkers: IFN signature score (ISG15, CXCL10)
       - FDA Question: Will FDA accept IFN signature suppression as a PD endpoint in Phase 1?

   Q6: Dose Selection and PK/PD
       - FDA Question: What PK/PD data are needed to project efficacious human dose?

6. CMC Discussion (10 min)
   Q7: CMC Readiness for IND
       - Current CMC status: [describe]
       - FDA Question: What CMC information is minimally required to support IND filing at this stage?

7. Regulatory Pathway Discussion (10 min)
   - ODD application status
   - Fast Track Designation strategy
   - Overall development timeline discussion

8. Wrap-Up and Action Items (5 min)

---
KEY QUESTIONS SUMMARY (for FDA written response)
[Questions numbered Q1-Q7 above]

---
ATTACHMENTS
1. Restinguo Corporate Overview
2. COPA Syndrome Disease Overview with Epidemiology
3. Nonclinical Summary Report
4. Proposed Phase 1 Protocol Synopsis
5. CMC Summary
"""


def get_meeting_type_info(meeting_type: str) -> dict:
    return MEETING_TYPES.get(meeting_type, {})


def get_pre_ind_agenda_template() -> str:
    return PRE_IND_AGENDA_TEMPLATE


def get_meeting_request_template(meeting_type: str, purpose: str) -> str:
    return f"""
[Company Letterhead]
[Date]

Division of [Relevant Division]
Center for Drug Evaluation and Research
Food and Drug Administration
10903 New Hampshire Avenue
Silver Spring, MD 20993

Re: Request for {meeting_type} Meeting — IND [NUMBER TBD]
    Restinguo — [Drug Name] for the Treatment of COPA Syndrome

Dear Division Director:

Restinguo, Inc. respectfully requests a {meeting_type} meeting with the Division of
[Division Name] to discuss {purpose}.

PROPOSED AGENDA ITEMS:
[List key agenda items]

PROPOSED MEETING DATE/FORMAT:
We request a meeting within [30/60/90] days of this request. We are available for a
teleconference or in-person meeting at FDA's convenience.

MEETING PARTICIPANTS:
Restinguo: [Names, Titles]
We anticipate [number] attendees.

BACKGROUND PACKAGE:
We will submit the meeting background package 30 days prior to the meeting date.

Please contact [Name] at [phone/email] to schedule this meeting.

Sincerely,

[Name]
[Title]
Restinguo, Inc.
[Contact Information]
"""
