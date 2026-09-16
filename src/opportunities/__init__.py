"""Scope-drift opportunity mapper.

Analytical tables live in BigQuery. Local JSON, Excel and log artifacts live
under ``scope_drift_outputs/opportunities``.
"""

from .config import (
    BQ_OUT_DATASET,
    BQ_PROJECT,
    COMMUNITY_LEVEL,
    DEFAULT_RUN,
    DRILLDOWN_LEVEL,
)

__all__ = [
    "DEFAULT_RUN",
    "BQ_PROJECT",
    "BQ_OUT_DATASET",
    "COMMUNITY_LEVEL",
    "DRILLDOWN_LEVEL",
]
