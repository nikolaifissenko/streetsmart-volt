#!/usr/bin/env python3
"""
StreetSmart export_api.py
Genera uno snapshot JSON statico del database a partire da
data/master/streetsmart_roma_completo.csv, da servire come API REST
statica (es. via GitHub Pages) a operatori di micromobilita, Comuni,
app di navigazione.

Output: dist/api/strade.json       — elenco completo
        dist/api/municipi/{N}.json — elenco filtrato per municipio

Uso: python scripts/export_api.py
"""

import csv
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
MASTER_CSV = ROOT / "data" / "master" / "streetsmart_roma_completo.csv"
API_DIR = ROOT / "dist" / "api"
MUNICIPI_DIR = API_DIR / "municipi"


def to_record(row):
    return {
        "id": row.get("id", ""),
        "nome": row.get("nome", ""),
        "quartiere": row.get("quartiere", ""),
        "municipio": row.get("municipio", ""),
        "classificazione": row.get("classificazione", ""),
        "score": int(row["score"]) if row.get("score") else None,
        "ciclabile_presente": row.get("ciclabile_presente", ""),
        "n_corsie": int(row["n_corsie"]) if row.get("n_corsie") else None,
        "senso_unico": row.get("senso_unico", ""),
        "n_testimonianze": int(row["n_testimonianze"]) if row.get("n_testimonianze") else None,
        "note": row.get("note", ""),
    }


def main():
    print("=" * 60)
    print("StreetSmart export_api.py")
    print("=" * 60)

    if not MASTER_CSV.exists():
        print(f"ERRORE: file non trovato: {MASTER_CSV}")
        return

    with open(MASTER_CSV, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [{k: v.strip() for k, v in row.items()} for row in reader]

    records = [to_record(r) for r in rows]

    API_DIR.mkdir(parents=True, exist_ok=True)
    MUNICIPI_DIR.mkdir(parents=True, exist_ok=True)

    with open(API_DIR / "strade.json", "w", encoding="utf-8") as f:
        json.dump({"count": len(records), "strade": records}, f, ensure_ascii=False, indent=2)
    print(f"Scritto {API_DIR / 'strade.json'} ({len(records)} strade)")

    by_mun = {}
    for r in records:
        by_mun.setdefault(r["municipio"], []).append(r)

    for mun, items in by_mun.items():
        safe_mun = mun.replace("/", "-") or "sconosciuto"
        path = MUNICIPI_DIR / f"{safe_mun}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"municipio": mun, "count": len(items), "strade": items}, f, ensure_ascii=False, indent=2)
        print(f"Scritto {path} ({len(items)} strade)")

    print("=" * 60)


if __name__ == "__main__":
    main()
