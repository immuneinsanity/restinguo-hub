"""
Experimental roadmap logic.
"""

from scientist import database as db

STAGE_NAMES = {
    1: "Target Validation",
    2: "Disease Model Development",
    3: "Efficacy Proof of Concept",
    4: "IND-Enabling Prep",
}

STAGE_DESCRIPTIONS = {
    1: "Confirm IFNAR blockade suppresses IFN signature in COPA patient cells. Establish PD biomarkers.",
    2: "Build a disease-relevant cell model. Generate COPA iPSC line and differentiate to lung organoids.",
    3: "Demonstrate dose-dependent efficacy and selectivity in the validated COPA disease model.",
    4: "Select lead biologic, design safety studies, establish CMC path.",
}

STAGE_MILESTONE = {
    1: "IFN signature confirmed and IFNAR blockade validated in patient PBMCs",
    2: "Validated COPA iPSC-derived lung organoid showing constitutive IFN activation",
    3: "Dose-response efficacy data with PD biomarker panel in COPA organoids",
    4: "IND-enabling study designs approved by scientific advisory board",
}


def get_stage_progress() -> dict[int, dict]:
    """Return per-stage completion stats."""
    by_stage = db.get_roadmap_by_stage()
    result = {}
    for stage_num, items in by_stage.items():
        total = len(items)
        done = sum(1 for i in items if i.get("completed"))
        result[stage_num] = {
            "name": STAGE_NAMES.get(stage_num, f"Stage {stage_num}"),
            "description": STAGE_DESCRIPTIONS.get(stage_num, ""),
            "milestone": STAGE_MILESTONE.get(stage_num, ""),
            "items": items,
            "total": total,
            "done": done,
            "pct": (done / total * 100) if total else 0,
            "active": done > 0 and done < total,
            "complete": done == total and total > 0,
        }
    return result


def current_stage(stage_progress: dict) -> int:
    """Return the current active stage (lowest incomplete stage)."""
    for stage_num in sorted(stage_progress.keys()):
        if not stage_progress[stage_num]["complete"]:
            return stage_num
    return max(stage_progress.keys()) if stage_progress else 1


def overall_progress(stage_progress: dict) -> float:
    total = sum(s["total"] for s in stage_progress.values())
    done = sum(s["done"] for s in stage_progress.values())
    return (done / total * 100) if total else 0
