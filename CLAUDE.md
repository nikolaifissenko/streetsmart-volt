# StreetSmart — Contesto Progetto per Claude Code

## Cos'è
Database B2B delle strade di Roma classificate per pericolosità ciclistica.
Vendibile a operatori di micromobilità (Lime, Dott, Tier), Comuni, app di navigazione.
Sviluppato da Nikolai.

## Sistema di Classificazione
| Colore | Score | Significato |
|--------|-------|-------------|
| nero | 5 | Multicarreggiata ad alta velocità, pericolosissimo |
| rosso | 4 | Strada trafficata senza ciclabile |
| giallo | 3 | Strada urbana tranquilla senza ciclabile |
| verde | 1 | Pista ciclabile presente |
| blu | 2 | ZTL / pedonale / alto flusso pedoni |
| verde-giallo | 2 | Ciclabile presente ma inadeguata |
| verde-blu | 1 | Bike friendly ma alto flusso pedonale |

## Stack Tecnico
- **Database**: CSV → target GeoJSON / API REST
- **Schema colonne**: id, nome, quartiere, classificazione, score, note, ciclabile_presente, n_corsie, senso_unico, n_testimonianze, municipio
- **ID formato**: SS-ROM-XXXX (ultimo usato: SS-ROM-0441)
- **Hosting**: GitHub Pages — nikolaifissenko/Streetsmart-Sentille
- **Form backend**: Formspree endpoint `xlgookeg`

## File Master
`data/master/streetsmart_roma_completo.csv` — source of truth.
Non modificare i CSV in data/municipio/ senza aggiornare il master.

## Stato Database
- **433 strade** classificate totali
- Municipio I: ~80 strade (completato)
- Municipio II: ~80 strade (completato + segnalazioni Sentinelle)
- Municipio III: ~50 strade (completato + segnalazioni Sentinelle)
- Municipi IV, V, VII, VIII, IX, XI, XII, XIII, XIV, XV: segnalazioni Sentinelle, CSV dedicati in data/municipio/
- Ultimo ID usato: SS-ROM-0441

## Community Sentinelle
- Form iscrizione: nikolaifissenko.github.io/Streetsmart-Sentille/sentinelle_form.html
- Form segnalazione: nikolaifissenko.github.io/Streetsmart-Sentille/segnalazione_form.html
- Obiettivo: 100 Sentinelle, poi portare il database alle istituzioni

## Social
- Instagram: @streetsmart.nav — tono urban rebel, community building, italiano
- Post con statistiche: usare i numeri da `docs/stats.json` / `docs/stats.md`
  (generati da `scripts/stats.py`, sempre aggiornati)
- Formato caption tipo:
  - hook iniziale con emoji + numero shock (es. "433 STRADE MAPPATE")
  - 2-4 bullet con percentuali chiave (% pericolose, % ciclabili, municipio peggiore)
  - chiusura con CTA doppia: segnala una strada (link form segnalazione) +
    unisciti alle Sentinelle (link form iscrizione, ricordare obiettivo 100)
  - hashtag: #StreetSmart #Roma #ciclabili #micromobilità #datidiquartiere
- Tono: diretto, dati come "prova", mai vittimista — invita all'azione

## Struttura Directory
```
streetsmart/
├── CLAUDE.md                        # questo file
├── data/
│   ├── master/
│   │   └── streetsmart_roma_completo.csv   # SOURCE OF TRUTH
│   ├── municipio/
│   │   ├── municipio1_final.csv
│   │   ├── municipio2.csv
│   │   ├── municipio3.csv
│   │   ├── municipio4.csv
│   │   ├── municipio5.csv
│   │   ├── municipio7.csv
│   │   ├── municipio8.csv
│   │   ├── municipio9.csv
│   │   ├── municipio11.csv
│   │   ├── municipio12.csv
│   │   ├── municipio13.csv
│   │   ├── municipio14.csv
│   │   └── municipio15.csv
│   └── archive/                     # vecchie versioni, non toccare
│       └── municipio1_v1.csv
├── web/
│   ├── sentinelle_form.html
│   ├── segnalazione_form.html
│   ├── mappa.html                   # mappa Leaflet del GeoJSON
│   └── stato_sentinelle.html        # progresso community + stats
├── docs/
│   ├── pdf/                         # materiali presentazione
│   ├── stats.md / stats.json        # statistiche generate da scripts/stats.py
│   └── one_pager_tech.md            # pitch B2B generato da scripts/generate_one_pager.py
├── dist/
│   ├── streetsmart_roma.geojson     # generato da scripts/build.py
│   └── api/                         # snapshot JSON generati da scripts/export_api.py
└── scripts/
    ├── build.py                     # CSV -> GeoJSON (+ geocoding)
    ├── validate.py                  # controllo integrità CSV
    ├── stats.py                     # statistiche per docs/
    ├── export_api.py                # snapshot JSON API statica
    ├── generate_one_pager.py        # one-pager pitch da stats.json
    └── import_segnalazioni.py       # converte export Formspree in righe CSV
```

## Workflow Aggiunta Strade
1. Aggiungere righe a `data/master/streetsmart_roma_completo.csv`
2. Incrementare ID da SS-ROM-0441
3. Aggiornare anche il CSV del municipio corrispondente in `data/municipio/`
4. Aggiornare il contatore in questo file (riga "437 strade")
