from google.cloud import bigquery

PROJECT = "ocean-tech-adv-analytics-c-tfs"
client = bigquery.Client(project=PROJECT, location="EU")
sql = f"""
SELECT table_schema, table_name, total_rows
FROM `{PROJECT}.region-eu.INFORMATION_SCHEMA.TABLE_STORAGE`
WHERE table_name LIKE 'classification_raw%'
   OR table_name LIKE 'pub_metadata_raw%'
ORDER BY table_name
"""
for r in client.query(sql).result():
    print(f"{r.table_schema:28s} {r.table_name:44s} rows={r.total_rows}")
