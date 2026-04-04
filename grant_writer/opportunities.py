"""
NIH opportunity tracker — NIH Guide RSS + NIH REPORTER API.
"""

import httpx
import feedparser
from datetime import datetime
from .database import upsert_opportunity, list_opportunities


NIH_GUIDE_RSS = "https://grants.nih.gov/funding/searchGuide/search_results.cfm?all=1&type=PA&activity_code=R43&rss=1"
NIH_GUIDE_SBIR_RSS = "https://grants.nih.gov/funding/searchGuide/search_results.cfm?all=1&type=PA&activity_code=R44&rss=1"
NIH_REPORTER_URL = "https://api.reporter.nih.gov/v2/projects/search"


SBIR_KEYWORDS = [
    "rare disease", "interferonopathy", "autoimmune", "COPA", "IFNAR",
    "type I interferon", "STING", "lupus", "immunology",
]


def fetch_nih_guide_rss(url: str, label: str) -> list[dict]:
    """Parse NIH Guide RSS feed and return opportunity dicts."""
    try:
        feed = feedparser.parse(url)
    except Exception as e:
        return []

    results = []
    for entry in feed.entries:
        results.append({
            "title": entry.get("title", ""),
            "number": entry.get("id", entry.get("link", ""))[-20:],  # use tail of link as key
            "url": entry.get("link", ""),
            "posted_date": entry.get("published", ""),
            "close_date": "",
            "synopsis": entry.get("summary", "")[:500],
            "source": label,
        })
    return results


def fetch_nih_reporter_recent(limit: int = 20) -> list[dict]:
    """
    Query NIH REPORTER API for recent SBIR Phase I awards in immunology/rare disease.
    Returns opportunity-like dicts from funded project data.
    """
    payload = {
        "criteria": {
            "activity_codes": ["R43"],
            "award_amount_range": {"min_amount": 50000, "max_amount": 400000},
            "fiscal_years": [datetime.utcnow().year, datetime.utcnow().year - 1],
        },
        "offset": 0,
        "limit": limit,
        "sort_field": "project_start_date",
        "sort_order": "desc",
    }

    try:
        with httpx.Client(timeout=15) as client:
            resp = client.post(NIH_REPORTER_URL, json=payload)
            resp.raise_for_status()
            data = resp.json()
    except Exception:
        return []

    results = []
    for proj in data.get("results", []):
        results.append({
            "title": proj.get("project_title", ""),
            "number": proj.get("project_num", ""),
            "url": f"https://reporter.nih.gov/search/{proj.get('project_num', '')}",
            "posted_date": proj.get("project_start_date", ""),
            "close_date": proj.get("project_end_date", ""),
            "synopsis": (proj.get("abstract_text") or "")[:500],
            "source": "NIH REPORTER",
        })
    return results


def refresh_opportunities() -> tuple[int, str]:
    """Fetch from all sources, upsert to DB. Returns (count_new, status_msg)."""
    all_opps = []

    # NIH Guide RSS — SBIR R43
    rss_opps = fetch_nih_guide_rss(NIH_GUIDE_RSS, "NIH Guide RSS (R43)")
    all_opps.extend(rss_opps)

    # NIH REPORTER recent awards
    reporter_opps = fetch_nih_reporter_recent(20)
    all_opps.extend(reporter_opps)

    for opp in all_opps:
        try:
            upsert_opportunity(opp)
        except Exception:
            pass

    return len(all_opps), f"Fetched {len(all_opps)} opportunities ({len(rss_opps)} from NIH Guide, {len(reporter_opps)} from REPORTER)"


def get_opportunities(limit: int = 50) -> list[dict]:
    return list_opportunities(limit)


# Curated FOAs relevant to Restinguo
RELEVANT_FOAS = [
    {
        "number": "PA-24-185",
        "title": "SBIR Phase I (R43)",
        "url": "https://grants.nih.gov/grants/guide/pa-files/PA-24-185.html",
        "synopsis": "Small Business Innovation Research (SBIR) Phase I omnibus solicitation. ~$300K direct costs, 6 months.",
        "source": "Curated",
        "posted_date": "2024-01-01",
        "close_date": "2025-09-05",
    },
    {
        "number": "PA-24-186",
        "title": "STTR Phase I (R41)",
        "url": "https://grants.nih.gov/grants/guide/pa-files/PA-24-186.html",
        "synopsis": "Small Business Technology Transfer (STTR) Phase I. Requires academic partner with formal agreement.",
        "source": "Curated",
        "posted_date": "2024-01-01",
        "close_date": "2025-09-05",
    },
    {
        "number": "RFA-AR-24-xxx",
        "title": "NIAMS Rare Disease SBIR — Autoinflammatory",
        "url": "https://www.niams.nih.gov/grants-funding/funded-research/sbir-sttr",
        "synopsis": "NIAMS funds SBIR for musculoskeletal, skin, and rheumatic diseases including rare autoinflammatory conditions.",
        "source": "Curated",
        "posted_date": "",
        "close_date": "",
    },
]
