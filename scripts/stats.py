#!/usr/bin/env python3
"""
StreetSmart stats.py
Genera statistiche aggregate da data/master/streetsmart_roma_completo.csv:
- distribuzione classificazioni totale
- per municipio: numero strade, % rosso/nero (pericolose), % verde (ciclabile)

Scrive anche un report in docs/stats.md e docs/stats.json
(utili per pitch B2B / contenuti social).

Uso: python scripts/stats.py
"""

import csv
import json
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent.parent
MASTER_CSV = ROOT / "data" / "master" / "streetsmart_roma_completo.csv"
DOCS_DIR = ROOT / "docs"
STATS_MD = DOCS_DIR / "stats.md"
STATS_JSON = DOCS_DIR / "stats.json"

PERICOLOSE = {"rosso", "nero"}
CICLABILI = {"verde", "verde-giallo", "verde-blu"}

ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",
         "XI", "XII", "XIII", "XIV", "XV"]


def mun_sort_key(m):
    try:
        return ROMAN.index(m)
    except ValueError:
        return 99


def main():
    print("=" * 60)
    print("StreetSmart stats.py")
    print("=" * 60)

    if not MASTER_CSV.exists():
        print(f"ERRORE: file non trovato: {MASTER_CSV}")
        return

    rows = []
    with open(MASTER_CSV, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({k: v.strip() for k, v in row.items()})

    total = len(rows)

    # Distribuzione totale
    by_class = defaultdict(int)
    for row in rows:
        by_class[row.get("classificazione", "sconosciuta")] += 1

    print(f"\nStrade totali: {total}")
    print("\nDistribuzione classificazioni:")
    for cls, count in sorted(by_class.items(), key=lambda x: -x[1]):
        pct = 100 * count / total
        bar = "█" * (count // 5)
        print(f"  {cls:<14} {count:>4}  {pct:5.1f}%  {bar}")

    # Per municipio
    by_mun = defaultdict(lambda: defaultdict(int))
    for row in rows:
        mun = row.get("municipio", "?") or "?"
        by_mun[mun]["totale"] += 1
        cls = row.get("classificazione", "")
        if cls in PERICOLOSE:
            by_mun[mun]["pericolose"] += 1
        if cls in CICLABILI:
            by_mun[mun]["ciclabili"] += 1

    print("\nPer municipio:")
    print(f"  {'Municipio':<10} {'Totale':>7} {'Rosso/Nero':>11} {'Ciclabili':>10}")
    for mun in sorted(by_mun.keys(), key=mun_sort_key):
        stats = by_mun[mun]
        tot = stats["totale"]
        peric = stats["pericolose"]
        cicl = stats["ciclabili"]
        print(f"  {mun:<10} {tot:>7} {peric:>6} ({100*peric/tot:4.0f}%) {cicl:>5} ({100*cicl/tot:4.0f}%)")

    print("=" * 60)

    # ── Output file ──────────────────────────────────────────────────────
    DOCS_DIR.mkdir(exist_ok=True)
    today = date.today().isoformat()

    municipi = []
    for mun in sorted(by_mun.keys(), key=mun_sort_key):
        stats = by_mun[mun]
        tot = stats["totale"]
        municipi.append({
            "municipio": mun,
            "totale": tot,
            "pericolose": stats["pericolose"],
            "pct_pericolose": round(100 * stats["pericolose"] / tot, 1),
            "ciclabili": stats["ciclabili"],
            "pct_ciclabili": round(100 * stats["ciclabili"] / tot, 1),
        })

    data = {
        "generato_il": today,
        "strade_totali": total,
        "distribuzione_classificazioni": dict(
            sorted(by_class.items(), key=lambda x: -x[1])
        ),
        "per_municipio": municipi,
    }

    with open(STATS_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    lines = []
    lines.append(f"# StreetSmart — Statistiche database")
    lines.append("")
    lines.append(f"_Generato il {today} — {total} strade totali_")
    lines.append("")
    lines.append("## Distribuzione classificazioni")
    lines.append("")
    lines.append("| Classificazione | Strade | % |")
    lines.append("|---|---|---|")
    for cls, count in sorted(by_class.items(), key=lambda x: -x[1]):
        pct = 100 * count / total
        lines.append(f"| {cls} | {count} | {pct:.1f}% |")
    lines.append("")
    lines.append("## Per municipio")
    lines.append("")
    lines.append("| Municipio | Totale | Rosso/Nero | % Pericolose | Ciclabili | % Ciclabili |")
    lines.append("|---|---|---|---|---|---|")
    for m in municipi:
        lines.append(
            f"| {m['municipio']} | {m['totale']} | {m['pericolose']} | "
            f"{m['pct_pericolose']:.1f}% | {m['ciclabili']} | {m['pct_ciclabili']:.1f}% |"
        )
    lines.append("")

    with open(STATS_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"\nReport scritti: {STATS_MD}, {STATS_JSON}")


if __name__ == "__main__":
    main()
