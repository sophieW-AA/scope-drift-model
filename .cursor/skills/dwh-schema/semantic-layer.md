# Data model: SQL Server DWH

This file describes **grain**, **entity relationships**, and **safe join paths** for SQL Server tables so queries do not duplicate rows or mis-attribute metrics.

## Database scope

Tables span three databases in priority order:
1. `FrontiersReports` — star-schema reporting (EOf, BIRep)
2. `ReportingDataMart` — wide denormalized tables (Reporting schema)
3. `TenantsDataMarts` — transactional/event-level (Journal schema)

---

## Core grains

### FrontiersReports

| Table | Grain | Primary key |
|---|---|---|
| `[EOf].[ReviewBoardChartsDS]` | One row per review-board invitation/event | `[All Article ID]` + context |
| `[BIRep].[ArticlesDS.Articles]` | One row per article | `[New ArticleId]` |
| `[BIRep].[ArticlesDS.Editors]` | One row per editor–article assignment | `[ArticleId]` + `[UserId]` |

### ReportingDataMart

| Table | Grain | Primary key |
|---|---|---|
| `[Reporting].[Articles]` | One row per article (wide denormalized, ~400 cols) | `ArticleId` |
| `[Reporting].[Authors]` | One row per author–article role | `AuthorId` |
| `[Reporting].[Persons]` | One row per person profile | `PersonUserId` |
| `[Reporting].[ResearchTopics]` | One row per research topic | `ResearchTopicId` |
| `[Reporting].[TaxonomyMetrics]` | One row per taxonomy node | `TaxonomyId` |
| `[Reporting].[EditorialBoardMembers]` | One row per board member role | `EditorialBoardMemberId` |

### TenantsDataMarts

| Table | Grain | Primary key |
|---|---|---|
| `[Journal].[Articles]` | One row per article | `ArticleId` |
| `[Journal].[Articles_Review.Events]` | One row per review event | `ArticleId` + `ReviewEventId` |
| `[Journal].[Articles_ReviewBoardInvitations]` | One row per invitation | `ReviewBoardInvitationId` |
| `[Network].[Users]` | One row per user | `UserId` |
| `[Common].[Spaces]` | One row per publishing space | `SpaceId` |

---

## Recommended join paths

### FrontiersReports (star schema)

```
[EOf].[ReviewBoardChartsDS] rb
    JOIN [BIRep].[ArticlesDS.Articles] a ON rb.[All Article ID] = a.[New ArticleId]
    JOIN [BIRep].[ArticlesDS.Editors] ae ON rb.[All Article ID] = ae.[ArticleId]
```

### ReportingDataMart (denormalized — often no joins needed)

The `[Reporting].[Articles]` table is wide and includes taxonomy, dates, metrics, users. Only join when:
- You need author-level detail → join `[Reporting].[Authors]` on `ArticleId`
- You need person profile → join `[Reporting].[Persons]` on `PersonUserId`

```
[Reporting].[Articles] a
    JOIN [Reporting].[Authors] au ON a.ArticleId = au.[AuthorArticleId]
    JOIN [Reporting].[Persons] p ON au.[AuthorPersonUserId] = p.[PersonUserId]
```

### TenantsDataMarts (transactional)

```
[Journal].[Articles_Review.Events] e
    JOIN [Journal].[Articles_Review.Event] re ON e.ReviewEventId = re.ReviewEventId
```

---

## Author joins (high risk of row inflation)

Author data is **one-to-many** from the article perspective (multiple authors per article).

**Rules:**
- When counting **articles**, use `COUNT(DISTINCT ArticleId)` not `COUNT(*)`
- Pre-aggregate at article level before joining to authors
- Joining `Articles` → `Authors` → `Organizations` can multiply rows

---

## Lifecycle dates (ReportingDataMart.Reporting.Articles)

| Business event | Column |
|---|---|
| Editorial assignment | `[StageDate.EditorialAssignment.Source]` |
| Submitted | `[StageDate.Submitted]` |
| In review | `[StageDate.InReview]` |
| Accepted | `[StageDate.Accepted]` |
| Rejected | `[StageDate.Rejected]` |
| Published | `[StageDate.Published]` |
| Decision | `DecidedDate` |

---

## Anti-patterns

- **Cross join** between large tables without join keys
- **Many-to-many explosion**: `Articles` × `Authors` without `DISTINCT` article keys
- Mixing **submission year** and **acceptance year** in one ratio without cohort rules
- Using `COUNT(*)` after author joins when the question is article-level
