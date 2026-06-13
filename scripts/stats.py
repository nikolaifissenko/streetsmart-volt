#!/usr/bin/env python3
"""
StreetSmart stats.py
Genera statistiche aggregate da data/master/streetsmart_roma_completo.csv:
- distribuzione classificazioni totale
- per municipio: numero strade, % rosso/nero (pericolose), % verde (ciclabile)

Uso: python scripts/stats.py
"""

import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parent.parent
MASTER_CSV = ROOT / "data" / "master" / "streetsmart_roma_completo.csv"

PERICOLOSE = {"rosso", "nero"}
CICLABILI = {"verde", "verde-giallo", "verde-blu"}


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

    def mun_sort_key(m):
        try:
            from functools import cmp_to_key
            roman = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",
                     "XI", "XII", "XIII", "XIV", "XV"]
            return roman.index(m)
        except ValueError:
            return 99

    print("\nPer municipio:")
    print(f"  {'Municipio':<10} {'Totale':>7} {'Rosso/Nero':>11} {'Ciclabili':>10}")
    for mun in sorted(by_mun.keys(), key=mun_sort_key):
        stats = by_mun[mun]
        tot = stats["totale"]
        peric = stats["pericolose"]
        cicl = stats["ciclabili"]
        print(f"  {mun:<10} {tot:>7} {peric:>6} ({100*peric/tot:4.0f}%) {cicl:>5} ({100*cicl/tot:4.0f}%)")

    print("=" * 60)


if __name__ == "__main__":
    main()
