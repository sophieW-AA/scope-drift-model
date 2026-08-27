---
name: core-data-platform
description: Frontiers data platform reference — BigQuery lakehouse, AIRAK bibliometrics, cross-system joins, pipeline patterns, entity identifiers, and data quality gotchas. Use when querying BigQuery, joining RDM to AIRAK, understanding person/author IDs, or building data pipelines.
---

# Frontiers Data & SQL Skills Reference

> Synthesised from Confluence pages (2025–2026), weighted by recency and relevance to data platform / integration work.  
> Last generated: 2026-05-01 | Sources: 616 pages (DATAP ▲▲, DE ▲▲, ENG ▲▲, DA ▲▲, TECH ▲▲, AIS ▲, others ▲)

---

## 1. Data Ecosystem at a Glance

Frontiers runs a BigQuery lakehouse across **five GCP projects, ~68 datasets, ~2,700 tables**, with `reporting_data_mart` as the curated layer on top. The platform is batch-overnight today but is actively moving toward event-driven freshness.

| Layer | GCP Project | Key Datasets | Notes |
|---|---|---|---|
| Reporting Mart | `ocean-breeze-tier-1` | `reporting_data_mart` | Frontiers-internal identifiers. 486-column `article` table. Primary source for operational queries. |
| Bibliometrics (AIRAK) | `ocean-breeze-tier-1` | `airak` | OpenAlex data. 163M publications, 150M authors, 2.3B citation rows. External identifiers. |
| Dimensions / Salesforce | `ocean-breeze-tier-2` | `dimensions`, `salesforce`, `rosst` | Nested fields in Dimensions; Salesforce mirrored daily — use BQ mirror for analytics. |
| Platform / Integration | `ocean-tech-braavos-pro` | — | Service accounts for Crafters pipelines live here. |
| Project Spaces | `ocean-tech-adv-analytics-c-*`, `ocean-tech-admau-*` | EarlyFoS, Competitor Mapping, Article Forecast, Audience Manager | Team-specific; confirm dataset ownership before writing. |

> **Source:** [Data Platform — Capability Requirements](https://confluence.frontiersin.net/spaces/TECH/pages/767431329) (TECH, Apr 2026 ▲▲)

---

## 2. SQL Style Conventions (Frontiers Standard)

Taken directly from the DA team's SQL standards page:

```sql
-- ✅ Good: clear aliases, explicit join type, filter in WHERE not ON
SELECT
  c.customer_id,
  SUM(o.amount) AS total_amount
FROM sales.orders AS o
JOIN sales.customers AS c
  ON c.customer_id = o.customer_id
WHERE o.order_date >= DATE '2025-01-01'
GROUP BY c.customer_id
HAVING SUM(o.amount) > 100
ORDER BY total_amount DESC;
```

**Key rules:**
- Keywords in `UPPERCASE`; identifiers in `snake_case`
- One clause per line; indent 2–4 spaces for subqueries
- Always qualify columns in multi-table queries (`table.column` or `alias.column`)
- Prefer CTEs (`WITH` clauses) over nested subqueries for readability
- Treat `NULL` intentionally — never assume it equals anything; use `IS NULL / IS NOT NULL`
- Put join conditions in `ON`; put row filters in `WHERE` to avoid accidental row explosion
- Use `EXISTS` for semi-joins instead of `IN` when NULL semantics matter

> **Source:** [SQL](https://confluence.frontiersin.net/spaces/DA/pages/677675440) (DA, Oct 2025 ▲▲)

---

## 3. Data Integration Patterns

### 3.1 SQL Server → BigQuery (Reference Data Pipeline)

The standard Frontiers pattern for syncing SQL Server (Azure) reference data to BigQuery uses a **daily batch load via DevOps**. All SQL Server tables that feed Retool apps must include these compulsory metadata columns:

```sql
-- Compulsory columns for every SQL Server reference table
tech_id       UNIQUEIDENTIFIER NOT NULL DEFAULT NEWSEQUENTIALID()  -- stable row identity
edited_by     NVARCHAR(100)    NOT NULL                            -- user email or process name
update_date   DATETIME2(7)     NOT NULL DEFAULT SYSUTCDATETIME()   -- UTC modification timestamp
is_deleted    BIT              NOT NULL DEFAULT 0                  -- logical delete flag (never hard-delete)

-- Add tech_id to an existing table:
ALTER TABLE [reference_data_retool].[<table>]
ADD tech_id UNIQUEIDENTIFIER DEFAULT NEWSEQUENTIALID() NOT NULL;
```

**Pipeline stages:**
1. **Stage 0 – Azure SQL Server** (3 environments: dev / staging / prod). Retool app writes here; logical deletes only.
2. **Stage 1 – GCP Bucket** — DevOps-owned daily sync lands data in Cloud Storage.
3. **Stage 2 – BigQuery (Ocean)** — Crafters job promotes from bucket into `ocean-breeze-*` datasets. Two compulsory output tables per entity: a **historical table** (append-only) and a **latest-version view**.

> **Source:** [Pipeline 2.0: SQL Server & BigQuery](https://confluence.frontiersin.net/spaces/DATAP/pages/725619045) (DATAP, Feb 2026 ▲▲), [Schemas for SQL Server tables](https://confluence.frontiersin.net/spaces/DATAP/pages/725619014) (DATAP, Feb 2026 ▲▲)

---

### 3.2 ROSST Organization Integration

ROSST is Frontiers' abstraction layer between services and organization data providers (Ringgold, Ugarit, Grid). Key integration facts:

- **Identifiers:** ROSST IDs are always `"o" + numeric` (e.g. `o12345`). Never store raw Ringgold IDs as primary keys in new systems.
- **GBQ sync cadence:** Currently weekly (causes gaps for newly created Ugarit IDs). Migration to **daily promotion** in progress.
- **Key ROSST tables in BigQuery** (`ocean-breeze-tier-2.rosst`):

| Table | Purpose |
|---|---|
| `golden_data.rosst_organization` | Names, consortium flag, address ref |
| `golden_data.rosst_organization_source` | Org–source ID mappings (Ringgold, Ugarit) |
| `golden_data.rosst_organization_inactive_source` | Filter inactive orgs |
| `golden_data.rosst_organization_address` | Country ISO codes and names |
| `golden_data.rosst_organization_alias` | English names (Ringgold source, term `TR`) |
| `golden_data.rosst_organization_url` | Email domains per org |
| `golden_data.rosst_consortium_membership` | Consortium parent–member relationships |
| `golden_data.rosst_organization_hierarchy` | Parent–child org hierarchy |

- **Reading SQL tables from Databricks:** Use the `UgaritValidOrganizationsUpdate` reference implementation; retrieve secrets from Azure Key Vault via `dbutils`; prefer reading into a Delta table (source-to-bronze) over querying SQL Server directly.

> **Source:** [Application-RosstPipeline](https://confluence.frontiersin.net/spaces/ENG/pages/767429749) (ENG, Apr 2026 ▲▲), [SD - Integration of Institutional Profiles (ROSST)](https://confluence.frontiersin.net/spaces/DATAP/pages/721223862) (DATAP, Jan 2026 ▲▲)

---

### 3.3 Crafters — Deploying Data Pipelines

Crafters is Frontiers' internal pipeline framework, deployed to **Azure Kubernetes Service (AKS)** via Helm charts, orchestrated via **Azure DevOps** with trunk-based development.

**Service account convention:**
```
crafters-<repository-name>@ocean-tech-braavos-pro.iam.gserviceaccount.com
```
Contact Team Caladan to provision. Provide the GCP project names your pipeline needs.

**Key `values.yaml` settings:**

| Setting | Description |
|---|---|
| `dataLoadStageId` | Unique ID matching `id` in `pipelines.yml` under `data_load` |
| `crafters.name` | Crafters project name — matches `job_name` in `pipelines.yml` |
| `google.project_id` | GCP project where the Kubernetes Job Scheduling Agent runs |
| `google.application_credentials` | Service account credentials for GCP auth |

Config values resolved dynamically from **ConfigurationHub** using `@Model.<component_type>.<component_definition>.<key>` syntax. Example: `@Model.sqlDatabase.serviceAira.name`.

> **Source:** [1. Pipelines - Deploying your data pipelines](https://confluence.frontiersin.net/spaces/TECH/pages/677159627) (TECH, Jan 2026 ▲▲), [2. Customizing the release pipeline - Data Load Stage Deployment](https://confluence.frontiersin.net/spaces/TECH/pages/704089088) (TECH, Jan 2026 ▲▲)

---

### 3.4 Raw Data Pipeline (Giacomo / AIRAK Release Pipeline)

The **Raw Data Pipeline** (Azure Data Factory, `PDSNextGen-CI`) is step 1 of the AIRAK release pipeline. It populates the `frontierspdsinputlive/{run_date}/` blob container. Key source systems:

| Source | Content | Output Parquets |
|---|---|---|
| Space SQL Servers (ALF / FSHIP / Frontiers / GGSL / SSPH) | Articles, authors, affiliations, editorial board | `Article.parquet`, `ArticleAuthor.parquet`, `EditorialAppointment.parquet`, … |
| AuthDb / AlhambraDb / OrchisDb / Loop | Registered users, emails, affiliations | `RegisteredUser.parquet`, `UserEmail.parquet`, … |
| Ugarit SQL Server + SharedService.json | Organizations, hierarchy, rankings | `Organization.parquet`, `OrganizationHierarchy.parquet`, … |
| ManualCurationDb SQL Server | Manual edges, relevant users | `manual-edge.parquet`, `relevant-user.parquet` |
| MAG Container (Databricks notebook) | Fields of study | `FieldOfStudy.parquet`, `PublicationFieldsOfStudy.parquet` |

> **Source:** [Giacomo: Raw Data Pipeline - migration](https://confluence.frontiersin.net/spaces/ENG/pages/752355567) (ENG, Mar 2026 ▲▲)

---

## 4. Pipeline Architecture Patterns

### 4.1 Truncate-and-Reload (Databricks → SQL Server)

Used by the **IPP Organization Metrics Pipeline**:

```python
# Pattern: full truncate-and-reload, then promote via stored procedure
# Data sources: BigQuery golden tables + Spark delta tables

# Key BigQuery tables involved:
# ocean-breeze-tier-2.rosst.golden_data.*            — ROSST org data
# ocean-breeze-tier-1.reporting_data_mart.article    — article metadata
# ocean-breeze-tier-1.reporting_data_mart.author     — author details
# IppEntity.focus_organizations                      — seed list of in-scope Ringgold orgs
# IppEntity.rosst_doi_author_affiliations            — article–org affiliation links
# DhwEntity.article, article_funder, article_funding — funding data

# After load: invalidate Redis cache
```

Pipeline runs a stored procedure to promote staging data, then invalidates the Redis cache. Target: **IPP-DB** (SQL Server metrics database).

> **Source:** [IPP Organization Metrics Pipeline](https://confluence.frontiersin.net/spaces/ENG/pages/725457222) (ENG, Feb 2026 ▲▲)

---

### 4.2 LLM-Powered ETL Pipeline (Python / BigQuery)

From the **EB Mapping Editors** production pipeline — a modular ETL where BigQuery feeds an LLM and results write back to BigQuery:

```
Input (BigQuery) → Processing (LLM / OpenAI) → Output (BigQuery)

┌──────────────┐    ┌──────────────────┐    ┌────────────────┐
│ Bullet Points│──┐ │                  │    │                │
│ Editors      │──┼─│  LLM Matching    │───▶│ Editor-BP      │
│ Profiles     │──┤ │  (OpenAI API)    │    │ Mappings Table │
│ Mission Stmt │──┘ │                  │    │                │
└──────────────┘    └──────────────────┘    └────────────────┘
```

**Module responsibilities:**

| Module | Role |
|---|---|
| `data_loading.py` | Load inputs from BigQuery via SQL queries |
| `queries.py` | SQL query generators for all BigQuery interactions |
| `llm_processing.py` | Prompt construction, async OpenAI calls, JSON parsing |
| `prediction.py` | Output DataFrame preparation |
| `schemas.py` | Pandera output schema with BigQuery schema generation |
| `inference/pipeline.py` | Main orchestration (`EBMappingEditorsInferencePipeline`) |

Two pipeline modes: **Batch** (full section re-run, deletes previous results) and **Incremental** (new items only).

> **Source:** [ebmappingeditors — Package & Pipeline Documentation (Prod)](https://confluence.frontiersin.net/spaces/AIS/pages/725457673) (AIS, Feb 2026 ▲▲)

---

### 4.3 Researcher Profile Generation Pipeline

LLM-powered system running on **Azure Databricks**, using **Google Gemini**, writing output to **BigQuery**. Key facts for anyone inheriting or extending it:

- 4 of 10 components are dead code or deprecated — verify ownership before touching
- Adaptive concurrency stable to 100 workers (load-tested)
- LLM provider abstraction is well-designed and reusable
- **8 CRITICAL findings** as of Q2 2026: exposed credentials (rotate immediately), zero cost controls, hardcoded cluster IDs, hardcoded catalog references
- CI/CD and full documentation deferred to Q3 2026

> **Source:** [Q2 2026 Proposal — Researcher Profile Pipeline Ownership](https://confluence.frontiersin.net/spaces/ENG/pages/725461597) (ENG, Mar 2026 ▲▲)

---

## 5. Validated SQL Examples from Production

### 5.1 Review Board Invitation Count (BigQuery)

```sql
-- Count Perfect Emails sent on a specific date
-- Source: ocean-breeze-tier-2.editorial_assignment.review_board_invitation
SELECT COUNT(*) AS perfect_emails_sent
FROM `ocean-breeze-tier-2.editorial_assignment.review_board_invitation`
WHERE is_match = TRUE
  AND DATE(invite_at) = '2026-04-20';
```

Cross-validated against SQL Server:
```sql
-- SQL Server equivalent (FrontiersReports)
SELECT COUNT(*) AS perfect_emails_sent
FROM [FrontiersReports].[EOf].[ReviewBoardChartsDS]
WHERE IsMatch = 1
  AND CAST(InviteDate AS DATE) = '2026-04-20';
```
Both returned **4,620** on the validation date.

> **Source:** [PE Profile Coverage QC](https://confluence.frontiersin.net/spaces/DA/pages/769397047) (DA, Apr 2026 ▲▲)

---

### 5.2 SQL-to-Interested Conversion (Salesforce via BigQuery Mirror)

```sql
-- Salesforce opportunity conversion rate — use BQ mirror, not Salesforce API
SELECT
  opportunity_owner_id,
  COUNT(*) AS total_opps,
  COUNTIF(stage_name = 'Interested') AS converted,
  ROUND(COUNTIF(stage_name = 'Interested') / COUNT(*), 3) AS conversion_rate
FROM `ocean-breeze-tier-2.salesforce.opportunity`
WHERE opportunity_record_type_name = 'Research Topics'
GROUP BY opportunity_owner_id;
-- Validated conversion rate: 16.4% for owner 0054H0000048eb4QAA
```

> **Source:** [SQL calls conversion rates](https://confluence.frontiersin.net/spaces/DA/pages/592118324) (DA, Jul 2025 ▲)

---

## 6. BigQuery — Key Conventions

- **Billing project:** Always construct your BigQuery client with `gcp-innovation-hub` as the billing project. Data lives in `ocean-breeze-tier-1` through `-4`.
- **ANSI SQL:** BigQuery uses standard SQL. Queries are case-insensitive for keywords but backtick-quote project/dataset/table names containing hyphens.
- **Serverless:** No infrastructure to manage. Use partitioned and clustered tables to control cost on large scans (especially `airak.PublicationCitation` at 2.3B rows).
- **Cross-project queries:** Use fully qualified names: `` `project.dataset.table` ``
- **Nested fields (Dimensions):** Use `CROSS JOIN UNNEST()` for repeated fields like `concepts_scores`, `author_affiliations`.

```python
from google.cloud import bigquery
client = bigquery.Client(project="gcp-innovation-hub")  # always billing project
df = client.query("""
    SELECT article_id, title, published_date
    FROM `ocean-breeze-tier-1.reporting_data_mart.article`
    WHERE DATE(published_date) >= '2025-01-01'
    LIMIT 1000
""").to_dataframe()
```

> **Source:** [2. Getting started - BigQuery](https://confluence.frontiersin.net/spaces/TECH/pages/592120231) (TECH, Jul 2025 ▲), [Data Platform — Capability Requirements](https://confluence.frontiersin.net/spaces/TECH/pages/767431329) (TECH, Apr 2026 ▲▲)

---

## 7. Weighting & Source Quality Guide

When referencing or extending this document, weight pages by the following criteria:

| Signal | Weight | Rationale |
|---|---|---|
| Created/modified in 2026 | ▲▲ High | Reflects current platform state |
| Created/modified in 2025 | ▲ Medium | Still relevant but verify against 2026 pages |
| Space: DATAP, DE | ▲▲ High | Data Platform team — authoritative on pipelines and schemas |
| Space: ENG, TECH | ▲▲ High | Engineering — authoritative on infrastructure, CI/CD, service design |
| Space: DA, AIS | ▲ Medium-High | Analytics & AI Science — authoritative on models and SQL patterns |
| Space: CRM, RTA, IO, PP | ▲ Medium | Domain teams — good for business context, verify technical claims |
| Archived pages | ▼ Low | Check for a successor page before following |
| Pages with "ARCHIVED" in title | ▼ Ignore unless no alternative exists |

---

*Generated from 616 Confluence pages (2025–2026) matching `type=page AND text~"SQL" AND created>="2025-01-01"`. Prioritised by recency (days since creation) and data platform / integration space membership.*

---

## 8. Join Keys & Cross-System Bridges

### 8.1 Person ID disambiguation (Reporting Data Mart)

The `person` table has four overlapping ID columns. Use the right one or joins will silently return wrong results.

| Column | Meaning | When to use |
|---|---|---|
| `personuser_id` | True primary key of the `person` table — unique instance of UserId + Email within a Space | PK on `person` table only |
| `person_user_id` | Person-level ID derived from `personuser_id`. **The standard FK across all RDM tables** | **Default join key across RDM** — links person ↔ author ↔ editor ↔ EBM |
| `person_id` | Derived entity ID (M:1 from `personuser_id`). Maps directly to `AuthorId` in AIRAK | Cross-system joins to AIRAK; also used in RT editor workflows |
| `user_id` | Registered user ID. **`user_id = -1` = non-registered user** | Joining to `user_metrics` only |
| `author_id` | **Not person-level.** Unique instance of Role + Taxonomy + User + Space. One person → multiple `author_id`s | PK on `author` table only — never use to identify a person across tables |

**Common RDM join patterns:**

```sql
-- Person → editorial board memberships
FROM reporting_data_mart.person p
JOIN reporting_data_mart.editorial_board_member ebm
  ON p.person_user_id = ebm.editorial_board_member_person_user_id

-- Article → authors
FROM reporting_data_mart.article art
JOIN reporting_data_mart.author a
  ON art.article_id = a.author_article_id

-- Person → activity metrics
FROM reporting_data_mart.person p
JOIN reporting_data_mart.user_metrics um
  ON p.person_user_id = um.user_id

-- Research Topic → host editor only
FROM reporting_data_mart.research_topic rt
JOIN reporting_data_mart.research_topic_editor rte
  ON rt.research_topic_id = rte.editor_research_topic_id
WHERE rte.editor_order = 1
```

### 8.2 AIRAK internal joins

```sql
-- Publication → authors
FROM airak.Publication pub
JOIN airak.PublicationAuthor pub_auth ON pub.PublicationId = pub_auth.PublicationId
JOIN airak.Author auth               ON pub_auth.AuthorId  = auth.AuthorId

-- Publication → journal → publisher
FROM airak.Publication pub
JOIN airak.Journal jnl   ON pub.JournalId    = jnl.JournalId
JOIN airak.Publisher pbl ON jnl.PublisherId  = pbl.PublisherId

-- Citation direction: PublicationId = citing paper, CitedPublicationId = cited paper
FROM airak.PublicationCitation pc

-- Journal → top FoS categories
FROM airak.JournalFieldOfStudy jfos
JOIN airak.FieldOfStudy fos ON jfos.FieldOfStudyId = fos.FieldOfStudyId
WHERE fos.Level = 0
ORDER BY jfos.Score DESC
```

### 8.3 Cross-system bridges (RDM ↔ AIRAK)

There is **no direct shared ID**. Use these three bridges:

| Bridge | SQL | Match rate / notes |
|---|---|---|
| **DOI** | `LOWER(pub.Doi) = LOWER(art.doi)` | Always `LOWER()` both sides — casing is inconsistent across systems |
| **person_id → AuthorId** | `rdm.person.person_id = airak.Author.AuthorId` | 100% confirmed match — `person_id` IS the AIRAK `AuthorId` |
| **Loop ID** | `airak.AuthorSource WHERE SourceId = 20` → join to Loop fields in RDM | ~96.7% match rate for active researchers |

```sql
-- Extract Loop IDs from AIRAK
SELECT AuthorId, SourceValue AS loop_id
FROM `ocean-breeze-tier-1.airak.AuthorSource`
WHERE SourceId = 20;  -- 20 = Loop
```

**AuthorSource / SourceId reference:**

| SourceId | System |
|---|---|
| 1 | SSPH |
| 3 | ALF |
| 5 | FSHIP |
| 10 | ORCiD |
| 11 | Dimensions |
| 19 | Frontiers (use to filter AIRAK v2 editorial tables) |
| 20 | Loop |
| 23 | Ugarit (org source — legacy, being replaced by ROSST) |

### 8.4 Joining to Dimensions

```sql
-- Match AIRAK publication to Dimensions by DOI
FROM airak.Publication pub
JOIN dimensions.publications dim ON LOWER(pub.Doi) = LOWER(dim.doi)

-- Unnest Dimensions concept scores (nested/repeated field)
SELECT pub.doi, concept_scores.concept, concept_scores.relevance
FROM dimensions.publications pub
CROSS JOIN UNNEST(concepts_scores) AS concept_scores
WHERE concept_scores.relevance > (
  SELECT AVG(cs.relevance)
  FROM UNNEST(pub.concepts_scores) cs
)
```

---

## 9. Filtering Patterns & Critical Gotchas

### 9.1 Frontiers-only filter in AIRAK ⚠️

**AIRAK contains all publishers (163M publications).** Always scope to Frontiers unless you explicitly want competitor data:

```sql
-- Method 1: via Publisher name (preferred for publication queries)
FROM airak.Publication pub
JOIN airak.Journal jnl  ON pub.JournalId  = jnl.JournalId
JOIN airak.Publisher pbl ON jnl.PublisherId = pbl.PublisherId
WHERE pbl.Name = "Frontiers Publisher"
  AND jnl.DisplayName LIKE "Frontiers in %"

-- Method 2: via Author flag (for author-level queries)
FROM airak.Author
WHERE IsFrontiersAuthor = TRUE

-- Method 3: AIRAK v2 editorial tables — filter by SourceId
WHERE SourceId = 19  -- 19 = Frontiers
```

### 9.2 Active journals only

```sql
FROM airak.JournalMetadata
WHERE IsOpenForSubmissions = TRUE
-- Also filter: WHERE JournalId > -1  (JournalId = -1 means unknown journal)
```

### 9.3 Time filters

```sql
-- RDM: use stage_date_submitted
WHERE EXTRACT(YEAR FROM stage_date_submitted) IN (2024, 2025)

-- AIRAK: use PublishedYear (integer column — faster than date extraction)
WHERE pub.PublishedYear >= 2020
```

### 9.4 Author eligibility filters (RT host / editorial board)

```sql
WHERE RetractedPublicationCount = 0
  AND Activeness >= 0.01
  AND HasPublishedOpenAccess = TRUE
  AND has_email = TRUE
  AND email_validity_id IN (1, 2, 4)  -- valid, safeToSend, catch-all
```

### 9.5 Scope assessment thresholds (Out of Scope / OOS)

- FoS score **> 0.01** = relevant
- In scope if: (Level 0 in top 10% AND Level 1 in top 25%) OR (Level 0 in top 25% AND Level 1 in top 10%)
- Editor out of scope if **< 40%** of their articles match both journal and section scopes
- Limit publication history to **last 5 years** (career changes)

### 9.6 DOI casing ⚠️

DOIs are stored in mixed case across systems. **Always `LOWER()` both sides:**

```sql
ON LOWER(table_a.doi) = LOWER(table_b.doi)
```

---

## 10. Entity Identifier Cheat Sheet

| Entity | System | Primary key | Join key to other tables |
|---|---|---|---|
| Article (Frontiers) | RDM | `article_id` | `doi` for cross-system |
| Publication (all publishers) | AIRAK | `PublicationId` | `Doi` (lowercased) for cross-system |
| Person (Frontiers user) | RDM | `personuser_id` | **`person_user_id`** across RDM; `person_id` to AIRAK |
| Author (AIRAK) | AIRAK | `AuthorId` | = `person_id` in RDM |
| Author (RDM) | RDM | `author_id` (not person-level!) | Use `author_person_user_id` to find the person |
| Journal (AIRAK) | AIRAK | `JournalId` | `DisplayName` |
| Journal (Frontiers) | RDM | `journal_id` | Via taxonomy |
| Organisation | RDM | `organization_id` | `rosst_id` links to ROSST |
| Organisation | AIRAK | `OrganizationId` | — |
| Editorial Board Member | RDM | `editorial_board_member_id` | `editorial_board_member_person_user_id` |
| Research Topic | RDM | `research_topic_id` | — |
| RT Host Editor | RDM | `editor_person_user_id` | Filter `editor_order = 1` |
| Loop ID | AIRAK bridge | `AuthorSource.SourceValue` where `SourceId = 20` | — |
| ORCiD | AIRAK bridge | `AuthorSource.SourceValue` where `SourceId = 10` | — |

---

## 11. Table Sizes & Cost Warnings

| Table | Rows | Action required |
|---|---|---|
| `airak.PublicationCitation` | **2.3 billion** | Always filter by `PublicationId` — never scan full table |
| `airak.PublicationAuthor` | **576 million** | Filter before joining; pre-aggregate in a CTE |
| `airak.Publication` | 163 million | Use `PublishedYear` or `JournalId` filters |
| `airak.Author` | 150 million | Use `IsFrontiersAuthor = TRUE` to reduce scope |
| `reporting_data_mart.person` | 19 million | Filter by `is_registered_user` or other flags where possible |
| `reporting_data_mart.author` | 8.5 million | 250-column table — never `SELECT *` |
| `reporting_data_mart.article` | — | 486-column table — never `SELECT *`; specify columns explicitly |
| `fos_evaluated.pub_earlyfos` | 438 million | Always filter by `fos_level` and/or `pub_id` |

**Cost rules:**
1. Use CTEs to filter large tables **before** joining
2. Prefer `PublishedYear` (integer) over `EXTRACT(YEAR FROM ...)` on date columns in AIRAK
3. Use `LIMIT` during exploration
4. Specify columns explicitly — never `SELECT *` on tables > 100 columns
5. BigQuery billing project is always `gcp-innovation-hub` — never a data project

---

## 12. Data Quality — Known Issues

| Issue | Where | What to do |
|---|---|---|
| DOI casing inconsistency | AIRAK + RDM | Always `LOWER()` both sides of DOI joins |
| `JournalId = -1` | AIRAK | Filter out: `WHERE pub.JournalId > -1` |
| `author_id` is not person-level | RDM | Use `author_person_user_id` to identify the person, not `author_id` |
| `user_id = -1` | RDM | Non-registered user — exclude with `WHERE user_id != -1` if needed |
| `space_id = 0` | RDM | Missing space — exclude or handle explicitly |
| `HierarchyId` not stable | AIRAK | Do not use `OrganizationHierarchy.HierarchyId` as a tracking key — regenerated each load |
| Salesforce Task call/email field | Salesforce | Field distinguishing calls from emails is unreliable — calls are under-reported |
| Dimensions bot activity | Dimensions | Bot inflates download counts (especially through 2024). Treat download metrics with caution |
| RT contributor counts differ across platforms | RTM / Salesforce / Tableau | Tableau typically lower; Salesforce misses non-RTM invitations. Always state your source |
| EarlyFoS ≠ OpenAlex FoS | FoS | Not identical — EarlyFoS is consistent internally but uses different vocab. Don't mix scores |
| Organisation affiliation mismatch | RDM vs AIRAK | Loop takes priority over AIRAK for primary org/email. RDM may show a different org than AIRAK for the same person |
| RT contributor–article linking | RTM / Salesforce | ~5% of confirmed contributors who submit are not linked to their profile |
| `RetractedPublicationCount` incomplete | AIRAK | May miss some retractions — cross-reference with `Retraction` table and Retraction Watch if precision required |

---

## 13. CDP / Impact Data (Views, Downloads, Citations)

Lives in the **`frontiers-cdp`** GCP project. Tables are partitioned and clustered — **query in cluster field order** for performance.

### Key tables

| Table | Contents | Cluster order |
|---|---|---|
| `facts_all_tenants_live_v2.t_fact_cons_events` | Daily events. Partitioned by `id_time` (monthly) | `id_time`, `id_space`, `id_entity_type`, `id_action` |
| `facts_all_tenants_live_v2.t_agg_cons_events` | Aggregated by time / space / entity / action | — |
| `facts_all_tenants_live_v2.mv_agg_cons_alltime` | All-time views + downloads per article | `id_space`, `id_entity_type`, `id_action` |
| `facts_all_tenants_live_v2.t_agg_citations` | All-time citations per article | Clustered by `id_article` |
| `facts_all_tenants_live_v2.t_daily_dataid_country` | Daily metrics by country | `id_country`, then `id_data` |

### Action type codes

| Action | Meaning |
|---|---|
| `art_abstr_view` | Abstract view |
| `art_full_txt_view` | Full text view |
| `art_pdf_dwnld` | PDF download |
| `art_epub_dwnld` | EPUB download |
| `art_xml_dwnld` | XML download |
| `rt_details_view` | RT home page view |
| `loop_profile_page_view` | Loop profile view |
| `journal_home_view` | Journal home view |
| `sectioin_page_view` | Section home view (note: typo in source — `sectioin`, not `section`) |

---

## 14. Field of Study (FoS) Hierarchy

### FoS levels

| Level | Granularity | Count | Examples |
|---|---|---|---|
| 0 | Broadest | ~19 | Medicine, Physics, Computer Science |
| 1 | Intermediate | ~300 | Neuroscience, Oncology, AI |
| 2+ | Narrow | Thousands | Specific sub-disciplines |

### Which FoS source to use

| Source | Table | Available when | Use for |
|---|---|---|---|
| OpenAlex (AIRAK) | `airak.PublicationFieldOfStudy` | After publication only | Published article classification |
| EarlyFoS (AA model) | `ocean-tech-adv-analytics-c-esf.fos_evaluated.pub_earlyfos` | At submission time | Pre-publication scope checks |
| Dimensions | `dimensions.publications.concepts_scores` (nested) | After publication | Alternative scoring; use `CROSS JOIN UNNEST` |

```sql
-- Journal top FoS (Level 0)
FROM `ocean-breeze-tier-1.airak.JournalFieldOfStudy` jfos
JOIN `ocean-breeze-tier-1.airak.FieldOfStudy` fos
  ON jfos.FieldOfStudyId = fos.FieldOfStudyId
WHERE fos.Level = 0
ORDER BY jfos.Score DESC;

-- EarlyFoS: filter by level and score threshold
SELECT pub_id, fos, fos_score, fos_level
FROM `ocean-tech-adv-analytics-c-esf.fos_evaluated.pub_earlyfos`
WHERE fos_score > 0.01
  AND fos_level = 0;
```

---

## 15. Common Query Patterns

### 15.1 Peer review turnaround times

```sql
SELECT
  EXTRACT(YEAR FROM stage_date_submitted) AS year,
  ROUND(AVG(DATETIME_DIFF(
    reviewer_last_independent_review_submitted,
    reviewer_first_independent_review_submitted,
    DAY
  )), 2) AS days_between_reviews
FROM `ocean-breeze-tier-1.reporting_data_mart.article`
WHERE reviewer_first_independent_review_submitted IS NOT NULL
  AND EXTRACT(YEAR FROM stage_date_submitted) IN (2024, 2025)
GROUP BY 1
ORDER BY 1;
```

### 15.2 Institutional publication tracking

```sql
FROM `ocean-breeze-tier-1.reporting_data_mart.author` a
JOIN `ocean-breeze-tier-1.reporting_data_mart.organization` o
  ON a.author_organization_id = o.organization_id
-- Roll up to parent institutions:
JOIN `ocean-breeze-tier-1.airak.OrganizationTopParent` tp
  ON o.rosst_id = tp.OrganizationId  -- confirm join key with your project's org bridge
```

### 15.3 Salesforce SQL-to-Interested conversion rate

```sql
-- Always use BigQuery mirror — not the Salesforce API
SELECT
  opportunity_owner_id,
  COUNT(*)                                     AS total_opps,
  COUNTIF(stage_name = 'Interested')           AS converted,
  ROUND(COUNTIF(stage_name = 'Interested') / COUNT(*), 3) AS conversion_rate
FROM `ocean-breeze-tier-2.salesforce.opportunity`
WHERE opportunity_record_type_name = 'Research Topics'
GROUP BY 1;
```

### 15.4 Competitor author mapping (authors publishing in similar journals)

```sql
SELECT
  auth.AuthorId,
  auth.FullName,
  loop_src.loop_id,
  jnl.DisplayName AS journal
FROM `ocean-breeze-tier-1.airak.PublicationAuthor` pub_auth
JOIN `ocean-breeze-tier-1.airak.Publication`        pub      ON pub_auth.PublicationId = pub.PublicationId
JOIN `ocean-breeze-tier-1.airak.Author`             auth     ON pub_auth.AuthorId      = auth.AuthorId
JOIN `ocean-breeze-tier-1.airak.Journal`            jnl      ON pub.JournalId          = jnl.JournalId
JOIN `ocean-breeze-tier-1.airak.JournalMetadata`    jnl_md   ON jnl.JournalId          = jnl_md.JournalId
LEFT JOIN (
  SELECT AuthorId, SourceValue AS loop_id
  FROM `ocean-breeze-tier-1.airak.AuthorSource`
  WHERE SourceId = 20
) loop_src ON auth.AuthorId = loop_src.AuthorId
WHERE jnl_md.IsOpenForSubmissions = TRUE
  AND pub.JournalId > -1
GROUP BY 1, 2, 3, 4;
```

---

## 16. Organisation Data Priority Rules

When a researcher appears in both Loop and AIRAK, **Loop takes priority**:

**Country fallback chain:**
1. Loop User Organisation Country
2. AIRAK User Organisation Country
3. AIRAK User Country
4. AIRAK User Primary Email Country
5. AIRAK Email Country

**Organisation fallback chain:**
1. Loop User Organisation
2. AIRAK User Organisation
3. AIRAK Email Organisation

> `reporting_data_mart.person` may show a **different primary org** than `airak.AuthorOrganization` for the same person. If you need AIRAK's assignment specifically, query it directly rather than assuming RDM and AIRAK agree.

---

## 17. RT Contributor Counts — Cross-Platform Discrepancies

Tableau, Salesforce, and RTM return **different counts for the same metric**. Always state your source.

| Metric | RTM | Salesforce | Tableau |
|---|---|---|---|
| Potential Contributors | All added to RTM (excl. co-authors, deleted) | Same as RTM | Only curated contributors → lower count |
| Invited Contributors | Status = "Pending" (incl. manual logging) | Only CfPs sent via RTM | Requires invite date OR evidence of curation |
| Spontaneous Contributors | Source = "Spontaneous Submission" | Same | May override to "Invited" if abstract submitted spontaneously |
| Confirmed Contributors | Accepts CfP / submits abstract / transferred | Similar, may differ on transfer logic | Similar, with spontaneous overrides |

---

## 18. Glossary of Domain Abbreviations

| Term | Meaning | ⚠️ Gotcha |
|---|---|---|
| SQL | **Sales Qualified Lead** (Salesforce pipeline stage) | Not the query language in this context |
| RT | Research Topic | — |
| TE | Topic Editor | — |
| AE | Associate Editor | — |
| RE | Review Editor | — |
| SCE | Specialty Chief Editor | — |
| HE | Handling Editor | — |
| EBM | Editorial Board Member | — |
| OOS | Out of Scope | Specific methodology with defined thresholds (see §9.5) |
| IRR | Independent Review Report | — |
| NPS | Net Promoter Score | — |
| CFJ | Closest Frontiers Journal | — |
| RDM | Reporting Data Mart | = `reporting_data_mart` dataset |
| CfP | Call for Papers | — |
| IC | Invited Contributor | — |
| CC | Confirmed Contributor | — |
| RTLA | Research Topic Launch Assistant | — |
| JHC | Journal Health Check | — |
| FoS | Field of Study | OpenAlex taxonomy — not the same as Dimensions concepts |
| ROSST | Research Organisation Shared Services Tool | Replacing Ugarit as org identifier |
| APC | Article Processing Charge | — |
| CDP | Content Delivery Platform | Source of views/downloads/citations |
| AIRAK / AIRA | AI-enriched bibliometric platform | `airak` dataset in BigQuery |

---

## 19. Upcoming Platform Changes

| Change | Status | Impact |
|---|---|---|
| **ROSST replacing Ugarit** | Deployment pending | Organisation IDs will change — existing Ugarit IDs phased out |
| **AIRAK v2 invitation metrics** | In design | New tables: `AuthorInvitationMetric`, `AuthorInvitationByYear`, `AuthorInvitationByWindow`, `AuthorInvitation` |
| **AI Reporting semantic layer** | Discovery phase | Star schemas + MetricFlow/dbt on BQ. RDM continues alongside. |
| **EarlyFoS repointing** | In progress | JHC scope-checking scripts repointing from reference tables to EarlyFoS and ocean-breeze taxonomy tables |
| **Researcher Profile Pipeline** | Migrating Q2 2026 | Moving from Innovation Hub Databricks workspace to engineering workspace. 8 critical findings open. |
