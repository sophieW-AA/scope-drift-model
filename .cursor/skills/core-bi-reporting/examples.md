# Common query patterns: `reporting_data_mart`

## Before you run

Governance matches [SKILL.md](SKILL.md) and [rules.md](rules.md): **no exception**—KPI / metric meaning and which warehouse tables and columns apply come **only** from **[glossary.yml](glossary.yml)** (`terms[].name`, **`description`**, **`referenced_tables`**). Do not use DataHub MCP or other DataHub surfaces for those definitions.

- For any **named KPI**, open **[glossary.yml](glossary.yml)**, match **`terms[].name`**, then read **`description`** and **`referenced_tables`** (table `name` and nested **`columns`**). Align each SQL pattern below with that term, including which table to query if the glossary points to a different object than the example.
- For **execution and field-level technical semantics**, use **BigQuery** (prefer **BigQuery MCP** when available; otherwise BigQuery API or `bq`). Glossary text is not literal SQL—translate it into predicates and joins; use [semantic-layer.md](semantic-layer.md) when multiple tables are involved.

All examples use `` `ocean-breeze-tier-1.reporting_data_mart` `` as a typical scope. Adjust **filters and tables** from the **[glossary.yml](glossary.yml)** term and **BigQuery** schema `description` where needed.

## Submitted articles by year (Frontiers, default submission date)

Uses `stage_date_submitted` as first submission; confirm with user if they need `stage_date_received_by_journal`.

```sql
SELECT
  EXTRACT(YEAR FROM stage_date_submitted) AS submission_year,
  COUNT(*) AS submitted_articles
FROM `ocean-breeze-tier-1.reporting_data_mart.article`
WHERE space_id = 1
  AND is_deleted = false
  AND is_submitted = true
  AND stage_date_submitted IS NOT NULL
GROUP BY submission_year
ORDER BY submission_year;
```

## Accepted articles by year

```sql
SELECT
  EXTRACT(YEAR FROM stage_date_accepted) AS acceptance_year,
  COUNT(*) AS accepted_articles
FROM `ocean-breeze-tier-1.reporting_data_mart.article`
WHERE space_id = 1
  AND is_deleted = false
  AND is_accepted = true
  AND stage_date_accepted IS NOT NULL
GROUP BY acceptance_year
ORDER BY acceptance_year;
```

## Article submitted by region5

```sql
SELECT
  a.country5_regions_bin,
  COUNT(distinct a.article_id) AS article_count
FROM `ocean-breeze-tier-1.reporting_data_mart.article` AS a
WHERE a.space_id = 1
  AND is_deleted = false
  AND is_submitted = true
GROUP BY a.country5_regions_bin
ORDER BY article_count DESC;
```

## Article submitted by journal segment

```sql
SELECT
  t.journal_segment,
  COUNT(DISTINCT a.article_id) AS submitted_articles
FROM `ocean-breeze-tier-1.reporting_data_mart.article` AS a
LEFT JOIN `ocean-breeze-tier-1.reporting_data_mart.taxonomy` AS t
  ON a.taxonomy_id = t.taxonomy_id
WHERE
  a.space_id = 1
  AND a.is_deleted = false
  AND a.is_submitted = true
GROUP BY t.journal_segment
ORDER BY submitted_articles DESC;
```


## Article submitted by Article's Organization

```sql
SELECT
  a.main_corresponding_author_primary_organization,
  COUNT(distinct a.article_id) AS article_count
FROM `ocean-breeze-tier-1.reporting_data_mart.article` AS a
WHERE a.space_id = 1
  AND is_deleted = false
  AND is_submitted = true
  AND main_corresponding_author_primary_organization IS NOT NULL
GROUP BY a.main_corresponding_author_primary_organization
ORDER BY article_count DESC;
```

## Article submitted by Author's Organization

```sql
SELECT
  aa.user_primary_organization,
  COUNT(distinct a.article_id) AS article_count
FROM `ocean-breeze-tier-1.reporting_data_mart.article` AS a
LEFT JOIN `ocean-breeze-tier-1.reporting_data_mart.author` AS aa ON a.article_id = aa.article_id
WHERE a.space_id = 1
  AND a.is_deleted = false
  AND a.is_submitted = true
  AND aa.user_primary_organization IS NOT NULL
GROUP BY aa.user_primary_organization
ORDER BY article_count DESC;
```
## Article submitted by Article's Top Parent Highest Ranked Organization

```sql
SELECT
  a.authors_organizations_highest_rank_frontiers_priority_organization,
  COUNT(distinct a.article_id) AS article_count
FROM `ocean-breeze-tier-1.reporting_data_mart.article` AS a
WHERE a.space_id = 1
  AND is_deleted = false
  AND is_submitted = true
  AND a.authors_organizations_highest_rank_frontiers_priority_organization IS NOT NULL
GROUP BY a.authors_organizations_highest_rank_frontiers_priority_organization
ORDER BY article_count DESC;
```

## Article submitted by Author's Top Parent Highest Ranked Organization

```sql
SELECT
  aa.author_organizations_highest_rank_frontiers_priority_organization,
  COUNT(distinct a.article_id) AS article_count
FROM `ocean-breeze-tier-1.reporting_data_mart.article` AS a
LEFT JOIN `ocean-breeze-tier-1.reporting_data_mart.author` AS aa ON a.article_id = aa.article_id
WHERE a.space_id = 1
  AND a.is_deleted = false
  AND a.is_submitted = true
  AND aa.author_organizations_highest_rank_frontiers_priority_organization IS NOT NULL
GROUP BY aa.author_organizations_highest_rank_frontiers_priority_organization
ORDER BY article_count DESC;
```

## Article submitted by Author's region5

```sql
SELECT
  aa.country5_regions_bin,
  COUNT(distinct a.article_id) AS article_count
FROM `ocean-breeze-tier-1.reporting_data_mart.article` AS a
LEFT JOIN `ocean-breeze-tier-1.reporting_data_mart.author` AS aa
  ON a.article_id = aa.article_id
WHERE a.space_id = 1
  AND a.is_deleted = false
  AND a.is_submitted = true
GROUP BY aa.country5_regions_bin
ORDER BY article_count DESC;
```

## Article submitted by Article's H Index bins
```sql
SELECT
  h_index_bins,
  COUNT(distinct article_id) AS article_count
FROM `ocean-breeze-tier-1.reporting_data_mart.article` 
WHERE space_id = 1
  AND is_deleted = false
  AND is_submitted = true
GROUP BY h_index_bins
ORDER BY article_count DESC
```

## Article submitted by Article's Influence bins
```sql
SELECT
  influence_bins,
  COUNT(distinct article_id) AS article_count
FROM `ocean-breeze-tier-1.reporting_data_mart.article` 
WHERE space_id = 1
  AND is_deleted = false
  AND is_submitted = true
GROUP BY influence_bins
ORDER BY article_count DESC
```

## Article submitted by Author's H Index bins
```sql
SELECT
  aa.h_index_bins,
  COUNT(distinct a.article_id) AS article_count
FROM `ocean-breeze-tier-1.reporting_data_mart.article` a
LEFT JOIN `ocean-breeze-tier-1.reporting_data_mart.author` AS aa
  ON a.article_id = aa.article_id
  WHERE  a.is_deleted = false
  AND a.is_submitted = true
  AND a.space_id = 1
GROUP BY aa.h_index_bins
ORDER BY article_count DESC
```

## Article submitted by Author's Influence bins
```sql
SELECT
  aa.influence_bins,
  COUNT(distinct a.article_id) AS article_count
FROM `ocean-breeze-tier-1.reporting_data_mart.article` a
LEFT JOIN `ocean-breeze-tier-1.reporting_data_mart.author` AS aa
  ON a.article_id = aa.article_id
WHERE a.space_id = 1
  AND a.is_deleted = false
  AND a.is_submitted = true
GROUP BY aa.influence_bins
ORDER BY article_count DESC
```

## Research topics posted by Region5

```sql
SELECT
  country5_regions_bin AS r,
  COUNT(distinct research_topic_id) AS research_topics_posted
FROM `ocean-breeze-tier-1.reporting_data_mart.research_topic`
WHERE space_id = 1
  AND is_deleted = FALSE
  AND (
    is_completed = True OR is_online= true OR is_closed = true
  )
  AND online_date IS NOT NULL
GROUP BY r
ORDER BY r;
```

## Research topics posted by journal segment

```sql
SELECT
  t.journal_segment,
  COUNT(DISTINCT rt.research_topic_id) AS research_topic_posted
FROM `ocean-breeze-tier-1.reporting_data_mart.research_topic` AS rt
LEFT JOIN `ocean-breeze-tier-1.reporting_data_mart.taxonomy` AS t
  ON rt.taxonomy_id = t.taxonomy_id
WHERE rt.space_id = 1
  AND rt.is_deleted = FALSE
  AND (
    rt.is_completed = True OR rt.is_online= true OR rt.is_closed = true
  )
  AND rt.online_date IS NOT NULLS
  
GROUP BY t.journal_segment
ORDER BY research_topic_posted DESC
```

## Research topics posted by Year

```sql
SELECT
  EXTRACT(YEAR FROM online_date) AS y,
  COUNT(distinct research_topic_id) AS research_topics_posted
FROM `ocean-breeze-tier-1.reporting_data_mart.research_topic`
WHERE space_id = 1
  AND is_deleted = FALSE
  AND (
    is_completed = True OR is_online= true OR is_closed = true
  )
  AND online_date IS NOT NULL
GROUP BY y
ORDER BY y;
```


## Invited Contributors per Year
```sql
SELECT
		extract (YEAR FROM contributor_invitation_date ) AS Year
	, extract (MONTH FROM contributor_invitation_date ) AS Month
	, COUNT(DISTINCT c.contributor_id) AS contributors
	FROM `ocean-breeze-tier-1.reporting_data_mart.contributor` AS c
	WHERE c.space_id = 1
  AND contributor_invitation_date IS NOT NULL
	GROUP BY 		extract (YEAR FROM  contributor_invitation_date ) 
	, extract (MONTH FROM contributor_invitation_date )
	ORDER BY 1, 2
	
```


## Confirmed Contributors per Year
```sql
SELECT
		extract (YEAR FROM invitation_status_date_confirmed_last ) AS Year
	, extract (MONTH FROM invitation_status_date_confirmed_last ) AS Month
	, COUNT(DISTINCT c.contributor_id) AS contributors
	FROM `ocean-breeze-tier-1.reporting_data_mart.contributor` AS c
	WHERE c.space_id = 1
	AND c.contributor_invitation_date IS NOT null
	GROUP BY 		extract (YEAR FROM  invitation_status_date_confirmed_last ) 
	, extract (MONTH FROM  invitation_status_date_confirmed_last )
	ORDER BY  1, 2
	
```

## Invited to Confirmed Contributor Conversion Rate
```sql
	
WITH
  base AS (
    SELECT
      EXTRACT(YEAR FROM contributor_invitation_date) AS Year,
      EXTRACT(MONTH FROM contributor_invitation_date) AS Month,
      COUNT(DISTINCT c.contributor_id) AS invited_contributors,
      COUNT(
        DISTINCT
          CASE
            WHEN invitation_status_date_confirmed_last IS NOT NULL
              THEN c.contributor_id
            END) AS confirmed_contributors
    FROM `ocean-breeze-tier-1.reporting_data_mart.contributor` AS c
    WHERE
      c.space_id = 1
      AND c.contributor_invitation_date IS NOT NULL
    GROUP BY
      EXTRACT(YEAR FROM contributor_invitation_date),
      EXTRACT(MONTH FROM contributor_invitation_date)
  )
SELECT
  Year,
  Month,
  FORMAT('%.2f%%', SAFE_DIVIDE(SUM(confirmed_contributors), SUM(invited_contributors)) * 100)
    AS InvitedToConfirmedContributorConversionRate
FROM
  base
GROUP BY Year, Month
ORDER BY Year, Month
```

## Editorial Board Members (unique users)
```sql
SELECT
  EXTRACT(year FROM min_join_date) AS year,
  EXTRACT(month FROM min_join_date) AS month,
  COUNT(DISTINCT editorial_board_member_user_id)
FROM `ocean-breeze-tier-1.reporting_data_mart.editorial_board_member`
WHERE space_id = 1
GROUP BY
  EXTRACT(year FROM min_join_date),
  EXTRACT(month FROM min_join_date)
ORDER BY 1, 2
  
```


## Editorial Board Members (roles)
```sql
SELECT
  EXTRACT(year FROM join_date) AS year,
  EXTRACT(month FROM join_date) AS month,
  COUNT(DISTINCT editorial_board_member_id)
FROM `ocean-breeze-tier-1.reporting_data_mart.editorial_board_member`
WHERE space_id = 1
GROUP BY
  EXTRACT(year FROM join_date),
  EXTRACT(month FROM join_date)
ORDER BY 1, 2
  
```

## Inspect column descriptions (BigQuery metadata)

Use in tooling or ad-hoc validation—not a business KPI by itself.

```sql
SELECT table_name, column_name, description
FROM `ocean-breeze-tier-1.reporting_data_mart.INFORMATION_SCHEMA.COLUMN_FIELD_PATHS`
WHERE description IS NOT NULL AND description != ''
ORDER BY table_name, column_name;
```

If `COLUMN_FIELD_PATHS` does not expose `description` in your region, use the client API: `get_table('...article').schema` in Python and read `field.description`.


