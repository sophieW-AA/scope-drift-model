# Data model: `ocean-breeze-tier-1.reporting_data_mart`

**Canonical structured model (PKs, FKs, tables):** [ocean-breeze-tier-1.reporting_data_mart_NDM_V1.yaml](https://github.com/frontiersin/analytical-data-model/blob/main/dataset-model-NDM/ocean-breeze-tier-1.reporting_data_mart_NDM_V1.yaml) in [`frontiersin/analytical-data-model`](https://github.com/frontiersin/analytical-data-model/tree/main/dataset-model-NDM) (`dataset-model-NDM/`). New releases use the same path with a higher `NDM_V{n}` filename. If anything here conflicts with that YAML, **trust the YAML** for keys and relationships.

This file describes **grain**, **entity relationships**, and **safe join paths** so queries do not duplicate rows or mis-attribute metrics. **Column-level descriptions** should be read from **BigQuery** (table schema `description` or `INFORMATION_SCHEMA`), not duplicated here at length.

## Dataset scope

- All tables below live under `` `ocean-breeze-tier-1.reporting_data_mart` `` unless noted.

## Core grains

| Table / subject | Grain | Primary key (typical) |
|-----------------|-------|------------------------|
| `article` | One row per article (reporting grain for lifecycle KPIs) | `article_id` |
| `journal` | One row per taxonomy_id | `taxonomy_id` |
| `taxonomy` | One row per taxonomy node | `taxonomy_id` |
| `research_topic` | One row per research topic | `research_topic_id` |
| `author` | One row per author–article role row | composite: `article_id` + `author_id` pattern |
| `author_organizations` | Bridge: author ↔ organization | `author_id`, `organization_id` |
| `organization` | One row per organization | `organization_id` |
| `person` | One row per person profile row | `person_id` / `person_user_id` (see BQ docs) |
| `spaces` | One row per publishing space | `space_id` |

## Conformed dimensions

These tables are **conformed dimensions**: shared reference attributes with stable keys, reused across subject areas so the same entity (country, organization,  taxonomy node, space, person) is modeled once and joined consistently. Confirm join columns in the NDM YAML or BigQuery schema when a path is not listed below.

**Conformed dimension tables:**

- `country_metrics`
- `organization`
- `taxonomy`
- `spaces`
- `person`

**Typical joins (article-centric and related paths):**

- **Space / tenant:** `article.space_id` → `spaces.space_id`. Frontiers-only analytics often use `space_id = 1` when that is the business rule.
- **Taxonomy:** `article.taxonomy_id` → `taxonomy.taxonomy_id`. When a question is asked to get article counts using more information about journal attributes (e.g. `journal_segment`), always use `taxonomy` table joining via `taxonomy_id`to avoid duplicates using `journal_id`. Same is valid for joining other entities like `research_topic` to group count of research topics by  `journal_segment`
- **Organization:** `author_organizations.organization_id` → `organization.organization_id` (see **Author and organization paths** below); other facts may expose `organization_id`—use the key named on the fact side.
- **Country metrics:** join `country_metrics` on the foreign key present on the driving table (e.g. country identifier); do not assume column names beyond what the NDM or BQ metadata documents.
- **Person:** join `person` on `person_id`, `person_user_id`, or other documented keys from the driving table (see BQ schema for grain and which identifier applies).


## Recommended join paths (article-centric)

Use **explicit** joins on the keys below; avoid guessing join columns.

```
article.taxonomy_id          = taxonomy.taxonomy_id
article.article_research_topic_id = research_topic.research_topic_id
article.space_id             = spaces.space_id
```


## Author and organization paths (high risk of inflation)

Author data is often **one-to-many** from the article perspective (multiple authors per article).

```
article.article_id     = author.article_id
author.author_id       = author_organizations.author_id
author_organizations.organization_id = organization.organization_id
```

**Rules:**

- When counting **articles**, either pre-aggregate at `article_id` before joining to `author`, or use `COUNT(DISTINCT article.article_id)`.
- Joining `article` → `author` → `organization` without care can **multiply** article rows—never use bare `COUNT(*)` on such joins for article KPIs without deduplication.

## Lifecycle dates (article)

Canonical event timestamps on `article` (confirm exact semantics in BigQuery column descriptions):

| Business event | Typical column |
|----------------|----------------|
| Submitted (first submission) | `stage_date_submitted` |
| Received by journal | `stage_date_received_by_journal` |
| Accepted | `stage_date_accepted` |
| Published | `stage_date_published` |

## Research topic table

- Join from article when needed: `article.article_research_topic_id` = `research_topic.research_topic_id`.
- Time-to-event for “research topics posted” style metrics often uses `research_topic.online_date` (verify in BQ schema).

## Anti-patterns

- **Cross join** between large dimensions without join keys.
- **Many-to-many** explosion: `article` × `author` without `DISTINCT` article keys when the question is article-level.
- Mixing **submission year** and **acceptance year** in one ratio without defining cohort rules.

## When descriptions differ

If a **DataHub glossary** definition and a **BigQuery column description** appear to conflict, treat **glossary** as the business authority for *what the KPI means*, and **BigQuery** as the authority for *what the column stores*—escalate stewardship conflicts to data owners.
