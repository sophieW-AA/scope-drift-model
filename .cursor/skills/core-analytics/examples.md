# Common query patterns

Reusable SQL recipes for the most frequent questions this skill answers. Every example includes the space filter and uses fully-qualified project names. For cross-dataset joins, always cross-check keys with `references/dataset-integration-map.yaml` before adapting.

## Articles published in a date range

Join `article` → `journal` on `journal_id + space_id + journal_level`. Do **not** use `article_taxonomy_id ↔ taxonomy_id` for this — `article.taxonomy_id` classifies the article node; journal rows for headers use `journal_level = 'Journal'`.

```sql
SELECT a.article_id_original, a.doi, a.title, j.journal_name, a.create_date
FROM `ocean-breeze-tier-1.reporting_data_mart.article` a
JOIN `ocean-breeze-tier-1.reporting_data_mart.journal` j
  ON a.journal_id = j.journal_id
  AND a.space_id = j.space_id
  AND j.journal_level = 'Journal'
WHERE a.space_id = 1
  AND a.is_published = TRUE
  AND a.create_date >= '2024-01-01'
LIMIT 100
```

## Author organization lookup in AIRAK

```sql
SELECT a.AuthorId, a.FullName, a.IsFrontiersAuthor,
       o.DisplayName AS Organization, o.CountryIsoCode3
FROM `ocean-breeze-tier-1.airak.Author` a
JOIN `ocean-breeze-tier-1.airak.AuthorOrganization` ao ON a.AuthorId = ao.AuthorId
JOIN `ocean-breeze-tier-1.airak.Organization` o ON ao.OrganizationId = o.OrganizationId
WHERE a.NormalizedName LIKE '%smith%'
LIMIT 20
```

## Journal metrics overview

```sql
SELECT journal_name, section, domain, field, status, issn
FROM `ocean-breeze-tier-1.reporting_data_mart.journal`
WHERE space_id = 1
  AND journal_level = 'Journal'
  AND is_online = TRUE
  AND is_deleted = FALSE
ORDER BY journal_name
```

## Article impact over time (Impact Data Platform)

`id_data` must be `reporting_data_mart.article.article_id_original` (same key as peer_review / Salesforce). Resolve `id_action` and `id_entity_type` from the dimension tables in `gcp-innovation-hub.impact_data_platform_v1`.

```sql
SELECT
  dm.id_time,
  SUM(dm.human_amount) AS total_views,
  SUM(dm.unique_human_amount) AS unique_views
FROM `gcp-innovation-hub.impact_data_platform_v1.t_monthly_metrics` dm
WHERE dm.id_action = 1        -- article_views — confirm id in t_dim_action_extended
  AND dm.id_entity_type = 1   -- article — confirm id in t_dim_entity_type
  AND dm.id_space = 1
  AND dm.id_data = 12345      -- placeholder: mart article_id_original (NOT internal article_id);
                              -- same key as ART-003 / PR-001 in dataset-integration-map.yaml
GROUP BY dm.id_time
ORDER BY dm.id_time
```
