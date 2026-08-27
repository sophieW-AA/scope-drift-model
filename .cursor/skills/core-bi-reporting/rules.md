# Rules: BigQuery + business glossary (glossary.yml)

## BigQuery (execution and column docs)

1. **Project/dataset:** Default analytical scope is `ocean-breeze-tier-1.reporting_data_mart`.
2. **Column descriptions:** Treat **BigQuery schema `description`** on fields as the technical definition when writing or explaining SQL. Refresh understanding after warehouse DDL changes.
3. **Auth:** Use Application Default Credentials or `GOOGLE_APPLICATION_CREDENTIALS`; never embed secrets in prompts or committed files.
4. **Cost:** Prefer bounded queries (`LIMIT`, filtered partitions, selective columns) for exploration.

## KPI / governance

1. **KPI definitions:** **Always** take KPI / metric meaning and which warehouse tables and columns apply **only** from [glossary.yml](glossary.yml): for each term, use the **`description`** plus **`referenced_tables`** (table `name` and nested **`columns`** where present). Do not use DataHub MCP or other DataHub surfaces to resolve business KPI definitions when following these rules.
2. **Not literal SQL:** [glossary.yml](glossary.yml) descriptions are not runnable as-is—translate them into explicit predicates and date columns on the **referenced table(s)** from the matching term; use [semantic-layer.md](semantic-layer.md) for safe joins when multiple tables are involved.
3. **Sync:** Glossary and warehouse can drift; if [glossary.yml](glossary.yml) and BigQuery metadata or observed data conflict, treat **`glossary.yml` as the business definition** for KPI naming and rules, use **BigQuery schema `description`** for technical column semantics, and escalate or reconcile per your team process.

## Required workflow check for every user question

- Before drafting SQL or finalizing an answer, **always review [examples.md](examples.md)** and align the approach with the closest applicable pattern.
- Use [examples.md](examples.md) together with [rules.md](rules.md), [glossary.yml](glossary.yml), and [semantic-layer.md](semantic-layer.md) to keep joins, defaults, and KPI logic consistent.

## Submitted-articles date choice

- **`stage_date_received_by_journal`:**  default for “submission.”
- **`stage_date_submitted`:**only when the user or the relevant term in [glossary.yml](glossary.yml) explicitly requires stage_date_submitted.”
- Ask once if unclear.

## Segment choice

- **`journal_segment`:** default for “segment” kpi metrics aggregations.
- **`segment`:** only when the user explicitly requires “by section segment.”
- Ask once if unclear.


## Editorial Board Members clarification

- Editorial Board Members (unique users) as default when user asks for editorial board member counts
- Ask if user wants to see Editorial Board Members (roles) as second possibility
- Always ask if user wants to see all or only active records

## Editorial Board Members and articles activity

- When asked for articles submitted/accepted/rejected per editorial board member, make sure only are counted articles after the first **`join_date`**
- Ask if user wants to see all articles

## Country & Region attribution

- When asked about count of a kpi by country or region attributes, always pick by default the country/region of the same table. As example 'count of articles submitted by Region 8' use **`country5_regions_bin`** column in `ocean-breeze-tier-1.reporting_data_mart.article`. Other example 'count of research topics posted by Region 5' use **`country5_regions_bin`** column in `ocean-breeze-tier-1.reporting_data_mart.research_topic`
- When asked by articles counts by country or region attributes, always ask if the result has to be grouped by article's country/region as specified previously or it needs to grouped by author's country or region, in this case pick those fields from `ocean-breeze-tier-1.reporting_data_mart.author`

## Organization attribution

- When asked about count of a kpi by organization attributes, always pick by default the organization of the same table. As example 'count of articles submitted by organization' use **`main_corresponding_author_primary_organization`**  column in `ocean-breeze-tier-1.reporting_data_mart.article`. For `ocean-breeze-tier-1.reporting_data_mart.research_topic` use **`organization`**.
- When asked by articles counts by organization, always ask if the result has to be grouped by article's organization as specified previously or it needs to grouped by author's organization, in this case pick **`user_primary_organization`** field from `ocean-breeze-tier-1.reporting_data_mart.author`
- Always ask if user wants to see the results instead by the top parent highest ranked organization. In this case, for instance for 'count of articles submitted by organization' use **`authors_organizations_highest_rank_frontiers_priority_organization`** column in `ocean-breeze-tier-1.reporting_data_mart.article`. If its based on author's top parent highest ranked organization take that column from `ocean-breeze-tier-1.reporting_data_mart.author`
- As results by organization can results in a long list, limit by default to show only Top 50 organizations based on descendant order of count of articles 

## HIndex bins and Influence bins attribution

- When asked about count of a kpi by H Index or Influence, always pick by default the bins fields of the same table, i.e. h_index_bins, influence_bins. As example 'count of articles submitted by h index' use **`h_index_bins`** column in `ocean-breeze-tier-1.reporting_data_mart.article`. Other example 'count of research topics posted by H index' use **`hindex_bins`** column in `ocean-breeze-tier-1.reporting_data_mart.research_topic`
- When asked by articles counts by h_index or influence bins attributes, always ask if the result has to be grouped by article's h_index or influence bins  as specified previously or it needs to grouped by author's h_index or influence bins attributes, in this case pick those fields from `ocean-breeze-tier-1.reporting_data_mart.author`

## Join safety

- Default article KPIs are **article-grain** unless the question requires author- or org-grain.
- See [semantic-layer.md](semantic-layer.md) before joining `author` or bridges.

## Frontiers scope

- Unless the user asks for all spaces, confirm whether **`space_id = 1`** applies to the request.
