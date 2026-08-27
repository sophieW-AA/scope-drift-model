---
name: dwh-schema
description: SQL Server data warehouse schema, T-SQL conventions, and join patterns for FrontiersReports, ReportingDataMart, and TenantsDataMarts. Use when writing SQL queries against the DWH, joining tables, asking about columns/data types, or converting BigQuery to T-SQL.
---

# Data Warehouse Schema Reference

Reference for SQL Server tables and T-SQL conventions in the Frontiers data warehouse (`dataportal.dwh.frontiersin.net`).

Use **T-SQL** conventions. **Do not** rewrite bracketed `[…].[…].[…]` objects as BigQuery backticks—see `bigquery-querying.mdc` for GCP.

---

## Database priority

When writing queries, prefer databases in this order:

1. **`FrontiersReports`** — First choice. Star-schema reporting tables (`EOf`, `BIRep`). Best for review board analytics, editor metrics, article dimensions.
2. **`ReportingDataMart`** — Second choice. Wide denormalized tables (`Reporting.Articles`). Best for article lifecycle analytics when FrontiersReports doesn't have the columns you need.
3. **`TenantsDataMarts`** — Last resort. Transactional/event-level tables (`Journal` schema). Use only when you need granular event data not available in the reporting layers.

---

## Connection (Python / notebooks)

- **`pyodbc`** with **`DRIVER={ODBC Driver 17 for SQL Server}`**
- **Server:** `dataportal.dwh.frontiersin.net,11433`
- **Databases:** `FrontiersReports`, `ReportingDataMart`, `TenantsDataMarts` (in priority order)
- **Windows auth:** `UID=OFFICE\{first}.{last};`, `PWD=…` often empty, `Trusted_Connection=yes`
- Store connection as **`conn_dwh`**; query with **`pandas.read_sql_query(sql, conn_dwh)`**
- **Never commit** real passwords or production credentials

---

## Object naming (3- and 4-part names)

- **Bracket** all identifiers with **spaces** or **dots**: `[All Article ID]`, `[StageDate.EditorialAssignment.Source]`
- Prefer **3-part names** for clarity: `[Database].[Schema].[Table]`
- **4-part names** for linked server / remote DB: `[server].[database].[schema].[Table]` with `WITH (NOLOCK)` where existing queries use it

---

## Common schemas

| Database | Schema | Contains | Priority |
|---|---|---|---|
| FrontiersReports | EOf | Review board charts, editor analytics (`ReviewBoardChartsDS`) | **1st** |
| FrontiersReports | BIRep | Article and editor dimension tables (`ArticlesDS.Articles`, `ArticlesDS.Editors`) | **1st** |
| ReportingDataMart | Reporting | Wide denormalized tables — `Articles` (400+ cols), `Authors`, `Editors`, `ResearchTopics` | **2nd** |
| ReportingDataMart | Product | Article sub-tables (dates, metrics, users) — usually not needed | 2nd |
| ReportingDataMart | Process | Editorial board, invitations | 2nd |
| ReportingDataMart | Person | Person/user data | 2nd |
| TenantsDataMarts | Journal | Article events, reviews, invitations, recognition — granular/transactional | **3rd** |

---

## Key tables

### Priority 1: FrontiersReports

#### `[FrontiersReports].[EOf].[ReviewBoardChartsDS]`

Central fact-style table for review-board / invitation analytics. Common aliases: `rb`, `d`. **Try this first** for editor/reviewer metrics.

#### `[FrontiersReports].[BIRep].[ArticlesDS.Articles]`

Article grain table. Join key: `rb.[All Article ID] = a.[New ArticleId]`

#### `[FrontiersReports].[BIRep].[ArticlesDS.Editors]`

Editor roles per article. Join: `rb.[All Article ID] = ae.[ArticleId]` (alias `ae`)

### Priority 2: ReportingDataMart

#### `[ReportingDataMart].[Common].[PersonMetrics]`

Person-level metrics including **HIndex**, `HIndexBins`, publication counts, activity percentiles, and organization data. Join key: `[Person.UserId]` (int). Use for reviewer/editor bibliometric analysis.

#### `[ReportingDataMart].[Reporting].[Articles]`

Wide denormalized table (~400+ columns). Use when FrontiersReports doesn't have the columns you need. Includes:

- **Core:** `ArticleId`, `ArticleType`, `Stage`, `IsSubmitted`, `IsAccepted`, `IsPublished`, `IsRejected`, `IsDeleted`
- **Dates:** `[StageDate.EditorialAssignment.Source]`, `[StageDate.Submitted]`, `[StageDate.Rejected]`, `[StageDate.Published]`
- **Key metrics:** `[REAssignment.JoinDate]`, `[DaysIn.ReviewTime]`, `[DaysIn.EditorialAssignment]`
- **Rejection:** `[RejectionRecommenderRoleAbbr]`, `[RejecterRoleAbbr]`, `[FirstRejectionReasonLabel]`
- **Taxonomy:** `Journal`, `Section`, `Domain`, `Field`, `Specialty`

### Priority 3: TenantsDataMarts

#### `[TenantsDataMarts].[Journal].[Articles_Review.Events]`

Event-level data for article review lifecycle. Use only when you need granular event data. Join to `[Articles_Review.Event]` on `ReviewEventId` (aliases `e`, `re`).

#### `[TenantsDataMarts].[Journal].[Workflows_Tasks]`

Workflow task tracking. Contains `WorkflowId`, `WorkflowStatusId`, `ArticleId`, `CreateDate`. Join to `[Workflows]` on `WorkflowId` and `[Workflows_Status]` on `WorkflowStatusId`.

#### `[TenantsDataMarts].[Journal].[Articles_ReviewBoardInvitations]`

Linked from `ReviewBoardChartsDS` on `ReviewBoardInvitationId` (use **LEFT JOIN** to keep all chart rows).

---

## Workflow data sources (important quirk)

**Different workflows are logged in different tables.** When querying workflow data, check both `Articles_Review.Events` and `Workflows_Tasks`:

| WorkflowNo | Workflow | WorkflowId | Primary data source |
|---|---|---|---|
| 3.4 | Activate Interactive Review (manual) | 420 | `Articles_Review.Events` |
| 3.4a | Automatic Activation of Interactive Review | 629 | `Workflows_Tasks` |

**Example:** To compare manual vs automatic IR activation, you must query **both** tables:
- Manual (3.4): `Articles_Review.Events` WHERE `WorkflowId = 420`
- Automatic (3.4a): `Workflows_Tasks` WHERE `WorkflowId = 629 AND WorkflowStatusId = 3` (Complete)

Using only one table will give incomplete data. Always verify which table contains the workflow you need by checking row counts in both.

---

## Join patterns (recurring)

| Pattern | Typical ON clause / note |
|---|---|
| RB charts → articles | `rb.[All Article ID] = a.[New ArticleId]` |
| RB charts → editors (per article) | `rb.[All Article ID] = ae.[ArticleId]` |
| RB charts → review-board invitations | `tr.ReviewBoardInvitationId = rb.ReviewBoardInvitationId` (LEFT keeps all chart rows) |
| RB charts → person metrics (HIndex) | `rb.[UserId] = pm.[Person.UserId]` — for reviewer/editor HIndex, bibliometrics |
| Review events → event type | `e.ReviewEventId = re.ReviewEventId`; filter `Event`, `YEAR(EventDatetime)`, `CreatorRoleId` |
| CTE → self / filtered set | Build distinct user/article set in `WITH`, then `JOIN` on keys |

- **Aggregate first, then join wide** — CTE grouped by `[All Article ID]`, outer query LEFT JOINs back for labels
- Prefer **explicit INNER vs LEFT** to match intent

---

## SQL style

- **`WITH` (CTE)** for staged logic; leading **`;WITH`** when required by preceding statements
- **`SELECT TOP (n)`** for quick probes (not `LIMIT`)
- **Window functions:** `ROW_NUMBER() OVER (PARTITION BY … ORDER BY …)` then `WHERE rn = 1`
- **Dates:** `DATEDIFF`, `YEAR()`, `FORMAT(date, 'yyyy-MM')`; `DECLARE @… DATETIME2` for parameters
- **String cleanup:** `UPPER(LTRIM(RTRIM(...)))` or `LTRIM(RTRIM(LOWER(...)))` for roles/statuses
- **Comments** for event codes / business rules (e.g. `'1.6'` = AE accepts invitation, `'2.3'` = invite RE)

---

## BigQuery → T-SQL conversion

| BigQuery | SQL Server |
|---|---|
| `FORMAT_DATE('%Y-%m', col)` | `FORMAT(col, 'yyyy-MM')` |
| `COUNTIF(condition)` | `SUM(CASE WHEN condition THEN 1 ELSE 0 END)` |
| `SAFE_DIVIDE(a, b)` | `CAST(a AS FLOAT) / NULLIF(b, 0)` |
| `EXTRACT(YEAR FROM col)` | `YEAR(col)` |
| Backtick identifiers | Square brackets `[...]` |
| `LIMIT n` | `SELECT TOP (n)` |

---

## Quality / safety

- Align new SQL with **neighbouring cells** or same schema objects—do not invent schema
- Cross-database joins can be expensive; add **selective filters** (date, status) early
- For **`NOLOCK`**: only add/keep when following existing pattern; document if changing isolation semantics

---

## Reference files

| File | Contents |
|---|---|
| [schema-reference.yml](schema-reference.yml) | **Primary** — structured schema (YAML) |
| [schema-reference.md](schema-reference.md) | Human-readable schema (Markdown) |
| [semantic-layer.md](semantic-layer.md) | Table grains, PKs, safe join paths |
| [glossary.yml](glossary.yml) | Business KPI definitions |
| [rules.md](rules.md) | Query rules and governance |
| [examples.md](examples.md) | Common query patterns |

## Regenerating the schema

Run [scripts/extract_schema.ipynb](scripts/extract_schema.ipynb) to refresh schema files from SQL Server.

## Required workflow

Before drafting SQL:
1. Check [glossary.yml](glossary.yml) for KPI definitions
2. Review [semantic-layer.md](semantic-layer.md) for join paths and grain
3. Check [examples.md](examples.md) for similar patterns
4. Follow [rules.md](rules.md) for T-SQL conventions
