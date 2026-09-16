"""Thresholds for the scope-drift opportunity mapper.

Analytical inputs and versioned tables live in BigQuery. Presentation artifacts
and run logs are written under ``scope_drift_outputs/opportunities``; see
``opportunities.paths``.
"""

from __future__ import annotations

from .paths import REPO

DEFAULT_RUN = "20260721_122750"

# Citation-network level used as the "community" unit. macro has only 7 clusters
# in a full run, which is too coarse to name or launch against; meso (~406) is
# the section-shaped level and micro (~3031) is the drill-down.
COMMUNITY_LEVEL = "meso"
DRILLDOWN_LEVEL = "micro"
COMMUNITY_LEVELS = ("macro", "meso", "micro")

# Baseline is derived from the run when this year is absent from the data.
BASELINE_YEAR = 2020
# Keep every year the run covers, including a newest year that is still
# accruing. Share and CAGR endpoints are then measured against a part-year.
DROP_PARTIAL_LATE_YEAR = False
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

# ---------------------------------------------------------------------------
# Market opportunity map (market_map.py / world_market.py)
#
# Opportunity is decided against the complete AIRAK market, never against the
# Frontiers-seeded citation ego network. Leiden communities subdivide those
# independent fields into scopes. Frontiers volume is attached afterwards and
# only selects the action: greenfield launch, consolidation, or grow existing.
# ---------------------------------------------------------------------------
MARKET_LEVEL = "micro"
AIRAK_DATASET = "ocean-breeze-tier-1.airak"
AIRAK_PUBLICATION = f"{AIRAK_DATASET}.Publication"
AIRAK_PUBLICATION_FIELD = f"{AIRAK_DATASET}.PublicationFieldOfStudy"
AIRAK_FIELD_OF_STUDY = f"{AIRAK_DATASET}.FieldOfStudy"
AIRAK_JOURNAL = f"{AIRAK_DATASET}.Journal"
FRONTIERS_PUBLISHER_ID = 1563368095744
WORLD_MARKET_TABLE = "world_market_fields"
WORLD_OPPORTUNITIES_PREFIX = "world_opportunities"
WORLD_MARKET_YEAR_FROM = 2020
WORLD_MARKET_YEAR_TO = 2026
WORLD_MARKET_BASE_YEAR = 2020
WORLD_MARKET_LAST_FULL_YEAR = 2025
# Score scale for the market-only world-field ranking (three-year papers).
WORLD_MARKET_SIZE_SCORE_REF = 100_000
# AIRAK level-1 fields are broader than Leiden communities. A field enters the
# market sieve when it is either substantial and not collapsing, or at least
# viable and gaining share of world output. These are market-only thresholds.
WORLD_FIELD_MIN_ANNUAL = 4_000
WORLD_FIELD_LARGE_ANNUAL = 20_000
# Below this Frontiers volume over three full years, the action is greenfield.
# This threshold never enters opportunity qualification or ranking.
WORLD_GREENFIELD_MAX_FI_3Y = 30

# Every year the run covers is kept, including a newest year that is still
# accruing. Dropping it threw away the most decision-relevant data; using it
# raw is worse, because the run was exported part-way through the year and
# every community then reads as collapsing at once. Scaling it up to a
# full-year equivalent is worse again: any factor drawn from prior-year volume
# has that period's growth baked into it, which drags every growth rate toward
# zero. So growth compares the same calendar months in every year and volume
# counts every paper — see `market_map.resolve_growth_months`.
#
# Publication dates accrue for weeks after the fact, so the newest year's last
# month or two are under-reported. A trailing month holding less than this
# share of that year's peak month is treated as not yet in, and sets the
# month cut-off growth is measured to.
MARKET_MONTH_REPORTED_RATIO = 0.5
# How much literature has to exist per year, published anywhere by anyone,
# before a community can carry a title or a section of one. A statement about
# the field, carrying no Frontiers term: whether Frontiers already publishes
# here is the separate coverage axis below, and mixing the two is what let a
# 561-paper community be proposed as a journal on 20 Frontiers papers.
UNIT_JOURNAL_MIN_GLOBAL_PER_YEAR = 500
UNIT_SECTION_MIN_GLOBAL_PER_YEAR = 150
# The window every `*_3y` column is summed over.
WINDOW_YEARS = 3
# Ignore communities too small to support even a section.
MARKET_MIN_3Y = UNIT_SECTION_MIN_GLOBAL_PER_YEAR * WINDOW_YEARS
# "Large" = global papers in the 3y window at or above this, which is the
# journal floor: a community big enough to carry a title is worth looking at
# whether or not it is also gaining share of world output. These are the same
# number on purpose — `launch_units.calibrate_bands` reads its band floors from
# here so the size a launch needs and the size that counts as an opportunity
# cannot drift apart.
MARKET_LARGE_3Y = UNIT_JOURNAL_MIN_GLOBAL_PER_YEAR * WINDOW_YEARS
# Reference size for the volume term in `opportunity_score`. A scale, not a
# gate: tying that term to `MARKET_LARGE_3Y` now that the gate sits at the
# journal floor would put every community above ~15,000 papers on the same
# capped size factor and flatten the ranking.
MARKET_SIZE_SCORE_REF = 10_000
# Fallback journal/section volume bands, in global papers per 3y window. These
# are only used when band calibration against the existing portfolio fails —
# see `launch_units.calibrate_bands`, which derives them from the addressable
# market of journals and sections Frontiers already runs.
MARKET_LAUNCHABLE_MIN_3Y = 5_000
MARKET_LAUNCHABLE_MAX_3Y = 50_000
# "Growing" = gaining share of world output, not just growing. The corpus
# itself grows ~3.5%/yr on this run measured like-for-like, so absolute CAGR
# alone flags communities that are actually losing ground. Threshold is CAGR
# in excess of the corpus CAGR.
MARKET_EXCESS_CAGR = 0.02
# Being large is enough to be an opportunity, but not while the field is
# emptying out: formative assessment is an 88,000-paper community losing 25%
# of its share of world output a year, and nothing should propose a journal
# into that. Launches are withheld below this excess CAGR; the community still
# appears with its numbers so the decline is visible rather than filtered away.
MARKET_DECLINE_EXCESS_CAGR = -0.05
# A growth ratio needs a base endpoint big enough to be a rate rather than
# noise: 50 -> 500 papers reads as 216%/yr and says nothing. Communities below
# this can still qualify on size, just not on growth. Applied to the
# like-for-like base slice, which is the endpoint that forms the ratio.
#
# This only damps the problem. The run spans 2023-2026, so growth is a
# three-step ratio and stays fragile however the base is gated; a community
# that gained citation links late in the window looks like a new field.
# Exporting more years is the real fix.
MARKET_GROWTH_MIN_BASE = 300
# Whitespace and coverage are judged against Frontiers' own share of the
# corpus (~1.6%), not an absolute number: `whitespace` is below this multiple
# of the portfolio baseline, `covered` is at or above the second multiple.
MARKET_WHITESPACE_RATIO = 0.5
MARKET_COVERED_RATIO = 1.0

# ---------------------------------------------------------------------------
# Launch units (launch_units.py)
#
# A journal is not a micro community. There are ~3,031 micro communities
# against Frontiers' ~1,500 specialty sections, and ~406 meso communities
# against ~220 journals — micro is section-shaped and meso is journal-shaped.
# Micro names bear that out ("Object detection", "Learning to rank") next to
# meso ("Haematology", "Materials Science"). So a journal unit is a whole meso
# community or a bundle of micro communities under one meso parent, and a
# section unit is a single micro community or a small bundle of them.
# ---------------------------------------------------------------------------
UNIT_JOURNAL_LEVEL = "meso"
UNIT_SECTION_LEVEL = "micro"
# Bundles only ever form inside one meso parent: micro communities in different
# parents are not adjacent in the citation graph and would make an incoherent
# journal. Size is the guard on what a bundle may be, not member count, so a
# single journal-sized child is a valid bundle; this only caps how many topics
# one proposal may staple together before it stops being describable.
BUNDLE_MAX_MEMBERS = 8
# The band floors are the shared global publication rates defined in the market
# block above (`MARKET_LARGE_3Y` for a journal, `MARKET_MIN_3Y` for a section).
# Size alone no longer decides what a section is, though: see
# `launch_units.resolve_relative_sections`, where a micro community is a
# section candidate because its parent has a home — a journal proposed in the
# same run, or a live title that owns the parent — whatever its own size.
# Top of the journal band, as a percentile of the addressable market of the
# live titles that clear `PAPER_FLOOR_JOURNAL`. Unlike the floor this does look
# at the portfolio, because it answers a different question — how broad a
# community has one title ever actually covered? Wide on purpose: a sanity
# bound to stop 300k-paper clusters being proposed as one journal, not a
# scoring term.
BAND_HIGH_PCT = 90.0

# --- ownership vs coverage -------------------------------------------------
# Presence has two independent axes and conflating them is what produced
# "already publish" for communities Frontiers barely touches.
#
#   ownership  which Frontiers title, if any, actually owns the community —
#              and whether the work belongs there (core) or arrived by drift
#   coverage   how Frontiers' share of the global community compares to its
#              share of world output (under-indexed / at par / over-indexed)
#
# A journal owns a community when it holds this share of Frontiers' output
# there. Below it, the community is split across titles and nobody owns it.
OWNED_MIN_FI_SHARE = 0.40
# Frontiers papers in a community below this are too few to read an owner from.
UNIT_MIN_FI_PAPERS = 10
# Volume in a community that was not part of the journal's baseline primary set
# is drift, not core scope. High out-of-scope rate says the same thing about
# work the journal does consider its own.
DRIFT_OOS_PCT = 45.0
# A unit is *characterised* by drift only when most of what Frontiers prints
# there arrived that way. In a 290,000-paper community some title will always
# have a section's worth of off-baseline papers, and treating that as the
# unit's identity buried genuine launch candidates under "reroute". Drifting
# titles are still listed on every unit in `drift_journals`.
DRIFT_UNIT_SHARE = 0.5

# L2 topics (written by taxonomy_naming as cluster_l2_topics_{level}_{ts}).
# Communities are named at L1, which is reused across many clusters, so the
# launch unit is a (community, L2 topic) pair taken from the drilldown level.
# A topic must hold this share of its drilldown cluster to count as that
# cluster's topic — below it no single L2 term dominates and the argmax is noise.
L2_TOPICS_PREFIX = "cluster_l2_topics"
L2_SHARE_FLOOR = 0.10
# Clusters where no single L2 term clears the floor are genuinely mixed, so
# they get a compound label built from their leading terms rather than falling
# back to a reused L1 name. The floor still governs the single-topic name.
L2_COMPOUND_TERMS = 3
# Minimum Frontiers papers in the 3y window for a (journal, community, topic) row.
TOPIC_MIN_PAPERS = 10

TOPIC_JACCARD_HOME = 0.40
PARENT_JACCARD_OWN = 0.18
DOMAIN_HIT_ON_BRAND = 0.25
SECOND_FIELD_MIN = 0.30
# Minimum label-to-subfield token overlap before a market subfield is named.
# Without a floor the argmax matches on generic words: "Research impact
# assessment" -> "Safety Research", "Control strategies and integrated parasite
# management" -> "Control and Systems Engineering". Below this, field1 is left
# null so a bad match becomes no match.
FIELD_MATCH_MIN_JACCARD = 0.30
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
