"""
Sprinklr Paid Advertising — Frontiers Media SA.

Usage:
    from paid_ads import query_global_summary, query_by_group, query_raw
    
    rows = query_global_summary(start_ms=1772492400000, end_ms=1775080799999)
"""

from client import build_payload, post_report, parse_response

# ── Frontiers account & campaign constants ────────────────────────────
ACCOUNT_IDS = [1719371, 1719385]
CAMPAIGN_ID = "26608_44"

PAID_INITIATIVE_IDS = [
    "695bca7ead0aea15c0c28bdc", "695d33692edfeb0b95c089ae", "695cf5122edfeb0b9567a10e",
    "LINKEDIN_881500814", "695bd7c1ad0aea15c0d00ef9", "695be5c1ad0aea15c0df506f",
    "6964ddf12408f5091fb810fa", "696656ff2408f5091f657d1f", "6964f0532408f5091fd13f5b",
    "69737eef236134032f6570b2", "69735012236134032f3fc082", "6968c7902408f5091fbec7d1",
    "6985cf621437df297f93c5c8", "698308af9ec03f20865580db", "6979d5a28f044f17e0c5ba3e",
    "696a19ea2408f5091ff42999", "6970b006236134032f855cbe", "699db103a787ac0c5b2a7e05",
    "699dc3b3a787ac0c5b496774", "699ed7af3e5d9f55b8a0fa04", "679cdc11b474af26d0ad2f47",
    "67a6286ae8bfd41444d94ca5", "678a65550d0a57562f0876b3", "67a631a9e8bfd41444ea2ddc",
    "67af477916f35c13914fc839", "67af11fc16f35c139101a764", "67af599116f35c139170f65d",
    "67b34de606bce9020d6fbd4c", "67b5e3e02876310a9a96c56c", "67bde10760a6800dfec87428",
    "67b5b3b62876310a9a4a8a4f", "67beddc23d940043d53a157a", "67bef8d43d940043d55d2435",
    "67cb10c419c68e6c255f0da9", "67d3fd3e3cefb265381646a9", "67d3f86d3cefb26538125e04",
    "67dd4b88fe25b72ae1aadada", "67e2b4906c92d84327d5860b", "67e2c55a6c92d84327f6c434",
    "67e2c12a6c92d84327ee849b", "67ed0a89367924723e6c86e8", "67efe54df44ddb46426d17c1",
    "6800d817c2c9337386366b7f", "67efbcc8f44ddb46423b1a8b", "67ebc1be1d792f5090081740",
    "67f7d212ce34dc606ff3a892", "6800f9f4846e460f734716bb", "6808f82d3787cb390f305769",
    "680b96ce72f08a4636198ce4", "6808ea523787cb390f19b03b", "680b47d072f08a4636b0540f",
    "680107f0846e460f735cf8e2", "681cae256f57de7184e2ed33", "682368115059792180e8416e",
    "681e17a39a405c05b6f2e37e", "680b8b7772f08a46360ae39d", "68370b933a8a7c125b7e2bdf",
    "682da4f9662e760fb83e0ff8", "682dcee2662e760fb873b0dc", "6842e57f33504a42c864cc8c",
    "6842ea3333504a42c86dbebf", "685d2a90ea62e30ee5e2dd01", "685d2e37ea62e30ee5e9a1e4",
    "68623e89253e0d3f9f60a94e", "686e847b4f52101a51de7516", "686e7d9f4f52101a51d0a74f",
    "688233ba8db9d312fd1932b8", "6880a5278db9d312fd8f77da", "6890be9228d1cf564694aa01",
    "6878b1ebf18fe920e08dd6c4", "6892195a1499574594fd2404", "6890b88428d1cf5646897248",
    "68949a731499574594d6f445", "6891d983b0e1e842c2b913f1", "689db9cfb1ca02190ecdd8a1",
    "FACEBOOK_120230504083150697", "6880a1c28db9d312fd8a2cfa", "689a0a7f0102e7351f9027a7",
    "689dfbb2b1ca02190e3fb5ac", "68a47d9fd00a6d209ef311db", "689eecb22c926c202ec9a026",
    "68a72918e681c17b94f151c5", "6899fe980102e7351f781b6d", "68b076ed75e3c7118af956e9",
    "68b009de75e3c7118a4134cb", "68b16b88ebf85b61c454c3b5", "68b07aee75e3c7118a002542",
    "68b164c2ebf85b61c44d46b8", "68b599b128ada83727c6203e", "68bac226b320c271a31c3ad8",
    "68c2cc5259a97f0be744fe8b", "68bab2b6b320c271a30c1e21", "68bab612b320c271a30f7588",
    "68bedee0e6a1e43545bfe0ec", "68bedad8e6a1e43545ba4731", "68c2a29c4818e44d1f221e48",
    "68c03d002131db61762916bd", "68c133c4c2fa2464a1f97751", "68c193551692571ac0b626fc",
    "68c1834e1692571ac09e30af", "68c039102131db6176219867", "68c024e82131db6176fe857c",
    "68c1456f66230d0d4a94710f", "68c008382131db6176d1dc23", "68c0331c2131db617616f8a0",
    "68c19ed81692571ac0c6f593", "68dbd834dded8e4080860f4d", "68c14d281692571ac05ac51e",
    "68c19c3b1692571ac0c337de", "68dbd1bddded8e40807d2121", "68dd3372768b9a3dc03f95fb",
    "68dcdcb6ef032e2aa095a97d", "68e3f86fc9f9237bb6f846c2", "68e3ed32c9f9237bb6e5742b",
    "68e3ea50c9f9237bb6e13425", "68c2c5d74818e44d1f4aa483", "68e63df0bd01361c68726908",
    "68c02c132131db61760a8ed5", "68c2a13c4818e44d1f20b6e8", "68e3f4c6c9f9237bb6f202de",
    "68ee6ad40f92bf7375327caf", "68f2080d3895913bdc835379", "68ee602d0f92bf7375205bb1",
    "68f9e0b68abc6d38d1dceb7e", "68f201ab3895913bdc7d7c5a", "6901ddac622355184af59478",
    "69038e9179d2102903a24344", "68ff910c111b3b5446641024", "6904cd297595c055fb073e6f",
    "6901f355622355184a0e3834", "690ca93db1798b5dea5664da", "68ff3774111b3b5446f786d4",
    "690cb37db1798b5dea630590", "690dc3e4b1798b5dea6a4040", "6913049c24c4b228b267a203",
    "691f405a31b54a0dae5eb056", "691f3c3531b54a0dae596402", "68adc862a68e946d99291a5f",
    "692986ccc38a303ea499487a", "69286dd0c38a303ea4cceb4a", "6929c13dc38a303ea4d1ee4f",
    "68efa89182dd2b164a50018c", "6929de14c38a303ea4f8bf6e", "692833a0c38a303ea47f3432",
    "69398bfa46903d5f150650b6", "693839b546903d5f1589c935", "69382cca46903d5f15786059",
    "693aa199a8f63c700a043bdb",
]

# ── Standard filters ──────────────────────────────────────────────────
FILTER_ACCOUNTS = {
    "dimensionName": "accountIds",
    "filterType": "IN",
    "values": ACCOUNT_IDS,
    "details": {
        "reportName": "DAILY_AD_STAT",
        "contentType": "DB_FILTER",
        "DB_FILTER_REPORT_NAME": "ADS_CHECKLIST_STAT",
        "HAS_ALERT": False,
        "STATS_LEVEL": "ACCOUNT",
        "groupingSupported": True,
        "displayNameForWarning": "Ad Account",
        "HAS_TOOLTIP_DATA": True,
        "includeInactive": False,
        "uniqueId": "D_ACCOUNTIDS",
    },
}

FILTER_CAMPAIGN = {
    "dimensionName": "CAMPAIGN_ID",
    "filterType": "IN",
    "values": [CAMPAIGN_ID],
    "details": {
        "contentType": "DB_FILTER",
        "DB_FILTER_REPORT_NAME": "POST_INSIGHTS",
        "HAS_ALERT": False,
        "displayNameForWarning": "Campaign",
        "HAS_TOOLTIP_DATA": True,
        "uniqueId": "D_CAMPAIGN_ID",
    },
}

FILTER_INITIATIVES = {
    "dimensionName": "paidInitiativeId",
    "filterType": "IN",
    "values": PAID_INITIATIVE_IDS,
    "details": {
        "reportName": "PAID_INITIATIVE",
        "contentType": "DB_FILTER",
        "TEXT_FILTER": True,
        "ALLOWED_FILTER_TYPES": ["IN", "NIN", "STARTS_WITH", "TEXT_CONTAINS", "ENDS_WITH", "EXISTS"],
        "DB_FILTER_REPORT_NAME": "PAID_INITIATIVE",
        "displayNameForWarning": "Paid Initiative Name",
        "uniqueId": "D_PAIDINITIATIVEID",
    },
}

# ── Standard projections ─────────────────────────────────────────────
PROJECTIONS = [
    {"heading": "SPENT",            "measurementName": "spent",                                "aggregateFunction": "SUM", "details": {}},
    {"heading": "IMPRESSIONS",      "measurementName": "impressions",                          "aggregateFunction": "SUM", "details": {}},
    {"heading": "CPM",              "measurementName": "CPM",                                  "aggregateFunction": "SUM", "details": {}},
    {"heading": "CLICKS",           "measurementName": "clicks",                               "aggregateFunction": "SUM", "details": {}},
    {"heading": "CTR",              "measurementName": "CTR",                                  "aggregateFunction": "SUM", "details": {}},
    {"heading": "CPC",              "measurementName": "CPC",                                  "aggregateFunction": "SUM", "details": {}},
    {"heading": "ENGAGEMENTS",      "measurementName": "ACM_GLOBAL_TOTAL_ENGAGEMENTS_1851",    "aggregateFunction": "SUM", "details": {}},
    {"heading": "ENGAGEMENT_RATE",  "measurementName": "ENGAGEMENT_RATE",                      "aggregateFunction": "SUM", "details": {}},
    {"heading": "VIDEO_VIEWS",      "measurementName": "ACM_GLOBAL_VIDEO_VIEWS_5748",          "aggregateFunction": "SUM", "details": {}},
    {"heading": "VIDEO_VIEWS_50",   "measurementName": "ACM_GLOBAL_VIDEO_VIEWS_TO_50_733",     "aggregateFunction": "SUM", "details": {}},
]

# ── Default filters builder ──────────────────────────────────────────

def _default_filters(include_initiatives: bool = True) -> list[dict]:
    filters = [FILTER_ACCOUNTS, FILTER_CAMPAIGN]
    if include_initiatives:
        filters.append(FILTER_INITIATIVES)
    return filters

# ── Public API ────────────────────────────────────────────────────────

def query_global_summary(
    start_ms: int,
    end_ms: int,
    include_initiatives: bool = True,
) -> list[dict]:
    """Single-row global summary (no groupBy). Returns list with one dict."""
    payload = build_payload(
        report="DAILY_AD_STAT",
        engine="PAID",
        start_ms=start_ms,
        end_ms=end_ms,
        filters=_default_filters(include_initiatives),
        projections=PROJECTIONS,
    )
    return parse_response(post_report(payload))


def query_by_group(
    start_ms: int,
    end_ms: int,
    group_bys: list[dict],
    include_initiatives: bool = True,
    page: int = 0,
    page_size: int = 100,
) -> list[dict]:
    """Metrics broken down by one or more groupBy dimensions. Returns list of dicts."""
    payload = build_payload(
        report="DAILY_AD_STAT",
        engine="PAID",
        start_ms=start_ms,
        end_ms=end_ms,
        filters=_default_filters(include_initiatives),
        projections=PROJECTIONS,
        group_bys=group_bys,
        page=page,
        page_size=page_size,
    )
    return parse_response(post_report(payload))


def query_raw(
    start_ms: int,
    end_ms: int,
    group_bys=None,
    filters=None,
    projections=None,
    include_initiatives: bool = True,
    page: int = 0,
    page_size: int = 10,
) -> dict:
    """Full-control query. Returns raw {headings, rows} dict."""
    payload = build_payload(
        report="DAILY_AD_STAT",
        engine="PAID",
        start_ms=start_ms,
        end_ms=end_ms,
        filters=filters or _default_filters(include_initiatives),
        projections=projections or PROJECTIONS,
        group_bys=group_bys,
        page=page,
        page_size=page_size,
    )
    return post_report(payload)


# ── Quick test ────────────────────────────────────────────────────────
if __name__ == "__main__":
    rows = query_global_summary(start_ms=1772492400000, end_ms=1775080799999)
    for k, v in rows[0].items():
        print(f"  {k}: {v}")
