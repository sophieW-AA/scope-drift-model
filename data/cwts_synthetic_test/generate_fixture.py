"""
Write pubs.txt + cit_links.txt for CWTS PublicationClassificationCreator.

CWTS FileIO builds Network(..., sortedEdges=True): each undirected link must appear
twice (both directions), sorted by (pub_no1, pub_no2).

Run: python generate_fixture.py
"""

from __future__ import annotations

from pathlib import Path

OUT = Path(__file__).resolve().parent


def write_fixture(
    n_cliques: int = 3,
    clique_size: int = 8,
    weight: float = 1.0,
) -> None:
    n = n_cliques * clique_size
    pubs_lines = [f"{i}\t1" for i in range(n)]
    (OUT / "pubs.txt").write_text("\n".join(pubs_lines) + "\n", encoding="utf-8")

    edges: list[tuple[int, int, float]] = []
    for c in range(n_cliques):
        base = c * clique_size
        nodes = list(range(base, base + clique_size))
        for i, u in enumerate(nodes):
            for v in nodes[i + 1 :]:
                edges.append((u, v, weight))
                edges.append((v, u, weight))
        if c < n_cliques - 1:
            u = base + clique_size - 1
            v = base + clique_size
            edges.append((u, v, weight))
            edges.append((v, u, weight))

    edges.sort(key=lambda t: (t[0], t[1]))
    cit_lines = [f"{a}\t{b}\t{w}" for a, b, w in edges]
    (OUT / "cit_links.txt").write_text("\n".join(cit_lines) + "\n", encoding="utf-8")

    print(f"Wrote {OUT / 'pubs.txt'} ({n} rows)")
    print(f"Wrote {OUT / 'cit_links.txt'} ({len(edges)} directed rows)")


if __name__ == "__main__":
    write_fixture()
