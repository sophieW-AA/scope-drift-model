"""Re-parent meso clusters under the correct macro cluster in clusters.html.

Only the `parent_macro` field of each meso entry is changed. No label text is
created, edited or moved: every macro and meso keeps the exact label string it
already has in the dashboard.

Usage:
    python -X utf8 scripts/relink_meso_macro.py            # dry run report
    python -X utf8 scripts/relink_meso_macro.py --apply    # write (with .bak)
"""

import json
import re
import shutil
import sys
from pathlib import Path

HTML = Path(r"C:\Users\sophie.wilson\Documents\scope_drift_outputs\output\clusters.html")
REPORT = Path(__file__).resolve().parents[1] / "logs" / "meso_macro_relink_report.txt"

# meso cluster id -> macro cluster id it should hang under, chosen by matching
# the meso's existing label against the macro's existing label.
REASSIGN = {
    # --- oncology ---
    0: 37,    # Cancer Immunotherapy        -> Oncological Care and Treatment Integration
    45: 37,   # Cancer Research             -> Oncological Care and Treatment Integration
    35: 37,   # Cancer Imaging              -> Oncological Care and Treatment Integration
    76: 37,   # Radiation Oncology          -> Oncological Care and Treatment Integration
    48: 37,   # Hematologic Malignancies    -> Oncological Care and Treatment Integration
    58: 37,   # Neuro-Oncology Research     -> Oncological Care and Treatment Integration
    135: 37,  # Palliative Care             -> Oncological Care and Treatment Integration
    69: 36,   # Ovarian Cancer              -> Oncological Surgical Pathology Research
    53: 36,   # Prostate Cancer             -> Oncological Surgical Pathology Research
    94: 36,   # Cervical Cancer             -> Oncological Surgical Pathology Research
    26: 24,   # Liver Disease Research      -> Surgical Oncology in Hepatic Disease
    # --- neuroscience / mental health ---
    13: 4,    # Neuroscience Research       -> Neuroscience
    8: 4,     # Neurodegenerative Diseases  -> Neuroscience
    65: 4,    # Autoimmune Neurology        -> Neuroscience
    80: 4,    # Stroke Research             -> Neuroscience
    72: 4,    # Sleep Disorders             -> Neuroscience
    168: 43,  # Traumatic Brain Injury      -> Head and Neck Health Sciences
    5: 32,    # Mental Health Research      -> Maternal and Child Mental Health
    73: 32,   # Mental Health Research      -> Maternal and Child Mental Health
    162: 32,  # Eating Disorders            -> Maternal and Child Mental Health
    # --- cardiometabolic ---
    18: 14,   # Cardiovascular Health       -> Cardiometabolic Health Sciences
    78: 14,   # Cardiovascular Health       -> Cardiometabolic Health Sciences
    32: 14,   # Heart Failure Research      -> Cardiometabolic Health Sciences
    19: 14,   # Diabetes Research           -> Cardiometabolic Health Sciences
    28: 14,   # Kidney Disease              -> Cardiometabolic Health Sciences
    158: 14,  # Venous Thromboembolism      -> Cardiometabolic Health Sciences
    # --- infection / immunity ---
    10: 12,   # COVID-19 Research           -> Infectious Disease and Public Health
    79: 12,   # Tuberculosis Research       -> Infectious Disease and Public Health
    71: 12,   # Vaccine Uptake              -> Infectious Disease and Public Health
    33: 12,   # Respiratory Diseases        -> Infectious Disease and Public Health
    12: 19,   # Antimicrobial Resistance    -> Pathogenesis and Resistance
    110: 19,  # Fungal Infections           -> Pathogenesis and Resistance
    25: 19,   # Skin Diseases               -> Pathogenesis and Resistance
    47: 40,   # Vector-Borne Diseases       -> Parasitology Studies
    133: 35,  # Sexual Health               -> Sexual and Infectious Disease Research
    # --- molecular / cell biology ---
    29: 1,    # Gene Regulation             -> Biochemistry, Genetics and Molecular Biology
    52: 1,    # Genomic Research            -> Biochemistry, Genetics and Molecular Biology
    39: 1,    # Cellular Mechanisms         -> Biochemistry, Genetics and Molecular Biology
    167: 1,   # Cilia Biology               -> Biochemistry, Genetics and Molecular Biology
    38: 1,    # Mendelian Randomization     -> Biochemistry, Genetics and Molecular Biology
    3: 23,    # Wound Healing               -> Integrative Biological Sciences
    85: 23,   # Microbial Ecology           -> Integrative Biological Sciences
    # --- nutrition / microbiome / public health ---
    4: 5,     # Gut Microbiome Research     -> Nutraceuticals and Microbiome Interactions
    16: 5,    # Plant-Based Medicine        -> Nutraceuticals and Microbiome Interactions
    95: 33,   # Health Equity               -> Public Health and Nutrition Dynamics
    157: 33,  # Health Policy Research      -> Public Health and Nutrition Dynamics
    124: 33,  # Child Nutrition             -> Public Health and Nutrition Dynamics
    30: 22,   # Aging and Health            -> Aging Health and Nutrition Research
    150: 38,  # Research Integrity          -> Health Education and Knowledge Dissemination
    # --- clinical specialties ---
    20: 30,   # Ocular Health               -> Ophthalmology
    21: 29,   # Oral Health Research        -> Dentistry
    44: 25,   # Critical Care Medicine      -> Acute Care and Emergency Medicine
    62: 25,   # Surgical Innovations        -> Acute Care and Emergency Medicine
    40: 26,   # Reproductive Health         -> Reproductive Health
    75: 26,   # Maternal Health             -> Reproductive Health
    60: 27,   # Chronic Pain Research       -> Therapeutic Movement Sciences
    64: 27,   # Pain Management             -> Therapeutic Movement Sciences
    92: 27,   # Spinal Disorders            -> Therapeutic Movement Sciences
    42: 21,   # Physical Activity Research  -> Sports medicine
    # --- materials / chemistry / physics ---
    15: 0,    # Advanced Materials          -> Materials Science
    1: 0,     # Electrochemical Energy Storage -> Materials Science
    63: 0,    # Nanoparticle Research       -> Materials Science
    31: 31,   # Quantum Materials           -> Quantum mechanics
    34: 6,    # Perovskite Solar Cells      -> Electronic and photonic properties
    9: 6,     # Biosensing Technologies     -> Electronic and photonic properties
    22: 11,   # Drug Discovery              -> Organic and Organometallic Chemistry
    24: 11,   # Drug Discovery              -> Organic and Organometallic Chemistry
    # --- environment / energy / earth ---
    14: 2,    # Environmental Sustainability -> Earth and Planetary Sciences
    17: 2,    # Environmental Toxicology    -> Earth and Planetary Sciences
    37: 2,    # Air Pollution               -> Earth and Planetary Sciences
    86: 2,    # Water Quality Management    -> Earth and Planetary Sciences
    27: 2,    # Environmental Remediation   -> Earth and Planetary Sciences
    2: 2,     # Sustainable Development     -> Earth and Planetary Sciences
    46: 13,   # Renewable Energy Systems    -> Earth Sciences and Energy Resources
    130: 13,  # Sustainable Energy          -> Earth Sciences and Energy Resources
    # --- agriculture / life sciences ---
    43: 7,    # Plant Stress Responses      -> Agricultural and Biological Sciences
    81: 7,    # Animal Science              -> Agricultural and Biological Sciences
    49: 7,    # Aquaculture Research        -> Agricultural and Biological Sciences
    11: 7,    # Food Science                -> Agricultural and Biological Sciences
    # --- computing / AI / data ---
    7: 17,    # Artificial Intelligence     -> Intelligent Decision-Making Systems
    101: 17,  # Reinforcement Learning      -> Intelligent Decision-Making Systems
    103: 17,  # Explainable AI              -> Intelligent Decision-Making Systems
    6: 8,     # Medical Image Analysis      -> Computer vision
    136: 20,  # Sentiment Analysis          -> Interdisciplinary Language and Health Technology
    147: 20,  # Machine Learning Health     -> Interdisciplinary Language and Health Technology
    77: 20,   # Digital Health              -> Interdisciplinary Language and Health Technology
    36: 28,   # Education Technology        -> Digital Innovation in Education
    # --- business / transport ---
    138: 3,   # Financial Forecasting       -> Business, Management and Accounting
    23: 3,    # Sustainable Tourism         -> Business, Management and Accounting
    175: 47,  # Traffic Flow Prediction     -> Transport Geography
    61: 47,   # Smart Cities                -> Transport Geography
}

# Meso clusters with a placeholder label ("Cluster 194" etc.) carry no topic
# information, so there is no basis to re-parent them. Left exactly as found.
SKIP_UNLABELLED = True


def load(path: Path):
    text = path.read_text(encoding="utf8")
    match = re.search(r"(const D\s*=\s*)(\{.*?\})(;\s*\n)", text, re.S)
    if not match:
        raise SystemExit("could not locate the 'const D = {...};' payload")
    return text, match, json.loads(match.group(2))


def main() -> None:
    apply = "--apply" in sys.argv
    text, match, data = load(HTML)

    macro_label = {m["id"]: m.get("label", "?") for m in data["macro"]}
    macro_size = {m["id"]: m.get("size", 0) for m in data["macro"]}

    moves, kept, skipped, unknown_macro = [], [], [], []
    for meso in data["meso"]:
        mid = meso["id"]
        label = meso.get("label", "?")
        old = meso.get("parent_macro")
        if SKIP_UNLABELLED and re.fullmatch(r"Cluster \d+", str(label)):
            skipped.append((mid, label, old))
            continue
        new = REASSIGN.get(mid)
        if new is None:
            unknown_macro.append((mid, label, old))
            continue
        if new == old:
            kept.append((mid, label, old))
        else:
            moves.append((mid, label, old, new))
        meso["parent_macro"] = new

    # branchvalues:'total' requires macro size >= sum of its children's sizes.
    # Macro sizes were computed from the OLD grouping, so re-parenting leaves
    # some parents "smaller" than their new children. Lift those to the child
    # sum (a size number, not a label) so the sunburst still renders.
    child_sum: dict[int, int] = {}
    for meso in data["meso"]:
        pid = meso.get("parent_macro")
        if pid in macro_size:
            child_sum[pid] = child_sum.get(pid, 0) + meso.get("size", 0)
    resized = []
    for macro in data["macro"]:
        total = child_sum.get(macro["id"], 0)
        if total > macro.get("size", 0):
            resized.append((macro["id"], macro_label[macro["id"]], macro["size"], total))
            macro["size"] = total

    lines = [
        f"source        : {HTML}",
        f"mode          : {'APPLY' if apply else 'DRY RUN'}",
        f"meso re-parented : {len(moves)}",
        f"meso already correct : {len(kept)}",
        f"meso left alone (placeholder label) : {len(skipped)}",
        f"meso with no rule : {len(unknown_macro)}",
        "",
        "NOTE: only the parent_macro field changes. No label text is altered.",
        "",
        "=== RE-PARENTED ===",
    ]
    for mid, label, old, new in sorted(moves, key=lambda r: r[3]):
        lines.append(
            f"  meso C{mid:<4} {label:34s} "
            f"C{old} {macro_label.get(old,'?')[:34]:34s} -> C{new} {macro_label.get(new,'?')}"
        )
    lines += ["", "=== ALREADY UNDER THE RIGHT MACRO ==="]
    for mid, label, old in sorted(kept):
        lines.append(f"  meso C{mid:<4} {label:34s} stays under C{old} {macro_label.get(old,'?')}")
    lines += ["", "=== LEFT UNTOUCHED (placeholder label, no topic to match) ==="]
    for mid, label, old in sorted(skipped):
        lines.append(f"  meso C{mid:<4} {label:34s} stays under C{old} {macro_label.get(old,'?')}")
    if unknown_macro:
        lines += ["", "=== NO RULE (left untouched) ==="]
        for mid, label, old in sorted(unknown_macro):
            lines.append(f"  meso C{mid:<4} {label:34s} under C{old}")

    lines += [
        "",
        "=== MACRO SIZE RAISED TO COVER NEW CHILDREN (branchvalues:'total') ===",
        "    these are article-count numbers, not labels",
    ]
    if resized:
        for pid, lab, old_size, total in resized:
            lines.append(f"  C{pid:<3} {lab:50s} {old_size:>6} -> {total}")
    else:
        lines.append("  none needed - every macro size already covered its children")

    lines += ["", "=== NEW STRUCTURE ==="]
    new_children: dict[int, list] = {}
    for meso in data["meso"]:
        new_children.setdefault(meso.get("parent_macro"), []).append(meso)
    for pid in sorted(macro_label, key=lambda i: -len(new_children.get(i, []))):
        kids = sorted(new_children.get(pid, []), key=lambda m: -m.get("size", 0))
        lines.append(f"MACRO C{pid} {macro_label[pid]}  ({len(kids)} meso)")
        for kid in kids:
            lines.append(f"    meso C{kid['id']:<4} {kid.get('size',0):>6}  {kid.get('label','?')}")

    REPORT.parent.mkdir(exist_ok=True)
    REPORT.write_text("\n".join(lines), encoding="utf8")
    print("\n".join(lines[:10]))
    print(f"\nfull report -> {REPORT}")

    if apply:
        backup = HTML.with_suffix(".html.bak")
        if not backup.exists():
            shutil.copy2(HTML, backup)
            print(f"backup -> {backup}")
        new_json = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
        out = text[: match.start()] + match.group(1) + new_json + match.group(3) + text[match.end():]
        HTML.write_text(out, encoding="utf8")
        print(f"applied {len(moves)} re-parentings to {HTML}")
    else:
        print("dry run only - nothing written. re-run with --apply")


if __name__ == "__main__":
    main()
