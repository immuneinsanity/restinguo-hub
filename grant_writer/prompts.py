"""
Prompt templates for NIH SBIR/STTR Phase I grant sections.
Restinguo — COPA syndrome / IFNAR blockade.
"""

COMPANY_CONTEXT = """
Company: Restinguo — early-stage rare disease biotech.
Disease: COPA syndrome — autosomal dominant autoinflammatory disease caused by COPA gene mutations.
  - COPA encodes a COPI coatomer subunit that normally recycles STING from Golgi back to ER.
  - Loss-of-function COPA mutations impair STING recycling → STING accumulates in Golgi → aberrant activation → constitutive type I IFN signaling (interferonopathy).
  - Clinical: severe interstitial lung disease, inflammatory arthritis, nephritis. Ultra-rare: <500 diagnosed worldwide.
  - No approved therapy exists.
Therapeutic approach: Type I IFN receptor (IFNAR) blockade to interrupt downstream pathological signaling.
  - Blocking IFNAR disrupts the constitutive type I IFN-driven disease loop.
  - Precedent: anifrolumab (AstraZeneca) is an approved anti-IFNAR1 mAb for lupus — same target, different indication.
  - Current off-label standard: JAK inhibitors (baricitinib, ruxolitinib) — indirect comparators.
Current stage: Target validation. No lead compound yet.
Program: NIH SBIR Phase I (R43), ~$300K direct costs, 6-month project.
FOAs: PA-24-185 (SBIR), PA-24-186 (STTR).
"""

# ── Mistral preprocessing prompts ──────────────────────────────────────────

MISTRAL_SUMMARIZE_DOCS = """You are a scientific research assistant. Summarize the following source material into concise bullet points, focusing on:
- Key scientific findings
- Mechanistic insights
- Clinical data
- Any gaps in knowledge

Source material:
{source_text}

Provide a structured bullet-point summary in under 300 words."""

MISTRAL_EXTRACT_FACTS = """Extract the most grant-relevant scientific facts from this text for an NIH SBIR application about COPA syndrome and IFNAR blockade:

{source_text}

List facts as numbered items. Be specific: include numbers, citations context, and mechanistic claims."""

MISTRAL_OUTLINE = """Create a rough outline for the "{section}" section of an NIH SBIR Phase I grant application.

Context:
{company_context}

Additional notes: {additional_notes}

Output a numbered outline with 4-6 main points and sub-bullets. Be specific to COPA syndrome and IFNAR biology."""

# ── Claude final-draft prompts ──────────────────────────────────────────────

CLAUDE_SPECIFIC_AIMS = """You are an expert NIH grant writer with deep knowledge of rare disease biology and SBIR/STTR applications.

{company_context}

Preprocessed outline and key facts:
{preprocessed}

Write the Specific Aims page (1 page, ~600 words) for an NIH SBIR Phase I application. Follow this structure:
1. Opening paragraph: disease burden, unmet need, and opportunity (3-4 sentences)
2. Central hypothesis statement (1-2 sentences, italicized format)
3. Aim 1: [Scientific aim — target validation or mechanism] — include rationale and expected outcome
4. Aim 2: [Translational aim — in vitro or cell-based validation] — include rationale and expected outcome
5. Closing paragraph: impact statement and long-term vision

Write in NIH grant style: declarative, evidence-based, forward-looking. Avoid jargon that isn't defined. Make every sentence count.

Additional context from user: {additional_notes}"""

CLAUDE_SIGNIFICANCE = """You are an expert NIH grant writer.

{company_context}

Preprocessed key facts and outline:
{preprocessed}

Write the Significance section (~750 words) for an NIH SBIR Phase I application. Cover:
1. Disease background: COPA syndrome genetics, prevalence, and clinical burden
2. Pathogenic mechanism: COPA → COPI → STING recycling failure → constitutive type I IFN
3. Current treatment landscape and its limitations (JAK inhibitors off-label; no approved therapy)
4. Why IFNAR blockade is the scientifically justified approach (precedent from anifrolumab in lupus/interferonopathies)
5. Gap statement: what is unknown that this Phase I will address

Write in NIH Significance style. Cite mechanistic logic clearly. Use headings (bold).

Additional context: {additional_notes}"""

CLAUDE_INNOVATION = """You are an expert NIH grant writer.

{company_context}

Preprocessed notes:
{preprocessed}

Write the Innovation section (~400 words) for an NIH SBIR Phase I application. Argue:
1. What the current state of the art is (and its limitations)
2. How this project is conceptually/technically novel
3. Why IFNAR blockade specifically for COPA syndrome is innovative (not just repurposing — mechanistically justified, first dedicated therapeutic program for this disease)
4. What new knowledge will be generated

Be assertive. Reviewers want to see genuine novelty, not incremental work.

Additional context: {additional_notes}"""

CLAUDE_APPROACH = """You are an expert NIH grant writer and translational scientist.

{company_context}

Preprocessed outline and facts:
{preprocessed}

Write the Approach section (~1200 words) for an NIH SBIR Phase I application. Structure:
1. Overall Strategy (1 paragraph): logic linking aims, timeline overview
2. Aim 1 — [Target Validation]:
   - Rationale
   - Methods (specific assays: ISRE reporter, ISG scoring, pSTAT1/pSTAT2 readouts in COPA patient-derived cells or model system)
   - Expected outcomes
   - Potential pitfalls and alternatives
3. Aim 2 — [IFNAR Blockade Efficacy in COPA Model]:
   - Rationale
   - Methods (IFNAR blocking antibody or small molecule; relevant cell/organoid model; key endpoints)
   - Expected outcomes
   - Potential pitfalls and alternatives
4. Timeline (brief: 6-month SBIR Phase I milestones)

Write rigorously. Reviewers will critique methods — be specific. Acknowledge limitations proactively.

Additional context: {additional_notes}"""

CLAUDE_FACILITIES = """You are an expert NIH grant writer.

{company_context}

Write the Facilities & Other Resources section (~300 words) for an NIH SBIR Phase I application. Include:
1. Company lab/office space (describe as appropriate for early-stage biotech)
2. Key equipment relevant to the work (flow cytometry, cell culture, molecular biology)
3. Computational resources (for IFN signature analysis, bioinformatics)
4. Collaborator resources if applicable (academic partner for COPA patient samples, etc.)
5. Statement of adequacy for the proposed work

Write in standard NIH Facilities format. Be concrete but not over-claiming.

Additional context: {additional_notes}"""

SECTION_PROMPTS = {
    "specific_aims": CLAUDE_SPECIFIC_AIMS,
    "significance": CLAUDE_SIGNIFICANCE,
    "innovation": CLAUDE_INNOVATION,
    "approach": CLAUDE_APPROACH,
    "facilities": CLAUDE_FACILITIES,
}

SECTION_LABELS = {
    "specific_aims": "Specific Aims",
    "significance": "Significance",
    "innovation": "Innovation",
    "approach": "Approach",
    "facilities": "Facilities & Other Resources",
}
