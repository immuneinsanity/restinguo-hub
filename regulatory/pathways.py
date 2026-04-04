"""
Pathway definitions and display logic for FDA regulatory pathways.
"""

from dataclasses import dataclass, field

STATUS_COLORS = {
    "Not Started": "#6b7280",
    "In Progress": "#f59e0b",
    "Submitted": "#3b82f6",
    "Granted": "#10b981",
}

STATUS_ICONS = {
    "Not Started": "⬜",
    "In Progress": "🔄",
    "Submitted": "📬",
    "Granted": "✅",
}


@dataclass
class PathwayDefinition:
    key: str
    name: str
    short_name: str
    icon: str
    what_it_is: str
    eligibility: list[str]
    benefits: list[str]
    timing: str
    strategic_value: str
    application_notes: str
    timeline_estimate: str
    fda_office: str
    priority: int  # 1 = highest


PATHWAYS: dict[str, PathwayDefinition] = {
    "odd": PathwayDefinition(
        key="odd",
        name="Orphan Drug Designation",
        short_name="ODD",
        icon="🏷️",
        what_it_is=(
            "FDA designation for drugs/biologics intended to treat rare diseases "
            "affecting fewer than 200,000 people in the US. Administered by FDA's "
            "Office of Orphan Products Development (OOPD)."
        ),
        eligibility=[
            "Disease affects fewer than 200,000 US patients — COPA syndrome qualifies by a wide margin (<500 diagnosed worldwide)",
            "Drug must be intended to treat the designated rare disease",
            "Sponsor need not have a lead compound — ODD can be filed on a drug class or mechanism",
            "Plausible hypothesis that the drug may be effective",
        ],
        benefits=[
            "7 years of market exclusivity post-approval (blocks same drug/same indication)",
            "Federal tax credit of up to 25% of qualified clinical testing expenses",
            "Waiver of FDA PDUFA application fees (saves ~$4M at BLA/NDA stage)",
            "Eligibility for Orphan Products grants (up to $500K/year for clinical trials)",
            "Expedited ODD review (~90 days for designation decision)",
            "Enhanced FDA engagement and communication throughout development",
        ],
        timing=(
            "File as soon as possible — ideally before IND, even at target validation stage. "
            "No compound required for designation request. This is Restinguo's highest-priority "
            "near-term regulatory action."
        ),
        strategic_value=(
            "Foundational designation that unlocks fee waivers, tax credits, and exclusivity. "
            "Extremely low bar to clear for COPA syndrome — prevalence far below threshold. "
            "Also signals seriousness to investors and partners."
        ),
        application_notes=(
            "Submit to OOPD via CDER. Required: (1) description of disease/condition, "
            "(2) medical plausibility statement, (3) US prevalence estimate with citations, "
            "(4) description of drug/mechanism. No IND required. "
            "Use published COPA syndrome papers + anifrolumab TULIP data for medical plausibility."
        ),
        timeline_estimate="~90 days from submission to designation decision",
        fda_office="Office of Orphan Products Development (OOPD), CDER",
        priority=1,
    ),

    "rpdd": PathwayDefinition(
        key="rpdd",
        name="Rare Pediatric Disease Designation",
        short_name="RPDD",
        icon="👶",
        what_it_is=(
            "Designation for drugs targeting rare diseases that primarily affect children "
            "(under age 18). Grants a Priority Review Voucher (PRV) upon approval — "
            "a transferable voucher worth $100M+ that provides priority review for any future NDA/BLA."
        ),
        eligibility=[
            "Disease primarily affects individuals under 18 years old",
            "Fewer than 200,000 US patients annually (rare disease criterion)",
            "COPA syndrome has pediatric onset — first symptoms typically appear in childhood",
            "Must be a serious or life-threatening disease",
        ],
        benefits=[
            "Priority Review Voucher (PRV) upon drug approval — transferable, worth $100-150M on secondary market",
            "Does NOT require pediatric-specific trial — pediatric indication is sufficient",
            "Can be combined with ODD (both designations can be held simultaneously)",
            "PRV provides financial incentive independent of commercial COPA syndrome market size",
        ],
        timing=(
            "Apply in parallel with ODD. RPDD is a separate application to OOPD. "
            "File once ODD is in preparation — the applications share significant overlap."
        ),
        strategic_value=(
            "The PRV is potentially worth more than the entire COPA syndrome commercial market. "
            "PRVs have sold for $100-350M. This dramatically improves the economics of developing "
            "a therapy for an ultra-rare disease. Key investor/BD talking point."
        ),
        application_notes=(
            "Separate application from ODD but submitted to same office (OOPD). "
            "Requires documentation that disease primarily affects pediatric patients. "
            "COPA syndrome literature (Shum lab papers) documents pediatric onset. "
            "Note: PRV program subject to Congressional reauthorization — check current status."
        ),
        timeline_estimate="~90 days; review concurrent with or after ODD",
        fda_office="Office of Orphan Products Development (OOPD), CDER",
        priority=2,
    ),

    "btd": PathwayDefinition(
        key="btd",
        name="Breakthrough Therapy Designation",
        short_name="BTD",
        icon="⚡",
        what_it_is=(
            "FDA designation for drugs that treat serious conditions where preliminary clinical "
            "evidence shows substantial improvement over available therapy on a clinically "
            "significant endpoint. Provides intensive FDA guidance and rolling review."
        ),
        eligibility=[
            "Serious or life-threatening condition — COPA syndrome qualifies (severe ILD, arthritis, nephritis)",
            "Preliminary CLINICAL evidence of substantial improvement — requires Phase 1/2 data",
            "Must show improvement over existing therapies (JAK inhibitors used off-label)",
            "NOT applicable at current stage — need clinical data first",
        ],
        benefits=[
            "Intensive FDA guidance throughout development (senior staff involvement)",
            "Rolling review of BLA/NDA sections as completed",
            "Organizational commitment from FDA leadership",
            "Cross-disciplinary guidance on clinical trial design",
            "Associated with faster approval timelines historically",
        ],
        timing=(
            "Too early to apply — requires preliminary clinical evidence. "
            "Target application after Phase 1/2a with strong PD biomarker data "
            "(IFN signature suppression, clinical improvement over JAK inhibitors). "
            "Revisit at IND-stage or after first-in-human data."
        ),
        strategic_value=(
            "High value if clinical signal is strong. The lack of approved therapy for COPA syndrome "
            "means any efficacy signal against existing off-label standard-of-care (JAK inhibitors) "
            "could meet the 'substantial improvement' bar. Plan to apply at first opportunity."
        ),
        application_notes=(
            "Application submitted to review division. Requires: (1) disease description, "
            "(2) description of drug, (3) preliminary clinical evidence, (4) evidence of "
            "substantial improvement. Can be submitted with IND or at any time thereafter."
        ),
        timeline_estimate="60 days from submission to FDA designation decision",
        fda_office="Relevant CDER Review Division (likely Division of Rheumatology & Transplant Medicine)",
        priority=3,
    ),

    "ftd": PathwayDefinition(
        key="ftd",
        name="Fast Track Designation",
        short_name="FTD",
        icon="🚀",
        what_it_is=(
            "FDA designation for drugs treating serious conditions with unmet medical need. "
            "Lower bar than Breakthrough — intended to facilitate drug development and "
            "expedite review. Provides frequent FDA interactions and rolling review eligibility."
        ),
        eligibility=[
            "Drug intended to treat a serious or life-threatening condition — COPA syndrome qualifies",
            "Preliminary evidence showing potential to address unmet need (no approved therapy required)",
            "No approved therapy for COPA syndrome = clear unmet need",
            "Can apply at IND stage with preclinical data — lower evidentiary bar than BTD",
            "IFNAR mechanistic rationale + anifrolumab approval = plausible basis",
        ],
        benefits=[
            "More frequent meetings and communications with FDA",
            "Eligibility for rolling review (submit BLA/NDA sections as completed)",
            "Eligibility for priority review if criteria met",
            "Generally obtained with lower evidentiary bar than Breakthrough designation",
        ],
        timing=(
            "Apply at or shortly after IND submission. Can apply with IND or after. "
            "Strong case based on: (1) serious disease, (2) no approved therapy, "
            "(3) IFNAR mechanistic rationale, (4) preclinical PD data."
        ),
        strategic_value=(
            "Lower bar than BTD and appropriate for current trajectory. Apply at IND stage "
            "to open communication channel with FDA. Can be upgraded to BTD later with clinical data. "
            "Rolling review is especially valuable for rare disease programs with small trial sizes."
        ),
        application_notes=(
            "Letter to FDA review division. Relatively brief — describe disease, unmet need, "
            "drug mechanism, and why it has potential to address unmet need. "
            "Submit concurrently with IND or as a separate submission."
        ),
        timeline_estimate="60 days from submission to FDA response",
        fda_office="Relevant CDER Review Division",
        priority=4,
    ),
}


def get_pathway(key: str) -> PathwayDefinition | None:
    return PATHWAYS.get(key)


def get_all_pathways() -> list[PathwayDefinition]:
    return sorted(PATHWAYS.values(), key=lambda p: p.priority)
