"""Find every table in the project that looks like a cluster-label table."""

from google.cloud import bigquery

PROJECT = "ocean-tech-adv-analytics-c-tfs"

SQL = f"""
SELECT c.table_schema, c.table_name,
       STRING_AGG(c.column_name ORDER BY c.ordinal_position) AS cols
FROM `{PROJECT}.region-eu.INFORMATION_SCHEMA.COLUMNS` c
WHERE c.table_name IN (
  SELECT table_name
  FROM `{PROJECT}.region-eu.INFORMATION_SCHEMA.COLUMNS`
  WHERE column_name IN ('short_label', 'cluster_name', 'community_name')
)
GROUP BY c.table_schema, c.table_name
ORDER BY c.table_schema, c.table_name
"""

client = bigquery.Client(project=PROJECT, location="EU")
for r in client.query(SQL).result():
    print(f"{r.table_schema:26s} {r.table_name:48s} {r.cols[:110]}")
