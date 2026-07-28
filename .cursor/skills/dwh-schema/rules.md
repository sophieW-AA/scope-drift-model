# Rules: SQL Server DWH querying

## Database priority

1. **FrontiersReports** — First choice (star-schema reporting)
2. **ReportingDataMart** — Second choice (wide denormalized tables)
3. **TenantsDataMarts** — Last resort (granular/transactional)

## KPI / governance

1. **KPI definitions:** Take KPI meaning from [glossary.yml](glossary.yml). For each term, use the `description` plus `referenced_tables`.
2. **Not literal SQL:** Glossary descriptions are not runnable as-is—translate them into T-SQL predicates on the referenced tables.
3. **Join safety:** See [semantic-layer.md](semantic-layer.md) for safe joins when multiple tables are involved.

## Required workflow check

Before drafting SQL:
1. Check [glossary.yml](glossary.yml) for KPI definitions
2. Review [semantic-layer.md](semantic-layer.md) for join paths
3. Check [examples.md](examples.md) for similar patterns

---

## T-SQL conventions

- Use **3-part names**: `[Database].[Schema].[Table]`
- **Bracket** all identifiers with spaces or dots: `[StageDate.EditorialAssignment.Source]`
- Use **`WITH` (CTE)** for staged logic
- Use **`SELECT TOP (n)`** for exploration (not `LIMIT`)
- Use **`FORMAT(date, 'yyyy-MM')`** for month grouping

---

## Date column choices

- **`[StageDate.Submitted]`** — Default for "submission date"
- **`[StageDate.EditorialAssignment.Source]`** — When tracking editorial assignment
- Ask if unclear which date the user needs

---

## Article type filter

- Default to `ArticleType = 'Original Research'` unless user specifies otherwise
- Ask if user wants all article types

---

## Rejection analysis

When analyzing rejections:
- **Who rejected:** Check both `[RejectionRecommenderRoleAbbr]` AND `[RejecterRoleAbbr]`
- **Stage of rejection:** Use `[RejectedAtStage]` or check if `[REAssignment.JoinDate]` is NULL (rejected before RE assigned)

---

## Join safety

- Default article KPIs are **article-grain** unless question requires author/editor grain
- See [semantic-layer.md](semantic-layer.md) before joining author tables
- Use `COUNT(DISTINCT ArticleId)` when joining to authors

---

## Space / tenant filter

- Unless user asks for all spaces, confirm whether `SpaceId = 1` (Frontiers) applies
- TenantsDataMarts tables have `SpaceId` column for filtering

---

## Performance

- Cross-database joins can be expensive; add selective filters (date, status) early
- For `NOLOCK`: only add when following existing pattern in repo
- Use `SELECT TOP (100)` during exploration
