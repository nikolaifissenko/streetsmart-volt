#!/usr/bin/env python3
"""Riconcilia il dataset automatico di Napoli con le segnalazioni reali
raccolte via Formspree (stesso meccanismo di Roma, anche se Segnala/Sentinelle
non è ancora abilitato in PWA per le città diverse da Roma).

Legge cities/napoli/segnalazioni_napoli.csv (log grezzo, una riga per
segnalazione — stesso formato concettuale di
data/master/streetsmart_segnalazioni_aggiornamento.csv usato per Roma),
aggiorna cities/napoli/streetsmart_napoli.csv (classificazione/score/note/
n_testimonianze/data_segnalazione) e propaga le stesse modifiche ai tile
già generati in cities/napoli/tiles/zona-*.geojson, senza dover rifare il
fetch OSM completo con build_city.py.
"""
import csv
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).parent.parent
CITY_DIR = ROOT / "cities" / "napoli"
SEGNALAZIONI = CITY_DIR / "segnalazioni_napoli.csv"
MASTER = CITY_DIR / "streetsmart_napoli.csv"
TILES_DIR = CITY_DIR / "tiles"

SCORES = {"nero": 5, "rosso": 4, "giallo": 3, "blu": 2, "verde": 1}


def norm(s):
    s = s or ""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def seg_phrase(n):
    return f"{n} segnalazione reale" if n == 1 else f"{n} segnalazioni reali"


def main():
    with open(SEGNALAZIONI, encoding="utf-8", newline="") as f:
        records = list(csv.DictReader(f))
    print(f"Segnalazioni Napoli caricate: {len(records)}")

    groups = defaultdict(list)
    for r in records:
        groups[norm(r["strada"])].append(r)
    print(f"Vie distinte: {len(groups)}")

    with open(MASTER, encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = [row for row in reader]

    idx = {name: header.index(name) for name in [
        "id", "nome", "quartiere", "classificazione", "score", "note",
        "ciclabile_presente", "n_corsie", "senso_unico",
        "n_testimonianze", "zona", "data_segnalazione",
    ]}

    name_to_rowidxs = defaultdict(list)
    for i, row in enumerate(rows):
        name_to_rowidxs[norm(row[idx["nome"]])].append(i)

    updated_ids = {}  # id -> dict of new property values, for tile patching
    ricolorate, confermate, non_trovate = [], [], []

    for key, recs in sorted(groups.items()):
        counts = Counter(r["classificazione"] for r in recs)
        max_count = max(counts.values())
        top_colors = [c for c, ct in counts.items() if ct == max_count]
        if len(top_colors) == 1:
            majority = top_colors[0]
        else:
            recs_by_recency = sorted(recs, key=lambda r: r["data"], reverse=True)
            majority = next(r["classificazione"] for r in recs_by_recency if r["classificazione"] in top_colors)
        last_date = max(r["data"] for r in recs)
        n = len(recs)
        user_note = next((r["note"] for r in recs if r.get("note")), "")

        if key not in name_to_rowidxs:
            non_trovate.append((recs[0]["strada"], n))
            continue

        for i in name_to_rowidxs[key]:
            row = rows[i]
            old_color = row[idx["classificazione"]]
            nome = row[idx["nome"]]
            street_id = row[idx["id"]]

            note_parts = []
            if old_color != majority:
                row[idx["classificazione"]] = majority
                row[idx["score"]] = str(SCORES[majority])
                if majority == "verde":
                    row[idx["ciclabile_presente"]] = "si"
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

            row[idx["n_testimonianze"]] = str(int(row[idx["n_testimonianze"]] or 0) + n)
            row[idx["data_segnalazione"]] = last_date

            updated_ids[street_id] = {
                "classificazione": row[idx["classificazione"]],
                "score": int(row[idx["score"]]),
                "note": row[idx["note"]],
                "ciclabile": row[idx["ciclabile_presente"]],
                "n_testimonianze": row[idx["n_testimonianze"]],
            }

    with open(MASTER, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)

    # Propaga le modifiche ai tile già generati, senza rifare il fetch OSM
    patched_features = 0
    for tile_path in sorted(TILES_DIR.glob("zona-*.geojson")):
        with open(tile_path, encoding="utf-8") as f:
            tile = json.load(f)
        changed = False
        for feat in tile["features"]:
            pid = feat["properties"]["id"]
            if pid in updated_ids:
                feat["properties"].update(updated_ids[pid])
                changed = True
                patched_features += 1
        if changed:
            with open(tile_path, "w", encoding="utf-8") as f:
                json.dump(tile, f, ensure_ascii=False)

    print(f"\nStrade ricolorate: {len(ricolorate)}")
    for nome, old, new, n in ricolorate:
        print(f"  {nome}: {old} -> {new} ({n} segnalazioni)")

    print(f"\nStrade confermate (colore invariato): {len(confermate)}")
    for nome, colore, n in confermate:
        print(f"  {nome}: {colore} confermato ({n} segnalazioni)")

    if non_trovate:
        print(f"\nVie segnalate ma non trovate nel dataset: {len(non_trovate)}")
        for nome, n in non_trovate:
            print(f"  {nome} ({n} segnalazioni)")

    print(f"\nTile aggiornati: {patched_features} feature patchate in {TILES_DIR}")


if __name__ == "__main__":
    main()
