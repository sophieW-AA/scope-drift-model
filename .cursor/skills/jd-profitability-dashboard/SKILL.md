---
name: jd-profitability-dashboard
description: Frontiers Media SA journal-level profitability, operational efficiency, and high-level strategic dashboard analysis. Use when the user asks about journal economics, revenue yield, editorial efficiency, wasted effort, submission-to-publication conversion, journal portfolio strategy, quadrant analysis, comparative journal performance (Stars, Workhorses, Optimize, Long Tail), overall business performance, submission trends, acceptance rates, geographic distribution, domain growth, author retention, editorial pipeline speed, research topic performance, or any cross-cutting strategic question about Frontiers operations.
---

# Journal Profitability & Strategic Dashboard

Combined skill for both journal-level profitability analysis and cross-cutting strategic dashboards using `ocean-breeze-tier-1.reporting_data_mart`.

---

## Part 1 — Journal Profitability Analysis

Analyze journal-level operational efficiency as a proxy for profitability using `ocean-breeze-tier-1.reporting_data_mart.article`.

### Profitability Framework

Two axes define journal health:

- **Revenue Yield %** = paying articles published ÷ total submissions × 100. Higher is better.
- **Wasted Effort %** = peer-reviewed rejections (rejected *after* review, not at desk) ÷ total submissions × 100. Lower is better.

### Quadrant Classification

Classify journals with 100+ annual submissions into four quadrants using the median revenue yield and median wasted effort as thresholds. Tag journals below 100 submissions as "Long Tail".

| Quadrant | Yield | Waste | Action |
|----------|-------|-------|--------|
| **Stars** | ≥ median | ≤ median | Protect and replicate |
| **Workhorses** | ≥ median | > median | Shift rejections earlier in pipeline |
| **Emerging** | < median | ≤ median | Improve inbound quality; highest volume lives here |
| **Optimize** | < median | > median | Tighten scope, add pre-screening, raise desk rejection rate |
| **Long Tail** | — | — | Evaluate: invest or sunset |

### Core Profitability Query

```sql
WITH journal_metrics AS (
  SELECT
    journal_id, journal, journal_maturity, domain, program,
    jcr_impact_factor_last AS impact_factor,

    -- Volume
    COUNTIF(is_submitted AND EXTRACT(YEAR FROM stage_date_submitted) = @year) AS submitted,
    COUNTIF(is_published AND EXTRACT(YEAR FROM stage_date_published) = @year) AS published,
    COUNTIF(is_paying_article AND is_published
      AND EXTRACT(YEAR FROM stage_date_published) = @year) AS paying_published,

    -- Funnel
    COUNTIF(is_rejected AND EXTRACT(YEAR FROM stage_date_submitted) = @year) AS rejected,
    ROUND(COUNTIF(is_accepted AND EXTRACT(YEAR FROM stage_date_submitted) = @year)
      / NULLIF(COUNTIF(is_decided AND EXTRACT(YEAR FROM stage_date_submitted) = @year), 0)
      * 100, 1) AS acceptance_rate,

    -- Desk vs peer-reviewed rejections
    COUNTIF(is_rejected AND EXTRACT(YEAR FROM stage_date_submitted) = @year
      AND (rejected_at_stage IN ('Initial Validation', 'Editorial Assignment')
           OR stage_date_in_review IS NULL)) AS desk_rejected,

    -- Speed
    ROUND(AVG(CASE WHEN is_decided AND EXTRACT(YEAR FROM stage_date_submitted) = @year
      THEN days_in_Review_time END), 1) AS avg_review_days,
    ROUND(AVG(CASE WHEN is_decided AND EXTRACT(YEAR FROM stage_date_submitted) = @year
      THEN days_in_editorial_assignment END), 1) AS avg_editorial_assign_days,

    -- Reviewer load
    ROUND(AVG(CASE WHEN is_decided AND EXTRACT(YEAR FROM stage_date_submitted) = @year
      THEN reviewers_count END), 1) AS avg_reviewers,

    -- Impact
    ROUND(AVG(CASE WHEN is_published THEN count_views END)) AS avg_views,
    ROUND(AVG(CASE WHEN is_published THEN count_citations END), 1) AS avg_citations,

    -- Geographic concentration
    ROUND(COUNTIF(article_country8_regions_bin = 'China'
        AND EXTRACT(YEAR FROM stage_date_submitted) = @year)
      / NULLIF(COUNTIF(EXTRACT(YEAR FROM stage_date_submitted) = @year
        AND article_country8_regions_bin IS NOT NULL), 0) * 100, 1) AS china_pct,

    -- Author loyalty
    ROUND(COUNTIF(any_author_is_returning
        AND EXTRACT(YEAR FROM stage_date_submitted) = @year)
      / NULLIF(COUNTIF(EXTRACT(YEAR FROM stage_date_submitted) = @year), 0)
      * 100, 1) AS returning_author_pct

  FROM `ocean-breeze-tier-1.reporting_data_mart.article`
  WHERE journal_id IS NOT NULL
  GROUP BY 1, 2, 3, 4, 5, 6
)
SELECT *,
  ROUND(paying_published / NULLIF(submitted, 0) * 100, 1) AS revenue_yield_pct,
  rejected - desk_rejected AS peer_reviewed_rejections,
  ROUND(desk_rejected / NULLIF(rejected, 0) * 100, 1) AS desk_rejection_pct,
  ROUND((rejected - desk_rejected) / NULLIF(submitted, 0) * 100, 1) AS wasted_effort_pct
FROM journal_metrics
ORDER BY paying_published DESC
```

Replace `@year` with the target year (default: most recent full year).

### Key Profitability Metrics

Always include in analysis output:

1. **Revenue yield %** — the single best efficiency metric
2. **Wasted effort %** — editorial cost burned on late-stage rejections
3. **Desk rejection %** — proportion of rejections caught early (higher = more efficient)
4. **Avg review days** and **avg editorial assignment days** — speed indicators
5. **China submission %** — geographic concentration risk
6. **Returning author %** — community loyalty signal
7. **Impact factor** — brand/prestige positioning

### Profitability Output Format

When producing a profitability analysis:

1. Compute quadrant medians and classify all journals.
2. Present a summary table grouped by quadrant with totals.
3. Highlight the top 5 journals in each quadrant by paying articles.
4. Generate a scatter plot (revenue yield vs wasted effort, bubble size = paying articles, color = quadrant).
5. Export full data as formatted Excel with color-coded categories, frozen headers, and auto-filters.
6. End with 3–5 actionable recommendations tied to specific journals or quadrants.

---

## Part 2 — Strategic Dashboard

Generate a cross-cutting strategic overview of Frontiers business health.

### Six-Panel Dashboard

Produce a 2×3 grid of charts covering these dimensions:

#### 1. Submission Funnel (bar chart by year)

```sql
SELECT
  EXTRACT(YEAR FROM stage_date_submitted) AS year,
  COUNT(*) AS submitted,
  COUNTIF(is_accepted) AS accepted,
  COUNTIF(is_published) AS published,
  COUNTIF(is_rejected) AS rejected,
  ROUND(COUNTIF(is_accepted) / NULLIF(COUNTIF(is_decided), 0) * 100, 1) AS acceptance_rate,
  ROUND(AVG(CASE WHEN is_decided THEN days_in_Review_time END), 1) AS avg_review_days
FROM `ocean-breeze-tier-1.reporting_data_mart.article`
WHERE EXTRACT(YEAR FROM stage_date_submitted) BETWEEN @start_year AND @end_year
  AND is_submitted
GROUP BY 1 ORDER BY 1
```

#### 2. Acceptance Rate Trend (line chart)

Plot `acceptance_rate` from query above. Add a 50% reference line. Flag sustained declines.

#### 3. Geographic Distribution (horizontal bar)

```sql
SELECT
  article_country8_regions_bin AS region,
  COUNT(*) AS submitted,
  COUNTIF(is_accepted) AS accepted,
  ROUND(COUNTIF(is_accepted) / NULLIF(COUNTIF(is_decided), 0) * 100, 1) AS acceptance_rate,
  ROUND(AVG(CASE WHEN is_published THEN count_views END)) AS avg_views,
  ROUND(AVG(CASE WHEN is_published THEN count_citations END), 1) AS avg_citations
FROM `ocean-breeze-tier-1.reporting_data_mart.article`
WHERE EXTRACT(YEAR FROM stage_date_submitted) >= @recent_years_start
  AND is_submitted AND article_country8_regions_bin IS NOT NULL
GROUP BY 1 ORDER BY submitted DESC
```

#### 4. Review Pipeline Speed (multi-line by year)

```sql
SELECT
  EXTRACT(YEAR FROM stage_date_submitted) AS year,
  ROUND(AVG(days_in_initial_validation), 1) AS initial_validation,
  ROUND(AVG(days_in_editorial_assignment), 1) AS editorial_assignment,
  ROUND(AVG(days_in_independent_review), 1) AS independent_review,
  ROUND(AVG(days_in_interactive_review), 1) AS interactive_review,
  ROUND(AVG(overall_quality_rating), 2) AS avg_quality_rating
FROM `ocean-breeze-tier-1.reporting_data_mart.article`
WHERE EXTRACT(YEAR FROM stage_date_submitted) BETWEEN @start_year AND @end_year
  AND is_submitted AND is_decided
GROUP BY 1 ORDER BY 1
```

#### 5. Author Retention (bar chart by year)

```sql
SELECT
  EXTRACT(YEAR FROM stage_date_submitted) AS year,
  ROUND(COUNTIF(any_author_is_returning) / COUNT(*) * 100, 1) AS returning_pct,
  ROUND(COUNTIF(author_is_ebm) / COUNT(*) * 100, 1) AS ebm_author_pct,
  ROUND(COUNTIF(is_accepted AND any_author_is_returning)
    / NULLIF(COUNTIF(is_decided AND any_author_is_returning), 0) * 100, 1) AS returning_acceptance_rate,
  ROUND(COUNTIF(is_accepted AND NOT any_author_is_returning)
    / NULLIF(COUNTIF(is_decided AND NOT any_author_is_returning), 0) * 100, 1) AS new_author_acceptance_rate
FROM `ocean-breeze-tier-1.reporting_data_mart.article`
WHERE EXTRACT(YEAR FROM stage_date_submitted) BETWEEN @start_year AND @end_year
  AND is_submitted
GROUP BY 1 ORDER BY 1
```

#### 6. Domain Split (pie or donut chart)

```sql
SELECT
  domain,
  COUNT(*) AS submitted,
  COUNTIF(is_accepted) AS accepted,
  COUNTIF(is_published) AS published,
  ROUND(COUNTIF(is_accepted) / NULLIF(COUNTIF(is_decided), 0) * 100, 1) AS acceptance_rate,
  ROUND(AVG(CASE WHEN is_published THEN count_citations END), 1) AS avg_citations,
  ROUND(AVG(CASE WHEN is_published THEN count_views END)) AS avg_views
FROM `ocean-breeze-tier-1.reporting_data_mart.article`
WHERE EXTRACT(YEAR FROM stage_date_submitted) >= @recent_years_start
  AND is_submitted AND domain IS NOT NULL
GROUP BY 1 ORDER BY submitted DESC
```

### Supplementary: Research Topics Performance

```sql
SELECT
  EXTRACT(YEAR FROM research_topic_create_date) AS year,
  COUNT(*) AS rt_created,
  COUNTIF(is_online) AS online,
  COUNTIF(is_completed) AS completed,
  ROUND(AVG(count_published_articles), 1) AS avg_published_articles,
  ROUND(AVG(CASE WHEN count_published_articles > 0 THEN count_articles_views END)) AS avg_views,
  ROUND(AVG(CASE WHEN count_published_articles > 0 THEN count_articles_citations END), 1) AS avg_citations
FROM `ocean-breeze-tier-1.reporting_data_mart.research_topic`
WHERE EXTRACT(YEAR FROM research_topic_create_date) BETWEEN @start_year AND @end_year
GROUP BY 1 ORDER BY 1
```

Surface this when the user asks about research topics or content strategy.

### Supplementary: Top Journals Table

```sql
SELECT
  journal,
  COUNTIF(EXTRACT(YEAR FROM stage_date_published) = @year) AS published,
  ROUND(AVG(CASE WHEN is_published THEN count_views END)) AS avg_views,
  ROUND(AVG(CASE WHEN is_published THEN count_citations END), 1) AS avg_citations,
  MAX(jcr_impact_factor_last) AS impact_factor
FROM `ocean-breeze-tier-1.reporting_data_mart.article`
WHERE is_published AND EXTRACT(YEAR FROM stage_date_published) >= @year - 1
GROUP BY 1 ORDER BY published DESC
LIMIT 15
```

---

## Shared Interpretation Heuristics

- Revenue yield below 30% signals a journal attracting many unsuitable manuscripts.
- Wasted effort above 25% means 1 in 4 submissions consumes full review resources before rejection.
- China % above 50% combined with low acceptance rate suggests a quality-filtering problem, not a demand problem.
- Returning author % below 80% may indicate author dissatisfaction or competitive attrition.
- Editorial assignment days above 40 is the most common bottleneck — prioritize editor capacity.
- Desk rejection % below 50% means too many unsuitable manuscripts reach peer review.
- **Submission surge + declining acceptance**: Growing inbound demand with quality pressure. Focus on upstream filtering, not restricting volume.
- **Single-region dominance > 50%**: Geographic concentration risk. Track acceptance rate by region — a large gap signals quality filtering, not bias.
- **EBM author share declining**: Leading indicator of community disengagement. Investigate with targeted survey.
- **Research topic completions declining**: Content pipeline risk. Check if RT creation is also slowing or just conversion.
- **HSS and Sustainability acceptance rates > Health/Science**: Smaller, higher-quality portfolios with outsized growth potential.

## Output Conventions

1. Use `matplotlib` with appropriate subplot grids. For strategic dashboards: 2×3 at `figsize=(18, 10)`. For profitability: scatter + supporting panels.
2. Title strategic dashboards "Frontiers — Strategic Dashboard". Title profitability charts "Frontiers — Journal Profitability".
3. Always export charts as PNG and provide a download link.
4. Follow with 3–5 numbered strategic insights, each stating the finding, the business implication, and a recommended action.
5. Use the `brand-guidelines` skill colors when available.
6. Color-code quadrants consistently: Stars = green, Workhorses = orange, Emerging = blue, Optimize = red, Long Tail = grey.
7. Use bubble size proportional to paying articles published.
8. Label the top 10 journals by volume on scatter plots.
9. Invert the y-axis on the quadrant chart so lower waste appears higher (better).
10. Export full profitability data as formatted Excel with color-coded categories, frozen headers, and auto-filters.

## Reference Examples

The `assets/` directory contains example outputs from real analysis runs. Use these as templates for chart style and layout.

- `assets/journal-profitability-full.xlsx` — Complete dataset of all 241 journals with quadrant categories, color-coded headers, and auto-filters. Use as a baseline for comparison when generating updated analyses.
- `assets/strategic-dashboard.png` — Six-panel strategic overview: submission funnel, acceptance rate trend, geographic mix, review stage duration, returning author %, and domain split.
- `assets/journal-profitability-quadrant.png` — Four-panel profitability view: quadrant scatter plot (yield vs waste, bubble = paying articles), top 20 by revenue yield, top 20 by wasted effort, and impact factor vs efficiency.
