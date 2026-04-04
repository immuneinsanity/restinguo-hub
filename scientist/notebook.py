"""
Lab notebook logic — Opus-powered result interpretation and next-step generation.
"""

from scientist import database as db
from scientist import drafter
from scientist.prompts import RESULT_INTERPRETATION_SYSTEM


def interpret_results_with_opus(
    experiment_title: str,
    hypothesis_statement: str | None,
    protocol_summary: str | None,
    results_text: str,
) -> dict:
    """
    Run Opus interpretation on experimental results.
    Returns a dict with interpretation, next_steps, hypothesis_impact.
    """
    hyp_context = f"HYPOTHESIS BEING TESTED: {hypothesis_statement}" if hypothesis_statement else ""
    protocol_context = f"PROTOCOL SUMMARY: {protocol_summary}" if protocol_summary else ""

    # Preprocess results if long
    processed_results = (
        drafter.preprocess_with_mistral(results_text)
        if len(results_text) > 2000
        else results_text
    )

    prompt = f"""Interpret these experimental results for Restinguo's scientific program:

EXPERIMENT: {experiment_title}
{hyp_context}
{protocol_context}

RESULTS:
{processed_results}

Please provide:

1. MECHANISTIC INTERPRETATION
What do these results show at the molecular/cellular level? Be specific.

2. HYPOTHESIS IMPACT
How do these results affect the hypothesis being tested?
(strengthens / weakens / settles / neutral — explain why)

3. CONFOUNDS AND ALTERNATIVE EXPLANATIONS
What alternative interpretations exist? What could invalidate this interpretation?

4. NEXT EXPERIMENTS (Priority ordered)
Experiment 1 (Immediate): ...
Experiment 2 (Short-term): ...
Experiment 3 (If above confirms): ...

5. IND STRATEGY IMPLICATION
What does this mean for Restinguo's path to IND? Does this change timeline or approach?

6. QUALITY ASSESSMENT
Are these results publication-quality? What would strengthen them?"""

    return drafter.opus(prompt, RESULT_INTERPRETATION_SYSTEM, max_tokens=2500, preprocess=False)


def generate_experiment_plan(
    research_question: str,
    hypothesis_id: str | None = None,
) -> str:
    """Generate a brief experiment plan using Opus."""
    hypothesis_context = ""
    if hypothesis_id:
        hyp = db.get_hypothesis(hypothesis_id)
        if hyp:
            hypothesis_context = f"\nThis experiment addresses hypothesis: {hyp['statement']}"

    prompt = f"""Design a brief experimental plan for Restinguo:

RESEARCH QUESTION: {research_question}
{hypothesis_context}

Provide:
1. Experimental approach (2-3 sentences)
2. Key readouts
3. Expected timeline
4. Resource requirements
5. Go/No-go decision criteria

Keep it concise — this is a planning document, not a full protocol."""

    return drafter.opus(prompt, RESULT_INTERPRETATION_SYSTEM, max_tokens=800)


STATUS_OPTIONS = ["Planned", "In Progress", "Complete", "Failed"]

STATUS_COLORS = {
    "Planned": "#4A90D9",
    "In Progress": "#F5A623",
    "Complete": "#7ED321",
    "Failed": "#D0021B",
}
