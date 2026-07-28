---
name: partnership-transfer-revenue
description: Calculate total APC revenue from articles transferred from a Frontiers Publishing Partnerships journal (e.g. Transplant International, European Journal of Anaesthesiology) to Frontiers-owned journals. Use when asked about transfer revenue, APC income from partnership transfers, or the financial value of manuscript transfers from any partnership journal. Combines BigQuery article data with Salesforce discount/waiver records and current journal APC rates.
---

# Partnership Transfer Revenue Analysis

Calculate net APC revenue earned by Frontiers from manuscripts transferred out of a Publishing Partnerships journal into Frontiers-owned journals.

## Process

1. Identify the source partnership journal name (ask the user if unclear)
2. Query transferred articles from BigQuery
3. Join with Salesforce discount/waiver data
4. Look up current APC rates for each receiving journal
5. Calculate net fees and produce an Excel report

## Step 1 — Query transferred articles

Query `reporting_data_mart.article` for published, paying articles transferred from the partnership journal. Key filters and fields:

```sql
SELECT
  article_id, title, doi, journal, source_journal,
  article_type, article_type_category, stage,
  is_paying_article,
  stage_date_published, stage_date_submitted
FROM `ocean-breeze-tier-1.reporting_data_mart.article`
WHERE LOWER(source_journal) LIKE '%<JOURNAL_NAME>%'
  AND stage = 'Published'
  AND is_paying_article = TRUE
ORDER BY journal, stage_date_published DESC
```

Key columns:
- `source_journal` — the partnership journal the article was transferred from
- `article_type_category` — A, B, or C (maps to APC tier)
- `is_paying_article` — whether the article incurs an APC

## Step 2 — Join with Salesforce discount data

Link through `salesforce.Article__c` to `salesforce.Discount_Code__c` to find actual fees paid when a waiver or discount was applied.

Join logic:
- `reporting_data_mart.article.article_id` minus 1000000000000000, cast to STRING = `Article__c.ArticleId__c`
- `Discount_Code__c.Article__c` = `Article__c.Id`

Key fields from `Discount_Code__c`:
- `InitialFee__c` — listed APC before discount
- `DiscountPercentage__c` — percentage discount applied
- `DiscountedAmount__c` — absolute discount amount
- `NetFee__c` — actual amount paid by the author
- `CurrencyIsoCode` — CHF or USD
- `DecisionStatus__c` — use only records with `Processed_Approved`

Combined query:

```sql
SELECT
  rdm.article_id, rdm.title, rdm.doi, rdm.journal, rdm.source_journal,
  rdm.article_type, rdm.article_type_category, rdm.stage,
  rdm.stage_date_published,
  dc.InitialFee__c, dc.DiscountPercentage__c,
  dc.DiscountedAmount__c, dc.NetFee__c,
  dc.CurrencyIsoCode, dc.DecisionStatus__c
FROM `ocean-breeze-tier-1.reporting_data_mart.article` rdm
LEFT JOIN `ocean-breeze-tier-2.salesforce.Article__c` a
  ON CAST(rdm.article_id - 1000000000000000 AS STRING) = a.ArticleId__c
LEFT JOIN `ocean-breeze-tier-2.salesforce.Discount_Code__c` dc
  ON dc.Article__c = a.Id
WHERE LOWER(rdm.source_journal) LIKE '%<JOURNAL_NAME>%'
  AND rdm.stage = 'Published'
  AND rdm.is_paying_article = TRUE
ORDER BY rdm.journal, rdm.stage_date_published DESC
```

## Step 3 — Look up current APC rates

For each distinct receiving journal, fetch the current APC from:
`https://www.frontiersin.org/journals/<slug>/for-authors/publishing-fees`

Slug derivation: strip "Frontiers in ", lowercase, replace spaces with hyphens, keep "and" as "-and-".

Extract CHF amounts from the page. The first two distinct amounts in the 500–5000 range are typically the A-type and B-type APCs. C-type is always 0.

## Step 4 — Calculate net fee per article

For each article, determine the net fee:

1. **If a discount record exists with `DecisionStatus__c = 'Processed_Approved'`**: use `NetFee__c` as the actual amount paid, noting the currency.
2. **Otherwise**: assume the full listed APC for the receiving journal and article type category (A/B/C). Currency is CHF.

For USD amounts, convert to CHF using an approximate rate (note the rate used and flag it as approximate).

## Step 5 — Produce output

Generate an Excel workbook with three sheets:

**Sheet 1 — Article Detail:** Article ID, Title, DOI, Source Journal, Receiving Journal, Article Type, Type Category, Published Date, Year, Listed APC (CHF), Discount %, Net Fee Paid, Currency, Fee Method (discount vs full APC), Net Fee (CHF equiv).

**Sheet 2 — By Journal:** Receiving Journal, Article count, Total net APC (CHF equiv). Sorted by total descending.

**Sheet 3 — By Year:** Year, Article count, Total net APC (CHF equiv). Sorted by year.

Print a summary to chat including:
- Grand total (CHF) and article count
- Top receiving journals table
- Yearly breakdown table
- Count of articles at full APC vs verified discount
- Caveats: institutional agreements may mean the institution paid rather than the author; USD conversion is approximate

Export the Excel file and provide the download link.

## Caveats to always note

- Articles without a `Discount_Code__c` record are assumed to have paid full APC — some may have been covered by institutional/consortium agreements where the fee is handled separately.
- APC rates are current at time of query; historical rates may have differed.
- A small number of articles may be invoiced in USD; the CHF conversion is approximate.
