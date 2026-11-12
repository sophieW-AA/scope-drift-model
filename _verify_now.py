from google.cloud import bigquery

client = bigquery.Client(project="ocean-tech-adv-analytics-c-tfs", location="EU")
raw = "ocean-tech-adv-analytics-c-tfs.raw_citation_network_data"
read = "ocean-tech-adv-analytics-c-tfs.leiden_output"
ts = "20260827_081311"

queries = {
    "journal_summary": f"""
        SELECT cluster_level, COUNT(*) n_rows, COUNT(DISTINCT journal) n_journals,
               SUM(paper_llm_n_scored) scored, SUM(paper_llm_n_candidates) candidates,
               SUM(paper_llm_n_demoted) demoted
        FROM `{raw}.journal_summary_{ts}`
        GROUP BY 1 ORDER BY 1
    """,
    "paper_scope verdicts": f"""
        SELECT cluster_level,
               COUNT(*) n_rows,
               COUNTIF(paper_llm_verdict IS NOT NULL AND CAST(paper_llm_verdict AS STRING) != '') n_verdicts
        FROM `{raw}.paper_scope_{ts}`
        GROUP BY 1 ORDER BY 1
    """,
    "read journals": f"""
        SELECT cluster_level, COUNT(*) n_rows, COUNT(DISTINCT journal) n_journals
        FROM `{read}.journals`
        WHERE run_timestamp = '{ts}'
        GROUP BY 1 ORDER BY 1
    """,
    "read papers": f"""
        SELECT COUNT(*) n_rows, COUNT(DISTINCT int_id) n_papers,
               COUNTIF(scope_level = 'macro') macro_scope,
               COUNTIF(scope_level = 'meso') meso_scope
        FROM `{read}.papers`
        WHERE run_timestamp = '{ts}'
    """,
}
for name, sql in queries.items():
    print(name)
    try:
        for row in client.query(sql).result():
            print(" ", dict(row.items()))
    except Exception as exc:
        print("  error:", str(exc).split("\n")[0][:400])
