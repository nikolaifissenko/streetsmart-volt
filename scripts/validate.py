#!/usr/bin/env python3
"""
StreetSmart validate.py
Controlla l'integrità di data/master/streetsmart_roma_completo.csv:
- campi obbligatori presenti
- formato ID (SS-ROM-XXXX) e univocità
- classificazione valida
- score coerente con la classificazione

Uso: python scripts/validate.py
Exit code: 0 se nessun errore, 1 altrimenti.
"""

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
MASTER_CSV = ROOT / "data" / "master" / "streetsmart_roma_completo.csv"

VALID_CLASSIFICATIONS = {"nero", "rosso", "giallo", "verde", "blu", "verde-giallo", "verde-blu"}
SCORE_MAP = {"nero": 5, "rosso": 4, "giallo": 3, "blu": 2, "verde-giallo": 2, "verde-blu": 1, "verde": 1}
REQUIRED_FIELDS = ["id", "nome", "quartiere", "classificazione", "score", "municipio"]


def validate_row(row):
    errors = []

    for field in REQUIRED_FIELDS:
        if not row.get(field, "").strip():
            errors.append(f"campo '{field}' mancante")

    id_val = row.get("id", "")
    if id_val and not id_val.startswith("SS-ROM-"):
        errors.append(f"ID formato non valido: '{id_val}'")

    cls = row.get("classificazione", "").strip()
    if cls and cls not in VALID_CLASSIFICATIONS:
        errors.append(f"classificazione sconosciuta: '{cls}'")

    if cls in SCORE_MAP:
        expected_score = str(SCORE_MAP[cls])
        actual_score = row.get("score", "").strip()
        if actual_score and actual_score != expected_score:
            errors.append(f"score {actual_score} non corrisponde a {cls} (atteso {expected_score})")

    return errors


def main():
    print("=" * 60)
    print("StreetSmart validate.py")
    print("=" * 60)

    if not MASTER_CSV.exists():
        print(f"ERRORE: file non trovato: {MASTER_CSV}")
        sys.exit(1)

    errors_total = []
    seen_ids = {}

    with open(MASTER_CSV, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):
            row = {k: v.strip() for k, v in row.items()}
            for e in validate_row(row):
                errors_total.append(f"  Riga {i} ({row.get('id','')}): {e}")

            id_val = row.get("id", "")
            if id_val:
                if id_val in seen_ids:
                    errors_total.append(
                        f"  Riga {i} ({id_val}): ID duplicato (gia' usato in riga {seen_ids[id_val]})"
                    )
                else:
                    seen_ids[id_val] = i

    print(f"\nRighe lette: {len(seen_ids)}")
    print(f"Errori trovati: {len(errors_total)}")

    if errors_total:
        print("\nERRORI DI VALIDAZIONE:")
        for e in errors_total:
            print(e)
        print(f"\n[FALLITO] {len(errors_total)} errori — controlla il CSV.")
        sys.exit(1)

    print("\nValidazione OK — nessun errore.")
    print("=" * 60)


if __name__ == "__main__":
    main()
