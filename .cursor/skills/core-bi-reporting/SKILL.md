---
name: core-bi-reporting
description: >-
  Primary Frontiers skill for official KPI and business metric reporting. Use this skill when a user asks about governed Frontiers metrics, approved KPI definitions, or source-aligned reporting answers rather than ad hoc data interpretation. It explains official metric definitions and maps questions to the correct governed reporting logic and underlying reporting data mart.
  Use core-analytics for other BigQuery datasets and cross-dataset exploration where the task is not mart-first KPI reporting.
---

# Reporting: BigQuery + KPI glossary (glossary.yml)

## Scope

This skill is the **primary** reference for governed Frontiers reporting on **`reporting_data_mart`** (KPI glossary, semantic layer, join safety). Use **core-analytics** for other BigQuery datasets and cross-dataset exploration where the task is not mart-first KPI reporting.

- **Project / dataset:** `ocean-breeze-tier-1.reporting_data_mart`
- **Column-level meaning:** Prefer **BigQuery** table/column `description` (via MCP `get_table_info` / execution metadata, API, or `INFORMATION_SCHEMA`) as the technical source of truth.
- **KPI / metric meaning:** **Always** use [glossary.yml](glossary.yml). When a user’s question maps to a named KPI, find the matching term by **`name`**, then read **`description`** (business rules, date fields, scope) and **`referenced_tables`** (warehouse table `name` and nested **`columns`**) as the source of truth for what the KPI means and which objects apply. Do not use DataHub MCP or other DataHub surfaces for these definitions.
- **Joins and grain:** Use [semantic-layer.md](semantic-layer.md) after you know which tables [glossary.yml](glossary.yml) points to, to join safely and preserve grain.
- **Structured data model (tables, keys, relationships):** The versioned **NDM YAML** in GitHub is the canonical semantic layer for `reporting_data_mart`. Filename pattern: `ocean-breeze-tier-1.reporting_data_mart_NDM_V{n}.yaml` under `dataset-model-NDM/` (only the `V{n}` suffix changes between releases). **Current file:** [ocean-breeze-tier-1.reporting_data_mart_NDM_V1.yaml](https://github.com/frontiersin/analytical-data-model/blob/main/dataset-model-NDM/ocean-breeze-tier-1.reporting_data_mart_NDM_V1.yaml). When this skill’s markdown and the YAML disagree, **prefer the YAML** for PK/FK/grain; use BigQuery for live column descriptions.

## MCP server names (Cursor)

Your `mcp.json` keys map to tool namespaces with a `user-` prefix:

| `mcp.json` server key | Typical Cursor MCP id for tools |
|----------------------|----------------------------------|
| `bigquery` | `user-bigquery` |

Exact MCP tool prefixes and ids follow each workspace’s **`mcp.json`** server keys (and Cursor’s naming); some environments register **multiple or tier-specific BigQuery** servers, so tool names may differ from the table above. **Use the BigQuery-related tools listed in the current session**—do not assume a single fixed prefix. Names may also differ slightly by Cursor version.

KPI definitions live in **[glossary.yml](glossary.yml)** in this skill folder—not in an MCP server.

## Two sources of truth

| Need | Source | How |
|------|--------|-----|
| Run queries, counts, filters | **BigQuery MCP** (preferred in Cursor) | `execute_sql`, etc. against `ocean-breeze-tier-1.reporting_data_mart.*` |
| Run queries (no MCP) | **BigQuery API** (`google-cloud-bigquery`, `bq` query) | Same SQL; ADC or `GOOGLE_APPLICATION_CREDENTIALS` |
| Field/column descriptions | **BigQuery** | MCP `get_table_info` if available; else `get_table(...).schema` or `INFORMATION_SCHEMA` |
| KPI / metric **definition** (meaning + which BigQuery tables/columns apply) | **[glossary.yml](glossary.yml)** | Match **`terms`** by **`name`**; read **`description`** and **`referenced_tables`**. See [rules.md](rules.md). |

Glossary text is not literal SQL. **Infer** filters, date fields, and target tables from each term’s **description** and **referenced_tables**, then express them in SQL. Use [semantic-layer.md](semantic-layer.md), [rules.md](rules.md), and [examples.md](examples.md) for safe joins and common patterns once tables are known.

## Workflow

1. **KPI question:** Decide whether the question refers to a **named KPI** in [glossary.yml](glossary.yml) (synonyms, partial names, or domain terms may need mapping to a **`terms[].name`**). Open [glossary.yml](glossary.yml) and load the **description** and **referenced_tables** for that term. Use [rules.md](rules.md) for defaults (e.g. submitted-articles date fields).
2. **Required examples check (every question):** **Always review [examples.md](examples.md)** before drafting SQL or answering. Reuse the closest applicable query pattern and adapt it to the current KPI/table scope.
3. **Translate to SQL:** Map the glossary **description** into explicit predicates and date columns on the referenced table(s); use BigQuery MCP or API for execution and column-level `description` where needed.
4. **Joins and grain:** Use [semantic-layer.md](semantic-layer.md) for join keys and grain when multiple tables or bridges are involved; align with [rules.md](rules.md) and [examples.md](examples.md) for defaults (e.g. `space_id`, deleted exclusion).
5. **Column semantics:** Prefer live **BigQuery** metadata when validating or explaining fields.
6. **Execute SQL:** Prefer **BigQuery MCP** when available; otherwise **google-cloud-bigquery** or `bq` CLI with ADC.
7. **Submitted articles** time axis: ask whether to use `stage_date_submitted` (first submission) or `stage_date_received_by_journal` unless already specified (see [rules.md](rules.md) and the **Submitted articles** term in [glossary.yml](glossary.yml)).

## Article KPI split default (conformed dimensions)

- For **article-count KPIs** split by conformed-dimension attributes (for example: organization, region attribution, `h_index` bins, or influence bins), default to the **article's attribute** fields.
- In the response, state this explicitly, for example: `Default split shown by article attributes.`
- After returning the default result, ask a follow-up question offering the alternative split: `Do you want the same KPI split by author attributes instead?`
- If the user confirms author-level split, rerun using author attributes and clearly label the output as `author attributes`.

## Output certification marker

- If the response answers a question about a KPI that maps to a term in [glossary.yml](glossary.yml), the final answer must include a leading **green tick**: `✅`.
- For those responses, include a short certification note such as: `✅ Business certified KPI (source: glossary.yml, term: <term_name>)`.
- Only use this marker when the KPI definition was resolved from [glossary.yml](glossary.yml). Do not use it for non-KPI or ad-hoc metrics not defined in the glossary.

## Execution

- **In Cursor with MCP:** Prefer **BigQuery MCP** for queries; KPI meaning always from **[glossary.yml](glossary.yml)** as above.
- **Outside MCP:** Python `google-cloud-bigquery` or `bq` CLI.

## References

- KPI definitions: [glossary.yml](glossary.yml)
- Data model and joins: [semantic-layer.md](semantic-layer.md)
- **NDM semantic layer (YAML, versioned):** [github.com/frontiersin/analytical-data-model — `dataset-model-NDM/ocean-breeze-tier-1.reporting_data_mart_NDM_V{n}.yaml`](https://github.com/frontiersin/analytical-data-model/tree/main/dataset-model-NDM) — update the skill link above when `V{n}` increments.
- Common query patterns: [examples.md](examples.md)
- Operational rules: [rules.md](rules.md)
