#!/usr/bin/env python3
"""Riconcilia il master CSV con le segnalazioni reali raccolte via Formspree
tra il 9 e il 30 giugno 2026 (280 segnalazioni geolocalizzate, lette da
data/master/segnalazioni_geo_giugno.json).

Stesso meccanismo di reconcile_segnalazioni_luglio.py: per ogni via già
presente nel dataset, confronta il colore curato con il colore maggioritario
riportato dalle segnalazioni reali (raggruppate per nome via normalizzato);
se diverso lo corregge, altrimenti conferma; corregge il municipio quando la
geolocalizzazione lo smentisce; incrementa comunque n_testimonianze e
data_segnalazione anche a colore invariato.

4 vie di questo lotto (Lungomare Duilio, Lungomare Paolo Toscanelli,
Piazzale Magellano, Via dei Cerchi) sono state riconciliate di nuovo a
luglio con dati più recenti (vedi reconcile_segnalazioni_luglio.py) — quel
risultato è più aggiornato e va preservato, quindi qui vengono saltate.
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

SKIP_GIA_RICONCILIATE_A_LUGLIO = {
    "lungomare duilio",
    "lungomare paolo toscanelli",
    "piazzale magellano",
    "via dei cerchi",
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

    ricolorate, confermate, non_trovate, saltate = [], [], [], []

    for key, recs in sorted(groups.items()):
        if key in SKIP_GIA_RICONCILIATE_A_LUGLIO:
            saltate.append((recs[0]["v"], len(recs)))
            continue

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
        reported_municipio = municipio_from_quartiere(Counter(r["q"] for r in recs).most_common(1)[0][0])

        if key not in name_to_rowidxs:
            non_trovate.append((recs[0]["v"], n))
            continue

        for i in name_to_rowidxs[key]:
            row = rows[i]
            old_color = row[idx["classificazione"]]
            old_municipio = row[idx["municipio"]]
            nome = row[idx["nome"]]

            note_parts = []
            if old_color != majority:
                row[idx["classificazione"]] = majority
                row[idx["score"]] = str(SCORES[majority])
                row[idx["ciclabile_presente"]] = "si" if majority == "verde" else row[idx["ciclabile_presente"]]
                note_parts.append(f"Ricolorato da {old_color} a {majority} in base a {seg_phrase(n)} (ultima: {last_date}).")
                ricolorate.append((nome, old_color, majority, n))
            else:
                note_parts.append(f"Confermato {old_color} da {seg_phrase(n)} (ultima: {last_date}).")
                confermate.append((nome, old_color, n))

            existing_note = row[idx["note"]].strip()
            addition = " | ".join(note_parts)
            row[idx["note"]] = (existing_note + " | " + addition) if existing_note else addition

            if reported_municipio and reported_municipio != old_municipio:
                row[idx["municipio"]] = reported_municipio
                row[idx["quartiere"]] = f"Municipio Roma {reported_municipio}"

            row[idx["n_testimonianze"]] = str(int(row[idx["n_testimonianze"]] or 0) + n)
            row[idx["data_segnalazione"]] = last_date

    with open(MASTER, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)

    print(f"\nStrade ricolorate: {len(ricolorate)}")
    for nome, old, new, n in ricolorate:
        print(f"  {nome}: {old} -> {new} ({n} segnalazioni)")

    print(f"\nStrade confermate (colore invariato): {len(confermate)}")
    for nome, colore, n in confermate:
        print(f"  {nome}: {colore} confermato ({n} segnalazioni)")

    print(f"\nVie saltate (già riconciliate con dati più recenti a luglio): {len(saltate)}")
    for nome, n in saltate:
        print(f"  {nome} ({n} segnalazioni)")

    if non_trovate:
        print(f"\nVie segnalate ma non trovate nel master: {len(non_trovate)}")
        for nome, n in non_trovate:
            print(f"  {nome} ({n} segnalazioni)")


if __name__ == "__main__":
    main()
