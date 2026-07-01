#!/usr/bin/env python3
"""Riconcilia il master CSV con le segnalazioni reali raccolte via Formspree
tra il 9 e il 30 giugno 2026 (280 segnalazioni geolocalizzate).

Per ogni via già presente nel dataset: confronta il colore curato con il
colore maggioritario riportato dalle segnalazioni reali (raggruppate per
nome via normalizzato). Se diverso, aggiorna classificazione + score e
aggiunge una nota di provenienza.

Per le vie segnalate ma assenti dal dataset: le aggiunge come nuove righe
(la geometria verrà cercata su OSM dal prossimo build_fast.py).
"""
import csv
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).parent.parent
MASTER = ROOT / "data" / "master" / "streetsmart_roma_completo.csv"
SEGNALAZIONI = ROOT / "data" / "master" / "segnalazioni_geo_giugno.json"

SCORES = {"nero": 5, "rosso": 4, "giallo": 3, "blu": 2, "verde": 1}

MUNICIPIO_MAP = {
    "Aurelio": "XIII",
    "E.U.R.": "IX",
    "Flaminio": "I",
    "Lido di Castel Fusano": "X",
    "Lido di Ostia Levante": "X",
    "Monte Sacro Alto": "III",
    "Nomentano": "II",
    "Parioli": "II",
    "Pinciano": "II",
    "Salario": "II",
    "Trieste": "II",
    "Testaccio": "I",
    "Val Melaina": "III",
}


def norm(s):
    s = s or ""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def municipio_from_quartiere(q):
    if q in MUNICIPIO_MAP:
        return MUNICIPIO_MAP[q]
    m = re.match(r"Municipio Roma (\w+)", q)
    return m.group(1) if m else ""


def seg_phrase(n):
    return f"{n} segnalazione reale" if n == 1 else f"{n} segnalazioni reali"


def main():
    records = json.loads(SEGNALAZIONI.read_text(encoding="utf-8"))
    print(f"Segnalazioni geolocalizzate caricate: {len(records)}")

    groups = defaultdict(list)
    for r in records:
        groups[norm(r["v"])].append(r)
    print(f"Vie distinte (normalizzate): {len(groups)}")

    with open(MASTER, encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = [row for row in reader]

    idx = {name: header.index(name) for name in [
        "id", "nome", "quartiere", "classificazione", "score", "note",
        "ciclabile_presente", "n_corsie", "senso_unico",
        "n_testimonianze", "municipio", "data_segnalazione",
    ]}

    name_to_rowidxs = defaultdict(list)
    for i, row in enumerate(rows):
        name_to_rowidxs[norm(row[idx["nome"]])].append(i)

    last_id = max(int(row[idx["id"]].replace("SS-ROM-", "")) for row in rows)

    updated, added, new_rows = [], [], []

    for key, recs in sorted(groups.items()):
        counts = Counter(r["c"] for r in recs)
        max_count = max(counts.values())
        top_colors = [c for c, ct in counts.items() if ct == max_count]
        if len(top_colors) == 1:
            majority = top_colors[0]
        else:
            recs_by_recency = sorted(recs, key=lambda r: r["t"], reverse=True)
            majority = next(r["c"] for r in recs_by_recency if r["c"] in top_colors)
        last_date = max(r["t"] for r in recs)[:10]
        n = len(recs)

        if key in name_to_rowidxs:
            for i in name_to_rowidxs[key]:
                row = rows[i]
                current = row[idx["classificazione"]]
                if current != majority:
                    old = current
                    row[idx["classificazione"]] = majority
                    row[idx["score"]] = str(SCORES[majority])
                    note_add = (
                        f"Ricolorato da {old} a {majority} in base a "
                        f"{seg_phrase(n)} (ultima: {last_date})."
                    )
                    existing_note = row[idx["note"]].strip()
                    row[idx["note"]] = (existing_note + " | " + note_add) if existing_note else note_add
                    updated.append((row[idx["nome"]], old, majority, n))
        else:
            last_id += 1
            quartiere = Counter(r["q"] for r in recs).most_common(1)[0][0]
            nome = Counter(r["v"] for r in recs).most_common(1)[0][0]
            municipio = municipio_from_quartiere(quartiere)
            note = f"Aggiunta da {seg_phrase(n)} (ultima: {last_date})."

            new_row = [""] * len(header)
            new_row[idx["id"]] = f"SS-ROM-{last_id:04d}"
            new_row[idx["nome"]] = nome
            new_row[idx["quartiere"]] = quartiere
            new_row[idx["classificazione"]] = majority
            new_row[idx["score"]] = str(SCORES[majority])
            new_row[idx["note"]] = note
            new_row[idx["ciclabile_presente"]] = "si" if majority == "verde" else "no"
            new_row[idx["n_corsie"]] = ""
            new_row[idx["senso_unico"]] = ""
            new_row[idx["n_testimonianze"]] = str(n)
            new_row[idx["municipio"]] = municipio
            new_row[idx["data_segnalazione"]] = last_date
            new_rows.append(new_row)
            added.append((nome, majority, n))

    rows.extend(new_rows)

    with open(MASTER, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)

    print(f"\nStrade ricolorate: {len(updated)}")
    for nome, old, new, n in updated:
        print(f"  {nome}: {old} -> {new} ({n} segnalazioni)")

    print(f"\nStrade nuove aggiunte: {len(added)}")
    for nome, colore, n in added:
        print(f"  {nome}: {colore} ({n} segnalazioni)")

    print(f"\nTotale strade nel master: {len(rows)}. Ultimo ID: SS-ROM-{last_id:04d}")


if __name__ == "__main__":
    main()
