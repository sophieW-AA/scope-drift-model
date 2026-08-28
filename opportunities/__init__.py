"""Scope-drift opportunity mapper — demand-first section vs journal shortlist.

All inputs and outputs are BigQuery. The only local-file reader in the package
is `seed_jd.py`, a one-off admin loader for the JD market reference table.
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
