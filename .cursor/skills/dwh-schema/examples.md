# Common query patterns: SQL Server DWH

## Before you run

- For any **named KPI**, check [glossary.yml](glossary.yml) for the definition
- Use [semantic-layer.md](semantic-layer.md) for join paths
- Follow [rules.md](rules.md) for T-SQL conventions

---

## Submitted articles by month

```sql
SELECT
    FORMAT([StageDate.Submitted], 'yyyy-MM') AS month,
    COUNT(*) AS submitted_articles
FROM [ReportingDataMart].[Reporting].[Articles]
WHERE IsSubmitted = 1
    AND IsDeleted = 0
    AND [StageDate.Submitted] IS NOT NULL
GROUP BY FORMAT([StageDate.Submitted], 'yyyy-MM')
ORDER BY month;
```

---

## Accepted articles by year

```sql
SELECT
    YEAR([StageDate.Accepted]) AS acceptance_year,
    COUNT(*) AS accepted_articles
FROM [ReportingDataMart].[Reporting].[Articles]
WHERE IsAccepted = 1
    AND IsDeleted = 0
    AND [StageDate.Accepted] IS NOT NULL
GROUP BY YEAR([StageDate.Accepted])
ORDER BY acceptance_year;
```

---

## Rejected articles by journal

```sql
SELECT
    Journal,
    COUNT(*) AS rejected_articles
FROM [ReportingDataMart].[Reporting].[Articles]
WHERE IsRejected = 1
    AND IsDeleted = 0
GROUP BY Journal
ORDER BY rejected_articles DESC;
```

---

## HE rejections before RE assignment (by month)

```sql
SELECT
    FORMAT([StageDate.EditorialAssignment.Source], 'yyyy-MM') AS month,
    SUM(CASE WHEN [REAssignment.JoinDate] IS NULL THEN 1 ELSE 0 END) AS he_rejects_before_re,
    COUNT(*) AS all_he_rejects,
    ROUND(
        CAST(SUM(CASE WHEN [REAssignment.JoinDate] IS NULL THEN 1 ELSE 0 END) AS FLOAT)
        / NULLIF(COUNT(*), 0) * 100,
        1
    ) AS pct_before_re
FROM [ReportingDataMart].[Reporting].[Articles]
WHERE IsRejected = 1
    AND ([RejectionRecommenderRoleAbbr] = 'AE' OR [RejecterRoleAbbr] = 'AE')
    AND ArticleType = 'Original Research'
    AND YEAR([StageDate.EditorialAssignment.Source]) = 2025
GROUP BY FORMAT([StageDate.EditorialAssignment.Source], 'yyyy-MM')
ORDER BY month;
```

---

## Average review time by journal

```sql
SELECT
    Journal,
    AVG([DaysIn.ReviewTime]) AS avg_review_days,
    COUNT(*) AS article_count
FROM [ReportingDataMart].[Reporting].[Articles]
WHERE IsDecided = 1
    AND [DaysIn.ReviewTime] IS NOT NULL
GROUP BY Journal
ORDER BY avg_review_days;
```

---

## Review board analytics (FrontiersReports)

```sql
SELECT
    rb.[All Article ID],
    a.[New ArticleId],
    ae.[ArticleId],
    ae.[UserId]
FROM [FrontiersReports].[EOf].[ReviewBoardChartsDS] rb
JOIN [FrontiersReports].[BIRep].[ArticlesDS.Articles] a
    ON rb.[All Article ID] = a.[New ArticleId]
LEFT JOIN [FrontiersReports].[BIRep].[ArticlesDS.Editors] ae
    ON rb.[All Article ID] = ae.[ArticleId]
WHERE YEAR(rb.[Some Date Column]) = 2025;
```

---

## Review events by type (TenantsDataMarts)

```sql
SELECT
    re.Event,
    COUNT(*) AS event_count
FROM [TenantsDataMarts].[Journal].[Articles_Review.Events] e
JOIN [TenantsDataMarts].[Journal].[Articles_Review.Event] re
    ON e.ReviewEventId = re.ReviewEventId
WHERE YEAR(e.EventDatetime) = 2025
GROUP BY re.Event
ORDER BY event_count DESC;
```

---

## Articles by domain and field

```sql
SELECT
    Domain,
    Field,
    COUNT(*) AS article_count
FROM [ReportingDataMart].[Reporting].[Articles]
WHERE IsSubmitted = 1
    AND IsDeleted = 0
GROUP BY Domain, Field
ORDER BY article_count DESC;
```

---

## Top 10 journals by submission volume

```sql
SELECT TOP (10)
    Journal,
    COUNT(*) AS submissions
FROM [ReportingDataMart].[Reporting].[Articles]
WHERE IsSubmitted = 1
    AND IsDeleted = 0
    AND YEAR([StageDate.Submitted]) = 2025
GROUP BY Journal
ORDER BY submissions DESC;
```

---

## Interactive Review: Manual vs Automatic activation

**Note:** Manual (3.4) and automatic (3.4a) IR are logged in **different tables**. Must query both.

```sql
WITH manual_ir AS (
    SELECT
        FORMAT(e.EventDatetime, 'yyyy-MM') AS month,
        COUNT(DISTINCT e.ArticleId) AS manual_ir_articles
    FROM [TenantsDataMarts].[Journal].[Articles_Review.Events] e
    WHERE e.WorkflowId = 420  -- 3.4 manual
    GROUP BY FORMAT(e.EventDatetime, 'yyyy-MM')
),
auto_ir AS (
    SELECT
        FORMAT(wt.CreateDate, 'yyyy-MM') AS month,
        COUNT(DISTINCT wt.ArticleId) AS auto_ir_articles
    FROM [TenantsDataMarts].[Journal].[Workflows_Tasks] wt
    WHERE wt.WorkflowId = 629  -- 3.4a automatic
      AND wt.WorkflowStatusId = 3  -- Complete
      AND wt.ArticleId IS NOT NULL
    GROUP BY FORMAT(wt.CreateDate, 'yyyy-MM')
)
SELECT 
    COALESCE(m.month, a.month) AS month,
    ISNULL(m.manual_ir_articles, 0) AS manual_ir_3_4,
    ISNULL(a.auto_ir_articles, 0) AS auto_ir_3_4a,
    ISNULL(m.manual_ir_articles, 0) + ISNULL(a.auto_ir_articles, 0) AS total,
    ROUND(
        CAST(ISNULL(a.auto_ir_articles, 0) AS FLOAT) 
        / NULLIF(ISNULL(m.manual_ir_articles, 0) + ISNULL(a.auto_ir_articles, 0), 0) * 100,
        1
    ) AS pct_auto
FROM manual_ir m
FULL OUTER JOIN auto_ir a ON m.month = a.month
WHERE COALESCE(m.month, a.month) >= '2021-01'
ORDER BY month;
```

---

## Auto-IR timing: Days from RE assignment to trigger

```sql
SELECT
    wt.ArticleId,
    wt.CreateDate AS auto_ir_triggered_at,
    a.[REAssignment.JoinDate] AS re_assigned,
    DATEDIFF(DAY, a.[REAssignment.JoinDate], wt.CreateDate) AS days_from_re_to_auto_ir
FROM [TenantsDataMarts].[Journal].[Workflows_Tasks] wt
JOIN [ReportingDataMart].[Reporting].[Articles] a
    ON wt.ArticleId = a.ArticleId
WHERE wt.WorkflowId = 629  -- 3.4a automatic
  AND wt.WorkflowStatusId = 3  -- Complete
  AND wt.ArticleId IS NOT NULL
  AND a.IsDeleted = 0
  AND a.[REAssignment.JoinDate] IS NOT NULL
  AND YEAR(wt.CreateDate) >= 2024;
```

---

## Reviewer invitation acceptance by HIndex

Join `ReviewBoardChartsDS` to `PersonMetrics` for bibliometric analysis of reviewer invitations.

```sql
SELECT
    pm.HIndexBins,
    COUNT(*) AS total_sent,
    SUM(CASE WHEN rb.[Is Invitation Status Accepted ?] = 1 THEN 1 ELSE 0 END) AS accepted,
    ROUND(
        CAST(SUM(CASE WHEN rb.[Is Invitation Status Accepted ?] = 1 THEN 1 ELSE 0 END) AS FLOAT)
        / NULLIF(COUNT(*), 0) * 100,
        2
    ) AS acceptance_rate_pct
FROM [FrontiersReports].[EOf].[ReviewBoardChartsDS] rb
LEFT JOIN [ReportingDataMart].[Common].[PersonMetrics] pm
    ON rb.[UserId] = pm.[Person.UserId]
WHERE rb.InviteDate >= '2026-03-01'
  AND rb.InviteDate < '2026-04-01'
  AND rb.[AE-RE Workflows] = 'RE Workflows'
  AND rb.[EmailType] = 'Notification'
GROUP BY pm.HIndexBins
ORDER BY 
    CASE pm.HIndexBins 
        WHEN '0' THEN 1
        WHEN '1-5' THEN 2
        WHEN '6-10' THEN 3
        WHEN '11-20' THEN 4
        WHEN '21-50' THEN 5
        WHEN '51+' THEN 6
        ELSE 7
    END;
```
