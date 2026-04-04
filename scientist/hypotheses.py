"""
Hypothesis tracker logic — AI evaluation and evidence management.
"""

from scientist import database as db
from scientist import drafter
from scientist.prompts import HYPOTHESIS_EVAL_SYSTEM

STATUS_OPTIONS = ["Open", "Testing", "Supported", "Refuted", "Uncertain"]
PRIORITY_OPTIONS = ["Critical", "High", "Medium", "Low"]

STATUS_COLORS = {
    "Open": "#4A90D9",
    "Testing": "#F5A623",
    "Supported": "#7ED321",
    "Refuted": "#D0021B",
    "Uncertain": "#9B9B9B",
}

PRIORITY_COLORS = {
    "Critical": "#D0021B",
    "High": "#F5A623",
    "Medium": "#4A90D9",
    "Low": "#9B9B9B",
}


def evaluate_hypothesis_with_opus(hypothesis: dict) -> dict:
    """
    Run Opus evaluation on a hypothesis.
    Returns a structured dict with assessment, confidence, status_recommendation, next_experiment.
    """
    evidence_for = hypothesis.get("evidence_for") or []
    evidence_against = hypothesis.get("evidence_against") or []

    prompt = f"""Evaluate this hypothesis for Restinguo's scientific program:

HYPOTHESIS: {hypothesis['statement']}
CURRENT STATUS: {hypothesis['status']}
PRIORITY: {hypothesis['priority']}

EVIDENCE FOR ({len(evidence_for)} items):
{chr(10).join(f'- {e}' for e in evidence_for) if evidence_for else '- None recorded'}

EVIDENCE AGAINST ({len(evidence_against)} items):
{chr(10).join(f'- {e}' for e in evidence_against) if evidence_against else '- None recorded'}

KEY EXPERIMENT IDENTIFIED: {hypothesis.get('key_experiment', 'Not yet defined')}

Please provide:
1. EVIDENCE ASSESSMENT: Evaluate the strength and quality of current evidence
2. KEY UNCERTAINTIES: What do we still not know?
3. CONFIDENCE SCORE: 0-100% confidence in the hypothesis as stated
4. STATUS RECOMMENDATION: Should the status change? (Open/Testing/Supported/Refuted/Uncertain)
5. RECOMMENDED NEXT EXPERIMENT: The single most informative experiment right now
6. ADJACENT HYPOTHESES: What other Restinguo hypotheses would this experiment also address?
7. STRATEGIC IMPLICATION: What does the current state of this hypothesis mean for the IND timeline?"""

    return drafter.opus(prompt, HYPOTHESIS_EVAL_SYSTEM, max_tokens=2000)


def suggest_key_experiment(hypothesis_statement: str) -> str:
    """Ask Opus to suggest the key settling experiment for a hypothesis."""
    prompt = f"""For this hypothesis: "{hypothesis_statement}"

What is the single most informative, practically feasible experiment that would most definitively
settle whether this hypothesis is true or false?

Consider:
- Availability of COPA patient samples (limited — ultra-rare disease)
- No in-house animal facility (must use CRO or collaborator)
- Startup resource constraints
- Anifrolumab/anti-IFNAR1 Ab as available reagents
- Anthony Shum at UCSF as potential collaborator

Describe the experiment in 2-4 sentences. Be specific about cell type, reagents, and readout."""

    return drafter.opus(prompt, HYPOTHESIS_EVAL_SYSTEM, max_tokens=500)


def get_hypotheses_by_status() -> dict[str, list[dict]]:
    """Return hypotheses grouped by status for kanban view."""
    hypotheses = db.get_all_hypotheses()
    grouped: dict[str, list[dict]] = {s: [] for s in STATUS_OPTIONS}
    for h in hypotheses:
        status = h.get("status", "Open")
        grouped.setdefault(status, []).append(h)
    return grouped


def get_critical_open_hypotheses() -> list[dict]:
    hypotheses = db.get_all_hypotheses()
    return [
        h for h in hypotheses
        if h.get("status") in ("Open", "Testing")
        and h.get("priority") in ("Critical", "High")
    ]
