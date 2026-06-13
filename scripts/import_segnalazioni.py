#!/usr/bin/env python3
"""
StreetSmart import_segnalazioni.py
Converte un export CSV di Formspree del form di segnalazione
(web/segnalazione_form.html) in righe pronte da appendere a
data/master/streetsmart_roma_completo.csv.

Colonne attese nell'export Formspree (altre colonne vengono ignorate):
  strada, quartiere, municipio, classificazione, note, posizione

- "municipio" puo' essere "I — Centro Storico" o solo "I": viene estratto
  il numero romano.
- "posizione" puo' contenere un link Google Maps con coordinate
  (es. "https://maps.google.com/?q=41.9,12.5") o "lat,lon": se presente
  vengono estratte lat/lon (non scritte nel CSV master, che non ha quelle
  colonne, ma stampate a video per riferimento/geocoding manuale).
- score e ciclabile_presente sono derivati dalla classificazione.
- Righe che corrispondono a una via+quartiere+classificazione gia'
  presente nel master vengono segnalate come probabile duplicato
  (da unire a mano incrementando n_testimonianze, non aggiunte).

Uso:
  python scripts/import_segnalazioni.py export_formspree.csv

Output:
  stampa a video le righe CSV pronte da copiare in
  data/master/streetsmart_roma_completo.csv, con ID incrementali a
  partire dall'ultimo usato.
"""

import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
MASTER_CSV = ROOT / "data" / "master" / "streetsmart_roma_completo.csv"

SCORE_MAP = {"nero": 5, "rosso": 4, "giallo": 3, "blu": 2, "verde-giallo": 2, "verde-blu": 1, "verde": 1}
CICLABILE_MAP = {"verde": "si", "verde-giallo": "si", "verde-blu": "si"}

COORD_RE = re.compile(r'(-?\d{1,2}\.\d+)\s*,\s*(-?\d{1,3}\.\d+)')


def extract_municipio(value):
    value = (value or "").strip()
    if not value:
        return ""
    return value.split("—")[0].split("-")[0].strip()


def extract_coords(value):
    value = (value or "").strip()
    m = COORD_RE.search(value)
    if m:
        return m.group(1), m.group(2)
    return None


def load_master():
    rows = []
    last_num = 0
    existing_keys = set()
    with open(MASTER_CSV, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row = {k: v.strip() for k, v in row.items()}
            rows.append(row)
            m = re.match(r"SS-ROM-(\d+)", row["id"])
            if m:
                last_num = max(last_num, int(m.group(1)))
            key = (row["nome"].strip().lower(), row["quartiere"].strip().lower(), row["classificazione"].strip().lower())
            existing_keys.add(key)
    return last_num, existing_keys


def main():
    if len(sys.argv) != 2:
        print("Uso: python scripts/import_segnalazioni.py export_formspree.csv")
        sys.exit(1)

    input_csv = Path(sys.argv[1])
    if not input_csv.exists():
        print(f"ERRORE: file non trovato: {input_csv}")
        sys.exit(1)

    last_num, existing_keys = load_master()
    next_num = last_num + 1

    new_rows = []
    duplicates = []
    skipped = []

    with open(input_csv, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row = {k: (v or "").strip() for k, v in row.items()}
            nome = row.get("strada", "")
            quartiere = row.get("quartiere", "")
            cls = row.get("classificazione", "").strip().lower()
            municipio = extract_municipio(row.get("municipio", ""))
            note = row.get("note", "")

            if not nome or cls not in SCORE_MAP:
                skipped.append(row)
                continue

            key = (nome.strip().lower(), quartiere.strip().lower(), cls)
            if key in existing_keys:
                duplicates.append((nome, quartiere, cls))
                continue

            score = SCORE_MAP[cls]
            ciclabile = CICLABILE_MAP.get(cls, "no")

            new_id = f"SS-ROM-{next_num:04d}"
            next_num += 1

            new_rows.append([
                new_id, nome, quartiere, cls, str(score), note or "segnalazione community Sentinelle",
                ciclabile, "2", "no", "1", municipio
            ])

            coords = extract_coords(row.get("posizione", ""))
            if coords:
                print(f"# {new_id}: coordinate trovate {coords[0]},{coords[1]} -> aggiungere alla cache geocoding se serve")

    print("\n--- Righe da appendere a data/master/streetsmart_roma_completo.csv ---")
    for r in new_rows:
        print(",".join(r))

    print(f"\n# Nuove righe: {len(new_rows)}")
    if duplicates:
        print(f"# Probabili duplicati (gia' presenti, considera +1 a n_testimonianze a mano):")
        for d in duplicates:
            print(f"#   {d[0]} | {d[1]} | {d[2]}")
    if skipped:
        print(f"# Righe scartate (strada o classificazione mancante/non valida): {len(skipped)}")


if __name__ == "__main__":
    main()
