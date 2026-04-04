"""
Pre-IND roadmap stage definitions and checklist data.
"""

from dataclasses import dataclass, field

STATUS_ORDER = ["In Progress", "Pending", "Complete", "Blocked"]


@dataclass
class RoadmapStage:
    key: str
    name: str
    phase: str
    duration_estimate: str
    description: str
    checklist: list[str]
    key_questions: list[str]
    key_risks: list[str]
    deliverables: list[str]
    order: int


STAGES: dict[str, RoadmapStage] = {
    "target_validation": RoadmapStage(
        key="target_validation",
        name="Target Validation",
        phase="Research",
        duration_estimate="6–18 months",
        description=(
            "Confirm that IFNAR blockade is the right therapeutic approach for COPA syndrome. "
            "Generate mechanistic evidence that type I IFN signaling is pathogenic and suppressible. "
            "This is Restinguo's current stage."
        ),
        checklist=[
            "Confirm elevated type I IFN signature in COPA syndrome patient samples (ISG15, IFN score, CXCL10)",
            "Demonstrate that IFNAR blockade suppresses IFN signaling in COPA patient-derived cells",
            "Characterize the COPA mutation landscape in patient population",
            "Review COPA syndrome natural history data (Shum lab / published cohorts)",
            "Assess IFN signature as PD biomarker for future clinical trials",
            "Establish research collaboration with academic KOL (Anthony Shum, UCSF)",
            "Competitive analysis: IP landscape around IFNAR antagonism (anifrolumab FTO analysis)",
        ],
        key_questions=[
            "Does IFNAR blockade sufficiently suppress the IFN signature when STING activation is constitutive?",
            "Is there a secondary output from constitutive STING activation that bypasses IFNAR?",
            "What IFN signature suppression threshold correlates with clinical improvement?",
            "Are there patient subgroups (by COPA mutation) with differential IFNAR dependence?",
        ],
        key_risks=[
            "STING may activate non-IFN pathways (NF-kB) that are not addressed by IFNAR blockade",
            "IFN signature suppression may not translate to clinical improvement in lung/joint/kidney",
            "Small patient population limits ability to run controlled studies",
        ],
        deliverables=[
            "Target validation report with mechanistic rationale",
            "IFN signature biomarker panel defined",
            "IP freedom-to-operate assessment",
            "Go/no-go decision for lead compound identification",
        ],
        order=1,
    ),

    "lead_identification": RoadmapStage(
        key="lead_identification",
        name="Lead Compound Identification",
        phase="Research",
        duration_estimate="12–24 months",
        description=(
            "Identify and characterize a lead therapeutic candidate that blocks IFNAR. "
            "Options include: novel anti-IFNAR1 mAb, bispecific antibody, small molecule IFNAR antagonist, "
            "or differentiated follow-on to anifrolumab. Assess IP space carefully."
        ),
        checklist=[
            "Define target product profile (TPP) — route of administration, dosing, patient population",
            "Conduct IP landscape analysis to define freedom-to-operate relative to anifrolumab",
            "Evaluate whether anifrolumab itself can be developed for COPA (out-licensing vs. novel compound)",
            "Screen antibody candidates or small molecule libraries against IFNAR1/IFNAR2",
            "Evaluate bispecific approach (IFNAR + STING?) for differentiation",
            "Down-select to lead compound based on in vitro binding, selectivity, and ADME",
        ],
        key_questions=[
            "Can we differentiate from anifrolumab sufficiently to establish IP position?",
            "What is the ideal target: IFNAR1, IFNAR2, or dual?",
            "Is a subcutaneous formulation feasible (patient convenience for chronic dosing)?",
            "Should we pursue a novel compound or in-license/acquire an existing asset?",
        ],
        key_risks=[
            "Anifrolumab IP (AstraZeneca) may block key IFNAR1 epitopes — FTO analysis critical",
            "Novel mAb development timelines are long; may be faster to in-license",
            "Small molecule IFNAR antagonists are poorly precedented",
        ],
        deliverables=[
            "Target product profile (TPP) document",
            "IP freedom-to-operate analysis",
            "Lead compound with defined mechanism and selectivity data",
            "Lead optimization plan",
        ],
        order=2,
    ),

    "in_vitro_poc": RoadmapStage(
        key="in_vitro_poc",
        name="In Vitro Proof of Concept",
        phase="Preclinical",
        duration_estimate="6–12 months",
        description=(
            "Demonstrate that the lead compound suppresses IFN signaling in COPA syndrome-relevant "
            "cell models. Use patient-derived PBMCs, iPSC-derived macrophages, or COPA-mutant cell lines."
        ),
        checklist=[
            "Establish COPA syndrome cell model (patient PBMCs or COPA-mutant iPSC-derived cells)",
            "Demonstrate lead compound binds IFNAR with desired potency (IC50, KD)",
            "Show IFN signature suppression (ISG15, IFN score) in COPA cell model",
            "Evaluate selectivity (no off-target pathway suppression)",
            "Assess compound stability and ADME in vitro (half-life, protein binding)",
            "Cytotoxicity profiling (CC50/IC50 therapeutic window)",
        ],
        key_questions=[
            "What concentration of IFNAR blockade is needed to suppress IFN signature by 50%? 80%?",
            "Does efficacy hold across multiple COPA mutations?",
            "Are there any cytotoxicity signals at therapeutic concentrations?",
        ],
        key_risks=[
            "COPA patient-derived cells may be difficult to obtain (rare disease)",
            "Cell models may not recapitulate the in vivo constitutive STING activation",
        ],
        deliverables=[
            "In vitro proof-of-concept package",
            "Potency and selectivity data",
            "Initial ADME assessment",
            "Data package supporting IND-enabling study design",
        ],
        order=3,
    ),

    "in_vivo_models": RoadmapStage(
        key="in_vivo_models",
        name="In Vivo Models & Efficacy",
        phase="Preclinical",
        duration_estimate="12–24 months",
        description=(
            "Establish and validate in vivo efficacy using the best available animal model. "
            "CRITICAL RISK: no validated animal model for COPA syndrome exists. "
            "Options: (1) develop Copa knock-in mouse, (2) use STING gain-of-function model (SAVI), "
            "(3) use lupus/interferonopathy models as surrogates, (4) seek FDA guidance on surrogate."
        ),
        checklist=[
            "Assess Copa knock-in mouse availability (published: Murano et al.) — obtain or develop",
            "Evaluate STING GOF (SAVI) mouse as surrogate interferonopathy model",
            "Evaluate MRL/lpr or NZB/W lupus models as IFNAR blockade efficacy surrogates",
            "Define efficacy endpoints: IFN signature, lung histology, joint inflammation, survival",
            "Demonstrate lead compound PK/PD in vivo (dose, exposure, IFN signature suppression)",
            "Run efficacy study in chosen model with dose-response",
            "Discuss animal model strategy with FDA in Pre-IND meeting",
        ],
        key_questions=[
            "Will FDA accept a surrogate interferonopathy model (SAVI mouse) for IND-enabling tox?",
            "Is the Copa KI mouse phenotype severe enough to detect treatment effect?",
            "What PK/PD relationship is needed to project efficacious human dose?",
        ],
        key_risks=[
            "No validated animal model = primary development risk. Must resolve before IND.",
            "Copa KI mouse may have incomplete penetrance or mild phenotype",
            "SAVI mouse (STING GOF) has different upstream mechanism — FDA may not accept",
            "Developing a new Copa mouse model adds 12-18 months to timeline",
        ],
        deliverables=[
            "Animal model selection rationale document",
            "In vivo efficacy data package",
            "PK/PD model for human dose projection",
            "Animal model strategy rationale for FDA Pre-IND meeting",
        ],
        order=4,
    ),

    "ind_enabling": RoadmapStage(
        key="ind_enabling",
        name="IND-Enabling Studies",
        phase="IND-Enabling",
        duration_estimate="18–24 months",
        description=(
            "Conduct GLP-compliant studies required to support IND filing. Includes GLP tox, "
            "CMC development, pharmacology, and safety pharmacology. Run in parallel where possible."
        ),
        checklist=[
            "GLP 28-day repeat-dose toxicology study in two species (rodent + non-rodent)",
            "GLP safety pharmacology battery (cardiovascular, respiratory, CNS)",
            "Genotoxicity studies (Ames test, in vitro chromosomal aberration)",
            "CMC: manufacturing process defined, drug substance and drug product characterized",
            "Stability studies initiated (drug substance and product)",
            "Immunogenicity assessment (for biologics — anti-drug antibody assay)",
            "Bioanalytical method development and validation (PK assay)",
            "Toxicokinetics in GLP studies",
            "Pediatric study plan considerations (if pediatric IND)",
        ],
        key_questions=[
            "What tox species best reflects human IFNAR biology (given cross-reactivity of lead compound)?",
            "Are there immunosuppression-related risks in tox studies (infection, lymphopenia)?",
            "What CMC readiness is required at IND vs. what can be deferred?",
        ],
        key_risks=[
            "Immunosuppression risk in tox studies — IFNAR blockade may cause opportunistic infection signals",
            "Species selection for tox may be limited by compound cross-reactivity",
            "CMC timelines for biologics are typically 18-24 months — critical path item",
        ],
        deliverables=[
            "GLP tox study reports",
            "CMC section (IND Module 3)",
            "Pharmacology/safety pharmacology package",
            "Integrated nonclinical summary for IND",
        ],
        order=5,
    ),

    "pre_ind_meeting": RoadmapStage(
        key="pre_ind_meeting",
        name="Pre-IND Meeting with FDA",
        phase="IND-Enabling",
        duration_estimate="3–6 months (preparation + meeting)",
        description=(
            "Type B meeting with FDA to discuss the IND program before submission. "
            "Critical opportunity to align on: animal model acceptability, proposed clinical trial design, "
            "CMC requirements, and overall development plan."
        ),
        checklist=[
            "Submit Type B meeting request to relevant FDA division",
            "Prepare meeting background package (30 days before meeting)",
            "Define specific questions for FDA (animal model, trial design, endpoints, CMC)",
            "Present COPA syndrome natural history and unmet need data",
            "Present preclinical package (efficacy, tox, CMC status)",
            "Propose Phase 1 design (SAD/MAD, patient population, dose escalation scheme)",
            "Propose PD biomarkers and endpoints for Phase 1/2",
            "Discuss ODD and FTD applications (if not already filed)",
        ],
        key_questions=[
            "Will FDA accept [chosen animal model] for IND-enabling tox studies?",
            "Is a combined Phase 1/2 design acceptable given the ultra-rare population?",
            "What biomarkers will FDA accept as PD endpoints in Phase 1?",
            "Does FDA have guidance on trial design for COPA syndrome specifically?",
            "Are there any orphan disease-specific CMC flexibilities available?",
        ],
        key_risks=[
            "FDA may require a specific animal model that Restinguo doesn't have",
            "FDA may have concerns about pediatric inclusion in Phase 1",
            "Meeting logistics — FDA backlog can delay meeting scheduling",
        ],
        deliverables=[
            "Type B meeting request letter",
            "Pre-IND meeting background package",
            "Written meeting minutes / FDA response",
            "Revised IND plan based on FDA feedback",
        ],
        order=6,
    ),

    "ind_submission": RoadmapStage(
        key="ind_submission",
        name="IND Submission",
        phase="IND",
        duration_estimate="3–6 months (compilation + review)",
        description=(
            "File the Investigational New Drug application with FDA to initiate clinical trials. "
            "FDA has 30 days to respond with a clinical hold or proceed. "
            "IND goes effective if no clinical hold is issued."
        ),
        checklist=[
            "Compile IND: Form FDA 1571 cover sheet",
            "Module 1: Introductory statement, general investigational plan",
            "Module 2: Investigator's Brochure",
            "Module 3: Protocol(s) for Phase 1 study",
            "Module 4: Chemistry, Manufacturing, and Controls (CMC)",
            "Module 5: Pharmacology and toxicology data",
            "Module 6: Previous human experience (none expected; reference anifrolumab if relevant)",
            "Additional information (REMS if required, pediatric study plans)",
            "Submit electronically via ESG",
            "Await 30-day FDA review period (no news = clinical hold not imposed = can proceed)",
        ],
        key_questions=[
            "Are all IND components complete and internally consistent?",
            "Has FDA Pre-IND feedback been fully addressed?",
            "Is the CMC package sufficient for Phase 1 (not required to be commercial-scale)?",
        ],
        key_risks=[
            "Clinical hold from FDA (30-day review) — most commonly due to safety concerns in tox",
            "CMC hold — most common IND hold reason; requires complete CMC package",
            "Protocol design issues flagged by FDA",
        ],
        deliverables=[
            "IND application (complete)",
            "IND number assigned by FDA",
            "30-day review period cleared (or clinical hold resolved)",
            "Authorization to initiate Phase 1 clinical trial",
        ],
        order=7,
    ),
}


def get_stage(key: str) -> RoadmapStage | None:
    return STAGES.get(key)


def get_all_stages() -> list[RoadmapStage]:
    return sorted(STAGES.values(), key=lambda s: s.order)
