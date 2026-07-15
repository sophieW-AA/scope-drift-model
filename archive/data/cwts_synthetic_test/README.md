# Synthetic CWTS test files

Small citation network designed to produce **several** Leiden clusters when you use **low publication thresholds** (defaults like 25/250/1000 merge everything on tiny graphs).

## Files

- `pubs.txt` — `pub_no` 0…N−1, all **core** (`1`).
- `cit_links.txt` — **bidirectional** edges, sorted by `(pub_no1, pub_no2)` (required by CWTS `Network(..., sortedEdges=True)`).
- `generate_fixture.py` — regenerate with different clique counts/sizes.

## Regenerate

```bash
python generate_fixture.py
```

## Run CWTS (example)

From your `publicationclassification` clone, after `gradlew.bat build`, adjust paths:

```powershell
$JAR = "C:\Users\sophie.wilson\publicationclassification\build\libs\publicationclassification-1.1.0-1-g0894840.jar"
$HERE = "C:\Users\sophie.wilson\OneDrive - Frontiers Media SA\Repos\Sophie\2026\Scope drift oksana\cwts_synthetic_test"

java -Xmx2g -cp "$JAR" nl.cwts.publicationclassification.run.PublicationClassificationCreator `
  "$HERE\pubs.txt" "$HERE\cit_links.txt" "$HERE\classification.txt" `
  true 100 `
  0.02 3 `
  0.01 3 `
  0.005 3
```

Arguments: `largest_component`, `n_iterations`, then for each level `resolution` and **min publications per cluster** (use **3** here so 3×8-node cliques can stay split). If you still get one cluster, try **higher micro resolution** (e.g. `0.05`) or **threshold 2**.

Check stdout for **“Number of clusters:”** after micro/meso/macro.

## Inspect output

`classification.txt` is four tab-separated columns: `pub_no`, micro, meso, macro (no header).
