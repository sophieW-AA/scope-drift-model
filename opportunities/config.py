"""Thresholds for the scope-drift opportunity mapper (v2).

Every input and output is BigQuery. There are no local file paths here — see
`seed_jd.py` for the one-off admin load of the JD opportunities reference table.
"""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

DEFAULT_RUN = "20260721_122750"

# Citation-network level used as the "community" unit. macro has only 7 clusters
# in a full run, which is too coarse to name or launch against; meso (~406) is
# the section-shaped level and micro (~3031) is the drill-down.
COMMUNITY_LEVEL = "meso"
DRILLDOWN_LEVEL = "micro"
COMMUNITY_LEVELS = ("macro", "meso", "micro")

# Baseline is derived from the run when this year is absent from the data.
BASELINE_YEAR = 2020
# Exclude the newest year when it is still accruing, so share/CAGR endpoints
# are not measured against a partial year.
DROP_PARTIAL_LATE_YEAR = True
PARTIAL_YEAR_RATIO = 0.85
PRIMARY_COVERAGE = 0.80
MIN_PAPERS_YEAR = 10
MIN_COMMUNITY_PAPERS = 10

# Share-of-title gates (3-year window ending at max year in the run)
SECTION_SHARE = 0.08
JOURNAL_SHARE = 0.12
PAPER_FLOOR_SECTION = 40
PAPER_FLOOR_JOURNAL = 200
LARGE_JOURNAL_3Y = 500
VERY_LARGE_JOURNAL_3Y = 1500
SHARE_CAGR_SHIFT = 0.08
SHARE_PP_SHIFT = 3.0  # percentage points vs baseline year

TOPIC_JACCARD_HOME = 0.40
PARENT_JACCARD_OWN = 0.18
DOMAIN_HIT_ON_BRAND = 0.25
SECOND_FIELD_MIN = 0.30
MARKET_MIN_ARTICLES = 10_000
MARKET_MIN_CAGR = 0.05
# OpenAlex FI share below this = thin Frontiers presence (whitespace, not "we already publish")
FI_SHARE_WHITESPACE = 0.01
WHITESPACE_JD_PATTERNS = ("Standard Opportunity", "Massive Market")

LAUNCH_CALLS = frozenset(
    {"expand_rename", "new_gated_section", "new_journal"}
)

METHODS_SHARED_RE = (
    r"\b(computer vision|deep learning|machine learning|artificial intelligence|"
    r"control systems?|autonomous systems?|nlp|natural language|cloud and security|"
    r"intelligent decision|generic ai|pattern recognition)\b"
)

OFFBRAND_TITLE_RE = (
    r"privacy|cyber.?physical|image fusion|traffic|cancer imaging|pneumonia|"
    r"steel.?defect|vehicle re-?id|face restoration|geolog|thermal|"
    r"organic chem|immunotherap|management science|remote.?sens|"
    r"yolo|x-?ray"
)

BQ_PROJECT = "ocean-tech-adv-analytics-c-tfs"
BQ_DATASET = "raw_citation_network_data"
BQ_OUT_DATASET = "opportunity_mapping"
BQ_LABEL_DATASET = "taxonomy_labelling"
BQ_LOCATION = "EU"
# Reference tables that are not per-run (loaded once, reused by every run)
JD_TABLE = "jd_opportunities"
# Per-paper scope flags written by build_unified_dashboard; optional input.
PAPER_SCOPE_PREFIX = "paper_scope"
RDM_ARTICLE = "ocean-breeze-tier-1.reporting_data_mart.article"
RDM_TAXONOMY = "ocean-breeze-tier-1.reporting_data_mart.taxonomy"
RDM_RT = "ocean-breeze-tier-1.reporting_data_mart.research_topic"

JOURNAL_DOMAIN_TOKENS: dict[str, set[str]] = {
    "neurorobotics": {
        "robot",
        "neurorobotic",
        "neural",
        "embodied",
        "bci",
        "motor",
        "exoskeleton",
        "prosthetic",
        "rehabilitation",
        "humanoid",
        "semg",
        "enactive",
    },
}
