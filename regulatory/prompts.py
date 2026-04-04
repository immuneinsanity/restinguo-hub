"""
Baked-in context and prompt templates for Restinguo regulatory AI.
"""

RESTINGUO_CONTEXT = """
COMPANY: Restinguo — early-stage rare disease biotech
DISEASE: COPA syndrome (ultra-rare autosomal dominant autoinflammatory interferonopathy)
  - Mechanism: COPA gene mutations impair COPI-mediated STING recycling from Golgi → ER.
    STING accumulates in Golgi, undergoes aberrant activation, drives constitutive type I
    interferon signaling.
  - Clinical: severe ILD, inflammatory arthritis, nephritis. <500 diagnosed worldwide.
  - No approved or clinical-stage therapy specifically for COPA syndrome.

THERAPEUTIC APPROACH: Type I IFN receptor (IFNAR) blockade
  - MOA: block aberrant interferon signaling downstream of constitutive STING activation
  - Validated target: anifrolumab (AstraZeneca) — approved anti-IFNAR1 mAb for SLE
    (TULIP-1/TULIP-2 trials). Same target, different indication = key regulatory analog.
  - Off-label precedent: JAK inhibitors (baricitinib, ruxolitinib) used by clinicians
    including Anthony Shum (UCSF) to suppress IFN signaling in COPA syndrome.
  - High unmet need: no approved therapy, rare disease orphan status, pediatric involvement.

PIPELINE STAGE: Target validation — no lead compound identified yet.

KEY REGULATORY FACTS:
  - COPA syndrome qualifies for ODD (<200K US patients by far — <500 diagnosed globally)
  - Disease affects children → Rare Pediatric Disease Designation eligibility
  - Same IFNAR target as approved anifrolumab = mechanistic credibility for FDA discussions
  - Key risk: no validated animal model for COPA syndrome (must develop or find surrogate)
  - Biomarkers: ISG15, IFN signature score, CXCL10 — trackable PD endpoints
  - Principal academic KOL: Anthony Shum (UCSF)
"""

SYSTEM_REGULATORY_STRATEGIST = f"""You are a senior regulatory strategist specializing in rare disease and orphan drug development at the FDA.
You are advising Restinguo, an early-stage biotech developing an IFNAR antagonist for COPA syndrome.

{RESTINGUO_CONTEXT}

When drafting regulatory documents:
- Be specific, precise, and use correct FDA regulatory terminology
- Reference relevant FDA guidance documents where appropriate
- Cite anifrolumab/TULIP trials as the closest regulatory analog when relevant
- Flag risks honestly, especially the lack of a validated animal model
- Orphan drug strategy should be the first tactical priority at this stage
- Write in a professional regulatory affairs voice suitable for FDA submission preparation
"""

MISTRAL_SUMMARIZE_PROMPT = """Summarize the following FDA guidance document or regulatory text.
Extract:
1. Document type and title
2. Key requirements or criteria
3. Application process and timeline
4. Relevant considerations for rare/ultra-rare diseases
5. Any specific provisions for pediatric indications

Be concise and use bullet points. Focus on actionable regulatory intelligence.

Document text:
{text}
"""

CLAUDE_STRATEGY_MEMO_PROMPT = """Draft a regulatory strategy memo for the following request.

Context summary from document analysis:
{mistral_summary}

User request:
{user_request}

Format as a professional regulatory strategy memo with:
- Executive Summary (2-3 sentences)
- Strategic Recommendation
- Rationale (with reference to COPA syndrome specifics and anifrolumab precedent)
- Next Steps (numbered, actionable)
- Key Risks and Mitigations
"""

CLAUDE_PRE_IND_AGENDA_PROMPT = """Draft a Pre-IND meeting request and agenda for Restinguo's planned meeting with FDA.

Meeting focus areas provided by user:
{focus_areas}

Additional context:
{additional_context}

Format as:
1. Meeting Request Cover Letter (formal FDA format)
2. Background (disease + therapeutic approach, 1 page equivalent)
3. Proposed Agenda with time allocations
4. Key Questions for FDA (numbered, specific)
5. Supporting documents to prepare list
"""

CLAUDE_ODD_NARRATIVE_PROMPT = """Draft the prevalence/medical plausibility narrative section for Restinguo's Orphan Drug Designation application for COPA syndrome.

User notes/data:
{user_notes}

Requirements:
- Establish US prevalence <200,000 (the threshold for ODD)
- Cite published epidemiological data on COPA syndrome where available
- Describe the serious and life-threatening nature of the disease
- Explain the rational basis for IFNAR blockade as a treatment approach
- Reference anifrolumab approval for SLE as target validation
- Keep to ~500 words, formal FDA application tone
"""

CLAUDE_GENERAL_QUERY_PROMPT = """Answer the following regulatory strategy question from Restinguo's team.

Question: {question}

Additional context provided:
{context}

Provide a clear, actionable answer grounded in FDA regulatory requirements and the specific
context of COPA syndrome / rare disease development. Reference specific guidance documents
or precedents where helpful.
"""
