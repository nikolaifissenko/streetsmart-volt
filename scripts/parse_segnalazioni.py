#!/usr/bin/env python3
"""Parse Formspree segnalazioni and append to master CSV."""
import csv
import re

SCORES = {"nero": 5, "rosso": 4, "giallo": 3, "blu": 2, "verde": 1}
NOTES = {
    "nero": "multicarreggiata ad alta velocità, pericolosissimo",
    "rosso": "strada trafficata senza ciclabile",
    "giallo": "strada urbana tranquilla senza ciclabile",
    "blu": "ZTL / pedonale / alto flusso pedoni",
    "verde": "pista ciclabile presente",
}

MUNICIPIO_MAP = {
    "Municipio Roma I": "I",
    "Municipio Roma II": "II",
    "Municipio Roma III": "III",
    "Municipio Roma VII": "VII",
    "Municipio Roma VIII": "VIII",
    "Municipio Roma XII": "XII",
    "Municipio Roma XIII": "XIII",
    "Parioli": "II",
    "Pinciano": "II",
    "Flaminio": "I",
    "Nomentano": "II",
    "Trieste": "II",
    "Testaccio": "I",
    "Aurelio": "XIII",
    "Val Melaina": "III",
    "Monte Sacro Alto": "III",
    "Salario": "II",
}

raw = """Jun 13, 07:50,rosso,Municipio Roma XII,Circonvallazione Gianicolense
Jun 13, 07:50,nero,Municipio Roma XII,Via Leone Tredicesimo
Jun 13, 07:50,rosso,Municipio Roma XIII,Via del Casale di San Pio Quinto
Jun 13, 07:49,rosso,Municipio Roma XIII,Via Bartolo da Sassoferrato
Jun 13, 07:49,rosso,Aurelio,Via di Boccea
Jun 13, 07:49,nero,Municipio Roma XIII,Via di Boccea
Jun 16, 04:41,blu,Municipio Roma I,Via del Babuino
Jun 16, 04:42,giallo,Municipio Roma I,Via Federico Cesi
Jun 16, 04:42,giallo,Municipio Roma I,Via Cicerone
Jun 16, 04:42,giallo,Municipio Roma I,Via Plinio
Jun 16, 04:42,rosso,Municipio Roma I,Via Crescenzio
Jun 16, 04:42,rosso,Municipio Roma I,Via Giovanni Vitelleschi
Jun 16, 04:42,rosso,Municipio Roma I,Viale dei Bastioni di Michelangelo
Jun 16, 04:42,verde,Municipio Roma I,Viale delle Milizie
Jun 16, 04:42,verde,Municipio Roma I,Viale Angelico
Jun 16, 06:03,verde,Municipio Roma VIII,Via Francesco Negri
Jun 16, 06:04,blu,Municipio Roma VIII,Via Vito Bering
Jun 16, 06:04,blu,Municipio Roma VIII,Via Federico Nansen
Jun 16, 06:05,giallo,Municipio Roma VIII,Via Giacomo Bove
Jun 16, 06:05,giallo,Municipio Roma VIII,Via Pellegrino Matteucci
Jun 16, 06:05,giallo,Municipio Roma VIII,Piazzale 12 Ottobre 1492
Jun 16, 06:06,verde,Municipio Roma VIII,Via Francesco Antonio Pigafetta
Jun 16, 06:06,giallo,Municipio Roma VIII,Via della Moletta
Jun 16, 06:07,verde,Municipio Roma VIII,Via Prospero Alpino
Jun 16, 06:08,giallo,Municipio Roma VIII,Via di Santa Galla
Jun 16, 06:08,giallo,Municipio Roma VIII,Piazza Giovanni da Verrazzano
Jun 16, 06:09,giallo,Municipio Roma VIII,Via Manfredo Camperio
Jun 16, 06:09,blu,Municipio Roma VIII,Via Ermenegildo Frediani
Jun 16, 06:09,giallo,Municipio Roma VIII,Via Capitan Bavastro
Jun 16, 06:09,blu,Municipio Roma VIII,Via Fernando Colombo
Jun 16, 06:10,giallo,Municipio Roma VIII,Via Bartolomeo Diaz
Jun 16, 06:10,giallo,Municipio Roma VIII,Via Martin Alonzo Pinzòn
Jun 16, 13:13,blu,Municipio Roma I,Piazza dei Crociferi
Jun 16, 13:13,blu,Municipio Roma I,Via del Governo Vecchio
Jun 16, 13:14,rosso,Municipio Roma I,Corso Vittorio Emanuele Secondo
Jun 16, 14:43,giallo,Nomentano,Via Cremona
Jun 16, 14:43,rosso,Nomentano,Viale delle Provincie
Jun 16, 14:43,rosso,Nomentano,Piazzale delle Provincie
Jun 16, 14:43,rosso,Nomentano,Viale Ippocrate
Jun 16, 14:43,rosso,Nomentano,Via Catania
Jun 16, 14:43,verde,Nomentano,Via Tiburtina
Jun 16, 14:43,rosso,Nomentano,Viale delle Provincie
Jun 16, 14:43,rosso,Nomentano,Via Arduino
Jun 16, 14:43,rosso,Nomentano,Via Lorenzo il Magnifico
Jun 16, 14:43,verde,Nomentano,Via di Villa Ricotti
Jun 16, 14:44,verde,Nomentano,Via Nomentana
Jun 16, 14:44,verde,Trieste,Via Nomentana
Jun 16, 14:44,rosso,Municipio Roma III,Via Nomentana
Jun 16, 14:44,rosso,Municipio Roma III,Corso Sempione
Jun 16, 14:44,verde,Municipio Roma III,Viale Tirreno
Jun 16, 14:44,giallo,Municipio Roma III,Viale Tirreno
Jun 16, 14:44,giallo,Municipio Roma III,Via Valle Vermiglio
Jun 16, 14:44,rosso,Parioli,Viale del Casale della Finanziera
Jun 16, 14:44,nero,Parioli,Via Salaria
Jun 16, 14:44,nero,Val Melaina,Via Salaria
Jun 16, 14:45,verde,Municipio Roma III,Via dei Prati Fiscali
Jun 16, 14:45,nero,Val Melaina,Via Salaria
Jun 16, 14:45,rosso,Parioli,Viale della Moschea
Jun 16, 14:45,rosso,Pinciano,Piazza Santiago del Cile
Jun 16, 14:45,giallo,Pinciano,Via Eustachio Manfredi
Jun 16, 14:45,giallo,Parioli,Via di Villa San Filippo
Jun 16, 14:45,verde,Pinciano,Viale Bruno Buozzi
Jun 16, 14:45,giallo,Pinciano,Via Antonio Gramsci
Jun 16, 14:45,rosso,Pinciano,Viale Bruno Buozzi
Jun 16, 14:46,giallo,Flaminio,Via Gaetano Filangieri
Jun 16, 14:46,rosso,Flaminio,Via Gaetano Filangieri
Jun 16, 14:46,giallo,Flaminio,Via Domenico Alberto Azuni
Jun 16, 14:46,rosso,Flaminio,Via Giuseppe Pisanelli
Jun 16, 14:46,rosso,Municipio Roma I,Via Maria Cristina
Jun 16, 14:46,blu,Municipio Roma I,Via di Ripetta
Jun 16, 14:46,giallo,Municipio Roma I,Via di Ripetta
Jun 16, 14:46,giallo,Municipio Roma I,Piazza Augusto Imperatore
Jun 16, 14:47,rosso,Municipio Roma I,Via Vittoria Colonna
Jun 16, 14:47,rosso,Municipio Roma I,Ponte Cavour
Jun 16, 14:47,rosso,Municipio Roma I,Piazza Cavour
Jun 16, 14:47,verde,Municipio Roma I,Via Cicerone
Jun 16, 14:47,giallo,Municipio Roma I,Via Cicerone
Jun 16, 14:47,rosso,Pinciano,Piazzale Flaminio
Jun 17, 04:47,rosso,Salario,Sottovia Ignazio Guidi
Jun 17, 04:47,rosso,Nomentano,Viale del Policlinico
Jun 17, 04:47,rosso,Nomentano,Viale del Policlinico
Jun 17, 04:48,verde,Municipio Roma I,Viale Castro Pretorio
Jun 17, 04:48,verde,Municipio Roma I,Viale Pretoriano
Jun 17, 04:48,verde,Municipio Roma I,Via di Porta San Lorenzo
Jun 17, 04:48,rosso,Municipio Roma I,Via Marsala
Jun 17, 04:48,rosso,Municipio Roma I,Viale Enrico De Nicola
Jun 17, 04:48,rosso,Municipio Roma I,Viale Luigi Einaudi
Jun 17, 04:48,rosso,Municipio Roma I,Piazza della Repubblica
Jun 17, 04:48,rosso,Municipio Roma I,Via Napoli
Jun 17, 04:48,rosso,Municipio Roma I,Largo Magnanapoli
Jun 17, 04:48,rosso,Municipio Roma I,Via Biberatica
Jun 17, 04:48,rosso,Municipio Roma I,Via Quattro Novembre
Jun 17, 04:49,rosso,Municipio Roma I,Via del Plebiscito
Jun 17, 04:49,rosso,Municipio Roma I,Piazza di San Marco
Jun 17, 04:49,rosso,Municipio Roma I,Via del Plebiscito
Jun 17, 04:49,rosso,Municipio Roma I,Largo di Torre Argentina
Jun 17, 04:49,rosso,Municipio Roma I,Corso Vittorio Emanuele Secondo
Jun 17, 04:49,rosso,Municipio Roma I,Corso Vittorio Emanuele Secondo
Jun 17, 04:49,rosso,Municipio Roma I,Corso Vittorio Emanuele Secondo
Jun 17, 04:49,nero,Municipio Roma I,Lungotevere dei Sangallo
Jun 17, 04:49,nero,Municipio Roma I,Lungotevere Tor di Nona
Jun 17, 04:49,nero,Municipio Roma I,Lungotevere Marzio
Jun 17, 04:50,nero,Municipio Roma I,Lungotevere in Augusta
Jun 17, 04:50,nero,Municipio Roma I,Lungotevere in Augusta
Jun 17, 04:50,rosso,Pinciano,Piazzale Flaminio
Jun 17, 04:50,rosso,Trieste,Viale Libia
Jun 17, 04:50,rosso,Trieste,Via delle Valli
Jun 17, 04:50,nero,Trieste,Circonvallazione Salaria
Jun 17, 04:50,rosso,Trieste,Viale Somalia
Jun 17, 04:51,rosso,Trieste,Via Tripoli
Jun 17, 04:51,verde,Nomentano,Via Nomentana
Jun 17, 04:51,rosso,Trieste,Circonvallazione Salaria
Jun 17, 04:51,verde,Nomentano,Via Nomentana
Jun 17, 04:51,rosso,Nomentano,Piazza Bologna
Jun 17, 04:51,rosso,Nomentano,Via Bari
Jun 17, 04:52,rosso,Nomentano,Viale del Policlinico
Jun 17, 04:52,rosso,Nomentano,Via della Lega Lombarda
Jun 17, 04:52,giallo,Nomentano,Viale dell'Università
Jun 17, 04:52,giallo,Municipio Roma II,Viale dell'Università
Jun 17, 04:53,rosso,Municipio Roma I,Ciclabile Roma Termini-Sapienza
Jun 17, 04:53,verde,Municipio Roma I,Via Celio Vibenna
Jun 17, 04:53,verde,Municipio Roma I,Piazza del Colosseo
Jun 17, 04:54,rosso,Municipio Roma I,Via dei Cerchi
Jun 17, 04:54,rosso,Municipio Roma I,Via del Circo Massimo
Jun 17, 04:54,rosso,Municipio Roma I,Via dell'Ara Massima di Ercole
Jun 17, 04:54,giallo,Municipio Roma I,Via dei Cerchi
Jun 17, 04:54,rosso,Municipio Roma I,Via della Greca
Jun 17, 04:54,rosso,Municipio Roma I,Lungotevere Aventino
Jun 17, 04:54,rosso,Municipio Roma I,Via Luigi Petroselli
Jun 17, 04:54,rosso,Municipio Roma I,Via del Teatro di Marcello
Jun 17, 04:54,rosso,Municipio Roma I,Piazza d'Aracoeli
Jun 17, 04:54,rosso,Municipio Roma I,Via d'Aracoeli
Jun 17, 04:55,rosso,Municipio Roma I,Via Nicola Salvi
Jun 17, 04:55,rosso,Municipio Roma I,Via Vittorino da Feltre
Jun 17, 04:55,giallo,Municipio Roma I,Via della Madonna dei Monti
Jun 17, 04:56,blu,Municipio Roma I,Via Leonina
Jun 17, 04:56,blu,Municipio Roma I,Via dei Capocci
Jun 17, 04:56,blu,Municipio Roma I,Via Urbana
Jun 17, 04:56,blu,Municipio Roma I,Via dei Ciancaleoni
Jun 17, 04:56,blu,Municipio Roma I,Via Panisperna
Jun 17, 04:56,blu,Municipio Roma I,Via Cavour
Jun 17, 04:56,blu,Municipio Roma I,Via della Madonna dei Monti
Jun 17, 04:56,giallo,Municipio Roma I,Via Tor de' Conti
Jun 17, 04:56,giallo,Municipio Roma I,Via Baccina
Jun 17, 04:57,rosso,Municipio Roma I,Corso del Rinascimento
Jun 17, 04:57,blu,Municipio Roma I,Via Giustiniani
Jun 17, 04:57,blu,Municipio Roma I,Piazza di Sant'Eustachio
Jun 17, 04:57,blu,Municipio Roma I,Via di Tor Millina
Jun 17, 04:57,blu,Municipio Roma I,Via del Corallo
Jun 17, 04:57,blu,Municipio Roma I,Via dei Coronari
Jun 17, 04:57,blu,Municipio Roma I,Piazza dell'Orologio
Jun 17, 04:57,blu,Municipio Roma I,Via dei Banchi Vecchi
Jun 17, 04:57,blu,Municipio Roma I,Via Giulia
Jun 17, 04:58,blu,Municipio Roma I,Via del Pellegrino
Jun 17, 04:58,blu,Municipio Roma I,Via di Montoro
Jun 17, 04:58,nero,Municipio Roma I,Piazza di Monte Savello
Jun 17, 04:58,nero,Municipio Roma I,Lungotevere dei Pierleoni
Jun 17, 04:58,blu,Municipio Roma I,Via della Corda
Jun 17, 04:58,blu,Municipio Roma I,Via della Corda
Jun 17, 05:02,rosso,Municipio Roma XII,Piazzale Enrico Dunant
Jun 17, 05:02,rosso,Municipio Roma XII,Via di Donna Olimpia
Jun 17, 05:03,rosso,Municipio Roma XII,Via Fonteiana
Jun 17, 05:03,rosso,Municipio Roma XII,Via Abate Ugone
Jun 17, 05:03,rosso,Municipio Roma XII,Clivo Rutario
Jun 17, 05:08,blu,Municipio Roma I,Vicolo delle Orsoline
Jun 17, 05:08,blu,Municipio Roma I,Via Belsiana
Jun 17, 05:08,blu,Municipio Roma I,Via di San Giacomo
Jun 17, 05:08,blu,Municipio Roma I,Via di Gesù e Maria
Jun 17, 05:08,blu,Municipio Roma I,Via Laurina
Jun 17, 05:08,blu,Municipio Roma I,Via della Fontanella
Jun 17, 05:08,blu,Municipio Roma I,Via Angelo Brunetti
Jun 17, 05:08,blu,Municipio Roma I,Via del Vantaggio
Jun 17, 05:08,blu,Municipio Roma I,Via Antonio Canova
Jun 17, 05:09,rosso,Municipio Roma I,Via del Tritone
Jun 17, 05:09,blu,Municipio Roma I,Via Poli
Jun 17, 05:09,blu,Municipio Roma I,Via della Stamperia
Jun 17, 05:09,blu,Municipio Roma I,Vicolo Scavolino
Jun 17, 05:09,blu,Municipio Roma I,Via Bocca di Leone
Jun 17, 05:09,blu,Municipio Roma I,Via Frattina
Jun 17, 05:09,blu,Municipio Roma I,Via della Vite
Jun 17, 05:09,blu,Municipio Roma I,Piazza di San Silvestro
Jun 17, 05:09,blu,Municipio Roma I,Via della Frezza
Jun 17, 05:09,blu,Municipio Roma I,Via dei Condotti
Jun 17, 05:10,blu,Municipio Roma I,Via dell'Umiltà
Jun 17, 05:10,blu,Municipio Roma I,Via della Dataria
Jun 17, 05:10,blu,Municipio Roma I,Via de' Lucchesi
Jun 17, 05:11,rosso,Municipio Roma I,Via del Quirinale
Jun 17, 05:11,giallo,Municipio Roma I,Salita di Montecavallo
Jun 17, 05:18,rosso,Municipio Roma I,Piazza dei Tribunali
Jun 17, 05:18,rosso,Municipio Roma I,Via Triboniano
Jun 17, 05:18,rosso,Municipio Roma I,Via Ulpiano
Jun 17, 05:20,blu,Municipio Roma I,Piazza pia
Jun 17, 10:59,rosso,Flaminio,Corso Italia
Jun 18, 14:53,giallo,Municipio Roma II,Via di Porta Labicana
Jun 18, 14:53,giallo,Municipio Roma II,Via dei Marsi
Jun 18, 14:53,giallo,Municipio Roma II,Via degli Equi
Jun 18, 14:53,giallo,Municipio Roma II,Via dei Lucani
Jun 18, 14:53,giallo,Municipio Roma II,Via dei Marsi
Jun 18, 14:53,giallo,Municipio Roma II,Via dei Campani
Jun 18, 14:53,rosso,Municipio Roma II,Via di Porta Labicana
Jun 18, 14:53,giallo,Municipio Roma II,Via dei Rutoli
Jun 18, 14:54,blu,Municipio Roma II,Via dei Latini
Jun 18, 14:54,blu,Municipio Roma II,Via degli Aurunci
Jun 18, 14:54,blu,Municipio Roma II,Largo degli Osci
Jun 18, 14:54,giallo,Municipio Roma II,Largo degli Osci
Jun 18, 14:54,giallo,Municipio Roma II,Via dei Volsci
Jun 18, 14:54,giallo,Municipio Roma II,Via degli Etruschi
Jun 18, 14:54,giallo,Municipio Roma II,Via dei Sabelli
Jun 18, 14:54,giallo,Municipio Roma II,Via dei Sardi
Jun 18, 14:54,giallo,Municipio Roma II,Via dei Volsci
Jun 18, 14:54,giallo,Municipio Roma II,Via degli Ausoni
Jun 18, 14:54,rosso,Municipio Roma II,Via dei Sabelli
Jun 18, 14:54,giallo,Municipio Roma II,Via dei Volsci
Jun 18, 14:55,giallo,Municipio Roma II,Via dei Sabelli
Jun 18, 14:55,giallo,Municipio Roma I,Via di Porta San Lorenzo
Jun 18, 14:55,giallo,Municipio Roma II,Via dei Corsi
Jun 18, 14:55,giallo,Municipio Roma II,Via dei Ramni
Jun 18, 14:55,giallo,Municipio Roma II,Via dei Taurini
Jun 18, 14:55,rosso,Municipio Roma II,Via dei Marrucini
Jun 18, 14:55,rosso,Municipio Roma II,Piazzale Aldo Moro
Jun 18, 14:56,rosso,Municipio Roma II,Viale Piero Gobetti
Jun 18, 14:56,rosso,Municipio Roma II,Viale Regina Elena
Jun 18, 14:56,rosso,Nomentano,Viale Ippocrate
Jun 18, 14:56,giallo,Nomentano,Via Pavia
Jun 18, 14:56,giallo,Nomentano,Via Treviso
Jun 18, 17:09,rosso,Municipio Roma I,Piazza Vittorio Emanuele Secondo
Jun 18, 17:10,rosso,Municipio Roma I,Via Urbano Rattazzi
Jun 19, 12:54,rosso,Nomentano,Via Rodolfo Lanciani
Jun 19, 12:54,verde,Nomentano,Via Nomentana
Jun 19, 12:54,rosso,Municipio Roma III,Via Nomentana Nuova
Jun 19, 12:55,verde,Municipio Roma III,Viale Tirreno
Jun 19, 12:55,verde,Municipio Roma III,Piazzale Jonio
Jun 19, 12:55,verde,Municipio Roma III,Viale Tirreno
Jun 19, 12:55,verde,Municipio Roma III,Piazza Capri
Jun 19, 12:55,rosso,Municipio Roma III,Viale Tirreno
Jun 19, 12:56,verde,Municipio Roma III,Piazzale Jonio
Jun 19, 12:56,verde,Municipio Roma III,Viale Tirreno
Jun 19, 12:56,verde,Municipio Roma III,Viale Jonio
Jun 19, 12:56,rosso,Monte Sacro Alto,Viale Jonio
Jun 19, 12:56,rosso,Monte Sacro Alto,Via Domenico Comparetti
Jun 19, 14:40,rosso,Municipio Roma I,Via Giovanni Giolitti
Jun 19, 14:40,rosso,Municipio Roma I,Piazza di Porta Maggiore
Jun 19, 14:40,rosso,Municipio Roma VII,Via Casilina
Jun 19, 14:40,rosso,Municipio Roma VII,Piazza Lodi
Jun 19, 14:40,verde,Municipio Roma VII,Via La Spezia
Jun 19, 14:40,rosso,Municipio Roma VII,Via La Spezia
Jun 19, 14:40,giallo,Municipio Roma VII,Via Terni
Jun 19, 14:40,giallo,Municipio Roma VII,Via Terni
Jun 19, 14:40,giallo,Municipio Roma VII,Via Voghera
Jun 19, 14:40,giallo,Municipio Roma VII,Via Pistoia
Jun 19, 14:41,giallo,Municipio Roma VII,Via Volterra
Jun 19, 20:23,giallo,Municipio Roma I,Viale Gabriele D'Annunzio
Jun 19, 20:25,rosso,Municipio Roma I,Viale di Trastevere
Jun 19, 20:25,rosso,Municipio Roma I,Via Luigi Petroselli"""

MASTER = "data/master/streetsmart_roma_completo.csv"

# Read existing streets to avoid duplicates
existing = set()
rows = []
with open(MASTER, "r") as f:
    reader = csv.reader(f)
    header = next(reader)
    for row in reader:
        rows.append(row)
        existing.add(row[1].strip().lower())

last_id = int(rows[-1][0].replace("SS-ROM-", ""))

# Parse and deduplicate
seen_in_batch = set()
new_rows = []

for line in raw.strip().split("\n"):
    parts = line.split(",")
    # format: date, time, color, quartiere, nome
    if len(parts) < 5:
        continue
    colore = parts[2].strip()
    quartiere = parts[3].strip()
    nome = ",".join(parts[4:]).strip()

    key = nome.lower()
    if key in existing or key in seen_in_batch:
        continue
    seen_in_batch.add(key)

    last_id += 1
    score = SCORES.get(colore, 3)
    note = NOTES.get(colore, "")
    ciclabile = "si" if colore == "verde" else "no"
    municipio = MUNICIPIO_MAP.get(quartiere, "I")

    # Extract date
    date_match = re.match(r"(Jun \d+)", line)
    if date_match:
        day = int(date_match.group(1).split()[1])
        data = f"2026-06-{day:02d}"
    else:
        data = "2026-06-16"

    new_row = [
        f"SS-ROM-{last_id:04d}",
        nome,
        quartiere,
        colore,
        str(score),
        note,
        ciclabile,
        "2",
        "no",
        "1",
        municipio,
        data,
    ]
    new_rows.append(new_row)

# Append to CSV
with open(MASTER, "a") as f:
    writer = csv.writer(f)
    for row in new_rows:
        writer.writerow(row)

print(f"Added {len(new_rows)} new streets. Last ID: SS-ROM-{last_id:04d}")
print(f"Total streets: {len(rows) + len(new_rows)}")
