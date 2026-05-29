import json

with open('output/scope_global_network.json') as f:
    d = json.load(f)

for j in d['journals']:
    print(f"\n=== {j['name']} ({j['out_of_scope_pct']}% OOS) ===")
    for c in j['top_communities'][:5]:
        primary = "✓" if c['is_primary'] else "✗"
        print(f"  {c['share_of_journal']:5.1f}% - {c['label']} [{primary}]")
