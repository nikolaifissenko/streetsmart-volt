#!/usr/bin/env python3
"""Riconcilia il master CSV con le segnalazioni reali raccolte via Formspree
tra il 20 e il 21 luglio 2026 (10 segnalazioni nuove, incollate a mano da
Nikolai dall'export Formspree).

A differenza degli altri script reconcile_segnalazioni_*.py, qui le vie sono
risolte a mano riga per riga invece che per nome normalizzato, perché il
lotto conteneva casi ambigui che un matching automatico avrebbe gestito
male:
- "Via Collatina Vecchia" (18 lug, 13:09) è un duplicato esatto di una
  segnalazione già riconciliata in reconcile_segnalazioni_luglio.py — saltata.
- "Galleria Principe Amedeo Savoia Aosta" ha due righe nel master che
  rappresentano le due direzioni (SS-ROM-0733 rosso senza ciclabile,
  SS-ROM-0734 verde con ciclabile verso il Tevere) — la segnalazione reale
  conferma esattamente questa distinzione, quindi non viene ricolorata
  nessuna delle due righe (un match per nome normalizzato le avrebbe
  fuse in una sola), solo confermata la testimonianza su entrambe.
- "Viale Oceano Atlantico"/"Viale Oceano Pacifico" (senza "dell'") non
  matchano per nome normalizzato le righe esistenti "Viale dell'Oceano
  Atlantico/Pacifico" — risolte a mano verso le righe corrette in base al
  municipio IX/EUR indicato dalla segnalazione.
- "Via Grottaperfetta" e "Via Aurelia" non erano presenti nel dataset:
  aggiunte come nuove righe (a differenza degli altri script reconcile,
  che lasciano le vie nuove a parse_segnalazioni.py — qui gestite inline
  perché sono solo due).
"""
import csv
from pathlib import Path

ROOT = Path(__file__).parent.parent
MASTER = ROOT / "data" / "master" / "streetsmart_roma_completo.csv"

SCORES = {"nero": 5, "rosso": 4, "giallo": 3, "blu": 2, "verde": 1}

# Aggiornamenti su vie già presenti, risolti per id: (id, nuovo_colore o None, nota_utente, data)
UPDATES = [
    ("SS-ROM-0234", "nero", "Traffico molto intenso, con auto che, provenendo da 3-4 corsie, "
     "fanno a gara per spartirsi le 2 di via Druso. Solo con traffico bloccato la via diventa "
     "meno pericolosa", "2026-07-20"),
    ("SS-ROM-0059", "rosso", "Non c'è più la ciclabile su questo tratto e il traffico è intenso "
     "(ma il marciapiede è ampio ;-) )", "2026-07-20"),
    ("SS-ROM-13536", "giallo", "Non è pedonale", "2026-07-20"),
    ("SS-ROM-0054", "blu", "", "2026-07-20"),
    ("SS-ROM-15506", "verde", "Adesso ci sono le ciclabili ma con punti di attenzione importanti "
     "al semaforo", "2026-07-21"),
    ("SS-ROM-0341", "verde", "Adesso ci sono le ciclabili ma con punti di attenzione importanti "
     "al semaforo", "2026-07-21"),
    ("SS-ROM-15508", "verde", "Adesso ci sono le ciclabili", "2026-07-21"),
]
UPDATES_MUNICIPIO = {
    "SS-ROM-15506": "IX",
    "SS-ROM-15508": "IX",
}

# Confermate senza cambio colore: le due righe già rappresentano le due
# direzioni descritte dalla segnalazione reale (vedi docstring).
CONFIRM_ONLY = [
    ("SS-ROM-0733", "2026-07-20"),
    ("SS-ROM-0734", "2026-07-20"),
]

# Nuove vie, non presenti nel master.
NEW_STREETS = [
    {
        "nome": "Via Grottaperfetta", "quartiere": "Ardeatino", "classificazione": "verde",
        "note": 'Su parte c\'è la ciclabile. Nota utente: quartiere segnalato come "Ardeatino", '
                "non Ostia/Ostiense.",
        "ciclabile_presente": "si", "municipio": "VIII", "data_segnalazione": "2026-07-21",
    },
    {
        "nome": "Via Aurelia", "quartiere": "Aurelio", "classificazione": "nero",
        "note": "Strada molto dissestata che costringe a stare distante dal marciapiede, con "
                "auto e camion che corrono per sopravanzare le altre prima della strettoia e del "
                "semaforo. | Nota utente (tratto diverso, corsia laterale): \"Corsia laterale "
                "con traffico limitato e lento\"",
        "ciclabile_presente": "no", "municipio": "XIII", "data_segnalazione": "2026-07-20",
        "n_testimonianze": 2,
    },
]


def main():
    with open(MASTER, encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = [row for row in reader]

    idx = {name: header.index(name) for name in [
        "id", "nome", "quartiere", "classificazione", "score", "note",
        "ciclabile_presente", "n_corsie", "senso_unico",
        "n_testimonianze", "municipio", "data_segnalazione",
    ]}
    id_to_row = {row[idx["id"]]: row for row in rows}

    ricolorate, confermate = [], []

    for street_id, new_color, user_note, date in UPDATES:
        row = id_to_row[street_id]
        old_color = row[idx["classificazione"]]
        note_parts = []
        if old_color != new_color:
            row[idx["classificazione"]] = new_color
            row[idx["score"]] = str(SCORES[new_color])
            if new_color == "verde":
                row[idx["ciclabile_presente"]] = "si"
            note_parts.append(f"Ricolorato da {old_color} a {new_color} in base a 1 segnalazione reale (ultima: {date}).")
            ricolorate.append((row[idx["nome"]], old_color, new_color))
        else:
            note_parts.append(f"Confermato {old_color} da 1 segnalazione reale (ultima: {date}).")
            confermate.append((row[idx["nome"]], old_color))
        if user_note:
            note_parts.append(f'Nota utente: "{user_note}"')
        existing_note = row[idx["note"]].strip()
        addition = " | ".join(note_parts)
        row[idx["note"]] = (existing_note + " | " + addition) if existing_note else addition
        if street_id in UPDATES_MUNICIPIO:
            row[idx["municipio"]] = UPDATES_MUNICIPIO[street_id]
            row[idx["quartiere"]] = f"Municipio Roma {UPDATES_MUNICIPIO[street_id]}"
        row[idx["n_testimonianze"]] = str(int(row[idx["n_testimonianze"]] or 0) + 1)
        row[idx["data_segnalazione"]] = date

    for street_id, date in CONFIRM_ONLY:
        row = id_to_row[street_id]
        note_add = f"Confermato {row[idx['classificazione']]} da 1 segnalazione reale, direzione coerente con la riga esistente (ultima: {date})."
        existing_note = row[idx["note"]].strip()
        row[idx["note"]] = (existing_note + " | " + note_add) if existing_note else note_add
        row[idx["n_testimonianze"]] = str(int(row[idx["n_testimonianze"]] or 0) + 1)
        row[idx["data_segnalazione"]] = date
        confermate.append((row[idx["nome"]], row[idx["classificazione"]]))

    last_id = max(int(row[idx["id"]].replace("SS-ROM-", "")) for row in rows)
    new_rows = []
    aggiunte = []
    for s in NEW_STREETS:
        last_id += 1
        new_row = [""] * len(header)
        new_row[idx["id"]] = f"SS-ROM-{last_id:04d}"
        new_row[idx["nome"]] = s["nome"]
        new_row[idx["quartiere"]] = s["quartiere"]
        new_row[idx["classificazione"]] = s["classificazione"]
        new_row[idx["score"]] = str(SCORES[s["classificazione"]])
        new_row[idx["note"]] = s["note"]
        new_row[idx["ciclabile_presente"]] = s["ciclabile_presente"]
        new_row[idx["n_corsie"]] = ""
        new_row[idx["senso_unico"]] = ""
        new_row[idx["n_testimonianze"]] = str(s.get("n_testimonianze", 1))
        new_row[idx["municipio"]] = s["municipio"]
        new_row[idx["data_segnalazione"]] = s["data_segnalazione"]
        new_rows.append(new_row)
        aggiunte.append((s["nome"], s["classificazione"]))

    rows.extend(new_rows)

    with open(MASTER, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)

    print(f"Strade ricolorate: {len(ricolorate)}")
    for nome, old, new in ricolorate:
        print(f"  {nome}: {old} -> {new}")

    print(f"\nStrade confermate (colore invariato): {len(confermate)}")
    for nome, colore in confermate:
        print(f"  {nome}: {colore} confermato")

    print(f"\nStrade nuove aggiunte: {len(aggiunte)}")
    for nome, colore in aggiunte:
        print(f"  {nome}: {colore}")

    print(f"\nSaltate (duplicato di reconcile_segnalazioni_luglio.py): Via Collatina Vecchia (18 lug)")
    print(f"Totale strade nel master: {len(rows)}. Ultimo ID: SS-ROM-{last_id:04d}")


if __name__ == "__main__":
    main()
