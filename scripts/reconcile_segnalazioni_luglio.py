#!/usr/bin/env python3
"""Riconcilia il master CSV con le segnalazioni reali raccolte via Formspree
tra il 6 e il 18 luglio 2026 (16 segnalazioni geolocalizzate su vie già
presenti nel dataset).

A differenza di parse_segnalazioni.py (che aggiunge solo vie nuove), questo
script aggiorna vie già presenti: se il colore riportato dalle segnalazioni
reali diverge dal colore corrente (spesso auto-classificato da OSM, mai
verificato), lo corregge; corregge anche il municipio quando la
geolocalizzazione della segnalazione lo smentisce; incrementa comunque
n_testimonianze e data_segnalazione anche quando il colore non cambia, per
tracciare che la via è stata confermata da una segnalazione reale.
"""
import csv
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).parent.parent
MASTER = ROOT / "data" / "master" / "streetsmart_roma_completo.csv"

SCORES = {"nero": 5, "rosso": 4, "giallo": 3, "blu": 2, "verde": 1}

MUNICIPIO_MAP = {
    "Lido di Castel Fusano": "X",
    "Lido di Ostia Levante": "X",
}

# data, ora, colore, quartiere, nome, nota (nota può essere vuota)
raw = """Jul 18, 13:09,giallo,Municipio Roma IV,Via Collatina Vecchia,Molto poco trafficata
Jul 18, 09:50,nero,Municipio Roma I,Via Aurelia Antica,Una corsia per senso di marcia molto strette; con traffico moderato/intenso diventa quasi impossibile sorpassare in sicurezza una bici
Jul 15, 16:31,verde,Municipio Roma I,Via Tata Giovanni,
Jul 15, 16:31,verde,Municipio Roma I,Viale di Porta Ardeatina,
Jul 15, 13:37,verde,Municipio Roma I,Via dei Cerchi,
Jul 15, 13:37,verde,Municipio Roma I,Via dei Cerchi,
Jul 15, 13:37,verde,Municipio Roma I,Via dei Cerchi,
Jul 15, 13:37,verde,Municipio Roma I,Via dei Cerchi,
Jul 15, 13:37,verde,Municipio Roma I,Via dei Cerchi,
Jul 15, 13:37,verde,Municipio Roma I,Via dei Cerchi,
Jul 8, 14:50,giallo,Municipio Roma I,Via Marianna Dionigi,
Jul 6, 08:47,verde,Lido di Castel Fusano,Lungomare Amerigo Vespucci,
Jul 6, 08:47,verde,Lido di Castel Fusano,Lungomare Amerigo Vespucci,
Jul 6, 08:47,verde,Lido di Ostia Levante,Lungomare Duilio,
Jul 6, 08:46,verde,Lido di Ostia Levante,Piazzale Magellano,
Jul 6, 08:46,verde,Lido di Ostia Levante,Lungomare Paolo Toscanelli,"""

MONTHS = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
          "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}


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


def parse_date(day_month_str):
    mon, day = day_month_str.split()
    return f"2026-{MONTHS[mon]:02d}-{int(day):02d}"


def seg_phrase(n):
    return f"{n} segnalazione reale" if n == 1 else f"{n} segnalazioni reali"


def main():
    records = []
    for line in raw.strip().split("\n"):
        parts = line.split(",", 5)
        date_str, _ora, colore, quartiere, nome = [p.strip() for p in parts[:5]]
        nota = parts[5].strip() if len(parts) > 5 else ""
        records.append({
            "date": parse_date(date_str),
            "c": colore,
            "q": quartiere,
            "v": nome,
            "note": nota,
        })
    print(f"Segnalazioni caricate: {len(records)}")

    groups = defaultdict(list)
    for r in records:
        groups[norm(r["v"])].append(r)
    print(f"Vie distinte: {len(groups)}")

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

    ricolorate, confermate, non_trovate = [], [], []

    for key, recs in sorted(groups.items()):
        counts = Counter(r["c"] for r in recs)
        max_count = max(counts.values())
        top_colors = [c for c, ct in counts.items() if ct == max_count]
        if len(top_colors) == 1:
            majority = top_colors[0]
        else:
            recs_by_recency = sorted(recs, key=lambda r: r["date"], reverse=True)
            majority = next(r["c"] for r in recs_by_recency if r["c"] in top_colors)
        last_date = max(r["date"] for r in recs)
        n = len(recs)
        reported_municipio = municipio_from_quartiere(Counter(r["q"] for r in recs).most_common(1)[0][0])
        user_note = next((r["note"] for r in recs if r["note"]), "")

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

            if user_note:
                note_parts.append(f'Nota utente: "{user_note}"')

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

    if non_trovate:
        print(f"\nVie segnalate ma non trovate nel master: {len(non_trovate)}")
        for nome, n in non_trovate:
            print(f"  {nome} ({n} segnalazioni)")


if __name__ == "__main__":
    main()
