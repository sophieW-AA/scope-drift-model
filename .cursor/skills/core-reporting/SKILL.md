---
name: core-reporting
description: >
  Build branded PDF and Excel reports for Frontiers Media SA. Use when the user needs to export analysis results, dashboards, or data summaries into professional documents. Applies Frontiers brand guidelines (colors, typography, logos) and produces publication-ready output files.
---

# Report Builder

## Overview

This skill generates branded PDF and Excel reports from analysis results, applying Frontiers visual identity.

## When to Use

- Exporting a dashboard or analysis as a PDF
- Creating an Excel workbook with formatted data tables
- Building a presentation-ready report for stakeholders
- Any output that needs to look professional and on-brand

## Prerequisites

- `core-brand` — for colors, fonts, and visual identity
- Python libraries: `reportlab` (PDF), `openpyxl` (Excel), `matplotlib` (charts)

## Report Types

### PDF Report
- Cover page with Frontiers branding
- Table of contents (for multi-section reports)
- Charts and visualizations
- Data tables
- Executive summary section

### Excel Workbook
- Branded header row with Frontiers colors
- Formatted data tables with filters
- Chart sheets
- Summary/dashboard sheet

## Brand Application

| Element | Value |
|---------|-------|
| Primary color | Refer to `core-brand` skill |
| Font | Refer to `core-brand` skill |
| Logo placement | Top-left on cover, footer on subsequent pages |

## Guidelines

- Always apply brand colors to charts and headers
- Include data source and generation date in footer
- Use consistent number formatting (2 decimal places, thousand separators)
- Export files to `/home/user/` and use `export_file` to share
